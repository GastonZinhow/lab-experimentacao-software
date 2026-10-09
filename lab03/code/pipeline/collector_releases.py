from collections import Counter
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import quote

import pandas as pd
import requests

from metrics.datas import parse_data
from pipeline.client import GitHubClient, NotFoundError

API = "https://api.github.com"

# Valores da coluna status_compare em releases.csv
COMPARE_OK = "ok"
COMPARE_404 = "404"
COMPARE_UNAVAILABLE = "indisponivel"
SEM_ANTERIOR = "sem_anterior"
FORA_DA_JANELA = "fora_da_janela"
FORA_DA_SERIE = "fora_da_serie"


class CompareUnavailableError(Exception):
    """O GitHub não conseguiu gerar uma comparação válida dentro do limite."""


def tipo_release(release: Dict[str, Any]) -> str:
    if release.get("draft"):
        return "draft"
    if release.get("prerelease"):
        return "prerelease"
    return "publicada"


def separar_releases(releases_raw: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Separa as releases da API em publicadas, pré-releases e drafts."""
    grupos: Dict[str, List[Dict[str, Any]]] = {"publicada": [], "prerelease": [], "draft": []}
    for r in releases_raw:
        grupos[tipo_release(r)].append(r)
    return grupos


def ligar_anteriores(serie: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ordena a série de releases por published_at e anota em cada uma a tag da
    release anterior (que pode estar fora da janela). A primeira release da
    história fica com tag_anterior=None e sem_anterior=True.
    """
    ordenadas = sorted(
        (r for r in serie if r.get("published_at")),
        key=lambda r: (parse_data(r["published_at"]), r.get("id") or 0),
    )
    ligadas = []
    anterior: Optional[str] = None
    for r in ordenadas:
        ligadas.append({**r, "tag_anterior": anterior, "sem_anterior": anterior is None})
        anterior = r["tag_name"]
    return ligadas


def fetch_releases(client: GitHubClient, owner: str, repo: str) -> List[Dict[str, Any]]:
    return client.paginate(f"{API}/repos/{owner}/{repo}/releases", params={"per_page": 100})


def fetch_compare_commits(
    client: GitHubClient, owner: str, repo: str, base: str, head: str
) -> List[Dict[str, Any]]:
    """
    Commits de head que não estão em base. O compare sem paginação para em 250
    commits, por isso pagina com per_page=100 seguindo o cabeçalho Link.
    Lança NotFoundError se alguma das tags não existir mais e
    CompareUnavailableError quando o GitHub não consegue gerar uma comparação
    muito grande/complexa.
    """
    url = f"{API}/repos/{owner}/{repo}/compare/{quote(base, safe='')}...{quote(head, safe='')}"
    try:
        return client.paginate(url, params={"per_page": 100}, raise_on_404=True)
    except requests.HTTPError as exc:
        response = exc.response
        if response is not None and response.status_code == 422:
            try:
                payload = response.json()
            except ValueError:
                payload = {}
            if any(
                error.get("code") == "not_available"
                for error in payload.get("errors", [])
                if isinstance(error, dict)
            ):
                raise CompareUnavailableError(response.url) from exc
        raise


def _primeira_linha(mensagem: Optional[str]) -> str:
    return (mensagem or "").splitlines()[0] if mensagem else ""


def collect_repo_releases(
    client: GitHubClient,
    owner: str,
    repo: str,
    start_date: str,
    end_date: str,
    incluir_prerelease: bool = False,
    git=None,                      # <-- NOVO
) -> Tuple[pd.DataFrame, pd.DataFrame, Counter]:
    """
    Coleta as releases do repositório e, para cada release da janela [start, end),
    os commits incluídos nela (compare com a release anterior da mesma série).

    A série padrão é a das releases publicadas (draft=false, prerelease=false);
    incluir_prerelease=True usa releases + pré-releases (variante C2 da RQ 07).

    Retorna (df_releases, df_commits, contadores).
    """
    nome = f"{owner}/{repo}"
    inicio, fim = parse_data(start_date), parse_data(end_date)
    print(f"\n[Releases] {nome}...")

    grupos = separar_releases(fetch_releases(client, owner, repo))
    serie = grupos["publicada"] + (grupos["prerelease"] if incluir_prerelease else [])
    ligadas = {r["id"]: r for r in ligar_anteriores(serie)}

    contadores: Counter = Counter(
        releases_publicadas=len(grupos["publicada"]),
        prereleases=len(grupos["prerelease"]),
        drafts_descartados=len(grupos["draft"]),
    )
    linhas_releases: List[Dict[str, Any]] = []
    linhas_commits: List[Dict[str, Any]] = []

    # Drafts não entram em nada: nem no CSV, nem como "release anterior".
    for r in grupos["publicada"] + grupos["prerelease"]:
        publicada_em = r.get("published_at")
        na_janela = bool(publicada_em) and inicio <= parse_data(publicada_em) < fim
        ligada = ligadas.get(r["id"])
        tag_anterior = ligada["tag_anterior"] if ligada else None
        n_commits: Optional[int] = None

        if ligada is None:
            status = FORA_DA_SERIE
        elif not na_janela:
            status = FORA_DA_JANELA
        elif ligada["sem_anterior"]:
            status = SEM_ANTERIOR
            contadores["ignoradas_sem_anterior"] += 1
        else:
            contadores["releases_na_janela_com_anterior"] += 1
            try:
                if git is not None:
                    commits = git.compare_commits(tag_anterior, r["tag_name"])
                else:
                    commits = fetch_compare_commits(client, owner, repo, tag_anterior, r["tag_name"])
            except NotFoundError:
                status = COMPARE_404
                contadores["ignoradas_404"] += 1
                print(f"  [404] compare {tag_anterior}...{r['tag_name']} (tag apagada/reescrita?)")
            except CompareUnavailableError:
                status = COMPARE_UNAVAILABLE
                contadores["ignoradas_indisponivel"] += 1
                print(
                    f"  [422] compare {tag_anterior}...{r['tag_name']} "
                    "(comparação grande demais para a API)"
                )
            else:
                status = COMPARE_OK
                n_commits = len(commits)
                if n_commits == 0:
                    contadores["sem_commits_novos"] += 1
                contadores["commits_coletados"] += n_commits
                for c in commits:
                    info = c.get("commit", {})
                    linhas_commits.append({
                        "repo": nome,
                        "tag_name": r["tag_name"],
                        "tag_anterior": tag_anterior,
                        "release_published_at": publicada_em,
                        "sha": c.get("sha"),
                        "commit_author_date": (info.get("author") or {}).get("date"),
                        "commit_committer_date": (info.get("committer") or {}).get("date"),
                        "mensagem": _primeira_linha(info.get("message")),
                    })

        if na_janela:
            contadores["releases_na_janela"] += 1
        linhas_releases.append({
            "repo": nome,
            "release_id": r.get("id"),
            "tag_name": r.get("tag_name"),
            "nome": r.get("name"),
            "tipo": tipo_release(r),
            "draft": bool(r.get("draft")),
            "prerelease": bool(r.get("prerelease")),
            "created_at": r.get("created_at"),
            "published_at": publicada_em,
            "na_janela": na_janela,
            "tag_anterior": tag_anterior,
            "sem_anterior": bool(ligada and ligada["sem_anterior"]),
            "status_compare": status,
            "n_commits": n_commits,
            "html_url": r.get("html_url"),
        })

    print(
        f"  -> {contadores['releases_publicadas']} publicadas, {contadores['prereleases']} pré-releases, "
        f"{contadores['drafts_descartados']} drafts | na janela: {contadores['releases_na_janela']} | "
        f"ignoradas: {contadores['ignoradas_sem_anterior']} sem anterior, "
        f"{contadores['ignoradas_404']} por 404, "
        f"{contadores['ignoradas_indisponivel']} indisponíveis | "
        f"{contadores['commits_coletados']} commits"
    )
    df_releases = pd.DataFrame(linhas_releases)
    if not df_releases.empty:
        df_releases["n_commits"] = df_releases["n_commits"].astype("Int64")
    return df_releases, pd.DataFrame(linhas_commits), contadores


def collect_repo_tags(
    client: GitHubClient, owner: str, repo: str, max_tags: Optional[int] = None
) -> pd.DataFrame:
    """
    Coleta as tags (variante C3 da RQ 07). Tags não trazem data, então busca o
    commit apontado por cada uma (uma chamada por SHA distinto, com cache).
    max_tags limita quantas tags recebem data (na ordem da API), para repositórios
    com milhares de tags; None busca todas.
    """
    nome = f"{owner}/{repo}"
    tags = client.paginate(f"{API}/repos/{owner}/{repo}/tags", params={"per_page": 100})
    if max_tags is not None:
        tags = tags[:max_tags]

    datas_por_sha: Dict[str, Tuple[Optional[str], Optional[str]]] = {}
    linhas = []
    for t in tags:
        sha = (t.get("commit") or {}).get("sha")
        if sha and sha not in datas_por_sha:
            data, _ = client.get_json(f"{API}/repos/{owner}/{repo}/commits/{sha}")
            info = data.get("commit", {}) if isinstance(data, dict) else {}
            datas_por_sha[sha] = (
                (info.get("author") or {}).get("date"),
                (info.get("committer") or {}).get("date"),
            )
        author_date, committer_date = datas_por_sha.get(sha, (None, None))
        linhas.append({
            "repo": nome,
            "tag_name": t.get("name"),
            "sha": sha,
            "commit_author_date": author_date,
            "commit_committer_date": committer_date,
        })

    sem_data = sum(1 for l in linhas if l["commit_author_date"] is None)
    print(f"[Tags] {nome}: {len(linhas)} tags ({sem_data} sem data do commit)")
    return pd.DataFrame(linhas)


"""
Seleção da amostra (Issue #52): busca de candidatos, critério de inclusão,
metadados dos repositórios e funil de seleção.
"""
import random
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests

from pipeline.client import GitHubClient
from pipeline.collector_runs import collect_repo_runs, contar_runs_janela

API = "https://api.github.com"
SEARCH_CAP = 1000
SEARCH_PAGE_SIZE = 100
GITHUB_FOUNDED = date(2007, 10, 1)

INCLUIDO = "incluido"
DESCARTADO = "descartado"
NAO_AVALIADO = "nao_avaliado"

MOTIVO_ARQUIVADO = "arquivado"
MOTIVO_FORK = "fork"
MOTIVO_INDISPONIVEL = "indisponivel na API"
MOTIVO_SEM_ACTIONS = "sem GitHub Actions (total_count = 0)"
MOTIVO_POUCAS_RELEASES = "menos de {n} releases na janela"
MOTIVO_POUCOS_RUNS = "menos de {n} workflow runs validos na janela"


# ---------------------------------------------------------------------------
# Busca de candidatos
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SearchSlice:
    """Faixa de estrelas e, se necessário, de data de criação."""
    stars_lo: int
    stars_hi: Optional[int] = None
    created_from: Optional[date] = None
    created_to: Optional[date] = None

    def query(self) -> str:
        if self.stars_hi is None:
            q = f"stars:>={self.stars_lo}"
        else:
            q = f"stars:{self.stars_lo}..{self.stars_hi}"

        if self.created_from is not None:
            q += (
                f" created:{self.created_from.isoformat()}"
                f"..{self.created_to.isoformat()}"
            )
        return q

    def split(self, today: date) -> Optional[List["SearchSlice"]]:
        """Divide a faixa em duas; None se não houver como dividir mais."""
        lo, hi = self.stars_lo, self.stars_hi

        if hi is None:
            return [
                SearchSlice(lo, 2 * lo - 1),
                SearchSlice(2 * lo, None),
            ]

        if lo < hi:
            mid = (lo + hi) // 2
            return [
                SearchSlice(lo, mid),
                SearchSlice(mid + 1, hi),
            ]

        start = self.created_from or GITHUB_FOUNDED
        end = self.created_to or today

        if start >= end:
            return None

        mid = start + (end - start) / 2
        mid = mid.date() if isinstance(mid, datetime) else mid

        return [
            SearchSlice(lo, hi, start, mid),
            SearchSlice(lo, hi, mid + timedelta(days=1), end),
        ]


def initial_slices(min_stars: int, breaks: List[int]) -> List[SearchSlice]:
    """Ex.: [1001, 2000, 5000] -> 1001..1999, 2000..4999, >=5000."""
    bounds = [min_stars] + sorted(b for b in breaks if b > min_stars)
    slices = [
        SearchSlice(lo, hi - 1)
        for lo, hi in zip(bounds, bounds[1:])
    ]
    slices.append(SearchSlice(bounds[-1], None))
    return slices


def _slim_search(data: Dict[str, Any]) -> Dict[str, Any]:
    """Guarda somente os campos utilizados da resposta da busca."""
    return {
        "total_count": data.get("total_count", 0),
        "incomplete_results": data.get("incomplete_results", False),
        "items": [
            {
                "id": item["id"],
                "full_name": item["full_name"],
                "owner": item["owner"]["login"],
                "repo": item["name"],
                "stars": item["stargazers_count"],
                "language": item.get("language"),
                "created_at": item.get("created_at"),
                "default_branch": item.get("default_branch"),
                "fork": item.get("fork", False),
                "archived": item.get("archived", False),
            }
            for item in data.get("items", [])
        ],
    }


def _search_page(
    client: GitHubClient,
    query: str,
    page: int,
    per_page: int = SEARCH_PAGE_SIZE,
) -> Dict[str, Any]:
    data, _ = client.get_json(
        f"{API}/search/repositories",
        params={
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
            "page": page,
        },
        transform=_slim_search,
    )
    return data


def plan_slices(
    client: GitHubClient,
    slices: List[SearchSlice],
    today: date,
) -> List[Tuple[SearchSlice, int]]:
    """Subdivide as faixas até nenhuma ultrapassar o teto de resultados."""
    pending = list(slices)
    leaves = []

    while pending:
        s = pending.pop(0)
        total = _search_page(
            client, s.query(), 1, per_page=1
        ).get("total_count", 0)

        if total > SEARCH_CAP:
            parts = s.split(today)

            if parts:
                print(
                    f"  [Busca] {s.query()}: {total} > {SEARCH_CAP}, "
                    "subdividindo"
                )
                pending = parts + pending
                continue

            print(
                f"  [Aviso] {s.query()}: {total} resultados; "
                "nao ha como subdividir"
            )

        leaves.append((s, total))

    return leaves


def search_candidates(
    client: GitHubClient,
    min_stars: int,
    breaks: List[int],
    today: date,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Busca os candidatos e registra as faixas consultadas."""
    print("[Busca] Planejando faixas de estrelas...")
    leaves = plan_slices(
        client, initial_slices(min_stars, breaks), today
    )

    records, slice_log = [], []

    for s, total in leaves:
        query = s.query()
        n_pages = min(
            -(-total // SEARCH_PAGE_SIZE),
            SEARCH_CAP // SEARCH_PAGE_SIZE,
        )

        items, incomplete = [], False

        for page in range(1, n_pages + 1):
            data = _search_page(client, query, page)
            items.extend(data.get("items", []))
            incomplete = incomplete or bool(
                data.get("incomplete_results")
            )

        records.extend(
            {**item, "faixa_busca": query}
            for item in items
        )

        slice_log.append({
            "faixa_busca": query,
            "total_count": total,
            "coletados": len(items),
            "acima_do_teto": total > SEARCH_CAP,
            "incomplete_results": incomplete,
        })

        print(f"  [Busca] {query}: {len(items)}/{total}")

    df = pd.DataFrame(records)

    if not df.empty:
        df = (
            df.drop_duplicates(subset=["id"])
            .sort_values("stars", ascending=False)
            .reset_index(drop=True)
        )

    return df, pd.DataFrame(slice_log)


# ---------------------------------------------------------------------------
# Critério de inclusão e metadados
# ---------------------------------------------------------------------------

def _parse_ts(value: str) -> datetime:
    return datetime.strptime(value[:10], "%Y-%m-%d")


def count_releases_in_window(
    releases: List[Dict[str, Any]],
    start: str,
    end: str,
) -> Tuple[int, int]:
    """Conta releases e pré-releases publicadas dentro da janela."""
    start_dt, end_dt = _parse_ts(start), _parse_ts(end)
    n_releases = n_prereleases = 0

    for release in releases:
        if release.get("draft") or not release.get("published_at"):
            continue

        published = _parse_ts(release["published_at"])

        if not start_dt <= published <= end_dt:
            continue

        if release.get("prerelease"):
            n_prereleases += 1
        else:
            n_releases += 1

    return n_releases, n_prereleases


def count_valid_runs(df_runs: pd.DataFrame) -> int:
    """Conta somente runs classificadas como sucesso ou falha."""
    if df_runs.empty:
        return 0

    return int(
        df_runs["status_classificacao"]
        .isin(["sucesso", "falha"])
        .sum()
    )


def age_in_days(created_at: str, reference: str) -> int:
    """Calcula a idade do repositório no fim da janela."""
    return (_parse_ts(reference) - _parse_ts(created_at)).days


def evaluate_candidate(
    client: GitHubClient,
    cand: Dict[str, Any],
    sel: Dict[str, Any],
    window: Dict[str, str],
) -> Tuple[Dict[str, Any], Optional[pd.DataFrame]]:
    """
    Avalia o candidato na ordem:
    arquivado/fork -> workflows -> releases -> total de runs -> runs válidas.
    """
    owner, repo = cand["owner"], cand["repo"]
    base = f"{API}/repos/{owner}/{repo}"

    facts: Dict[str, Any] = {"full_name": cand["full_name"]}

    def descarte(motivo: str):
        facts.update(status=DESCARTADO, motivo_descarte=motivo)
        return facts, None

    if cand["archived"]:
        return descarte(MOTIVO_ARQUIVADO)

    if cand["fork"]:
        return descarte(MOTIVO_FORK)

    try:
        # 1. Verifica se o repositório possui GitHub Actions.
        workflows, _ = client.get_json(
            f"{base}/actions/workflows",
            params={"per_page": 1},
        )

        if "total_count" not in workflows:
            return descarte(MOTIVO_INDISPONIVEL)

        facts["n_workflows"] = workflows["total_count"]

        if facts["n_workflows"] == 0:
            return descarte(MOTIVO_SEM_ACTIONS)

        # 2. Pré-filtro de releases.
        # O total bruto é um limite superior para releases válidas na janela.
        total_releases = client.count_items(f"{base}/releases")

        if (
            total_releases is not None
            and total_releases < sel["min_releases"]
        ):
            return descarte(
                MOTIVO_POUCAS_RELEASES.format(n=sel["min_releases"])
            )

        releases = client.paginate(
            f"{base}/releases",
            params={"per_page": 100},
        )

        n_rel, n_pre = count_releases_in_window(
            releases, window["start"], window["end"]
        )

        facts.update(
            n_releases_janela=n_rel,
            n_prereleases_janela=n_pre,
        )

        if n_rel < sel["min_releases"]:
            return descarte(
                MOTIVO_POUCAS_RELEASES.format(n=sel["min_releases"])
            )

        # 3. NOVO: pré-filtro de workflow runs.
        # Uma chamada retorna o total bruto sem baixar todas as páginas.
        total_runs = contar_runs_janela(
            client,
            owner,
            repo,
            cand["default_branch"],
            window["start"],
            window["end"],
        )

        facts["n_runs_total_janela"] = total_runs

        # Todas as runs válidas são um subconjunto das runs totais.
        # Se o total bruto não atinge o mínimo, o descarte é seguro.
        if total_runs < sel["min_runs"]:
            return descarte(
                MOTIVO_POUCOS_RUNS.format(n=sel["min_runs"])
            )

        # 4. Somente coleta as runs quando o pré-filtro não descarta.
        df_runs = collect_repo_runs(
            client,
            owner,
            repo,
            cand["default_branch"],
            window["start"],
            window["end"],
        )

        n_validas = count_valid_runs(df_runs)
        facts["n_runs_validos_janela"] = n_validas

        if n_validas < sel["min_runs"]:
            return descarte(
                MOTIVO_POUCOS_RUNS.format(n=sel["min_runs"])
            )

        # 5. Metadados adicionais somente para candidatos aprovados.
        try:
            facts["contributors"] = client.count_items(
                f"{base}/contributors",
                params={"anon": "true"},
            )
        except requests.HTTPError as e:
            print(
                f"  [Aviso] {cand['full_name']}: "
                f"contribuidores indisponiveis ({e})"
            )
            facts["contributors"] = None

    except requests.HTTPError as e:
        status = (
            e.response.status_code
            if e.response is not None
            else "?"
        )
        return descarte(f"{MOTIVO_INDISPONIVEL} (HTTP {status})")

    except requests.RequestException as e:
        raise RuntimeError(
            f"Falha de rede ao avaliar {cand['full_name']} "
            f"({type(e).__name__}). "
            "Rode novamente: o cache retoma de onde parou."
        ) from e

    facts.update(status=INCLUIDO, motivo_descarte="")
    return facts, df_runs


def select_sample(
    client: GitHubClient,
    candidates: pd.DataFrame,
    sel: Dict[str, Any],
    window: Dict[str, str],
    seed: int,
) -> Tuple[pd.DataFrame, List[pd.DataFrame]]:
    """
    Avalia candidatos em ordem aleatória com semente fixa até atingir
    sample_size. Mantém o processamento determinístico dos lotes.
    """
    order = list(range(len(candidates)))
    random.Random(seed).shuffle(order)

    candidates = candidates.copy()
    candidates["ordem_avaliacao"] = pd.Series(
        {idx: pos + 1 for pos, idx in enumerate(order)}
    )

    workers = max(1, int(sel.get("eval_workers", 1)))
    evaluated: Dict[int, Dict[str, Any]] = {}
    runs: List[pd.DataFrame] = []
    n_incluidos = 0
    pos = 0

    with ThreadPoolExecutor(max_workers=workers) as ex:
        while pos < len(order) and n_incluidos < sel["sample_size"]:
            lote = order[pos:pos + workers]
            pos += workers

            cands = [
                candidates.loc[i].to_dict()
                for i in lote
            ]

            resultados = list(
                ex.map(
                    lambda c: evaluate_candidate(
                        client, c, sel, window
                    ),
                    cands,
                )
            )

            for idx, cand, (facts, df_runs) in zip(
                lote, cands, resultados
            ):
                if n_incluidos >= sel["sample_size"]:
                    break

                evaluated[idx] = facts

                if facts["status"] == INCLUIDO:
                    n_incluidos += 1
                    runs.append(df_runs)

                print(
                    f"[Selecao] {len(evaluated)} avaliados, "
                    f"{n_incluidos}/{sel['sample_size']} incluidos | "
                    f"{cand['full_name']}: "
                    f"{facts['motivo_descarte'] or INCLUIDO}"
                )

    facts_df = pd.DataFrame.from_dict(
        evaluated, orient="index"
    )

    result = candidates.join(
        facts_df.drop(columns="full_name", errors="ignore")
    )

    for col in ["status", "motivo_descarte"]:
        if col not in result:
            result[col] = None

    result["status"] = result["status"].fillna(NAO_AVALIADO)
    result["motivo_descarte"] = result["motivo_descarte"].fillna("")

    return result, runs


def build_metadata(
    selected: pd.DataFrame,
    window_end: str,
) -> pd.DataFrame:
    """Monta os metadados dos repositórios incluídos na amostra."""
    df = selected[selected["status"] == INCLUIDO].copy()

    df["idade_dias"] = df["created_at"].apply(
        lambda c: age_in_days(c, window_end)
    )

    cols = [
        "full_name", "owner", "repo", "stars", "language",
        "created_at", "idade_dias", "default_branch", "fork",
        "archived", "contributors", "n_workflows",
        "n_releases_janela", "n_prereleases_janela",
        "n_runs_validos_janela",
    ]

    df = (
        df.reindex(columns=cols)
        .sort_values("stars", ascending=False)
        .reset_index(drop=True)
    )

    for col in [
        "contributors",
        "n_workflows",
        "n_releases_janela",
        "n_prereleases_janela",
        "n_runs_validos_janela",
    ]:
        df[col] = df[col].astype("Int64")

    return df


def build_funnel(
    selected: pd.DataFrame,
    sel: Dict[str, Any],
) -> pd.DataFrame:
    """Monta o funil de seleção a partir dos status e motivos."""
    motivos = selected["motivo_descarte"]

    steps = [
        ("Candidatos da busca (sem duplicatas)", None),
        (
            "Avaliados em ordem aleatoria (seed)",
            "nao avaliados: amostra atingiu o tamanho-alvo",
        ),
        ("Nao arquivados", MOTIVO_ARQUIVADO),
        ("Nao fork", MOTIVO_FORK),
        ("Disponiveis na API", MOTIVO_INDISPONIVEL),
        ("Com GitHub Actions", MOTIVO_SEM_ACTIONS),
        (
            f">= {sel['min_releases']} releases na janela",
            MOTIVO_POUCAS_RELEASES.format(n=sel["min_releases"]),
        ),
        (
            f">= {sel['min_runs']} workflow runs validos na janela",
            MOTIVO_POUCOS_RUNS.format(n=sel["min_runs"]),
        ),
    ]

    rows = []
    remaining = len(selected)

    for etapa, motivo in steps:
        if motivo is None:
            dropped = 0
        elif etapa.startswith("Avaliados"):
            dropped = int(
                (selected["status"] == NAO_AVALIADO).sum()
            )
        else:
            dropped = int(motivos.str.startswith(motivo).sum())

        remaining -= dropped

        rows.append({
            "etapa": etapa,
            "quantidade": remaining,
            "descartados": dropped,
            "motivo_descarte": motivo or "",
        })

    rows.append({
        "etapa": "Amostra final",
        "quantidade": int(
            (selected["status"] == INCLUIDO).sum()
        ),
        "descartados": 0,
        "motivo_descarte": "",
    })

    return pd.DataFrame(rows)
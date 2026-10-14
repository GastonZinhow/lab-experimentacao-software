"""
Sorteio da amostra-ouro (Issue #59, seção 6 do enunciado): 60 repositórios da
amostra final e 5 releases de cada um, com semente fixa, e a planilha de
rotulagem com links diretos e SEM nenhuma coluna da heurística.

A base do sorteio são os `base_amostra` primeiros repositórios incluídos na
ordem de avaliação (seed do config). Essa ordem não muda quando a amostra
cresce na coleta completa (#63), então rodar o script de novo, antes ou depois
dela, gera exatamente o mesmo sorteio.

As releases vêm da API pelo mesmo cliente e cache do pipeline (a lista de
releases já foi baixada na seleção), com a mesma série e a mesma "release
anterior" de `releases.csv`, sem depender da coleta de commits e tags.

Uso: python -m rotulagem.sorteio --config config.yaml
"""
import argparse
import os
from typing import Any, Dict

import pandas as pd

from metrics.datas import parse_data
from pipeline.cache import ResponseCache
from pipeline.client import GitHubClient
from pipeline.collector_releases import (
    fetch_releases,
    ligar_anteriores,
    separar_releases,
    tipo_release,
)
from pipeline.config import load_config

GITHUB = "https://github.com"

# Colunas que cada avaliador preenche
COLUNAS_ROTULO = ["tipo_projeto", "entregas_reais", "corretiva", "observacoes"]

COLUNAS_PLANILHA = [
    "item", "full_name", "repo_url", "tag_name", "tag_anterior", "published_at",
    "release_url", "commits_url",
] + COLUNAS_ROTULO


def base_do_sorteio(candidatos: pd.DataFrame, n_base: int) -> pd.DataFrame:
    """Os n_base primeiros incluídos na ordem de avaliação, ordenados por nome."""
    incluidos = candidatos[candidatos["status"] == "incluido"]
    base = incluidos.sort_values("ordem_avaliacao").head(n_base)
    if len(base) < n_base:
        raise ValueError(f"A amostra tem só {len(base)} incluídos; a base pede {n_base}.")
    return base.sort_values("full_name").reset_index(drop=True)


def sortear_repositorios(base: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
    return base.sample(n=n, random_state=seed).sort_values("full_name").reset_index(drop=True)


def releases_da_amostra(
    client: GitHubClient, repos: pd.Series, window: Dict[str, str]
) -> pd.DataFrame:
    """
    Releases publicadas e pré-releases dos repositórios, com as mesmas colunas
    (e a mesma tag_anterior da série publicada) que o pipeline grava em releases.csv.
    """
    inicio, fim = parse_data(window["start"]), parse_data(window["end"])
    linhas = []
    for full_name in repos:
        owner, repo = full_name.split("/", 1)
        grupos = separar_releases(fetch_releases(client, owner, repo))
        ligadas = {r["id"]: r for r in ligar_anteriores(grupos["publicada"])}
        for r in grupos["publicada"] + grupos["prerelease"]:
            publicada_em = r.get("published_at")
            ligada = ligadas.get(r["id"])
            linhas.append({
                "repo": full_name,
                "tag_name": r.get("tag_name"),
                "tipo": tipo_release(r),
                "published_at": publicada_em,
                "na_janela": bool(publicada_em) and inicio <= parse_data(publicada_em) < fim,
                "tag_anterior": ligada["tag_anterior"] if ligada else None,
                "html_url": r.get("html_url"),
            })
    return pd.DataFrame(linhas)


def sortear_releases(
    releases: pd.DataFrame, repos: pd.Series, k: int, seed: int
) -> pd.DataFrame:
    """
    k releases publicadas (sem pré-releases) na janela de cada repositório.
    Repositórios com menos de k releases entram com todas.
    """
    elegiveis = releases[
        releases["repo"].isin(repos) & releases["na_janela"] & (releases["tipo"] == "publicada")
    ].sort_values(["repo", "published_at", "tag_name"])
    partes = []
    for repo in sorted(repos):
        do_repo = elegiveis[elegiveis["repo"] == repo]
        partes.append(do_repo.sample(n=min(k, len(do_repo)), random_state=seed))
    return (
        pd.concat(partes, ignore_index=True)
        .sort_values(["repo", "published_at"])
        .reset_index(drop=True)
    )


def montar_planilha(sorteadas: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por release; os rótulos de repositório se repetem nas 5 linhas."""
    linhas = []
    for i, r in enumerate(sorteadas.itertuples(index=False), start=1):
        anterior = r.tag_anterior if isinstance(r.tag_anterior, str) else ""
        commits_url = (
            f"{GITHUB}/{r.repo}/compare/{anterior}...{r.tag_name}" if anterior
            else f"{GITHUB}/{r.repo}/commits/{r.tag_name}"
        )
        linhas.append({
            "item": i,
            "full_name": r.repo,
            "repo_url": f"{GITHUB}/{r.repo}",
            "tag_name": r.tag_name,
            "tag_anterior": anterior,
            "published_at": r.published_at,
            "release_url": r.html_url,
            "commits_url": commits_url,
            **{c: "" for c in COLUNAS_ROTULO},
        })
    return pd.DataFrame(linhas, columns=COLUNAS_PLANILHA)


def sortear(cfg: Dict[str, Any], client: GitHubClient) -> Dict[str, pd.DataFrame]:
    val = cfg["validation"]
    candidatos = pd.read_csv(os.path.join(cfg["output_dir"], "candidatos.csv"))

    base = base_do_sorteio(candidatos, val["base_amostra"])
    repos = sortear_repositorios(base, val["n_repos"], val["seed"])
    releases = releases_da_amostra(client, repos["full_name"], cfg["window"])
    sorteadas = sortear_releases(releases, repos["full_name"], val["releases_por_repo"], val["seed"])
    return {
        "repos": repos[["full_name", "ordem_avaliacao"]],
        "planilha": montar_planilha(sorteadas),
    }


def main():
    parser = argparse.ArgumentParser(description="Sorteio da amostra-ouro (#59)")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg = load_config(args.config)
    out_dir = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(args.config)), cfg["validation"]["dir"])
    )
    os.makedirs(out_dir, exist_ok=True)

    cache = ResponseCache(os.path.join(cfg["cache_dir"], "api_cache.db"))
    client = GitHubClient(cache=cache, max_retries=cfg.get("max_retries", 5))
    resultado = sortear(cfg, client)
    resultado["repos"].to_csv(os.path.join(out_dir, "amostra_ouro_repos.csv"), index=False)
    resultado["planilha"].to_csv(os.path.join(out_dir, "planilha_rotulagem.csv"), index=False)

    planilha = resultado["planilha"]
    print(f"[Sorteio] {planilha['full_name'].nunique()} repositórios, {len(planilha)} releases")
    curtos = planilha.groupby("full_name").size()
    curtos = curtos[curtos < cfg["validation"]["releases_por_repo"]]
    if not curtos.empty:
        print(f"[Aviso] repositórios com menos releases que o pedido: {curtos.to_dict()}")
    print(f"Planilha em {os.path.join(out_dir, 'planilha_rotulagem.csv')}")


if __name__ == "__main__":
    main()

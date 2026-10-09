from concurrent.futures import ThreadPoolExecutor
from pipeline.git_local import GitRepo, collect_repo_tags_git
import time
import argparse
from datetime import date
from pipeline.config import load_config
import os
import sys
import pandas as pd
from pipeline.cache import ResponseCache
from pipeline.client import GitHubClient
from collections import Counter
from pipeline.collector_releases import collect_repo_releases, collect_repo_tags
from pipeline.selection import (
    build_funnel,
    build_metadata,
    search_candidates,
    select_sample,
)

def impedir_suspensao() -> None:
    """
    No Windows, impede a suspensão automática enquanto o pipeline roda (a tela
    ainda pode apagar). O bloqueio é liberado sozinho quando o processo termina.
    """
    if sys.platform == "win32":
        import ctypes
        ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)


def main():
    start_time = time.time()
    impedir_suspensao()
    parser = argparse.ArgumentParser(description="Pipeline DORA Mining")
    parser.add_argument("--config", required=True, help="Caminho para config.yaml")
    parser.add_argument(
        "--sample-size", type=int,
        help="Sobrescreve selection.sample_size (ex.: 5 para um teste rápido)",
    )
    args = parser.parse_args()

    cfg = load_config(args.config)

    sel = cfg["selection"]
    if args.sample_size:
        sel["sample_size"] = args.sample_size
    window = cfg["window"]
    out_dir = cfg.get("output_dir", "data")
    os.makedirs(out_dir, exist_ok=True)

    cache = ResponseCache(os.path.join(cfg.get("cache_dir", ".cache"), "api_cache.db"))
    client = GitHubClient(cache=cache, max_retries=cfg.get("max_retries", 5))

    # 1. Candidatos: busca fatiada por faixas de estrelas
    candidates, slice_log = search_candidates(
        client, sel["min_stars"], sel["star_breaks"], date.today()
    )
    slice_log.to_csv(os.path.join(out_dir, "faixas_busca.csv"), index=False)
    print(f"[Busca] {len(candidates)} candidatos em {len(slice_log)} faixas.")

    # 2. Critério de inclusão, até atingir o tamanho da amostra
    selected, runs = select_sample(client, candidates, sel, window, cfg.get("seed", 42))

    selected.to_csv(os.path.join(out_dir, "candidatos.csv"), index=False)
    metadata = build_metadata(selected, window["end"])
    metadata.to_csv(os.path.join(out_dir, "metadados.csv"), index=False)
    funnel = build_funnel(selected, sel)
    funnel.to_csv(os.path.join(out_dir, "funil.csv"), index=False)

    print("\nFunil de seleção:")
    print(funnel.to_string(index=False))

    # 3. Workflow runs da amostra final
    if runs:
        final_df = pd.concat(runs, ignore_index=True)
        final_df.to_csv(os.path.join(out_dir, "runs.csv"), index=False)
        print(f"Salvo runs.csv com {len(final_df)} execuções coletadas.")

    # 4. Releases, commits entre releases e tags da amostra final (#54)
    repos = metadata[["owner", "repo", "default_branch"]].to_dict(orient="records")
    releases_dfs, commits_dfs, tags_dfs = [], [], []
    contadores_total: Counter = Counter()

        # 4. Releases, commits entre releases e tags da amostra final (#54)
    repos = metadata[["owner", "repo", "default_branch"]].to_dict(orient="records")
    releases_dfs, commits_dfs, tags_dfs = [], [], []
    contadores_total: Counter = Counter()

    # 4a. Clones locais em paralelo (só subprocess, sem tocar no client)
    git_repos = {}
    if cfg.get("usar_git_local", True):
        base = cfg.get("git_dir", ".git_cache")
        candidatos_git = {(r["owner"], r["repo"]): GitRepo(r["owner"], r["repo"], base) for r in repos}
        with ThreadPoolExecutor(max_workers=cfg.get("clone_workers", 4)) as ex:
            oks = list(ex.map(lambda g: g.ensure_cloned(), candidatos_git.values()))
        git_repos = {k: g for (k, g), ok in zip(candidatos_git.items(), oks) if ok}
        print(f"[Git] {len(git_repos)}/{len(repos)} repositórios disponíveis localmente.")

    # 4b. Coleta (git quando disponível, API como fallback)
    for r in repos:
        t_repo = time.time()
        git = git_repos.get((r["owner"], r["repo"]))
        df_rel, df_com, contadores = collect_repo_releases(
            client, r["owner"], r["repo"], cfg["window"]["start"], cfg["window"]["end"], git=git
        )
        releases_dfs.append(df_rel)
        commits_dfs.append(df_com)
        contadores_total.update(contadores)
        if git:
            tags_dfs.append(collect_repo_tags_git(git, r["owner"], r["repo"], cfg.get("max_tags_por_repo")))
        else:
            tags_dfs.append(collect_repo_tags(client, r["owner"], r["repo"], cfg.get("max_tags_por_repo")))
        print(f"  [Tempo] {r['owner']}/{r['repo']}: {time.time() - t_repo:.1f}s")

    for nome_csv, dfs in [("releases.csv", releases_dfs), ("commits_por_release.csv", commits_dfs), ("tags.csv", tags_dfs)]:
        df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
        df.to_csv(os.path.join(out_dir, nome_csv), index=False)
        print(f"Salvo {nome_csv} com {len(df)} linhas.")

    print("\n[Releases] Contadores totais:")
    for chave in ["releases_publicadas", "prereleases", "drafts_descartados", "releases_na_janela",
                  "ignoradas_sem_anterior", "ignoradas_404", "ignoradas_indisponivel",
                  "sem_commits_novos", "commits_coletados"]:
        print(f"  {chave:<24}: {contadores_total[chave]}")

    elapsed = time.time() - start_time

    print("\n" + "=" * 50)
    print("           RELATÓRIO DE DESEMPENHO E CACHE        ")
    print("=" * 50)
    print(f"Tempo total de execução  : {elapsed:.2f} segundos")
    print(f"Total de chamadas lógicas: {client.total_requests}")
    print(f"Requisições na REDE (API): {client.network_requests}")
    print(f"Requisições via CACHE    : {client.cache_hits}")

    if client.total_requests > 0:
        taxa_cache = (client.cache_hits / client.total_requests) * 100
        print(f"Taxa de acerto de Cache  : {taxa_cache:.1f}%")
    print("=" * 50)

if __name__ == "__main__":
    main()

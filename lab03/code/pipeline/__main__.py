import time
import argparse
import yaml
import os
import pandas as pd
from pipeline.cache import ResponseCache
from pipeline.client import GitHubClient
from pipeline.collector_runs import collect_repo_runs
from collections import Counter
from pipeline.collector_releases import collect_repo_releases, collect_repo_tags

def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(description="Pipeline DORA Mining")
    parser.add_argument("--config", required=True, help="Caminho para config.yaml")
    args = parser.parse_args()

    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)

    cache = ResponseCache(os.path.join(cfg.get("cache_dir", ".cache"), "api_cache.db"))
    client = GitHubClient(cache=cache, max_retries=cfg.get("max_retries", 5))

    input_repos_path = os.path.join(cfg.get("output_dir", "data"), "candidates.csv")
    if os.path.exists(input_repos_path):
        df_cand = pd.read_csv(input_repos_path)
        repos = df_cand[["owner", "repo", "default_branch"]].to_dict(orient="records")
    else:
        repos = [{"owner": "octocat", "repo": "Hello-World", "default_branch": "master"}]

    os.makedirs(cfg.get("output_dir", "data"), exist_ok=True)
    all_runs_dfs = []

    for r in repos:
        df_runs = collect_repo_runs(
            client, r["owner"], r["repo"], r["default_branch"],
            cfg["window"]["start"], cfg["window"]["end"]
        )
        all_runs_dfs.append(df_runs)

    if all_runs_dfs:
        final_df = pd.concat(all_runs_dfs, ignore_index=True)
        final_df.to_csv(os.path.join(cfg.get("output_dir", "data"), "runs.csv"), index=False)
        print(f"Salvo runs.csv com {len(final_df)} execuções coletadas.")

    out_dir = cfg.get("output_dir", "data")
    releases_dfs, commits_dfs, tags_dfs = [], [], []
    contadores_total: Counter = Counter()

    for r in repos:
        df_rel, df_com, contadores = collect_repo_releases(
            client, r["owner"], r["repo"], cfg["window"]["start"], cfg["window"]["end"]
        )
        releases_dfs.append(df_rel)
        commits_dfs.append(df_com)
        contadores_total.update(contadores)
        tags_dfs.append(collect_repo_tags(client, r["owner"], r["repo"], cfg.get("max_tags_por_repo")))

    for nome_csv, dfs in [("releases.csv", releases_dfs), ("commits_por_release.csv", commits_dfs), ("tags.csv", tags_dfs)]:
        df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
        df.to_csv(os.path.join(out_dir, nome_csv), index=False)
        print(f"Salvo {nome_csv} com {len(df)} linhas.")

    print("\n[Releases] Contadores totais:")
    for chave in ["releases_publicadas", "prereleases", "drafts_descartados", "releases_na_janela",
                  "ignoradas_sem_anterior", "ignoradas_404", "sem_commits_novos", "commits_coletados"]:
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
import time
import argparse
import yaml
import os
import pandas as pd
from pipeline.cache import ResponseCache
from pipeline.client import GitHubClient
from pipeline.collector_runs import collect_repo_runs

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
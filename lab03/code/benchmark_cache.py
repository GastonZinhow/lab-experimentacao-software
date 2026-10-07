import os
import time
import yaml
import pandas as pd
from pipeline.cache import ResponseCache
from pipeline.client import GitHubClient
from pipeline.collector_runs import collect_repo_runs

CONFIG_PATH = "config.yaml"
CACHE_BENCH = ".cache/benchmark_cache.db"

with open(CONFIG_PATH, "r") as f:
    cfg = yaml.safe_load(f)

start = cfg["window"]["start"]
end = cfg["window"]["end"]

CANDIDATES_PATH = os.path.join(cfg.get("output_dir", "data"), "candidates.csv")
if not os.path.exists(CANDIDATES_PATH):
    CANDIDATES_PATH = os.path.join(cfg.get("output_dir", "data"), "candidates.csv")

df_candidates = pd.read_csv(CANDIDATES_PATH)

sample_repos = df_candidates.to_dict(orient="records")

print(f"Repositórios selecionados para o benchmark ({len(sample_repos)}):")
for r in sample_repos:
    print(f" - {r['owner']}/{r['repo']} (branch: {r['default_branch']})")

if os.path.exists(CACHE_BENCH):
    os.remove(CACHE_BENCH)

print("\n>>> [1/2] Executando SEM CACHE (todas as chamadas vão para a API)...")
cache1 = ResponseCache(CACHE_BENCH)
client1 = GitHubClient(cache=cache1)

t0 = time.time()
total_runs_frio = 0
for r in sample_repos:
    df_runs = collect_repo_runs(
        client1, r["owner"], r["repo"], r["default_branch"], start, end
    )
    total_runs_frio += len(df_runs)
tempo_frio = time.time() - t0

print("\n>>> [2/2] Executando COM CACHE (lendo do banco SQLite local)...")
cache2 = ResponseCache(CACHE_BENCH)
client2 = GitHubClient(cache=cache2)

t1 = time.time()
total_runs_quente = 0
for r in sample_repos:
    df_runs = collect_repo_runs(
        client2, r["owner"], r["repo"], r["default_branch"], start, end
    )
    total_runs_quente += len(df_runs)
tempo_quente = time.time() - t1

ganho_velocidade = (tempo_frio / tempo_quente) if tempo_quente > 0 else 0

print("\n" + "=" * 68)
print("             BENCHMARK DE PERFORMANCE: CACHE SQLite             ")
print("=" * 68)
print(f"{'Métrica':<32} | {'Sem Cache (Frio)':<15} | {'Com Cache (Quente)':<15}")
print("-" * 68)
print(f"{'Tempo Total':<32} | {tempo_frio:.2f}s{'':<10} | {tempo_quente:.2f}s")
print(f"{'Requisições na Rede (API)':<32} | {client1.network_requests:<15} | {client2.network_requests:<15}")
print(f"{'Requisições via Cache (Disco)':<32} | {client1.cache_hits:<15} | {client2.cache_hits:<15}")
print(f"{'Total de Runs Extraídos':<32} | {total_runs_frio:<15} | {total_runs_quente:<15}")
print("-" * 68)
print(f"Aceleração obtida com Cache : {ganho_velocidade:.1f}x mais rápido")
print("=" * 68)
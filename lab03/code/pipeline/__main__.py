import time
import argparse
from datetime import date
from pipeline.config import load_config
import os
import pandas as pd
from pipeline.cache import ResponseCache
from pipeline.client import GitHubClient
from pipeline.selection import (
    build_funnel,
    build_metadata,
    search_candidates,
    select_sample,
)

def main():
    start_time = time.time()
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

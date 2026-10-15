"""
CFR (b) por repositório (RQ 03 b, Issue #61) a partir das saídas do pipeline.

Lê `data/releases.csv` e `data/commits_por_release.csv`, marca cada release da
janela como corretiva ou não com a heurística na versão atual
(metrics.corretiva.VERSAO_ATUAL) e grava `data/cfr_b.csv` com uma linha por
repositório: cfr_b, falhas, avaliadas, censuradas, corretivas e releases.
As releases com a marcação ficam em `data/releases_corretivas.csv` (base do
rework rate da seção 7.4).

Uso: python calcular_cfr_b.py --config config.yaml
"""
import argparse
import os
import sys

import pandas as pd

from metrics.cfr import DIAS_CFR_B, cfr_b_por_repositorio, marcar_corretivas
from metrics.corretiva import VERSAO_ATUAL, VERSOES
from pipeline.config import load_config


def main():
    parser = argparse.ArgumentParser(description="CFR (b) por repositório (#61)")
    parser.add_argument("--config", required=True)
    parser.add_argument("--versao", default=VERSAO_ATUAL, choices=sorted(VERSOES))
    args = parser.parse_args()

    cfg = load_config(args.config)
    pasta = cfg["output_dir"]
    caminhos = {nome: os.path.join(pasta, nome) for nome in ("releases.csv", "commits_por_release.csv")}
    faltando = [c for c in caminhos.values() if not os.path.exists(c)]
    if faltando:
        sys.exit(f"Rode o pipeline antes: faltam {', '.join(faltando)}")

    releases = pd.read_csv(caminhos["releases.csv"], dtype=str, keep_default_na=False)
    commits = pd.read_csv(caminhos["commits_por_release.csv"], dtype=str, keep_default_na=False)
    if "body" not in releases.columns:
        print("[Aviso] releases.csv sem a coluna body (release notes): rode o pipeline de novo; "
              "sem as notas, a v3 usa só os commits.")
    classificar = VERSOES[args.versao]
    fim = cfg["window"]["end"]

    resultado = cfr_b_por_repositorio(releases, commits, fim, classificar)
    resultado.insert(1, "versao_heuristica", args.versao)
    resultado.to_csv(os.path.join(pasta, "cfr_b.csv"), index=False)

    na_janela = releases[releases["na_janela"].str.lower().eq("true")]
    marcadas = marcar_corretivas(na_janela, commits, classificar)
    marcadas.drop(columns=["body"], errors="ignore").to_csv(
        os.path.join(pasta, "releases_corretivas.csv"), index=False
    )

    validos = resultado["cfr_b"].notna()
    print(f"[CFR b] heurística {args.versao}, prazo de {DIAS_CFR_B} dias, janela até {fim}")
    print(f"  {len(resultado)} repositórios ({validos.sum()} com CFR definido); "
          f"mediana do CFR (b) = {resultado.loc[validos, 'cfr_b'].median():.3f}")
    print(f"  {int(resultado['avaliadas'].sum())} releases avaliadas, "
          f"{int(resultado['censuradas'].sum())} censuradas, {int(resultado['falhas'].sum())} falhas")
    print(f"  gravado em {os.path.join(pasta, 'cfr_b.csv')}")


if __name__ == "__main__":
    main()

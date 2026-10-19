"""
Dataset final (Issue #63, usado pelas análises do Lab03S03): uma linha por
repositório da amostra, com os metadados e todas as métricas DORA em todas as
variantes, mais a classificação de referência C1.

Lê as saídas do pipeline em `data/` (metadados.csv, runs.csv, releases.csv,
commits_por_release.csv, tags.csv) e grava `data/dataset_dora.csv`. Cada
coluna está documentada em docs/dicionario_de_dados.md. Todos os tempos estão
em horas, as frequências em deploys por semana e as taxas como fração (0 a 1).

Uso: python gerar_dataset.py --config config.yaml
"""
import argparse
import os
import sys
from typing import Any, Dict, List

import pandas as pd

from metrics.cfr import calcular_cfr_a, cfr_b_por_repositorio
from metrics.classificacao import categorias_repositorio
from metrics.datas import parse_data
from metrics.deploy import calcular_deploy_frequency, semanas_da_janela
from metrics.lead_time import calcular_lead_time_a, calcular_lead_time_b
from metrics.recovery import avaliar_tempo_recuperacao
from pipeline.config import load_config

ENTRADAS = ("metadados.csv", "runs.csv", "releases.csv", "commits_por_release.csv", "tags.csv")
COLUNAS_METADADOS = [
    "full_name", "owner", "repo", "stars", "language", "created_at", "idade_dias",
    "default_branch", "contributors", "n_workflows",
]


def _verdadeiro(serie: pd.Series) -> pd.Series:
    return serie.astype(str).str.lower().eq("true")


def metricas_releases(
    releases: pd.DataFrame, commits: pd.DataFrame, tags: pd.DataFrame, inicio: str, fim: str
) -> pd.DataFrame:
    """Deployment frequency (release, release + pré-release, tag) e lead time (a)/(b)."""
    semanas = semanas_da_janela(inicio, fim)
    ini, fi = parse_data(inicio), parse_data(fim)
    datas_commits = commits.groupby(["repo", "tag_name"])["commit_author_date"].apply(list).to_dict()

    linhas = []
    for repo, grupo in releases.groupby("repo", sort=True):
        registros = [
            {"published_at": r["published_at"] or None, "draft": False,
             "prerelease": r["prerelease"].lower() == "true"}
            for _, r in grupo.iterrows()
        ]
        publicadas = grupo[_verdadeiro(grupo["na_janela"]) & ~_verdadeiro(grupo["prerelease"])]
        status = publicadas["status_compare"]
        avaliaveis = [
            {"published_at": r["published_at"], "sem_anterior": False,
             "commit_dates": datas_commits.get((repo, r["tag_name"]), [])}
            for _, r in publicadas[status.eq("ok")].iterrows()
        ]
        com_commits = [r for r in avaliaveis if r["commit_dates"]]
        linhas.append({
            "full_name": repo,
            "n_releases": len(publicadas),
            "n_prereleases": int((_verdadeiro(grupo["na_janela"]) & _verdadeiro(grupo["prerelease"])).sum()),
            "deploy_freq_release": calcular_deploy_frequency(registros, inicio, fim),
            "deploy_freq_release_pre": calcular_deploy_frequency(registros, inicio, fim, incluir_prerelease=True),
            "lead_time_a_horas": calcular_lead_time_a(avaliaveis),
            "lead_time_b_horas": calcular_lead_time_b(avaliaveis),
            "lt_releases_avaliadas": len(com_commits),
            "lt_commits_avaliados": sum(len(r["commit_dates"]) for r in com_commits),
            "lt_releases_sem_commits": len(avaliaveis) - len(com_commits),
            "lt_releases_sem_anterior": int(status.eq("sem_anterior").sum()),
            "lt_releases_404": int(status.eq("404").sum()),
            "lt_releases_indisponivel": int(status.eq("indisponivel").sum()),
        })
    df = pd.DataFrame(linhas)

    datas_tags = pd.to_datetime(tags["commit_author_date"], utc=True, errors="coerce")
    na_janela = tags[(datas_tags >= ini) & (datas_tags < fi)]
    n_tags = na_janela.groupby("repo").size().rename("n_tags").reset_index()
    n_tags = n_tags.rename(columns={"repo": "full_name"})
    df = df.merge(n_tags, on="full_name", how="left")
    df["n_tags"] = df["n_tags"].fillna(0).astype(int)
    df["deploy_freq_tag"] = df["n_tags"] / semanas
    return df


def metricas_runs(runs: pd.DataFrame) -> pd.DataFrame:
    """CFR (a) e tempo de recuperação, com as contagens de runs e de episódios."""
    linhas: List[Dict[str, Any]] = []
    for repo, grupo in runs.groupby("repo", sort=True):
        registros = grupo.to_dict("records")
        rec = avaliar_tempo_recuperacao(registros)
        status = grupo["status_classificacao"]
        linhas.append({
            "full_name": repo,
            "runs_sucesso": int(status.eq("sucesso").sum()),
            "runs_falha": int(status.eq("falha").sum()),
            "cfr_a": calcular_cfr_a(registros),
            "tempo_recuperacao_horas": rec["mediana_horas"],
            "episodios_falha": rec["episodios"],
            "episodios_recuperados": rec["recuperados"],
            "episodios_censurados": rec["censurados"],
            "prop_episodios_censurados": rec["prop_censurados"] if rec["episodios"] else None,
        })
    return pd.DataFrame(linhas)


def classificar_c1(df: pd.DataFrame) -> pd.DataFrame:
    """Classificação de referência C1: release, lead time (a), CFR (a)."""
    def nulo(v):
        return None if pd.isna(v) else float(v)

    cats = [
        categorias_repositorio(
            nulo(r.deploy_freq_release), nulo(r.lead_time_a_horas),
            nulo(r.cfr_a), nulo(r.tempo_recuperacao_horas),
        )
        for r in df.itertuples()
    ]
    return pd.DataFrame(cats, index=df.index).add_prefix("c1_")


def gerar_dataset(dados: Dict[str, pd.DataFrame], inicio: str, fim: str) -> pd.DataFrame:
    meta = dados["metadados.csv"]
    releases = dados["releases.csv"].fillna("")
    commits = dados["commits_por_release.csv"].fillna("")

    df = meta[COLUNAS_METADADOS].copy()
    df = df.merge(metricas_releases(releases, commits, dados["tags.csv"], inicio, fim),
                  on="full_name", how="left")

    cfr_b = cfr_b_por_repositorio(releases, commits, fim).rename(columns={
        "repo": "full_name", "falhas": "cfr_b_falhas", "avaliadas": "cfr_b_avaliadas",
        "censuradas": "cfr_b_censuradas", "corretivas": "releases_corretivas",
    }).drop(columns="releases")
    df = df.merge(cfr_b, on="full_name", how="left")
    df = df.merge(metricas_runs(dados["runs.csv"]), on="full_name", how="left")
    df = pd.concat([df, classificar_c1(df)], axis=1)

    inteiros = [c for c in df.columns if c.startswith(("n_", "lt_releases", "lt_commits", "runs_", "episodios_"))
                or c in ("cfr_b_falhas", "cfr_b_avaliadas", "cfr_b_censuradas", "releases_corretivas", "contributors")]
    df[inteiros] = df[inteiros].astype("Int64")
    return df.sort_values("full_name").reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(description="Gera data/dataset_dora.csv (#63)")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg = load_config(args.config)
    pasta = cfg["output_dir"]
    faltando = [n for n in ENTRADAS if not os.path.exists(os.path.join(pasta, n))]
    if faltando:
        sys.exit(f"Rode o pipeline antes: faltam {', '.join(faltando)} em {pasta}")

    textos = {"releases.csv", "commits_por_release.csv"}
    dados = {
        n: pd.read_csv(os.path.join(pasta, n), low_memory=False,
                       **({"dtype": str, "keep_default_na": False} if n in textos else {}))
        for n in ENTRADAS
    }
    inicio, fim = cfg["window"]["start"], cfg["window"]["end"]
    df = gerar_dataset(dados, inicio, fim)

    sem_dados = df["n_releases"].isna() | df["runs_sucesso"].isna()
    if sem_dados.any():
        print(f"[Aviso] {sem_dados.sum()} repositórios sem releases ou runs coletados: "
              + ", ".join(df.loc[sem_dados, "full_name"]))
    destino = os.path.join(pasta, "dataset_dora.csv")
    df.to_csv(destino, index=False)
    print(f"[Dataset] {len(df)} repositórios, {len(df.columns)} colunas -> {destino}")
    print(df["c1_geral"].value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()

from datetime import timedelta
from typing import Callable, Iterable, List, Dict, Any, Optional

import pandas as pd

from metrics.corretiva import e_corretiva
from metrics.datas import DataLike, parse_data

# Prazo, em dias, para uma corretiva marcar a release anterior como falha (RQ 03 b)
DIAS_CFR_B = 7


def calcular_cfr_a(runs: List[Dict[str, Any]]) -> Optional[float]:
    """
    Calcula o Change Failure Rate (CFR) - Variante (a) Proxy de CI.
    Fórmula: nº de falhas ÷ (nº de falhas + nº de sucessos)
    Status considerados:
      - sucesso: conclusion == 'success'
      - falha: conclusion in ['failure', 'timed_out', 'startup_failure']
      - ignorar: 'cancelled', 'skipped', 'neutral', etc.
    Retorna float entre 0.0 e 1.0, ou None se não houver execuções válidas.
    """
    sucessos = 0
    falhas = 0

    for run in runs:
        # Dá suporte ao campo já mapeado ou ao campo bruto
        status = run.get("status_classificacao")
        conclusion = run.get("conclusion_original", run.get("conclusion"))

        if status == "sucesso" or conclusion == "success":
            sucessos += 1
        elif status == "falha" or conclusion in ["failure", "timed_out", "startup_failure"]:
            falhas += 1

    total_validos = sucessos + falhas
    if total_validos == 0:
        return None

    return falhas / total_validos


def avaliar_cfr_b(
    releases: List[Dict[str, Any]], fim_janela: DataLike, dias: int = DIAS_CFR_B
) -> Dict[str, Any]:
    """
    Change Failure Rate (CFR) - Variante (b) Proxy de entrega.

    Cada release é um dict com `published_at` e `corretiva` (bool, saída da
    heurística de metrics.corretiva). Uma release R falhou se alguma release
    publicada depois dela, em até `dias` dias, for corretiva.

    Censura: releases publicadas nos últimos `dias` dias da janela [inicio, fim)
    não têm o prazo inteiro observado e saem do numerador e do denominador.
    Elas ainda podem marcar como falha uma release anterior.

    Retorna {"cfr", "falhas", "avaliadas", "censuradas"}; cfr é None se
    nenhuma release puder ser avaliada.
    """
    prazo = timedelta(days=dias)
    limite_censura = parse_data(fim_janela) - prazo
    ordenadas = sorted(
        ((parse_data(r["published_at"]), bool(r.get("corretiva"))) for r in releases),
        key=lambda x: x[0],
    )

    falhas = avaliadas = censuradas = 0
    for i, (data_r, _) in enumerate(ordenadas):
        if data_r >= limite_censura:
            censuradas += 1
            continue
        avaliadas += 1
        seguintes = (c for data_s, c in ordenadas[i + 1:] if data_s - data_r <= prazo)
        if any(seguintes):
            falhas += 1

    return {
        "cfr": falhas / avaliadas if avaliadas else None,
        "falhas": falhas,
        "avaliadas": avaliadas,
        "censuradas": censuradas,
    }


def calcular_cfr_b(
    releases: List[Dict[str, Any]], fim_janela: DataLike, dias: int = DIAS_CFR_B
) -> Optional[float]:
    """Atalho: só a taxa de avaliar_cfr_b (fração entre 0 e 1, ou None)."""
    return avaliar_cfr_b(releases, fim_janela, dias)["cfr"]


Classificador = Callable[..., bool]


def _texto(valor) -> Optional[str]:
    return None if valor is None or pd.isna(valor) or valor == "" else str(valor)


def marcar_corretivas(
    df_releases: pd.DataFrame,
    df_commits: pd.DataFrame,
    classificar: Classificador = e_corretiva,
) -> pd.DataFrame:
    """
    Aplica a heurística a cada release de releases.csv, usando as mensagens de
    commits_por_release.csv (ligadas por repo + tag_name) e, se houver, as
    release notes da coluna `body`. Releases sem compare (sem anterior ou 404)
    são classificadas sem commits. Devolve uma cópia de df_releases com a
    coluna booleana `corretiva`.
    """
    mensagens: Dict[tuple, List[str]] = {}
    if not df_commits.empty:
        for (repo, tag), grupo in df_commits.groupby(["repo", "tag_name"]):
            mensagens[(repo, tag)] = grupo["mensagem"].tolist()

    out = df_releases.copy()
    out["corretiva"] = [
        classificar(
            _texto(r["tag_name"]),
            _texto(r["tag_anterior"]),
            mensagens.get((r["repo"], r["tag_name"]), []),
            _texto(r.get("body")),
        )
        for _, r in out.iterrows()
    ]
    return out


def cfr_b_por_repositorio(
    df_releases: pd.DataFrame,
    df_commits: pd.DataFrame,
    fim_janela: DataLike,
    classificar: Classificador = e_corretiva,
    dias: int = DIAS_CFR_B,
) -> pd.DataFrame:
    """
    CFR (b) de cada repositório a partir das saídas do pipeline. Entram as
    releases publicadas (não pré-releases) da janela. Devolve uma linha por
    repositório com cfr_b, falhas, avaliadas, censuradas e corretivas.
    """
    publicadas = df_releases[
        df_releases["na_janela"].astype(str).str.lower().eq("true")
        & ~df_releases["prerelease"].astype(str).str.lower().eq("true")
    ]
    marcadas = marcar_corretivas(publicadas, df_commits, classificar)
    linhas = []
    for repo, grupo in marcadas.groupby("repo", sort=True):
        res = avaliar_cfr_b(grupo.to_dict("records"), fim_janela, dias)
        linhas.append({
            "repo": repo,
            "cfr_b": res["cfr"],
            "falhas": res["falhas"],
            "avaliadas": res["avaliadas"],
            "censuradas": res["censuradas"],
            "corretivas": int(grupo["corretiva"].sum()),
            "releases": len(grupo),
        })
    return pd.DataFrame(
        linhas,
        columns=["repo", "cfr_b", "falhas", "avaliadas", "censuradas", "corretivas", "releases"],
    )

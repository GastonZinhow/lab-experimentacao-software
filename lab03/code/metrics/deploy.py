from typing import List, Dict, Any
from metrics.datas import DataLike, parse_data


def semanas_da_janela(inicio: DataLike, fim: DataLike) -> float:
    """
    Duração da janela em semanas. A janela é o intervalo semiaberto [inicio, fim):
    com inicio=2025-09-30 e fim=2026-09-30 são 365 dias ≈ 52,1 semanas.
    """
    return (parse_data(fim) - parse_data(inicio)).total_seconds() / (7 * 24 * 3600)


def releases_na_janela(
    releases: List[Dict[str, Any]],
    inicio: DataLike,
    fim: DataLike,
    incluir_prerelease: bool = False,
) -> List[Dict[str, Any]]:
    """
    Filtra as releases que contam como deploy dentro da janela [inicio, fim).
    Drafts nunca contam. Pré-releases só contam com incluir_prerelease=True
    (variante C2 da RQ 07).
    """
    ini, fi = parse_data(inicio), parse_data(fim)
    selecionadas = []
    for r in releases:
        if r.get("draft") or not r.get("published_at"):
            continue
        if r.get("prerelease") and not incluir_prerelease:
            continue
        if ini <= parse_data(r["published_at"]) < fi:
            selecionadas.append(r)
    return selecionadas


def calcular_deploy_frequency(
    releases: List[Dict[str, Any]],
    inicio: DataLike,
    fim: DataLike,
    incluir_prerelease: bool = False,
) -> float:
    """
    Deployment frequency (RQ 01), em releases por semana:
    nº de releases publicadas na janela ÷ nº de semanas da janela.
    """
    semanas = semanas_da_janela(inicio, fim)
    if semanas <= 0:
        raise ValueError("A data de fim da janela deve ser posterior à de início.")
    return len(releases_na_janela(releases, inicio, fim, incluir_prerelease)) / semanas

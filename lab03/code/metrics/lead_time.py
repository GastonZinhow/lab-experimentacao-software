from statistics import median
from typing import List, Dict, Any, Optional
from metrics.datas import DataLike, diferenca_horas


def lead_time_release_horas(
    data_release: DataLike, datas_commits: List[DataLike]
) -> Optional[float]:
    """
    Variante (a) para uma release R: data de R − data do commit mais antigo de R, em horas.
    Retorna None se a release não tiver commits novos.
    """
    if not datas_commits:
        return None
    return max(diferenca_horas(data_release, c) for c in datas_commits)


def lead_times_commits_horas(
    data_release: DataLike, datas_commits: List[DataLike]
) -> List[float]:
    """Variante (b) para uma release R: data de R − data de cada commit de R, em horas."""
    return [diferenca_horas(data_release, c) for c in datas_commits]


def _releases_avaliaveis(releases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Cada release é um dict com:
      - published_at: data de publicação da release
      - commit_dates: lista de commit.author.date dos commits incluídos em R
        (None quando o compare não pôde ser feito, ex.: 404)
      - sem_anterior: True se for a primeira release da história do repositório
    Releases sem anterior ou sem compare são ignoradas no lead time.
    """
    return [
        r for r in releases
        if not r.get("sem_anterior") and r.get("commit_dates") is not None
    ]


def calcular_lead_time_a(releases: List[Dict[str, Any]]) -> Optional[float]:
    """
    Lead time por release (RQ 02 a): mediana, entre as releases do repositório,
    de (data de R − commit mais antigo de R). Em horas; None se nada for avaliável.
    """
    valores = [
        lt for r in _releases_avaliaveis(releases)
        if (lt := lead_time_release_horas(r["published_at"], r["commit_dates"])) is not None
    ]
    return median(valores) if valores else None


def calcular_lead_time_b(releases: List[Dict[str, Any]]) -> Optional[float]:
    """
    Lead time por commit (RQ 02 b): mediana de (data de R − data do commit) sobre
    todos os commits de todas as releases. Em horas; None se não houver commits.
    """
    valores: List[float] = []
    for r in _releases_avaliaveis(releases):
        valores.extend(lead_times_commits_horas(r["published_at"], r["commit_dates"]))
    return median(valores) if valores else None

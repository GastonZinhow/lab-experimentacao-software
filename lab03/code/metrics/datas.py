from datetime import datetime, timezone
from typing import Union

DataLike = Union[str, datetime]


def parse_data(valor: DataLike) -> datetime:
    """
    Converte strings ISO-8601 da API ("2024-03-15T10:00:00Z") ou datas simples
    do config ("2024-03-15") em datetime UTC ciente de fuso.
    """
    if isinstance(valor, datetime):
        dt = valor
    else:
        dt = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def diferenca_horas(fim: DataLike, inicio: DataLike) -> float:
    return (parse_data(fim) - parse_data(inicio)).total_seconds() / 3600.0

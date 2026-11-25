"""Baixa, com cache e intervalo educado, os relatórios mensais do GitHub.

Este módulo é executado somente durante a coleta. O pipeline reproduzível lê os
HTMLs já versionados e nunca acessa a internet.
"""

from __future__ import annotations

import csv
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path

import requests


MESES = (
    "november-2025",
    "december-2025",
    "january-2026",
    "february-2026",
    "march-2026",
    "april-2026",
    "may-2026",
    "june-2026",
    "july-2026",
    "august-2026",
    "september-2026",
    "october-2026",
)
PASTA_PADRAO = Path(__file__).resolve().parents[1] / "dados" / "brutos" / "github" / "relatorios"
MANIFESTO_PADRAO = PASTA_PADRAO.parent / "manifesto.csv"
URL = "https://github.blog/news-insights/company-news/github-availability-report-{mes}/"
USER_AGENT = "lab05-coleta/1.0 (pesquisa academica)"


def _ano_mes(indice: int) -> str:
    return f"2025-{indice + 11:02d}" if indice < 2 else f"2026-{indice - 1:02d}"


def _registrar_manifesto(pasta: Path, manifesto: Path = MANIFESTO_PADRAO) -> None:
    campos = ("url", "data_hora_utc", "status_http", "arquivo", "sha256")
    with manifesto.open(encoding="utf-8", newline="") as entrada:
        linhas = list(csv.DictReader(entrada))
    urls = {linha["url"] for linha in linhas}
    for indice, mes in enumerate(MESES):
        url = URL.format(mes=mes)
        arquivo = pasta / f"{_ano_mes(indice)}.html"
        if url in urls or not arquivo.exists():
            continue
        instante = datetime.fromtimestamp(arquivo.stat().st_mtime, timezone.utc)
        linhas.append({
            "url": url,
            "data_hora_utc": instante.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status_http": "200",
            "arquivo": arquivo.relative_to(pasta.parent).as_posix(),
            "sha256": hashlib.sha256(arquivo.read_bytes()).hexdigest(),
        })
    with manifesto.open("w", encoding="utf-8", newline="") as saida:
        escritor = csv.DictWriter(saida, fieldnames=campos, lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(linhas)


def coletar(pasta: Path = PASTA_PADRAO) -> None:
    pasta.mkdir(parents=True, exist_ok=True)
    with requests.Session() as sessao:
        sessao.headers["User-Agent"] = USER_AGENT
        for indice, mes in enumerate(MESES):
            destino = pasta / f"{_ano_mes(indice)}.html"
            if destino.exists():
                continue
            if indice:
                time.sleep(1)
            resposta = sessao.get(URL.format(mes=mes), timeout=30)
            resposta.raise_for_status()
            destino.write_bytes(resposta.content)
            print(f"Salvo: {destino.name}")
    _registrar_manifesto(pasta)


if __name__ == "__main__":
    coletar()

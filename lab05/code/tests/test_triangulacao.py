"""Testes offline da triangulação com os relatórios oficiais."""

from __future__ import annotations

import csv
import importlib.util
from pathlib import Path


CAMINHO = Path(__file__).resolve().parents[1] / "etapas" / "03_triangulacao.py"
SPEC = importlib.util.spec_from_file_location("etapa_triangulacao", CAMINHO)
assert SPEC and SPEC.loader
MODULO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULO)


def test_extrai_todos_os_meses_e_ocorrencias() -> None:
    linhas = []
    for arquivo in sorted(MODULO.PASTA_RELATORIOS.glob("*.html")):
        linhas.extend(MODULO._extrair_relatorio(arquivo))

    assert len(linhas) == 65
    assert {linha["mes"] for linha in linhas} == {
        "2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04",
        "2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10",
    }
    assert all(linha["inicio"].endswith("Z") and linha["causa"] for linha in linhas)


def test_triangulacao_preserva_universo_da_pagina_de_status() -> None:
    relatorios = []
    for arquivo in sorted(MODULO.PASTA_RELATORIOS.glob("*.html")):
        relatorios.extend(MODULO._extrair_relatorio(arquivo))
    linhas = MODULO.triangular(relatorios)

    with MODULO.ARQUIVO_INCIDENTES.open(encoding="utf-8", newline="") as entrada:
        total_github = sum(r["plataforma"] == "github" for r in csv.DictReader(entrada))
    github = [r for r in linhas if r["plataforma"] == "github"]
    ids_status = {r["id_status"] for r in github if r["id_status"]}

    assert len(ids_status) == total_github
    assert len([r for r in github if r["situacao"] != "somente_status"]) == 65
    assert len([r for r in linhas if r["plataforma"] == "gitlab"]) == 1

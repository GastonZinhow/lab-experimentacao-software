"""Peças comuns às seções do dashboard: cores, caminhos e leitura dos dados.

Toda seção pode fazer ``from dashboard_comum import ...`` sem depender do
código de outra pessoa. Enquanto ``incidentes.csv`` não existir, os dados vêm de
``exemplo_incidentes.csv`` e a seção deve chamar ``avisar_se_exemplo``.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PASTA_CODIGO = Path(__file__).resolve().parent
PASTA_DADOS = PASTA_CODIGO / "dados"
PASTA_RESULTADOS = PASTA_CODIGO / "resultados"
ARQUIVO_INCIDENTES = PASTA_DADOS / "processados" / "incidentes.csv"
ARQUIVO_EXEMPLO = PASTA_DADOS / "processados" / "exemplo_incidentes.csv"

JANELA_INICIO = "2025-11-01T00:00:00Z"
JANELA_FIM = "2026-10-31T23:59:59Z"

CORES = {"github": "#6e40c9", "gitlab": "#fc6d26"}
NOMES = {"github": "GitHub.com", "gitlab": "GitLab.com"}
COLUNAS = (
    "plataforma",
    "id",
    "titulo",
    "componentes_originais",
    "componente_equivalente",
    "impacto",
    "inicio_utc",
    "fim_utc",
    "duracao_min",
    "fonte",
    "url",
)


def carregar_incidentes(
    real: Path = ARQUIVO_INCIDENTES, exemplo: Path = ARQUIVO_EXEMPLO
) -> tuple[pd.DataFrame, bool]:
    """Lê os incidentes no formato comum.

    Devolve ``(tabela, eh_exemplo)``. Datas vêm como ``datetime`` em UTC.
    """
    eh_exemplo = not real.exists()
    tabela = pd.read_csv(exemplo if eh_exemplo else real, dtype={"id": str})
    faltando = [coluna for coluna in COLUNAS if coluna not in tabela.columns]
    if faltando:
        raise ValueError(f"Colunas ausentes no formato comum: {', '.join(faltando)}")
    for coluna in ("inicio_utc", "fim_utc"):
        tabela[coluna] = pd.to_datetime(tabela[coluna], utc=True, errors="coerce")
    return tabela, eh_exemplo


def avisar_se_exemplo(eh_exemplo: bool) -> None:
    """Mostra na seção que os números ainda são fictícios."""
    if eh_exemplo:
        import streamlit as st

        st.warning(
            "Dados de exemplo (fictícios). Os números desta seção só valem depois que "
            "`dados/processados/incidentes.csv` for gerado pelo comando único."
        )

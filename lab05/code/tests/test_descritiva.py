"""Testes offline da estatística descritiva."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd


CAMINHO = Path(__file__).resolve().parents[1] / "etapas" / "03_descritiva.py"
SPEC = importlib.util.spec_from_file_location("etapa_descritiva", CAMINHO)
assert SPEC and SPEC.loader
MODULO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULO)


def test_categorias_comparaveis_vem_do_mapa() -> None:
    assert MODULO.categorias_comparaveis() == [
        "api", "ci_cd", "git", "pacotes", "pages", "web"
    ]


def test_frequencia_e_duracao_usam_incidentes_comparaveis() -> None:
    categorias = MODULO.categorias_comparaveis()
    tabela, unicos, _ = MODULO.calcular_descritiva(
        MODULO.carregar_incidentes(), categorias
    )
    mensal = tabela[tabela["metrica"] == "frequencia_mensal"]
    resumo = tabela[tabela["metrica"] == "frequencia_resumo"].set_index("plataforma")
    duracao = tabela[tabela["metrica"] == "duracao"].set_index("plataforma")

    assert len(mensal) == 24
    assert mensal.groupby("plataforma")["valor"].sum().to_dict() == {
        "github": 134, "gitlab": 86,
    }
    assert resumo["valor"].to_dict() == {"github": 134, "gitlab": 86}
    assert (resumo["dispersao"] > 0).all()
    assert unicos.groupby("plataforma")["id"].nunique().to_dict() == {
        "github": 134, "gitlab": 86,
    }
    assert duracao["n"].to_dict() == {"github": 126, "gitlab": 86}
    assert (duracao["iqr"] == duracao["q3"] - duracao["q1"]).all()


def test_mtbf_nao_fica_negativo_e_impacto_ausente_e_explicito() -> None:
    tabela, _, _ = MODULO.calcular_descritiva(
        MODULO.carregar_incidentes(), MODULO.categorias_comparaveis()
    )
    mtbf = tabela[tabela["metrica"] == "mtbf_proxy"]
    impacto = tabela[tabela["metrica"] == "distribuicao_impacto"]

    assert len(mtbf) == 14  # total + seis componentes, por plataforma
    assert (pd.to_numeric(mtbf["minimo"], errors="coerce").dropna() >= 0).all()
    gitlab = impacto[impacto["plataforma"] == "gitlab"]
    assert gitlab[["impacto", "n", "proporcao"]].to_dict("records") == [
        {"impacto": "nao_informado", "n": 86, "proporcao": 1.0}
    ]


def test_graficos_sao_gerados_com_ids_estaveis(tmp_path: Path) -> None:
    categorias = MODULO.categorias_comparaveis()
    tabela, unicos, explodida = MODULO.calcular_descritiva(
        MODULO.carregar_incidentes(), categorias
    )
    MODULO.gerar_figuras(tabela, unicos, explodida, categorias, tmp_path)

    esperados = {
        "serie_mensal.html": "serie-mensal",
        "duracao_violino.html": "duracao-violino",
        "incidentes_componente.html": "incidentes-componente",
    }
    for nome, identificador in esperados.items():
        conteudo = (tmp_path / nome).read_text(encoding="utf-8")
        assert identificador in conteudo
        assert "cdn.plot.ly" in conteudo

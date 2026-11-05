import numpy as np
import pandas as pd
import pytest

pytest.importorskip("streamlit")
pytest.importorskip("plotly")

from secoes.secao_2_dados import (
    FAIXAS_DEFEITOS,
    FAIXAS_LOC,
    figura_g1,
    percentual_por_faixa,
    simular_para_g1,
    tabela_g1,
    texto_g1,
)
from dados_reais import ARQUIVO_AMOSTRA


@pytest.fixture
def dados():
    return pd.read_csv(ARQUIVO_AMOSTRA), simular_para_g1()


def test_faixas_nao_perdem_nenhum_modulo(dados):
    real, simulado = dados
    for conjunto in (real, simulado):
        assert percentual_por_faixa(conjunto["loc"], FAIXAS_LOC).sum() == pytest.approx(100)
        assert percentual_por_faixa(conjunto["defeitos"], FAIXAS_DEFEITOS).sum() == pytest.approx(100)


def test_faixa_de_zero_defeito_conta_so_os_zeros():
    percentuais = percentual_por_faixa(np.array([0, 0, 1, 5, 6, 51]), FAIXAS_DEFEITOS)
    assert percentuais["0"] == pytest.approx(100 * 2 / 6)
    assert percentuais["1–5"] == pytest.approx(100 * 2 / 6)
    assert percentuais["51+"] == pytest.approx(100 / 6)


def test_g1_tem_titulo_eixos_legenda_e_real_e_simulado_nas_duas_variaveis(dados):
    figura = figura_g1(*dados)
    assert len(figura.data) == 4
    assert "G1" in figura.layout.title.text
    assert "LOC" in figura.layout.xaxis.title.text
    assert "Defeitos" in figura.layout.xaxis2.title.text
    assert "%" in figura.layout.yaxis.title.text
    assert sum(1 for serie in figura.data if serie.showlegend) == 2


def test_tabela_tem_uma_linha_por_faixa(dados):
    assert len(tabela_g1(*dados)) == len(FAIXAS_LOC[1]) + len(FAIXAS_DEFEITOS[1])


def test_texto_tem_de_duas_a_quatro_frases_e_usa_os_valores_reais(dados):
    texto = texto_g1(*dados)
    assert 2 <= texto.count(". ") + 1 <= 4
    assert "2883" in texto
    assert "63%" in texto

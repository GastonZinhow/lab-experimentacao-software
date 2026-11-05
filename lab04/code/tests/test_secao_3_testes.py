import numpy as np
import pytest
from scipy import stats

pytest.importorskip("streamlit")
pytest.importorskip("plotly")

from exemplo import N, rodar_exemplo
from secoes.secao_3_testes import (
    COR_PEARSON,
    COR_SPEARMAN,
    figura_g2,
    resumo_pearson,
    resumo_spearman,
    simular_rho_h0,
    tabela_g2,
    texto_g2,
)

REPETICOES_TESTE = 2_000


@pytest.fixture(scope="module")
def exemplo():
    _, resultados = rodar_exemplo()
    return resultados, simular_rho_h0(repeticoes=REPETICOES_TESTE)


def test_rho_sob_h0_fica_centrado_em_zero(exemplo):
    _, rhos = exemplo
    assert len(rhos) == REPETICOES_TESTE
    assert np.all(np.abs(rhos) <= 1)
    assert rhos.mean() == pytest.approx(0, abs=0.01)


def test_regiao_de_rejeicao_do_pearson_e_o_quantil_da_t():
    # Valor de tabela: t(0,975; 28) = 2,048. Para r = 0,3 e n = 30, t = 1,664 e p = 0,107.
    resumo = resumo_pearson({"coeficiente": 0.3, "p_valor": 0.107}, n=30)
    assert resumo["critico"] == pytest.approx(2.048, abs=1e-3)
    assert resumo["observado"] == pytest.approx(1.664, abs=1e-3)
    assert resumo["p_valor_area"] == pytest.approx(0.107, abs=1e-3)


def test_regiao_de_rejeicao_do_spearman_deixa_5_por_cento_nas_caudas(exemplo):
    resultados, rhos = exemplo
    resumo = resumo_spearman(resultados["spearman"], rhos)
    fora = np.mean((rhos < resumo["critico_inf"]) | (rhos > resumo["critico"]))
    assert fora == pytest.approx(0.05, abs=0.005)


def test_p_valor_da_area_simulada_fica_perto_do_scipy(exemplo):
    resultados, rhos = exemplo
    resumo = resumo_spearman(resultados["spearman"], rhos)
    assert resumo["p_valor_area"] == pytest.approx(resumo["p_valor"], abs=0.01)


def test_g2_tem_titulo_eixos_legenda_e_cores_do_grupo(exemplo):
    figura = figura_g2(*exemplo)
    assert "G2" in figura.layout.title.text
    assert "t" in figura.layout.xaxis.title.text
    assert "ρ" in figura.layout.xaxis2.title.text
    assert "Densidade" in figura.layout.yaxis.title.text
    nomes = [serie.name for serie in figura.data if serie.showlegend is not False]
    assert any("Região de rejeição" in nome for nome in nomes)
    assert any("p-valor" in nome and "Pearson" in nome for nome in nomes)
    assert any("p-valor" in nome and "Spearman" in nome for nome in nomes)
    cores_das_curvas = {serie.line.color for serie in figura.data if serie.mode == "lines"}
    assert cores_das_curvas == {COR_PEARSON, COR_SPEARMAN}


def test_regiao_de_rejeicao_e_p_valor_sao_areas(exemplo):
    figura = figura_g2(*exemplo)
    areas = [serie for serie in figura.data if serie.fill == "tozeroy"]
    assert any("Região de rejeição" in serie.name for serie in areas)
    assert any("p-valor" in serie.name for serie in areas)


def test_tabela_tem_uma_linha_por_teste(exemplo):
    tabela = tabela_g2(*exemplo)
    assert list(tabela["Teste"]) == ["Pearson", "Spearman"]


def test_texto_tem_de_duas_a_quatro_frases_e_usa_os_valores_do_exemplo(exemplo):
    resultados, rhos = exemplo
    texto = texto_g2(resultados, rhos)
    assert 2 <= texto.count(". ") + 1 <= 4
    assert f"n = {N}" in texto
    assert f"{resultados['spearman']['coeficiente']:.2f}".replace(".", ",") in texto

import numpy as np
import pytest

pytest.importorskip("streamlit")
pytest.importorskip("plotly")

from poder_interativo import CORES, estimar_poder, figura_poder, tabela_poder, texto_poder


def gerar_normal(situacao, efeito, n, rng):
    x = rng.standard_normal(n)
    return {"loc": x, "defeitos": efeito * x + np.sqrt(1 - efeito**2) * rng.standard_normal(n)}


def test_poder_cresce_com_o_efeito_e_com_n():
    fraco = estimar_poder("base", 0.2, 30, repeticoes=400, _gerar=gerar_normal)
    forte = estimar_poder("base", 0.6, 30, repeticoes=400, _gerar=gerar_normal)
    grande = estimar_poder("base", 0.2, 150, repeticoes=400, _gerar=gerar_normal)
    for teste in ("pearson", "spearman"):
        assert forte[teste] > fraco[teste]
        assert grande[teste] > fraco[teste]


def test_usa_o_gerador_real_por_padrao():
    poder = estimar_poder("base", 0.0, 30, repeticoes=200)
    assert set(poder) == {"pearson", "spearman"}
    assert all(0 <= valor <= 0.15 for valor in poder.values())


def test_grafico_tem_titulo_eixos_legenda_cores_e_linha_em_alfa():
    figura = figura_poder({"pearson": 0.4, "spearman": 0.6}, n=30, efeito=0.3)
    assert "n = 30" in figura.layout.title.text
    assert "Teste" in figura.layout.xaxis.title.text
    assert "%" in figura.layout.yaxis.title.text
    assert {serie.marker.color for serie in figura.data} == set(CORES.values())
    assert figura.layout.showlegend
    assert figura.layout.shapes[0].y0 == pytest.approx(5)


def test_com_efeito_zero_o_grafico_e_o_texto_falam_de_erro_tipo_i():
    poder = {"pearson": 0.06, "spearman": 0.05}
    assert "erro tipo I" in figura_poder(poder, n=30, efeito=0.0).layout.title.text
    assert "erro tipo I" in texto_poder(poder, n=30, efeito=0.0)


@pytest.mark.parametrize("poder, esperado", [
    ({"pearson": 0.40, "spearman": 0.60}, "o Spearman detectou"),
    ({"pearson": 0.70, "spearman": 0.50}, "o Pearson detectou"),
    ({"pearson": 0.50, "spearman": 0.51}, "frequência parecida"),
])
def test_texto_compara_os_testes(poder, esperado):
    texto = texto_poder(poder, n=30, efeito=0.3)
    assert esperado in texto
    assert 2 <= texto.count(". ") + 1 <= 4


def test_tabela_tem_uma_linha_por_teste():
    assert list(tabela_poder({"pearson": 0.4, "spearman": 0.6}, 30, 0.3)["Teste"]) == ["Pearson", "Spearman"]

import pandas as pd
import pytest
from scipy.stats import kruskal

from metrics.estatistica import (
    cliffs_delta,
    comparar_grupos,
    epsilon_quadrado,
    interpretar_cliffs_delta,
    interpretar_epsilon_quadrado,
    quartis,
)


def test_cliffs_delta_extremos():
    assert cliffs_delta([4, 5, 6], [1, 2, 3]) == pytest.approx(1.0)
    assert cliffs_delta([1, 2, 3], [4, 5, 6]) == pytest.approx(-1.0)


def test_cliffs_delta_grupos_iguais_e_zero():
    assert cliffs_delta([1, 2, 3], [1, 2, 3]) == pytest.approx(0.0)


def test_cliffs_delta_bate_com_contagem_de_pares():
    x, y = [1, 3, 5, 7], [2, 2, 6]
    # pares x > y menos pares x < y, dividido por n1·n2
    maiores = sum(a > b for a in x for b in y)
    menores = sum(a < b for a in x for b in y)
    assert cliffs_delta(x, y) == pytest.approx((maiores - menores) / (len(x) * len(y)))


def test_cliffs_delta_grupo_vazio():
    with pytest.raises(ValueError):
        cliffs_delta([], [1, 2])


@pytest.mark.parametrize("delta, esperado", [
    (0.0, "desprezível"), (-0.146, "desprezível"), (0.147, "pequeno"),
    (-0.329, "pequeno"), (0.33, "médio"), (0.473, "médio"),
    (0.474, "grande"), (-1.0, "grande"),
])
def test_interpretacao_romano(delta, esperado):
    assert interpretar_cliffs_delta(delta) == esperado


@pytest.mark.parametrize("eps2, esperado", [
    (0.005, "desprezível"), (0.01, "pequeno"), (0.08, "médio"), (0.26, "grande"),
])
def test_interpretacao_epsilon(eps2, esperado):
    assert interpretar_epsilon_quadrado(eps2) == esperado


def test_epsilon_quadrado_formula():
    assert epsilon_quadrado(9.9, 100) == pytest.approx(0.1)
    with pytest.raises(ValueError):
        epsilon_quadrado(1.0, 1)


def test_quartis_divide_em_quatro_grupos_iguais():
    grupos = quartis(pd.Series(range(1, 9)))
    assert grupos.tolist() == ["Q1", "Q1", "Q2", "Q2", "Q3", "Q3", "Q4", "Q4"]


def test_comparar_tres_grupos_usa_kruskal():
    grupos = {"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]}
    res = comparar_grupos(grupos)
    h, p = kruskal(*grupos.values())
    assert res["teste"] == "Kruskal-Wallis"
    assert res["estatistica"] == pytest.approx(h)
    assert res["p"] == pytest.approx(p)
    assert res["n"] == 9 and res["grupos"] == 3
    assert res["tamanho_efeito"] == pytest.approx(h / 8)


def test_comparar_dois_grupos_usa_mann_whitney():
    res = comparar_grupos({"a": [4, 5, 6], "b": [1, 2, 3], "vazio": []})
    assert res["teste"] == "Mann-Whitney"
    assert res["efeito"] == "Cliff's delta"
    assert res["tamanho_efeito"] == pytest.approx(1.0)
    assert res["interpretacao"] == "grande"


def test_comparar_um_grupo_falha():
    with pytest.raises(ValueError):
        comparar_grupos({"a": [1, 2], "b": []})

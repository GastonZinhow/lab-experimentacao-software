import numpy as np
import pytest
from scipy import stats

from exemplo import N, rodar_exemplo
from testes import TESTES, aplicar_testes, classificar_magnitude, estatistica_t, resumir


def test_devolve_coeficiente_e_p_valor_dos_dois_testes():
    resultado = aplicar_testes({"loc": [10, 20, 30, 40], "defeitos": [0, 1, 1, 3]})
    assert set(resultado) == set(TESTES)
    for valores in resultado.values():
        assert set(valores) == {"coeficiente", "p_valor"}
        assert isinstance(valores["coeficiente"], float)
        assert isinstance(valores["p_valor"], float)


def test_exemplo_calculado_a_mao():
    # Os valores já são postos, então r = ρ = 1 − 6·Σd² / (n(n² − 1)) = 1 − 6·4 / 120 = 0,8.
    # t = 0,8·√(3 / 0,36) = 2,309 com 3 g.l., cujo p-valor bicaudal é 0,1041.
    resultado = aplicar_testes({"loc": [1, 2, 3, 4, 5], "defeitos": [2, 1, 4, 3, 5]})
    for teste in TESTES:
        assert resultado[teste]["coeficiente"] == pytest.approx(0.8)
        assert resultado[teste]["p_valor"] == pytest.approx(0.1041, abs=1e-4)


def test_confere_com_as_formulas_de_cada_teste():
    rng = np.random.default_rng(3)
    loc = rng.lognormal(5, 1.4, size=40).round() + 1
    defeitos = rng.poisson(loc / 100)
    resultado = aplicar_testes({"loc": loc, "defeitos": defeitos})
    n = len(loc)

    r = np.corrcoef(loc, defeitos)[0, 1]
    assert resultado["pearson"]["coeficiente"] == pytest.approx(r)
    assert resultado["pearson"]["p_valor"] == pytest.approx(2 * stats.t.sf(abs(estatistica_t(r, n)), n - 2))

    rho = np.corrcoef(stats.rankdata(loc), stats.rankdata(defeitos))[0, 1]
    assert resultado["spearman"]["coeficiente"] == pytest.approx(rho)
    assert resultado["spearman"]["p_valor"] == pytest.approx(2 * stats.t.sf(abs(estatistica_t(rho, n)), n - 2))


def test_relacao_monotonica_nao_linear_da_rho_1_e_r_menor_que_1():
    x = np.arange(1, 21)
    resultado = aplicar_testes({"loc": x, "defeitos": np.exp(x / 2)})
    assert resultado["spearman"]["coeficiente"] == pytest.approx(1)
    assert resultado["pearson"]["coeficiente"] < 0.8


def test_um_ponto_extremo_infla_r_mas_pouco_muda_rho():
    loc = [10, 20, 30, 40, 50, 60, 70, 80, 90, 3000]
    defeitos = [5, 1, 4, 0, 3, 2, 6, 0, 1, 100]
    resultado = aplicar_testes({"loc": loc, "defeitos": defeitos})
    assert resultado["pearson"]["coeficiente"] > 0.9
    assert resultado["spearman"]["coeficiente"] < 0.3


def test_correlacao_negativa_tem_sinal_negativo():
    resultado = aplicar_testes({"loc": [1, 2, 3, 4, 5, 6], "defeitos": [9, 7, 6, 4, 2, 1]})
    assert resultado["pearson"]["coeficiente"] < -0.9
    assert resultado["spearman"]["coeficiente"] == pytest.approx(-1)


@pytest.mark.parametrize("dados", [
    {"loc": [1, 2, 3], "defeitos": [1, 2]},
    {"loc": [1, 2], "defeitos": [1, 2]},
])
def test_dados_invalidos_geram_erro(dados):
    with pytest.raises(ValueError):
        aplicar_testes(dados)


@pytest.mark.parametrize("coeficiente, esperado", [
    (0.0, "desprezível"), (0.099, "desprezível"), (0.1, "fraca"), (-0.29, "fraca"),
    (0.3, "moderada"), (-0.49, "moderada"), (0.5, "forte"), (-1.0, "forte"),
])
def test_classificar_magnitude_segue_os_limiares_de_cohen(coeficiente, esperado):
    assert classificar_magnitude(coeficiente) == esperado


def test_resumir_acrescenta_magnitude_e_decisao():
    resumo = resumir({
        "pearson": {"coeficiente": 0.62, "p_valor": 0.0003},
        "spearman": {"coeficiente": 0.25, "p_valor": 0.18},
    })
    assert resumo["pearson"]["magnitude"] == "forte"
    assert resumo["pearson"]["rejeita_h0"] is True
    assert resumo["spearman"]["magnitude"] == "fraca"
    assert resumo["spearman"]["rejeita_h0"] is False


def test_exemplo_e_reproduzivel_e_usa_n_modulos():
    dados, primeiro = rodar_exemplo()
    _, segundo = rodar_exemplo()
    assert len(dados["loc"]) == N
    assert primeiro == segundo


def test_exemplo_aceita_gerador_e_testes_como_parametros():
    def gerar_fixo(situacao, efeito, n, rng):
        return {"loc": np.arange(1, n + 1), "defeitos": np.arange(1, n + 1)}

    _, resultado = rodar_exemplo(gerar=gerar_fixo, efeito=0.0)
    assert resultado["pearson"]["coeficiente"] == pytest.approx(1)
    assert resultado["spearman"]["coeficiente"] == pytest.approx(1)

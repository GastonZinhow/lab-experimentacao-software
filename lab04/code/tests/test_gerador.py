import numpy as np
import pytest
from scipy import stats

from gerador import SITUACOES, carregar_parametros, gerar

N_GRANDE = 100_000


def amostra_grande(efeito, semente=7):
    return gerar("base", efeito, N_GRANDE, np.random.default_rng(semente))


def test_devolve_loc_e_defeitos_com_n_modulos_validos():
    dados = gerar("base", 0.3, 50, np.random.default_rng(1))
    assert set(dados) == {"loc", "defeitos"}
    assert len(dados["loc"]) == len(dados["defeitos"]) == 50
    assert dados["loc"].min() >= 1
    assert dados["defeitos"].min() >= 0
    assert np.issubdtype(dados["loc"].dtype, np.integer)
    assert np.issubdtype(dados["defeitos"].dtype, np.integer)


def test_mesma_semente_gera_os_mesmos_dados():
    primeira = gerar("base", 0.3, 100, np.random.default_rng(42))
    segunda = gerar("base", 0.3, 100, np.random.default_rng(42))
    np.testing.assert_array_equal(primeira["loc"], segunda["loc"])
    np.testing.assert_array_equal(primeira["defeitos"], segunda["defeitos"])


def test_sementes_diferentes_geram_dados_diferentes():
    primeira = gerar("base", 0.3, 100, np.random.default_rng(1))
    segunda = gerar("base", 0.3, 100, np.random.default_rng(2))
    assert not np.array_equal(primeira["loc"], segunda["loc"])


def test_parametros_simulados_ficam_proximos_dos_definidos():
    parametros = carregar_parametros()
    dados = amostra_grande(0.0)
    logs = np.log(dados["loc"])
    assert logs.mean() == pytest.approx(parametros["loc"]["mu"], abs=0.05)
    assert logs.std() == pytest.approx(parametros["loc"]["sigma"], abs=0.05)
    assert dados["defeitos"].mean() == pytest.approx(parametros["defeitos"]["media"], rel=0.05)
    media, k = parametros["defeitos"]["media"], parametros["defeitos"]["k"]
    assert np.mean(dados["defeitos"] == 0) == pytest.approx((k / (k + media)) ** k, abs=0.01)


def test_efeito_nao_muda_a_forma_de_cada_variavel():
    sem_efeito, com_efeito = amostra_grande(0.0), amostra_grande(0.6)
    assert np.median(sem_efeito["loc"]) == pytest.approx(np.median(com_efeito["loc"]), rel=0.05)
    assert np.mean(sem_efeito["defeitos"] == 0) == pytest.approx(np.mean(com_efeito["defeitos"] == 0), abs=0.01)


def test_efeito_zero_nao_gera_associacao():
    dados = amostra_grande(0.0)
    assert abs(stats.spearmanr(dados["loc"], dados["defeitos"]).statistic) < 0.01


def test_associacao_cresce_com_o_efeito():
    rhos = []
    for efeito in (0.0, 0.2, 0.4, 0.6, 0.8):
        dados = amostra_grande(efeito)
        rhos.append(stats.spearmanr(dados["loc"], dados["defeitos"]).statistic)
    assert all(a < b for a, b in zip(rhos, rhos[1:]))


def test_efeito_calibrado_reproduz_o_rho_da_amostra():
    associacao = carregar_parametros()["associacao"]
    dados = amostra_grande(associacao["efeito_calibrado"])
    rho = stats.spearmanr(dados["loc"], dados["defeitos"]).statistic
    assert rho == pytest.approx(associacao["rho_spearman_amostra"], abs=0.01)


def test_situacao_base_esta_disponivel():
    assert "base" in SITUACOES


@pytest.mark.parametrize("situacao, efeito", [("inexistente", 0.0), ("base", 1.0), ("base", -1.0), ("base", 1.5)])
def test_argumentos_invalidos_geram_erro(situacao, efeito):
    with pytest.raises(ValueError):
        gerar(situacao, efeito, 10, np.random.default_rng(1))

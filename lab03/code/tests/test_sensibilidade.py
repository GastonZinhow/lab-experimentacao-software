import pytest
from sklearn.metrics import cohen_kappa_score

from metrics.classificacao import ELITE, HIGH, LOW, MEDIUM
from metrics.sensibilidade import (
    ORDEM_CATEGORIAS,
    classificar_combinacao,
    comparar_classificacoes,
)


def test_classificar_combinacao_devolve_metricas_e_geral():
    resultado = classificar_combinacao(2.0, 12.0, 0.20, 10 * 24.0)
    assert resultado == {
        "deploy_frequency": HIGH,
        "lead_time": ELITE,
        "cfr": HIGH,
        "tempo_recuperacao": LOW,
        "geral": HIGH,
    }


def test_comparar_classificacoes_usa_ordem_ordinal_explicitamente():
    a = [ELITE, HIGH, MEDIUM, LOW, MEDIUM, ELITE]
    b = [HIGH, HIGH, LOW, LOW, ELITE, MEDIUM]
    resultado = comparar_classificacoes(a, b)

    esperado = cohen_kappa_score(
        a, b, labels=list(ORDEM_CATEGORIAS), weights="linear"
    )
    ordem_alfabetica = cohen_kappa_score(a, b, weights="linear")
    assert resultado["kappa_ponderado_linear"] == pytest.approx(esperado)
    assert resultado["kappa_ponderado_linear"] != pytest.approx(ordem_alfabetica)
    assert resultado["n_mudaram"] == 4
    assert resultado["n_mudancas_adjacentes"] == 2
    assert resultado["n_mudancas_distantes"] == 2


def test_comparar_classificacoes_ignora_pares_ausentes():
    resultado = comparar_classificacoes(
        [ELITE, None, MEDIUM, LOW],
        [HIGH, HIGH, MEDIUM, None],
    )
    assert resultado["n_repositorios"] == 2
    assert resultado["n_mudaram"] == 1
    assert resultado["percentual_mudanca"] == 50.0


def test_comparar_classificacoes_sem_pares_validos():
    resultado = comparar_classificacoes([None], [None])
    assert resultado["n_repositorios"] == 0
    assert resultado["percentual_mudanca"] is None
    assert resultado["kappa_ponderado_linear"] is None


def test_comparar_classificacoes_exige_tamanhos_iguais():
    with pytest.raises(ValueError, match="mesmo tamanho"):
        comparar_classificacoes([ELITE], [ELITE, HIGH])

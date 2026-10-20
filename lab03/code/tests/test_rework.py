import pytest

from metrics.rework import calcular_rework_rate


@pytest.mark.parametrize("corretivas,total,esperado", [
    (0, 10, 0.0),
    (3, 12, 0.25),
    (10, 10, 1.0),
])
def test_calcular_rework_rate(corretivas, total, esperado):
    assert calcular_rework_rate(corretivas, total) == esperado


@pytest.mark.parametrize("corretivas,total", [(None, 10), (0, None), (0, 0)])
def test_rework_rate_indefinida_sem_denominador(corretivas, total):
    assert calcular_rework_rate(corretivas, total) is None


@pytest.mark.parametrize("corretivas,total", [(-1, 10), (11, 10), (1, -1)])
def test_rework_rate_rejeita_contagens_invalidas(corretivas, total):
    with pytest.raises(ValueError, match="Contagens de releases inválidas"):
        calcular_rework_rate(corretivas, total)

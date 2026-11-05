import json

import numpy as np
import pandas as pd
import pytest

from dados_reais import (
    ARQUIVO_AMOSTRA,
    ARQUIVO_PARAMETROS,
    ajustar_binomial_negativa,
    ajustar_lognormal,
    descrever,
    ler_arff,
    preparar,
    sortear_amostra,
)


def test_ler_arff_devolve_as_145_classes_sem_valores_invalidos():
    dados = ler_arff()
    assert len(dados) == 145
    assert list(dados.columns) == ["linha_arff", "loc", "defeitos"]
    assert dados["loc"].min() >= 1
    assert dados["defeitos"].min() >= 0
    assert dados["defeitos"].max() == 101


def test_sorteio_da_amostra_e_reproduzivel_e_sem_repeticao():
    populacao = ler_arff()
    primeira = sortear_amostra(populacao)
    segunda = sortear_amostra(populacao)
    pd.testing.assert_frame_equal(primeira, segunda)
    assert len(primeira) == 30
    assert primeira["linha_arff"].is_unique


def assert_parametros_iguais(novos, versionados):
    """Compara os parâmetros tolerando só o ruído de ponto flutuante entre plataformas.

    `k` vem de uma otimização numérica, e o último dígito pode mudar entre
    sistemas operacionais ou versões do NumPy/SciPy.
    """
    assert novos.keys() == versionados.keys()
    for chave, valor in versionados.items():
        if isinstance(valor, dict):
            assert_parametros_iguais(novos[chave], valor)
        elif isinstance(valor, float):
            assert novos[chave] == pytest.approx(valor, rel=1e-9), chave
        else:
            assert novos[chave] == valor, chave


def test_arquivos_versionados_sao_regerados_igualmente(tmp_path):
    amostra_nova = tmp_path / "amostra.csv"
    parametros_novos = tmp_path / "parametros.json"
    preparar(arquivo_amostra=amostra_nova, arquivo_parametros=parametros_novos)
    pd.testing.assert_frame_equal(pd.read_csv(amostra_nova), pd.read_csv(ARQUIVO_AMOSTRA))
    assert_parametros_iguais(
        json.loads(parametros_novos.read_text(encoding="utf-8")),
        json.loads(ARQUIVO_PARAMETROS.read_text(encoding="utf-8")),
    )


def test_ajuste_lognormal_recupera_os_parametros():
    valores = np.random.default_rng(1).lognormal(5, 1.5, 50_000)
    mu, sigma = ajustar_lognormal(valores)
    assert mu == pytest.approx(5, abs=0.03)
    assert sigma == pytest.approx(1.5, abs=0.03)


def test_ajuste_binomial_negativa_recupera_os_parametros():
    media_real, k_real = 8.0, 0.2
    valores = np.random.default_rng(1).negative_binomial(k_real, k_real / (k_real + media_real), 50_000)
    media, k = ajustar_binomial_negativa(valores)
    assert media == pytest.approx(media_real, rel=0.05)
    assert k == pytest.approx(k_real, rel=0.05)


def test_descrever_calcula_valores_conhecidos():
    resumo = descrever(np.array([0, 0, 1, 2, 100]))
    assert resumo["n"] == 5
    assert resumo["mediana"] == 1
    assert resumo["maximo"] == 100
    assert resumo["proporcao_zeros"] == pytest.approx(0.4)
    assert resumo["outliers_iqr"] == 1

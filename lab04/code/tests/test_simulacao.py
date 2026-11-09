import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from simulacao import (
    COLUNAS_ERRO_TIPO1,
    arquivo_erro_tipo1,
    gerar_conjuntos,
    margem_monte_carlo,
    proporcao_rejeicao,
    simular_erro_tipo1,
)
from testes import aplicar_testes, aplicar_testes_em_lote

ETAPA = Path(__file__).resolve().parents[1] / "etapas" / "03_erro_tipo1.py"


def carregar_etapa():
    especificacao = importlib.util.spec_from_file_location("etapa_03", ETAPA)
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


def gerar_normal(situacao, efeito, n, rng):
    """Gerador provisório: normal bivariada, em que o Pearson é exatamente válido."""
    x = rng.standard_normal(n)
    y = efeito * x + np.sqrt(1 - efeito**2) * rng.standard_normal(n)
    return {"loc": x, "defeitos": y}


def test_lote_da_os_mesmos_resultados_que_aplicar_testes_um_a_um():
    loc, defeitos = gerar_conjuntos("base", 0.3, 30, 200, np.random.default_rng(5))
    lote = aplicar_testes_em_lote(loc, defeitos)
    for i in range(len(loc)):
        individual = aplicar_testes({"loc": loc[i], "defeitos": defeitos[i]})
        for teste, valores in individual.items():
            assert lote[teste]["coeficiente"][i] == pytest.approx(valores["coeficiente"], abs=1e-12)
            assert lote[teste]["p_valor"][i] == pytest.approx(valores["p_valor"], abs=1e-12)


def test_lote_devolve_nan_quando_uma_variavel_e_constante():
    lote = aplicar_testes_em_lote([[1, 2, 3, 4]], [[0, 0, 0, 0]])
    assert np.isnan(lote["pearson"]["p_valor"][0])
    assert np.isnan(lote["spearman"]["p_valor"][0])


def test_p_valor_nan_conta_como_nao_rejeicao():
    def gerar_constante(situacao, efeito, n, rng):
        return {"loc": rng.standard_normal(n), "defeitos": np.zeros(n)}

    proporcoes = proporcao_rejeicao("base", 0.0, 10, 50, np.random.default_rng(1), gerar=gerar_constante)
    assert proporcoes == {"pearson": 0.0, "spearman": 0.0}


def test_teste_valido_fica_perto_de_5_por_cento():
    tabela = simular_erro_tipo1("normal", gerar=gerar_normal)
    margem = margem_monte_carlo()
    assert margem == pytest.approx(0.0043, abs=1e-4)
    for proporcao in tabela["proporcao_rejeicao"]:
        assert proporcao == pytest.approx(0.05, abs=margem)


def test_tabela_tem_as_colunas_combinadas_e_uma_linha_por_teste():
    tabela = simular_erro_tipo1("normal", repeticoes=200, gerar=gerar_normal)
    assert list(tabela.columns) == COLUNAS_ERRO_TIPO1
    assert list(tabela["teste"]) == ["pearson", "spearman"]
    assert set(tabela["n"]) == {30}
    assert set(tabela["alfa"]) == {0.05}
    assert set(tabela["repeticoes"]) == {200}


def test_mesma_semente_da_o_mesmo_resultado():
    primeira = simular_erro_tipo1("normal", repeticoes=500, gerar=gerar_normal)
    segunda = simular_erro_tipo1("normal", repeticoes=500, gerar=gerar_normal)
    pd.testing.assert_frame_equal(primeira, segunda)


def test_gera_os_dados_com_h0_verdadeira():
    efeitos = []

    def gerar_espiao(situacao, efeito, n, rng):
        efeitos.append(efeito)
        return gerar_normal(situacao, efeito, n, rng)

    simular_erro_tipo1("normal", repeticoes=20, gerar=gerar_espiao)
    assert set(efeitos) == {0.0}
    assert len(efeitos) == 20


def test_etapa_salva_um_csv_por_situacao(tmp_path):
    carregar_etapa().main(gerar=gerar_normal, situacoes=("a", "b"), pasta=tmp_path, repeticoes=100)
    for situacao in ("a", "b"):
        tabela = pd.read_csv(arquivo_erro_tipo1(situacao, tmp_path))
        assert list(tabela.columns) == COLUNAS_ERRO_TIPO1
        assert set(tabela["situacao"]) == {situacao}

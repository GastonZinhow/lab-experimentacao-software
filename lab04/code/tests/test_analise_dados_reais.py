import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from analise_dados_reais import (
    ARQUIVO_RESULTADO,
    COLUNAS,
    analisar,
    carregar_amostra,
    conjuntos_analisados,
    intervalo_confianca,
)
from testes import aplicar_testes


def test_intervalo_de_pearson_bate_com_a_conta_de_fisher():
    inferior, superior = intervalo_confianca(0.5, 30, "pearson")
    assert inferior == pytest.approx(0.1704, abs=1e-4)
    assert superior == pytest.approx(0.7289, abs=1e-4)


@pytest.mark.parametrize("teste", ["pearson", "spearman"])
def test_intervalo_contem_o_coeficiente_e_estreita_com_n(teste):
    pequeno = intervalo_confianca(0.4, 20, teste)
    grande = intervalo_confianca(0.4, 200, teste)
    assert pequeno[0] < 0.4 < pequeno[1]
    assert grande[1] - grande[0] < pequeno[1] - pequeno[0]


def test_intervalo_de_spearman_e_mais_largo_que_o_de_pearson():
    pearson = intervalo_confianca(0.5, 30, "pearson")
    spearman = intervalo_confianca(0.5, 30, "spearman")
    assert spearman[1] - spearman[0] > pearson[1] - pearson[0]


@pytest.mark.parametrize("teste, n", [("kendall", 30), ("pearson", 3)])
def test_intervalo_com_argumentos_invalidos_gera_erro(teste, n):
    with pytest.raises(ValueError):
        intervalo_confianca(0.5, n, teste)


def test_sensibilidade_remove_so_a_maior_classe():
    amostra = carregar_amostra()
    conjuntos = conjuntos_analisados(amostra)
    sem_maior = conjuntos["sem_maior_classe"]
    assert len(sem_maior) == len(amostra) - 1
    assert amostra["loc"].max() not in set(sem_maior["loc"])
    assert sem_maior["loc"].max() == np.sort(amostra["loc"])[-2]


def test_analise_usa_os_mesmos_numeros_de_aplicar_testes():
    amostra = carregar_amostra()
    tabela = analisar(amostra)
    assert list(tabela.columns) == COLUNAS
    assert len(tabela) == 4
    esperado = aplicar_testes({"loc": amostra["loc"], "defeitos": amostra["defeitos"]})
    linhas = tabela[tabela["conjunto"] == "amostra"].set_index("teste")
    for teste, valores in esperado.items():
        assert linhas.loc[teste, "coeficiente"] == pytest.approx(valores["coeficiente"])
        assert linhas.loc[teste, "p_valor"] == pytest.approx(valores["p_valor"])
        assert linhas.loc[teste, "rejeita_h0"] == (valores["p_valor"] < 0.05)
    assert (tabela["ic95_inferior"] < tabela["coeficiente"]).all()
    assert (tabela["coeficiente"] < tabela["ic95_superior"]).all()


def test_etapa_regera_o_csv_versionado(tmp_path):
    caminho = Path(__file__).resolve().parents[1] / "etapas" / "05_dados_reais.py"
    especificacao = importlib.util.spec_from_file_location("etapa_05_dados_reais", caminho)
    etapa = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(etapa)
    saida = tmp_path / "dados_reais.csv"
    etapa.main(arquivo_saida=saida)
    pd.testing.assert_frame_equal(pd.read_csv(saida), pd.read_csv(ARQUIVO_RESULTADO), rtol=1e-9)

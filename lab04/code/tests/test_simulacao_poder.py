import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from simulacao import COLUNAS_PODER, EFEITOS, arquivo_poder, simular_poder

ETAPA = Path(__file__).resolve().parents[1] / "etapas" / "04_poder.py"


def carregar_etapa():
    especificacao = importlib.util.spec_from_file_location("etapa_04", ETAPA)
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


def gerar_normal(situacao, efeito, n, rng):
    """Gerador controlado em que `efeito` é a correlação populacional."""
    x = rng.standard_normal(n)
    y = efeito * x + np.sqrt(1 - efeito**2) * rng.standard_normal(n)
    return {"loc": x, "defeitos": y}


def test_tabela_tem_colunas_e_uma_linha_por_efeito_e_teste():
    efeitos = (0.0, 0.2, 0.5)
    tabela = simular_poder("normal", efeitos=efeitos, repeticoes=100, gerar=gerar_normal)

    assert list(tabela.columns) == COLUNAS_PODER
    assert len(tabela) == len(efeitos) * 2
    assert list(tabela["efeito"]) == [efeito for efeito in efeitos for _ in range(2)]
    assert list(tabela["teste"]) == ["pearson", "spearman"] * len(efeitos)
    assert set(tabela["situacao"]) == {"normal"}
    assert set(tabela["n"]) == {30}
    assert set(tabela["alfa"]) == {0.05}
    assert set(tabela["repeticoes"]) == {100}


def test_lista_padrao_tem_pelo_menos_cinco_efeitos_e_comeca_em_zero():
    assert len(EFEITOS) >= 5
    assert EFEITOS[0] == 0.0


def test_mesma_semente_da_o_mesmo_poder():
    primeira = simular_poder("normal", efeitos=(0.0, 0.3), repeticoes=500, gerar=gerar_normal)
    segunda = simular_poder("normal", efeitos=(0.0, 0.3), repeticoes=500, gerar=gerar_normal)

    pd.testing.assert_frame_equal(primeira, segunda)


def test_poder_com_efeito_zero_fica_perto_de_alfa_e_cresce():
    tabela = simular_poder("normal", efeitos=EFEITOS, repeticoes=5_000, gerar=gerar_normal)
    por_teste = tabela.pivot(index="efeito", columns="teste", values="proporcao_rejeicao")

    for teste in ("pearson", "spearman"):
        assert por_teste.loc[0.0, teste] == pytest.approx(0.05, abs=0.015)
        assert np.all(np.diff(por_teste[teste]) > 0)
        assert por_teste.loc[0.5, teste] > 0.75


def test_usa_gerador_e_funcao_de_testes_injetados():
    geracoes = []
    chamadas_dos_testes = []

    def gerar_espiao(situacao, efeito, n, rng):
        geracoes.append((situacao, efeito, n))
        return {"loc": np.arange(n), "defeitos": np.arange(n)}

    def testes_espiao(loc, defeitos):
        chamadas_dos_testes.append((loc.shape, defeitos.shape))
        repeticoes = len(loc)
        return {
            "pearson": {"p_valor": np.zeros(repeticoes)},
            "spearman": {"p_valor": np.ones(repeticoes)},
        }

    tabela = simular_poder(
        "espia",
        efeitos=(0.0, 0.3),
        n=8,
        repeticoes=7,
        gerar=gerar_espiao,
        aplicar_testes_em_lote=testes_espiao,
    )

    assert len(geracoes) == 14
    assert set(geracoes) == {("espia", 0.0, 8), ("espia", 0.3, 8)}
    assert chamadas_dos_testes == [((7, 8), (7, 8)), ((7, 8), (7, 8))]
    assert list(tabela["proporcao_rejeicao"]) == [1.0, 0.0, 1.0, 0.0]


def test_etapa_salva_um_csv_por_situacao(tmp_path):
    carregar_etapa().main(
        gerar=gerar_normal,
        situacoes=("base", "normal", "outliers"),
        pasta=tmp_path,
        efeitos=(0.0, 0.5),
        repeticoes=100,
    )

    for situacao in ("base", "normal", "outliers"):
        tabela = pd.read_csv(arquivo_poder(situacao, tmp_path))
        assert list(tabela.columns) == COLUNAS_PODER
        assert set(tabela["situacao"]) == {situacao}
        assert set(tabela["efeito"]) == {0.0, 0.5}
        assert set(tabela["teste"]) == {"pearson", "spearman"}

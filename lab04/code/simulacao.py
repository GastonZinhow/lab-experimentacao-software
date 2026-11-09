"""Simulações de Monte Carlo: proporção de rejeições de H₀ de cada teste."""
from pathlib import Path

import numpy as np
import pandas as pd

from gerador import gerar
from testes import ALFA, TESTES, aplicar_testes_em_lote

PASTA_RESULTADOS = Path(__file__).resolve().parent / "resultados"
N = 30  # mesmo tamanho da amostra real do KC1
REPETICOES = 10_000
SEMENTE = 42
COLUNAS_ERRO_TIPO1 = ["situacao", "teste", "n", "alfa", "repeticoes", "proporcao_rejeicao"]


def gerar_conjuntos(situacao, efeito, n, repeticoes, rng, gerar=gerar):
    """Chama `gerar` uma vez por conjunto e empilha os resultados em matrizes (repeticoes, n)."""
    conjuntos = [gerar(situacao, efeito, n, rng) for _ in range(repeticoes)]
    loc = np.array([conjunto["loc"] for conjunto in conjuntos])
    defeitos = np.array([conjunto["defeitos"] for conjunto in conjuntos])
    return loc, defeitos


def proporcao_rejeicao(situacao, efeito, n, repeticoes, rng, alfa=ALFA, gerar=gerar,
                       aplicar_testes_em_lote=aplicar_testes_em_lote):
    """Proporção de conjuntos em que cada teste tem p-valor < `alfa`.

    Um p-valor indefinido (`nan`, quando uma variável é constante no conjunto)
    conta como não rejeição.
    """
    loc, defeitos = gerar_conjuntos(situacao, efeito, n, repeticoes, rng, gerar)
    resultados = aplicar_testes_em_lote(loc, defeitos)
    return {teste: float(np.mean(resultados[teste]["p_valor"] < alfa)) for teste in TESTES}


def simular_erro_tipo1(situacao, n=N, repeticoes=REPETICOES, alfa=ALFA, semente=SEMENTE, gerar=gerar,
                       aplicar_testes_em_lote=aplicar_testes_em_lote):
    """Gera `repeticoes` conjuntos com H₀ verdadeira (`efeito = 0`) e conta as rejeições de cada teste.

    Cada situação começa da mesma semente, então o resultado de uma não depende
    da ordem nem de quantas outras situações existem.
    """
    rng = np.random.default_rng(semente)
    proporcoes = proporcao_rejeicao(situacao, 0.0, n, repeticoes, rng, alfa, gerar, aplicar_testes_em_lote)
    return pd.DataFrame(
        [{"situacao": situacao, "teste": teste, "n": n, "alfa": alfa, "repeticoes": repeticoes,
          "proporcao_rejeicao": proporcoes[teste]} for teste in TESTES],
        columns=COLUNAS_ERRO_TIPO1,
    )


def margem_monte_carlo(proporcao=ALFA, repeticoes=REPETICOES):
    """Meia largura do intervalo de 95% de uma proporção estimada com `repeticoes` conjuntos."""
    return 1.96 * np.sqrt(proporcao * (1 - proporcao) / repeticoes)


def arquivo_erro_tipo1(situacao, pasta=PASTA_RESULTADOS):
    return Path(pasta) / f"erro_tipo1_{situacao}.csv"

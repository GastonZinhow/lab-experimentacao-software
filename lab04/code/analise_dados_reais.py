"""Pearson e Spearman aplicados à amostra real do KC1 (tabela da seção 6)."""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from dados_reais import ARQUIVO_AMOSTRA
from testes import ALFA, TESTES, aplicar_testes, estatistica_t, resumir

ARQUIVO_RESULTADO = Path(__file__).resolve().parent / "resultados" / "dados_reais.csv"
NIVEL_CONFIANCA = 0.95
COLUNAS = ["conjunto", "teste", "n", "coeficiente", "ic95_inferior", "ic95_superior",
           "estatistica_t", "p_valor", "magnitude", "rejeita_h0"]


def intervalo_confianca(coeficiente, n, teste, nivel=NIVEL_CONFIANCA):
    """Intervalo de confiança de r ou de ρ pela transformação z de Fisher.

    Para o Pearson, o erro-padrão de z é 1/√(n − 3). Para o Spearman, usa-se a
    correção de Bonett e Wright (2000), √((1 + ρ²/2) / (n − 3)), que deixa o
    intervalo um pouco mais largo.
    """
    if teste not in TESTES:
        raise ValueError(f"Teste desconhecido: {teste!r}")
    if n < 4:
        raise ValueError("São necessários pelo menos 4 módulos para o intervalo de confiança")
    variancia = 1.0 if teste == "pearson" else 1 + coeficiente**2 / 2
    erro_padrao = np.sqrt(variancia / (n - 3))
    z = np.arctanh(coeficiente)
    quantil = stats.norm.ppf(0.5 + nivel / 2)
    return float(np.tanh(z - quantil * erro_padrao)), float(np.tanh(z + quantil * erro_padrao))


def conjuntos_analisados(amostra):
    """A amostra completa e, como sensibilidade, a amostra sem a maior classe.

    A maior classe (2.883 LOC e 101 defeitos) é a que mais pesa no r, por isso
    o resultado sem ela mostra o quanto a conclusão depende de um único módulo.
    """
    maior = amostra["loc"].idxmax()
    return {
        "amostra": amostra,
        "sem_maior_classe": amostra.drop(index=maior).reset_index(drop=True),
    }


def analisar(amostra, alfa=ALFA):
    """Uma linha por conjunto e por teste, com coeficiente, intervalo, t, p-valor e decisão."""
    linhas = []
    for conjunto, dados in conjuntos_analisados(amostra).items():
        n = len(dados)
        resultados = resumir(aplicar_testes({"loc": dados["loc"], "defeitos": dados["defeitos"]}), alfa)
        for teste in TESTES:
            valores = resultados[teste]
            inferior, superior = intervalo_confianca(valores["coeficiente"], n, teste)
            linhas.append({
                "conjunto": conjunto,
                "teste": teste,
                "n": n,
                "coeficiente": valores["coeficiente"],
                "ic95_inferior": inferior,
                "ic95_superior": superior,
                "estatistica_t": float(estatistica_t(valores["coeficiente"], n)),
                "p_valor": valores["p_valor"],
                "magnitude": valores["magnitude"],
                "rejeita_h0": bool(valores["rejeita_h0"]),
            })
    return pd.DataFrame(linhas, columns=COLUNAS)


def carregar_amostra(arquivo=ARQUIVO_AMOSTRA):
    return pd.read_csv(arquivo)

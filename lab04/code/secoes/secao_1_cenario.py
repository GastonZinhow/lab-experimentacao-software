"""Seção 1 do dashboard: cenário, hipóteses, origem dos dados e expectativa."""

import pandas as pd
import streamlit as st

from dados_reais import ARQUIVO_AMOSTRA, ler_arff

URL_DATASET = "http://promise.site.uottawa.ca/SERepository/datasets/kc1-class-level-numericdefect.arff"

PERGUNTA = "Módulos maiores têm mais defeitos registrados?"
INTRODUCAO = (
    "Comparamos as correlações de Pearson e de Spearman para investigar a associação entre o tamanho de uma "
    "classe, medido em linhas de código (LOC), e seu número de defeitos registrados. O Pearson mede a "
    "associação **linear** nos valores; o Spearman mede a associação **monotônica** nos postos."
)
H0 = "**H₀ — sem associação**\n\nO tamanho do módulo e o número de defeitos têm correlação igual a zero."
H1 = "**H₁ — há associação**\n\nO tamanho do módulo e o número de defeitos têm correlação diferente de zero."
BICAUDAL = (
    "O teste é **bicaudal**, pois tanto uma associação positiva quanto uma "
    "negativa seria relevante. Adotamos nível de significância **α = 0,05**."
)
EXPECTATIVA = (
    "Antes de simular, esperávamos que o **Spearman** se saísse melhor. Como LOC e defeitos são muito "
    "assimétricos, o p-valor do Pearson, que supõe dados aproximadamente normais, deveria se afastar mais de 5%, "
    "e poucos módulos extremos deveriam tornar o r instável e reduzir seu poder. O que mudaria nossa opinião seria "
    "o Pearson manter o erro tipo I perto de 5% e ter poder igual ou maior. A expectativa foi registrada em "
    "`lab04/docs/cenario.md` antes das simulações e é comparada com os resultados na seção 7."
)


def texto_origem(n_amostra, n_populacao):
    return (
        "Os dados reais vêm do **KC1, sistema da NASA (NASA MDP), disponibilizado pelo repositório PROMISE** no "
        f"nível de classe. Sorteamos uma amostra aleatória simples de **{n_amostra} classes entre {n_populacao}**, "
        "com `numpy.random.default_rng(42)`. Para cada classe, usamos o tamanho em **LOC** (coluna `sumLOC_TOTAL`, "
        "a soma das linhas de código dos métodos) e o **número de defeitos registrados** (coluna `NUMDEFECTS`). "
        f"[Acessar o dataset original]({URL_DATASET})."
    )


def texto_origem_atual():
    return texto_origem(len(pd.read_csv(ARQUIVO_AMOSTRA)), len(ler_arff()))


def render():
    st.header("1. Cenário")
    st.subheader(PERGUNTA)
    st.write(INTRODUCAO)

    h0, h1 = st.columns(2)
    with h0:
        st.info(H0)
    with h1:
        st.info(H1)

    st.write(BICAUDAL)
    st.markdown(texto_origem_atual())

    st.subheader("O que esperávamos antes de simular")
    st.markdown(EXPECTATIVA)

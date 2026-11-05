"""Seção 1 do dashboard: cenário, hipóteses e origem dos dados."""

import streamlit as st


def render():
    st.header("1. Cenário")
    st.subheader("Módulos maiores têm mais defeitos registrados?")
    st.write(
        "Comparamos as correlações de Pearson e de Spearman para investigar "
        "a associação entre o tamanho de uma classe, medido em linhas de código "
        "(LOC), e seu número de defeitos registrados."
    )

    h0, h1 = st.columns(2)
    with h0:
        st.info(
            "**H₀ — sem associação**\n\n"
            "O tamanho do módulo e o número de defeitos têm correlação igual a zero."
        )
    with h1:
        st.info(
            "**H₁ — há associação**\n\n"
            "O tamanho do módulo e o número de defeitos têm correlação diferente de zero."
        )

    st.write(
        "O teste é **bicaudal**, pois tanto uma associação positiva quanto uma "
        "negativa seria relevante. Adotamos nível de significância **α = 0,05**."
    )
    st.markdown(
        "Os dados reais vêm do **KC1, da NASA MDP, disponibilizado pelo PROMISE**. "
        "Foi coletada uma amostra aleatória simples de **30 classes entre 145**, "
        "usando `numpy.random.default_rng(42)`; para cada classe, foram mantidos "
        "o total de LOC e o número de defeitos. "
        "[Acessar o dataset original](http://promise.site.uottawa.ca/SERepository/"
        "datasets/kc1-class-level-numericdefect.arff)."
    )

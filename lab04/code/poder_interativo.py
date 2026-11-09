"""Gráfico interativo (bônus): poder dos dois testes conforme o tamanho da amostra e do efeito."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from gerador import SITUACOES, carregar_parametros, gerar
from simulacao import margem_monte_carlo, proporcao_rejeicao
from testes import ALFA, TESTES

CORES = {"pearson": "#1f77b4", "spearman": "#ff7f0e"}
NOMES = {"pearson": "Pearson", "spearman": "Spearman"}
REPETICOES = 1_000
SEMENTE = 42


def _br(valor, casas=2):
    return f"{valor:.{casas}f}".replace(".", ",")


@st.cache_data(show_spinner="Simulando 1.000 conjuntos...", max_entries=200)
def estimar_poder(situacao, efeito, n, repeticoes=REPETICOES, semente=SEMENTE, _gerar=gerar):
    """Proporção de rejeições de H₀ de cada teste em `repeticoes` conjuntos com esse `efeito` e esse `n`."""
    return proporcao_rejeicao(situacao, efeito, n, repeticoes, np.random.default_rng(semente), gerar=_gerar)


def figura_poder(poder, n, efeito, repeticoes=REPETICOES, alfa=ALFA):
    """Duas barras, uma por teste, com o intervalo de 95% da simulação e a linha em α."""
    figura = go.Figure()
    for teste in TESTES:
        valor = poder[teste]
        figura.add_trace(go.Bar(
            x=[NOMES[teste]], y=[100 * valor], name=NOMES[teste], marker_color=CORES[teste],
            error_y={"type": "data", "array": [100 * margem_monte_carlo(valor, repeticoes)],
                     "color": "rgba(60,60,60,0.8)", "thickness": 1.5},
            text=[f"{_br(100 * valor, 1)}%"], textposition="inside", insidetextanchor="middle",
            textfont={"color": "white"},
            hovertemplate="%{y:.1f}% de rejeições<extra>" + NOMES[teste] + "</extra>",
        ))
    figura.add_hline(
        y=100 * alfa, line={"color": "rgba(60,60,60,0.9)", "dash": "dash", "width": 2},
        annotation_text=f"α = {_br(100 * alfa, 0)}%", annotation_position="top right",
    )
    medida = "erro tipo I" if efeito == 0 else "poder"
    figura.update_layout(
        title=f"Proporção de rejeições de H₀ ({medida}) com n = {n} módulos e efeito = {_br(efeito)}",
        bargap=0.45, barcornerradius=4, showlegend=True,
        legend={"orientation": "h", "y": -0.2, "x": 0}, margin={"t": 70, "b": 80},
    )
    figura.update_xaxes(title_text="Teste")
    figura.update_yaxes(
        title_text=f"Rejeições de H₀ (% de {REPETICOES:,} conjuntos)".replace(",", "."),
        range=[0, 109], gridcolor="rgba(128,128,128,0.2)",
    )
    return figura


def texto_poder(poder, n, efeito):
    p, s = 100 * poder["pearson"], 100 * poder["spearman"]
    if efeito == 0:
        return (
            f"Com efeito = 0 não há associação, então toda rejeição é um erro tipo I: com n = {n}, o Pearson rejeitou "
            f"H₀ em {_br(p, 1)}% dos conjuntos e o Spearman em {_br(s, 1)}%, e o esperado é ficar perto de 5%. "
            "Aumente o efeito para ver o poder, ou seja, com que frequência cada teste detecta a associação que existe."
        )
    if abs(p - s) <= 3:
        comparacao = "os dois testes detectaram a associação com frequência parecida"
    else:
        melhor = "Spearman" if s > p else "Pearson"
        comparacao = f"o {melhor} detectou a associação com mais frequência"
    return (
        f"Com n = {n} módulos e efeito = {_br(efeito)}, o Pearson rejeitou H₀ em {_br(p, 1)}% dos conjuntos e o "
        f"Spearman em {_br(s, 1)}%: {comparacao}. "
        "Cada barra é estimada com 1.000 conjuntos simulados e tem margem de até cerca de 3 pontos percentuais "
        "(traço preto), então diferenças menores que isso podem ser só variação da simulação. "
        "Aumentar n ou o efeito sobe o poder dos dois testes, e 80% costuma ser o mínimo desejado."
    )


def tabela_poder(poder, n, efeito):
    return pd.DataFrame({
        "Teste": [NOMES[t] for t in TESTES],
        "n": n,
        "Efeito": efeito,
        "Rejeições de H₀ (%)": [round(100 * poder[t], 1) for t in TESTES],
    })


def render(gerar=gerar):
    st.subheader("Experimente: tamanho da amostra × poder")
    efeito_calibrado = carregar_parametros()["associacao"]["efeito_calibrado"]
    st.caption(
        "Escolha o número de módulos e a força da associação. O efeito é a correlação usada pelo gerador para ligar "
        f"LOC e defeitos (0 = sem associação; {_br(efeito_calibrado)} reproduz o ρ = 0,51 da amostra real do KC1)."
    )
    colunas = st.columns(3 if len(SITUACOES) > 1 else 2)
    with colunas[0]:
        n = st.slider("Tamanho da amostra (módulos)", min_value=10, max_value=200, value=30, step=10)
    with colunas[1]:
        efeito = st.slider("Efeito (força da associação)", min_value=0.0, max_value=0.9, value=0.3, step=0.05)
    situacao = "base"
    if len(SITUACOES) > 1:
        with colunas[2]:
            situacao = st.selectbox("Situação", SITUACOES)

    poder = estimar_poder(situacao, round(efeito, 2), n, _gerar=gerar)
    st.plotly_chart(figura_poder(poder, n, efeito), width="stretch")
    st.write(texto_poder(poder, n, efeito))
    with st.expander("Ver os valores do gráfico em tabela"):
        st.dataframe(tabela_poder(poder, n, efeito), hide_index=True)

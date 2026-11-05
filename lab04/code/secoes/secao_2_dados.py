"""Seção 2 do dashboard: os dados reais ao lado dos simulados (gráfico G1)."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from dados_reais import ARQUIVO_AMOSTRA
from gerador import carregar_parametros, gerar

COR_REAL = "#6250d6"
COR_SIMULADO = "#1baf7a"
N_SIMULADO = 10_000

FAIXAS_LOC = ([1, 10, 50, 100, 200, 500, 1000, np.inf],
              ["1–9", "10–49", "50–99", "100–199", "200–499", "500–999", "1.000+"])
FAIXAS_DEFEITOS = ([0, 1, 6, 11, 21, 51, np.inf],
                   ["0", "1–5", "6–10", "11–20", "21–50", "51+"])


def percentual_por_faixa(valores, faixas):
    limites, rotulos = faixas
    contagem, _ = np.histogram(valores, bins=limites)
    return pd.Series(100 * contagem / len(valores), index=rotulos)


def simular_para_g1():
    """Gera um conjunto grande, com o efeito calibrado, para mostrar a forma da distribuição."""
    efeito = carregar_parametros()["associacao"]["efeito_calibrado"]
    return gerar("base", efeito, N_SIMULADO, np.random.default_rng(42))


def figura_g1(real, simulado):
    """Monta o G1: histogramas de LOC e de defeitos, com dados reais ao lado dos simulados."""
    figura = make_subplots(
        rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.06,
        subplot_titles=("Tamanho do módulo", "Defeitos por módulo"),
    )
    paineis = [("loc", FAIXAS_LOC, "LOC"), ("defeitos", FAIXAS_DEFEITOS, "defeitos")]
    series = [("Real (n = {n})", real, COR_REAL), ("Simulado (n = {n})", simulado, COR_SIMULADO)]
    for coluna, (variavel, faixas, unidade) in enumerate(paineis, start=1):
        for nome, dados, cor in series:
            percentuais = percentual_por_faixa(dados[variavel], faixas)
            figura.add_trace(
                go.Bar(
                    x=percentuais.index, y=percentuais.values,
                    name=nome.format(n=f"{len(dados[variavel]):,}".replace(",", ".")),
                    marker_color=cor, legendgroup=nome, showlegend=coluna == 1,
                    hovertemplate=f"%{{x}} {unidade}<br>%{{y:.1f}}% dos módulos<extra>%{{fullData.name}}</extra>",
                ),
                row=1, col=coluna,
            )
    figura.update_layout(
        title="G1: dados reais e simulados de LOC e de defeitos",
        barmode="group", bargap=0.25, bargroupgap=0.05, barcornerradius=4,
        legend={"orientation": "h", "y": -0.25, "x": 0},
        margin={"t": 90, "b": 90},
    )
    figura.update_xaxes(title_text="Tamanho (LOC, faixas crescentes)", row=1, col=1, type="category")
    figura.update_xaxes(title_text="Defeitos registrados (quantidade, faixas)", row=1, col=2, type="category")
    figura.update_yaxes(title_text="Módulos (%)", row=1, col=1)
    figura.update_yaxes(gridcolor="rgba(128,128,128,0.2)")
    return figura


def tabela_g1(real, simulado):
    """Devolve os mesmos valores do gráfico, em formato de tabela."""
    partes = []
    for variavel, faixas in (("loc", FAIXAS_LOC), ("defeitos", FAIXAS_DEFEITOS)):
        partes.append(pd.DataFrame({
            "Variável": variavel,
            "Faixa": faixas[1],
            "Real (%)": percentual_por_faixa(real[variavel], faixas).round(1).values,
            "Simulado (%)": percentual_por_faixa(simulado[variavel], faixas).round(1).values,
        }))
    return pd.concat(partes, ignore_index=True)


def texto_g1(real, simulado):
    zeros_real = 100 * np.mean(real["defeitos"] == 0)
    zeros_simulado = 100 * np.mean(simulado["defeitos"] == 0)
    faixa_real = percentual_por_faixa(real["loc"], FAIXAS_LOC)["200–499"]
    faixa_simulada = percentual_por_faixa(simulado["loc"], FAIXAS_LOC)["200–499"]
    return (
        f"Na amostra de {len(real)} classes do sistema KC1 da NASA, a maioria dos módulos é pequena, mas poucos são "
        f"muito maiores: a mediana é de {np.median(real['loc']):.0f} LOC e o máximo, de "
        f"{real['loc'].max():.0f} LOC. Além disso, {zeros_real:.0f}% dos módulos não têm defeito registrado, "
        f"enquanto um deles chega a {real['defeitos'].max():.0f}. "
        "Por isso, simulamos o LOC com uma lognormal e os defeitos com uma binomial negativa, "
        "com parâmetros estimados nessa amostra. "
        f"A simulação reproduz a forma geral dos dados, inclusive a proporção de módulos sem defeito "
        f"({zeros_simulado:.0f}% contra {zeros_real:.0f}%), mas difere nas faixas intermediárias, como 200–499 LOC "
        f"({faixa_simulada:.0f}% contra {faixa_real:.0f}%), em parte porque 30 módulos são poucos para estimar cada faixa."
    )


def render():
    st.header("2. Os dados")
    real = pd.read_csv(ARQUIVO_AMOSTRA)
    simulado = simular_para_g1()
    st.plotly_chart(figura_g1(real, simulado), width="stretch")
    st.write(texto_g1(real, simulado))
    with st.expander("Ver os valores do gráfico em tabela"):
        st.dataframe(tabela_g1(real, simulado), hide_index=True)

"""Seção 5 do dashboard: curvas de poder de Pearson e Spearman (gráfico G4)."""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from simulacao import COLUNAS_PODER, PASTA_RESULTADOS

CORES = {"pearson": "#1f77b4", "spearman": "#ff7f0e"}
NOMES = {"pearson": "Pearson", "spearman": "Spearman"}
VANTAGEM_RELEVANTE = 0.03


def _br(valor, casas=2):
    return f"{valor:.{casas}f}".replace(".", ",")


def _lista_pt(valores):
    textos = [_br(valor) for valor in valores]
    if len(textos) < 2:
        return "".join(textos)
    return ", ".join(textos[:-1]) + " e " + textos[-1]


def ler_resultados(pasta=PASTA_RESULTADOS):
    """Junta todos os arquivos ``poder_*.csv`` encontrados na pasta."""
    arquivos = sorted(Path(pasta).glob("poder_*.csv"))
    if not arquivos:
        return pd.DataFrame(columns=COLUNAS_PODER)
    tabela = pd.concat([pd.read_csv(arquivo) for arquivo in arquivos], ignore_index=True)
    faltantes = set(COLUNAS_PODER) - set(tabela.columns)
    if faltantes:
        raise ValueError("Colunas ausentes nos resultados de poder: " + ", ".join(sorted(faltantes)))
    ordem_situacoes = list(dict.fromkeys(tabela["situacao"]))
    tabela["situacao"] = pd.Categorical(tabela["situacao"], categories=ordem_situacoes, ordered=True)
    tabela = tabela.sort_values(["situacao", "efeito", "teste"]).reset_index(drop=True)
    tabela["situacao"] = tabela["situacao"].astype(str)
    return tabela[COLUNAS_PODER]


def figura_g4(tabela):
    """Monta o G4: um painel por situação, com as duas curvas de poder."""
    situacoes = list(dict.fromkeys(tabela["situacao"]))
    figura = make_subplots(
        rows=1,
        cols=len(situacoes),
        shared_yaxes=True,
        horizontal_spacing=0.06,
        subplot_titles=[f"Situação: {situacao}" for situacao in situacoes],
    )
    for coluna, situacao in enumerate(situacoes, start=1):
        linhas_situacao = tabela[tabela["situacao"] == situacao]
        for teste in ("pearson", "spearman"):
            linhas = linhas_situacao[linhas_situacao["teste"] == teste].sort_values("efeito")
            figura.add_trace(
                go.Scatter(
                    x=linhas["efeito"],
                    y=100 * linhas["proporcao_rejeicao"],
                    mode="lines+markers",
                    name=NOMES[teste],
                    legendgroup=teste,
                    showlegend=coluna == 1,
                    line={"color": CORES[teste], "width": 3},
                    marker={"color": CORES[teste], "size": 8},
                    customdata=np.full((len(linhas), 1), situacao),
                    hovertemplate=(
                        "Situação: %{customdata[0]}<br>Efeito: %{x:.2f}<br>"
                        "Poder: %{y:.2f}%<extra>" + NOMES[teste] + "</extra>"
                    ),
                ),
                row=1,
                col=coluna,
            )
        figura.add_hline(
            y=5,
            line={"color": "rgba(90,90,90,0.75)", "dash": "dot", "width": 1.5},
            row=1,
            col=coluna,
        )
        figura.add_hline(
            y=80,
            line={"color": "rgba(60,120,60,0.75)", "dash": "dash", "width": 1.5},
            row=1,
            col=coluna,
        )
        figura.update_xaxes(title_text="Tamanho do efeito (adimensional)", row=1, col=coluna)

    figura.add_annotation(
        xref="paper", yref="y", x=1, y=5, text="α = 5%", showarrow=False, xanchor="right", yanchor="bottom"
    )
    figura.add_annotation(
        xref="paper", yref="y", x=1, y=80, text="Poder = 80%", showarrow=False, xanchor="right", yanchor="bottom"
    )
    figura.update_layout(
        title=(
            "G4: poder dos testes conforme cresce o tamanho do efeito "
            f"(n = {int(tabela['n'].iloc[0])} módulos)"
        ),
        legend={"orientation": "h", "y": -0.28, "x": 0},
        margin={"t": 95, "b": 120},
        hovermode="closest",
    )
    figura.update_yaxes(
        title_text="Poder (% de rejeições de H₀)",
        range=[0, 105],
        gridcolor="rgba(128,128,128,0.2)",
        row=1,
        col=1,
    )
    return figura


def _comparacao_situacao(linhas):
    por_efeito = linhas[linhas["efeito"] > 0].pivot(
        index="efeito", columns="teste", values="proporcao_rejeicao"
    ).dropna(subset=["pearson", "spearman"])
    por_efeito["diferenca"] = por_efeito["pearson"] - por_efeito["spearman"]
    return por_efeito


def _cruzamentos(por_efeito):
    cruzamentos = []
    efeitos = list(por_efeito.index)
    diferencas = list(por_efeito["diferenca"])
    for anterior, atual, diferenca_anterior, diferenca_atual in zip(
        efeitos, efeitos[1:], diferencas, diferencas[1:]
    ):
        if diferenca_anterior * diferenca_atual < 0:
            cruzamentos.append(f"entre {_br(anterior)} e {_br(atual)}")
    return cruzamentos


def texto_g4(tabela):
    """Compara os testes dinamicamente em quatro frases, sem conclusões fixas."""
    comparacoes = {
        situacao: _comparacao_situacao(linhas)
        for situacao, linhas in tabela.groupby("situacao", sort=False)
    }

    medias = []
    vantagens = []
    inversoes = []
    for situacao, por_efeito in comparacoes.items():
        media_pearson = por_efeito["pearson"].mean()
        media_spearman = por_efeito["spearman"].mean()
        vencedor = "Pearson" if media_pearson > media_spearman else "Spearman"
        medias.append(
            f"em {situacao}, {vencedor} teve o maior poder médio "
            f"({_br(100 * max(media_pearson, media_spearman), 1)}% contra "
            f"{_br(100 * min(media_pearson, media_spearman), 1)}%)"
        )

        relevantes_pearson = por_efeito.index[por_efeito["diferenca"] >= VANTAGEM_RELEVANTE].tolist()
        relevantes_spearman = por_efeito.index[por_efeito["diferenca"] <= -VANTAGEM_RELEVANTE].tolist()
        partes = []
        if relevantes_pearson:
            partes.append(f"Pearson em {_lista_pt(relevantes_pearson)}")
        if relevantes_spearman:
            partes.append(f"Spearman em {_lista_pt(relevantes_spearman)}")
        vantagens.append(
            f"em {situacao}, " + (" e ".join(partes) if partes else "nenhum teste")
        )

        cruzamentos = _cruzamentos(por_efeito)
        inversoes.append(
            f"em {situacao}, " + (" e ".join(cruzamentos) if cruzamentos else "não houve inversão")
        )

    resumo_medias = "; ".join(medias)
    resumo_medias = resumo_medias[0].upper() + resumo_medias[1:]
    return (
        "Nos efeitos positivos, cada curva mostra com que frequência o teste detecta a associação que existe; "
        "uma diferença de pelo menos 3 pontos percentuais é tratada como vantagem relevante. "
        + resumo_medias
        + ". As vantagens relevantes foram: "
        + "; ".join(vantagens)
        + ". A vantagem mudou de lado: "
        + "; ".join(inversoes)
        + "."
    )


def tabela_g4(tabela):
    return pd.DataFrame({
        "Situação": tabela["situacao"],
        "Teste": tabela["teste"].map(NOMES),
        "Tamanho do efeito": tabela["efeito"],
        "Poder (%)": (100 * tabela["proporcao_rejeicao"]).round(2),
        "n": tabela["n"],
        "Repetições": tabela["repeticoes"],
    })


def render(pasta=PASTA_RESULTADOS):
    st.header("5. Poder")
    tabela = ler_resultados(pasta)
    if tabela.empty:
        st.info("Ainda não há resultados de poder. Rode `python lab04/code/run_all.py` para gerá-los.")
        return
    st.plotly_chart(figura_g4(tabela), width="stretch")
    st.write(texto_g4(tabela))
    with st.expander("Ver os valores do gráfico em tabela"):
        st.dataframe(tabela_g4(tabela), hide_index=True)

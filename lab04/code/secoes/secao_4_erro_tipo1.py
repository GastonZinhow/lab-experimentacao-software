"""Seção 4 do dashboard: erro tipo I de cada teste em cada situação (gráfico G3)."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from gerador import SITUACOES
from simulacao import PASTA_RESULTADOS, margem_monte_carlo

CORES = {"pearson": "#1f77b4", "spearman": "#ff7f0e"}
NOMES = {"pearson": "Pearson", "spearman": "Spearman"}
COR_FAIXA = "rgba(128,128,128,0.18)"


def _br(valor, casas=2):
    return f"{valor:.{casas}f}".replace(".", ",")


def ler_resultados(pasta=PASTA_RESULTADOS):
    """Junta todos os `erro_tipo1_*.csv`, com as situações na ordem de `SITUACOES`."""
    arquivos = sorted(pasta.glob("erro_tipo1_*.csv"))
    if not arquivos:
        return pd.DataFrame()
    tabela = pd.concat([pd.read_csv(arquivo) for arquivo in arquivos], ignore_index=True)
    ordem = list(SITUACOES) + sorted(set(tabela["situacao"]) - set(SITUACOES))
    tabela["situacao"] = pd.Categorical(tabela["situacao"], categories=ordem, ordered=True)
    tabela = tabela.sort_values(["situacao", "teste"]).reset_index(drop=True)
    tabela["situacao"] = tabela["situacao"].astype(str)
    return tabela


def classificar(tabela):
    """Acrescenta a margem de Monte Carlo e diz se cada teste ficou perto de α, liberal ou conservador.

    O teste só é considerado desviado quando α fica fora do intervalo de 95% da
    proporção estimada, ou seja, quando a diferença não se explica pela
    variação da própria simulação.
    """
    tabela = tabela.copy()
    tabela["margem"] = margem_monte_carlo(tabela["alfa"], tabela["repeticoes"])
    diferenca = tabela["proporcao_rejeicao"] - tabela["alfa"]
    tabela["classificacao"] = np.select(
        [diferenca > tabela["margem"], diferenca < -tabela["margem"]],
        ["liberal", "conservador"],
        default="perto de α",
    )
    return tabela


def figura_g3(tabela):
    """Monta o G3: barras do erro tipo I por situação, com a linha de α e a faixa de variação esperada."""
    alfa = float(tabela["alfa"].iloc[0])
    margem = float(margem_monte_carlo(alfa, int(tabela["repeticoes"].min())))
    situacoes = list(dict.fromkeys(tabela["situacao"]))
    figura = go.Figure()
    figura.add_hrect(y0=100 * (alfa - margem), y1=100 * (alfa + margem), fillcolor=COR_FAIXA, line_width=0, layer="below")
    figura.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers", marker={"symbol": "square", "size": 14, "color": COR_FAIXA},
        name=f"Variação esperada da simulação ({_br(100 * alfa)}% ± {_br(100 * margem)} ponto percentual)",
    ))
    for teste in ("pearson", "spearman"):
        linhas = tabela[tabela["teste"] == teste].set_index("situacao").reindex(situacoes)
        figura.add_trace(go.Bar(
            x=situacoes, y=100 * linhas["proporcao_rejeicao"], name=NOMES[teste], marker_color=CORES[teste],
            error_y={"type": "data", "array": 100 * linhas["margem"], "color": "rgba(60,60,60,0.8)", "thickness": 1.5},
            text=[f"{_br(100 * p)}%" for p in linhas["proporcao_rejeicao"]], textposition="inside",
            insidetextanchor="middle", textfont={"color": "white"},
            hovertemplate="%{x}<br>%{y:.2f}% de rejeições<extra>" + NOMES[teste] + "</extra>",
        ))
    figura.add_hline(
        y=100 * alfa, line={"color": "rgba(60,60,60,0.9)", "dash": "dash", "width": 2},
        annotation_text=f"α = {_br(100 * alfa, 0)}%", annotation_position="top left",
    )
    maximo = 100 * float((tabela["proporcao_rejeicao"] + tabela["margem"]).max())
    figura.update_layout(
        title=f"G3: erro tipo I de cada teste por situação (H₀ verdadeira, n = {int(tabela['n'].iloc[0])} módulos)",
        barmode="group", bargap=0.3, bargroupgap=0.08, barcornerradius=4,
        legend={"orientation": "h", "y": -0.2, "x": 0},
        margin={"t": 80, "b": 100},
    )
    figura.update_xaxes(title_text="Situação simulada", type="category")
    figura.update_yaxes(
        title_text=f"Erro tipo I (% de rejeições em {int(tabela['repeticoes'].min()):,} conjuntos)".replace(",", "."),
        range=[0, max(10, maximo * 1.2)], gridcolor="rgba(128,128,128,0.2)",
    )
    return figura


def tabela_g3(tabela):
    return pd.DataFrame({
        "Situação": tabela["situacao"],
        "Teste": tabela["teste"].map(NOMES),
        "Erro tipo I (%)": (100 * tabela["proporcao_rejeicao"]).round(2),
        "Intervalo de 95% (%)": [
            f"{_br(100 * (p - m))} a {_br(100 * (p + m))}" for p, m in zip(tabela["proporcao_rejeicao"], tabela["margem"])
        ],
        "Classificação": tabela["classificacao"],
        "n": tabela["n"],
        "Repetições": tabela["repeticoes"],
    })


def _resultado_da_situacao(linhas):
    partes = [f"o {NOMES[l.teste]} ficou em {_br(100 * l.proporcao_rejeicao)}% ({l.classificacao})"
              for l in linhas.itertuples()]
    return f"na situação {linhas['situacao'].iloc[0]}, " + " e ".join(partes)


def _spearman_mais_perto(tabela, situacoes):
    """Diz se, em todas as `situacoes`, o Spearman ficou mais perto de α do que o Pearson."""
    desvio = (tabela["proporcao_rejeicao"] - tabela["alfa"]).abs()
    por_teste = tabela.assign(desvio=desvio).pivot(index="situacao", columns="teste", values="desvio")
    por_teste = por_teste.loc[list(situacoes)]
    return bool((por_teste["spearman"] < por_teste["pearson"]).all())


def texto_g3(tabela):
    alfa = float(tabela["alfa"].iloc[0])
    margem = float(margem_monte_carlo(alfa, int(tabela["repeticoes"].min())))
    resultados = "; ".join(_resultado_da_situacao(linhas) for _, linhas in tabela.groupby("situacao", sort=False))
    frases = [
        "O G3 mostra, em conjuntos simulados sem nenhuma associação entre LOC e defeitos, a proporção de vezes em "
        f"que cada teste rejeitou H₀; um teste válido fica dentro da faixa cinza ({_br(100 * alfa)}% ± "
        f"{_br(100 * margem)} ponto percentual), que é a variação esperada da própria simulação",
        resultados[0].upper() + resultados[1:],
    ]

    desviados = tabela[tabela["classificacao"] != "perto de α"]
    if desviados.empty:
        frases.append("Nenhum teste se desviou de α além do que a simulação explica")
    else:
        pior = desviados.loc[(desviados["proporcao_rejeicao"] - desviados["alfa"]).abs().idxmax()]
        sentido = ("encontra associação que não existe com mais frequência que α"
                   if pior["classificacao"] == "liberal" else "encontra associação que não existe com menos frequência que α")
        frases.append(
            f"O maior desvio foi o do {NOMES[pior['teste']]} na situação {pior['situacao']}, que ficou "
            f"{pior['classificacao']}: {sentido}"
        )
        pearson_liberal = desviados[(desviados["teste"] == "pearson") & (desviados["classificacao"] == "liberal")]
        if not pearson_liberal.empty:
            frase = ("Isso acontece porque o p-valor do Pearson supõe dados aproximadamente normais, e com LOC e "
                     "defeitos muito assimétricos um módulo extremo basta para produzir um r alto por acaso")
            if _spearman_mais_perto(tabela, pearson_liberal["situacao"]):
                frase += "; o Spearman, que usa postos, sofre menos com isso e fica mais perto de α"
            frases.append(frase)
    return ". ".join(frases) + "."


def render():
    st.header("4. Erro tipo I")
    tabela = ler_resultados()
    if tabela.empty:
        st.info("Ainda não há resultados de erro tipo I. Rode `python lab04/code/run_all.py` para gerá-los.")
        return
    tabela = classificar(tabela)
    st.plotly_chart(figura_g3(tabela), width="stretch")
    st.write(texto_g3(tabela))
    with st.expander("Ver os valores do gráfico em tabela"):
        st.dataframe(tabela_g3(tabela), hide_index=True)

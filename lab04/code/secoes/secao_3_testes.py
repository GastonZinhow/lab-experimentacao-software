"""Seção 3 do dashboard: como os testes decidem (gráfico G2)."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots
from scipy import stats

from exemplo import N, SITUACAO, rodar_exemplo
from gerador import gerar
from testes import ALFA, classificar_magnitude, estatistica_t

COR_PEARSON = "#1f77b4"
COR_SPEARMAN = "#ff7f0e"
COR_REJEICAO = "rgba(128,128,128,0.12)"
REPETICOES_H0 = 10_000
PONTOS_CURVA = 801


def rgba(cor_hex, opacidade):
    r, g, b = (int(cor_hex[i:i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r},{g},{b},{opacidade})"


@st.cache_data(show_spinner="Simulando a distribuição de ρ sob H₀...")
def simular_rho_h0(n=N, repeticoes=REPETICOES_H0, semente=42, _gerar=gerar):
    """Distribuição de ρ com H₀ verdadeira, obtida gerando conjuntos com `efeito = 0`.

    Por simulação, e não por fórmula, porque os muitos empates em zero defeito
    mudam a distribuição de ρ em relação à de dados sem empates.
    """
    # Os módulos gerados são independentes entre si, então uma única chamada com
    # n × repeticoes módulos, dividida em linhas de n, equivale a `repeticoes` conjuntos.
    dados = _gerar(SITUACAO, 0.0, n * repeticoes, np.random.default_rng(semente))
    postos_loc = stats.rankdata(np.asarray(dados["loc"]).reshape(repeticoes, n), axis=1)
    postos_def = stats.rankdata(np.asarray(dados["defeitos"]).reshape(repeticoes, n), axis=1)
    postos_loc -= postos_loc.mean(axis=1, keepdims=True)
    postos_def -= postos_def.mean(axis=1, keepdims=True)
    return (postos_loc * postos_def).sum(axis=1) / np.sqrt(
        (postos_loc**2).sum(axis=1) * (postos_def**2).sum(axis=1)
    )


def resumo_pearson(resultado, n, alfa=ALFA):
    gl = n - 2
    t_obs = float(estatistica_t(resultado["coeficiente"], n))
    return {
        "observado": t_obs,
        "critico": float(stats.t.ppf(1 - alfa / 2, gl)),
        "p_valor": resultado["p_valor"],
        "p_valor_area": float(2 * stats.t.sf(abs(t_obs), gl)),
    }


def resumo_spearman(resultado, rhos_h0, alfa=ALFA):
    rho_obs = resultado["coeficiente"]
    return {
        "observado": rho_obs,
        "critico_inf": float(np.quantile(rhos_h0, alfa / 2)),
        "critico": float(np.quantile(rhos_h0, 1 - alfa / 2)),
        "p_valor": resultado["p_valor"],
        "p_valor_area": float(np.mean(np.abs(rhos_h0) >= abs(rho_obs))),
    }


def _area(figura, x, y, mascara, nome, grupo, mostrar, coluna, **estilo):
    """Preenche a área sob a curva onde `mascara` é verdadeira, um trecho contíguo por vez."""
    trechos = np.split(np.arange(len(x)), np.where(np.diff(mascara.astype(int)) != 0)[0] + 1)
    for trecho in (t for t in trechos if mascara[t[0]]):
        figura.add_trace(
            go.Scatter(
                x=x[trecho], y=y[trecho], fill="tozeroy", mode="none", name=nome,
                legendgroup=grupo, showlegend=mostrar, hoverinfo="skip", **estilo,
            ),
            row=1, col=coluna,
        )
        mostrar = False


def _painel(figura, coluna, x, densidade, cor, nome_teste, rotulo, resumo, criticos, legenda):
    """Desenha um painel do G2: p-valor (cor do teste), região de rejeição (hachura cinza) e a curva."""
    alem_do_observado = np.abs(x) >= abs(resumo["observado"])
    _area(figura, x, densidade, alem_do_observado, f"p-valor do exemplo ({nome_teste})",
          f"p_{nome_teste}", True, coluna, fillcolor=rgba(cor, 0.55))
    rejeita = (x <= criticos[0]) | (x >= criticos[1])
    _area(figura, x, densidade, rejeita, f"Região de rejeição (α = {_br(ALFA)})", "rejeicao", legenda, coluna,
          fillcolor=COR_REJEICAO, fillpattern={"shape": "/", "fgcolor": "rgba(90,90,90,0.9)", "size": 8,
                                                "solidity": 0.25})
    figura.add_trace(
        go.Scatter(
            x=x, y=densidade, mode="lines", line={"color": cor, "width": 2},
            name=f"Distribuição sob H₀ ({nome_teste}: {rotulo})",
            hovertemplate=f"{rotulo} = %{{x:.2f}}<br>densidade = %{{y:.3f}}<extra></extra>",
        ),
        row=1, col=coluna,
    )
    for critico in criticos:
        figura.add_vline(x=critico, line={"color": "rgba(90,90,90,0.9)", "dash": "dot", "width": 1},
                         row=1, col=coluna)
    figura.add_vline(
        x=resumo["observado"], line={"color": cor, "dash": "dash", "width": 2}, row=1, col=coluna,
        annotation_text=f"observado: {rotulo} = {_br(resumo['observado'])}",
        annotation_position="top right" if resumo["observado"] > 0 else "top left",
    )


def figura_g2(resultados, rhos_h0, n=N):
    """Monta o G2: distribuição de cada estatística sob H₀, região de rejeição e p-valor do exemplo."""
    pearson = resumo_pearson(resultados["pearson"], n)
    spearman = resumo_spearman(resultados["spearman"], rhos_h0)

    limite_t = max(4.5, abs(pearson["observado"]) + 0.5)
    x_t = np.linspace(-limite_t, limite_t, PONTOS_CURVA)
    densidade_t = stats.t.pdf(x_t, n - 2)

    x_rho = np.linspace(-1, 1, PONTOS_CURVA)
    densidade_rho = stats.gaussian_kde(rhos_h0)(x_rho)

    figura = make_subplots(
        rows=1, cols=2, horizontal_spacing=0.08,
        subplot_titles=(
            f"Pearson: t com {n - 2} graus de liberdade (teórica)",
            f"Spearman: ρ em {len(rhos_h0):,} conjuntos simulados".replace(",", "."),
        ),
    )
    _painel(figura, 1, x_t, densidade_t, COR_PEARSON, "Pearson", "t", pearson,
            (-pearson["critico"], pearson["critico"]), True)
    _painel(figura, 2, x_rho, densidade_rho, COR_SPEARMAN, "Spearman", "ρ", spearman,
            (spearman["critico_inf"], spearman["critico"]), False)

    figura.update_layout(
        title=f"G2: distribuição da estatística de cada teste sob H₀ (n = {n} módulos)",
        legend={"orientation": "h", "y": -0.25, "x": 0},
        margin={"t": 90, "b": 110},
        hovermode="x unified",
    )
    figura.update_xaxes(title_text="Estatística t (adimensional)", row=1, col=1)
    figura.update_xaxes(title_text="Coeficiente ρ de Spearman (adimensional, de −1 a 1)", row=1, col=2)
    figura.update_yaxes(title_text="Densidade de probabilidade", row=1, col=1)
    figura.update_xaxes(zeroline=False)
    figura.update_yaxes(rangemode="tozero", gridcolor="rgba(128,128,128,0.2)")
    return figura


def tabela_g2(resultados, rhos_h0, n=N):
    pearson = resumo_pearson(resultados["pearson"], n)
    spearman = resumo_spearman(resultados["spearman"], rhos_h0)
    linhas = []
    for nome, chave, resumo, regiao in (
        ("Pearson", "pearson", pearson, f"|t| ≥ {_br(pearson['critico'], 3)}"),
        ("Spearman", "spearman", spearman,
         f"ρ ≤ {_br(spearman['critico_inf'], 3)} ou ρ ≥ {_br(spearman['critico'], 3)}"),
    ):
        coeficiente = resultados[chave]["coeficiente"]
        linhas.append({
            "Teste": nome,
            "Coeficiente (tamanho do efeito)": round(coeficiente, 3),
            "Magnitude": classificar_magnitude(coeficiente),
            "Estatística observada": round(resumo["observado"], 3),
            "Região de rejeição": regiao,
            "p-valor (SciPy)": f"{resumo['p_valor']:.2g}",
            "p-valor (área no G2)": f"{resumo['p_valor_area']:.2g}",
            "Decisão (α = 0,05)": "Rejeita H₀" if resumo["p_valor"] < ALFA else "Não rejeita H₀",
        })
    return pd.DataFrame(linhas)


def _br(valor, casas=2):
    return f"{valor:.{casas}f}".replace(".", ",")


def _formatar_p(p):
    return "menor que 0,001" if p < 0.001 else _br(p, 3)


def texto_g2(resultados, rhos_h0, n=N):
    pearson = resumo_pearson(resultados["pearson"], n)
    spearman = resumo_spearman(resultados["spearman"], rhos_h0)
    r, rho = resultados["pearson"]["coeficiente"], resultados["spearman"]["coeficiente"]
    return (
        "O Pearson mede a associação linear nos valores de LOC e de defeitos e a converte na estatística t; "
        "o Spearman mede a associação nos postos e usa o próprio ρ. "
        "Com H₀ verdadeira, as duas estatísticas ficam perto de zero, então a região de rejeição (cinza) fica nas duas "
        f"caudas, onde estão os 5% de valores mais extremos: |t| ≥ {_br(pearson['critico'])} e |ρ| ≥ cerca de "
        f"{_br(spearman['critico'])}. "
        f"No conjunto de exemplo (n = {n}), r = {_br(r)} e ρ = {_br(rho)}, e o p-valor é a área colorida além do valor "
        f"observado ({_formatar_p(pearson['p_valor'])} no Pearson e {_formatar_p(spearman['p_valor'])} no Spearman): "
        "a probabilidade de uma correlação tão forte quanto essa, ou mais, se LOC e defeitos fossem independentes, "
        "e não a probabilidade de H₀ ser verdadeira."
    )


def render():
    st.header("3. Como os testes funcionam")
    _, resultados = rodar_exemplo()
    rhos_h0 = simular_rho_h0()
    st.plotly_chart(figura_g2(resultados, rhos_h0), width="stretch")
    st.write(texto_g2(resultados, rhos_h0))
    with st.expander("Ver os valores do gráfico em tabela"):
        st.dataframe(tabela_g2(resultados, rhos_h0), hide_index=True)

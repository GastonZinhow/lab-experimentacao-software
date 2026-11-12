"""Versão estática do dashboard: um único arquivo HTML, que abre direto no navegador.

Reaproveita as funções de gráfico, texto e tabela de cada seção do dashboard
em Streamlit, então as duas versões mostram sempre os mesmos números. Só o
gráfico interativo do bônus fica de fora, porque ele simula na hora.
"""
import html
import re
from pathlib import Path

import pandas as pd
import plotly.offline

from dashboard import PROJETOS_PADRAO, REPOSITORIO_PADRAO, SECOES
from secoes import (
    secao_1_cenario,
    secao_2_dados,
    secao_3_testes,
    secao_4_erro_tipo1,
    secao_5_poder,
    secao_6_dados_reais,
    secao_7_conclusao,
)
from dados_reais import ARQUIVO_AMOSTRA
from exemplo import N, rodar_exemplo
from gerador import carregar_parametros

ARQUIVO_HTML = Path(__file__).resolve().parents[1] / "dashboard.html"
URL_PLOTLY = f"https://cdn.plot.ly/plotly-{plotly.offline.get_plotlyjs_version()}.min.js"
CONFIG_PLOTLY = {"responsive": True, "displaylogo": False}

LEGENDA_G2 = (
    f"Exemplo: um conjunto simulado de {N} módulos, com a associação calibrada na amostra real do KC1 "
    "(semente 42). Como ler: a curva mostra os valores que a estatística assume quando não há associação; "
    "a hachura cinza é a região de rejeição; a área colorida é o p-valor do exemplo."
)
LEGENDA_G4 = (
    "Cada ponto resume 10.000 amostras simuladas de 30 módulos. No efeito zero não há associação e a altura "
    "mede o erro tipo I; nos efeitos positivos, mede a frequência com que o teste detecta a associação existente."
)
AVISO_BONUS = (
    "O gráfico interativo do bônus, em que se escolhe o tamanho da amostra e do efeito, simula na hora e por isso "
    "só existe na versão em Streamlit: `python -m streamlit run lab04/code/dashboard.py`."
)


def markdown_simples(texto):
    """Converte o Markdown usado nos textos das seções (negrito, código, links e parágrafos) em HTML."""
    paragrafos = []
    for bloco in texto.split("\n\n"):
        trecho = html.escape(bloco, quote=False)
        trecho = re.sub(r"`([^`]+)`", r"<code>\1</code>", trecho)
        trecho = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", trecho)
        trecho = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', trecho)
        paragrafos.append(f"<p>{trecho}</p>")
    return "\n".join(paragrafos)


# Mesmo tema do Streamlit (`.streamlit/config.toml`): fundo branco, letra preta e fonte maior para o projetor.
FUNDO = "#FFFFFF"
FUNDO_SECUNDARIO = "#F2F2F2"
TEXTO = "#000000"
TAMANHO_FONTE_GRAFICO = 15
# Rótulos dos eixos um pouco menores, para as faixas do G1 (ex.: "100–199") caberem sem inclinar.
TAMANHO_FONTE_EIXOS = 12


def aplicar_tema_claro(figura):
    """Fundo branco, texto preto e fonte um pouco maior nos gráficos, como na versão em Streamlit."""
    figura = type(figura)(figura)
    figura.update_layout(
        template="plotly_white", paper_bgcolor=FUNDO, plot_bgcolor=FUNDO,
        font={"color": TEXTO, "size": TAMANHO_FONTE_GRAFICO},
    )
    figura.update_xaxes(tickfont={"size": TAMANHO_FONTE_EIXOS}, tickangle=0)
    figura.update_yaxes(tickfont={"size": TAMANHO_FONTE_EIXOS})
    return figura


def grafico(figura, identificador):
    """Div do Plotly com id fixo, para o arquivo gerado ser sempre o mesmo."""
    figura = aplicar_tema_claro(figura)
    div = figura.to_html(full_html=False, include_plotlyjs=False, div_id=identificador, config=CONFIG_PLOTLY)
    return f'<div class="grafico">{div}</div>'


def tabela(dados, resumo="Ver os valores do gráfico em tabela", aberta=False):
    corpo = dados.to_html(index=False, escape=True, border=0, classes="tabela", na_rep="—")
    atributo = " open" if aberta else ""
    return f"<details{atributo}><summary>{html.escape(resumo)}</summary>{corpo}</details>"


def legenda(texto):
    return f'<p class="legenda">{markdown_simples(texto)[3:-4]}</p>'


def secao(numero, titulo, conteudo):
    return f'<section id="secao-{numero}"><h2>{numero}. {html.escape(titulo)}</h2>\n{conteudo}\n</section>'


def conteudo_secao_1():
    return "\n".join([
        f"<h3>{html.escape(secao_1_cenario.PERGUNTA)}</h3>",
        markdown_simples(secao_1_cenario.INTRODUCAO),
        '<div class="hipoteses">',
        f'<div class="caixa">{markdown_simples(secao_1_cenario.H0)}</div>',
        f'<div class="caixa">{markdown_simples(secao_1_cenario.H1)}</div>',
        "</div>",
        markdown_simples(secao_1_cenario.BICAUDAL),
        markdown_simples(secao_1_cenario.texto_origem_atual()),
        "<h3>O que esperávamos antes de simular</h3>",
        markdown_simples(secao_1_cenario.EXPECTATIVA),
    ])


def conteudo_secao_2():
    real = pd.read_csv(ARQUIVO_AMOSTRA)
    simulado = secao_2_dados.simular_para_g1()
    return "\n".join([
        grafico(secao_2_dados.figura_g1(real, simulado), "g1"),
        markdown_simples(secao_2_dados.texto_g1(real, simulado)),
        tabela(secao_2_dados.tabela_g1(real, simulado)),
        tabela(secao_2_dados.tabela_parametros(carregar_parametros()), "Ver os parâmetros da simulação"),
        tabela(secao_2_dados.tabela_situacoes(), "Ver as situações da Q3"),
    ])


def conteudo_secao_3():
    _, resultados = rodar_exemplo()
    rhos_h0 = secao_3_testes.simular_rho_h0()
    return "\n".join([
        legenda(LEGENDA_G2),
        grafico(secao_3_testes.figura_g2(resultados, rhos_h0), "g2"),
        markdown_simples(secao_3_testes.texto_g2(resultados, rhos_h0)),
        tabela(secao_3_testes.tabela_g2(resultados, rhos_h0)),
        f'<p class="aviso">{markdown_simples(AVISO_BONUS)[3:-4]}</p>',
    ])


def conteudo_secao_4():
    resultados = secao_4_erro_tipo1.ler_resultados()
    if resultados.empty:
        return "<p>Ainda não há resultados de erro tipo I.</p>"
    resultados = secao_4_erro_tipo1.classificar(resultados)
    return "\n".join([
        grafico(secao_4_erro_tipo1.figura_g3(resultados), "g3"),
        markdown_simples(secao_4_erro_tipo1.texto_g3(resultados)),
        tabela(secao_4_erro_tipo1.tabela_g3(resultados)),
    ])


def conteudo_secao_5():
    resultados = secao_5_poder.ler_resultados()
    if resultados.empty:
        return "<p>Ainda não há resultados de poder.</p>"
    return "\n".join([
        legenda(LEGENDA_G4),
        grafico(secao_5_poder.figura_g4(resultados), "g4"),
        markdown_simples(secao_5_poder.texto_g4(resultados)),
        tabela(secao_5_poder.tabela_g4(resultados)),
    ])


def conteudo_secao_6():
    resultado = secao_6_dados_reais.ler_resultado()
    if resultado.empty:
        return "<p>Ainda não há resultado nos dados reais.</p>"
    return "\n".join([
        tabela(secao_6_dados_reais.tabela_secao_6(resultado), "Resultado dos dois testes nos dados reais", aberta=True),
        markdown_simples(secao_6_dados_reais.texto_secao_6(resultado)),
    ])


def conteudo_secao_7():
    erro_tipo1, poder = secao_7_conclusao.carregar_resultados()
    if erro_tipo1.empty or poder.empty:
        return "<p>Ainda faltam resultados para a conclusão.</p>"
    textos = secao_7_conclusao.resumir_conclusao(erro_tipo1, poder)
    return "\n".join([
        "<h3>O que esperávamos × o que encontramos</h3>",
        markdown_simples(textos["expectativa"]),
        markdown_simples(textos["contraste"]),
        "<h3>Recomendação</h3>",
        f'<div class="caixa destaque">{markdown_simples(textos["recomendacao"])}</div>',
        "<h3>Quando a escolha mudaria?</h3>",
        markdown_simples(textos["mudanca"]),
        legenda(textos["limitacao"]),
    ])


CONTEUDOS = {
    1: conteudo_secao_1, 2: conteudo_secao_2, 3: conteudo_secao_3, 4: conteudo_secao_4,
    5: conteudo_secao_5, 6: conteudo_secao_6, 7: conteudo_secao_7,
}

ESTILO = """
:root { color-scheme: light; --fundo: #FFFFFF; --texto: #000000; --suave: #3d3d3d; --borda: #d0d0d0;
  --secundario: #F2F2F2; --caixa: #e8eefa; --destaque: #e3f3e8; --acento: #1a4fc4; --aviso: #fdf3d6; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--fundo); color: var(--texto);
  font: 20px/1.6 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
main { max-width: 1200px; margin: 0 auto; padding: 24px 16px 64px; }
header h1 { margin: 0 0 4px; font-size: 2rem; }
header p { margin: 0 0 12px; color: var(--suave); }
.links { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
.links a, nav a, section a { color: var(--acento); }
.links a { border: 1px solid var(--borda); border-radius: 8px; padding: 6px 12px; text-decoration: none; }
nav { display: flex; flex-wrap: wrap; gap: 4px 14px; border-top: 1px solid var(--borda);
  border-bottom: 1px solid var(--borda); padding: 8px 0; font-size: .9rem; }
nav a { text-decoration: none; }
.grafico { overflow-x: auto; overflow-y: hidden; max-width: 100%; }
section { padding-top: 28px; border-bottom: 1px solid var(--borda); padding-bottom: 20px; }
h2 { font-size: 1.5rem; margin: 0 0 8px; }
h3 { font-size: 1.15rem; margin: 20px 0 6px; }
code { background: var(--secundario); border-radius: 4px; padding: 1px 4px; font-size: .85em; overflow-wrap: anywhere; }
.hipoteses { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.caixa { background: var(--caixa); border-radius: 8px; padding: 4px 14px; }
.caixa.destaque { background: var(--destaque); }
.legenda { color: var(--suave); font-size: .9rem; }
.aviso { background: var(--aviso); border-radius: 8px; padding: 10px 14px; font-size: .9rem; }
details { margin: 10px 0; }
summary { cursor: pointer; color: var(--acento); }
.tabela { border-collapse: collapse; margin-top: 8px; font-size: .85rem; display: block; overflow-x: auto; }
.tabela th, .tabela td { border-bottom: 1px solid var(--borda); padding: 6px 10px; text-align: left; }
.tabela th { background: var(--secundario); }
footer { color: var(--suave); font-size: .8rem; margin-top: 24px; }
@media (max-width: 700px) { body { font-size: 17px; } .hipoteses { grid-template-columns: 1fr; } header h1 { font-size: 1.5rem; } }
"""


def montar_html():
    secoes = "\n".join(secao(s.numero, s.titulo, CONTEUDOS[s.numero]()) for s in SECOES)
    indice = "".join(f'<a href="#secao-{s.numero}">{s.numero}. {html.escape(s.titulo)}</a>' for s in SECOES)
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lab04 · Pearson × Spearman</title>
<style>{ESTILO}</style>
<script src="{URL_PLOTLY}"></script>
</head>
<body>
<main>
<header>
<h1>Testes de hipótese por dentro</h1>
<p>Pearson × Spearman · tamanho do módulo × número de defeitos</p>
<div class="links">
<a href="{REPOSITORIO_PADRAO}">Repositório</a>
<a href="{PROJETOS_PADRAO}">GitHub Projects</a>
</div>
<nav>{indice}</nav>
</header>
{secoes}
<footer>Gerado por <code>lab04/code/dashboard_html.py</code> (etapa <code>06_dashboard_html.py</code> do comando único).
Os gráficos precisam de internet para carregar o Plotly.</footer>
</main>
</body>
</html>
"""


def gerar_html(arquivo=ARQUIVO_HTML):
    conteudo = montar_html()
    Path(arquivo).write_text(conteudo, encoding="utf-8", newline="\n")
    return Path(arquivo)

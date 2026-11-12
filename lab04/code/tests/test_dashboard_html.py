import re

import pytest

pytest.importorskip("streamlit")
pytest.importorskip("plotly")

from dashboard import SECOES
from dashboard_html import gerar_html, markdown_simples, montar_html


@pytest.fixture(scope="module")
def pagina():
    return montar_html()


def test_markdown_simples_converte_negrito_codigo_link_e_paragrafos():
    resultado = markdown_simples("**H₀** usa `rng(42)` e [o dataset](http://exemplo.org/a.arff).\n\nSegundo")
    assert "<strong>H₀</strong>" in resultado
    assert "<code>rng(42)</code>" in resultado
    assert '<a href="http://exemplo.org/a.arff">o dataset</a>' in resultado
    assert resultado.count("<p>") == 2


def test_markdown_simples_escapa_html():
    assert "&lt;script&gt;" in markdown_simples("<script>alert(1)</script>")


def test_pagina_tem_as_sete_secoes_na_ordem_e_os_quatro_graficos(pagina):
    titulos = re.findall(r"<h2>(\d)\. ", pagina)
    assert titulos == [str(secao.numero) for secao in SECOES]
    for identificador in ("g1", "g2", "g3", "g4"):
        assert f'id="{identificador}"' in pagina
    assert "cdn.plot.ly/plotly-" in pagina


def test_pagina_traz_links_textos_e_tabela_dos_dados_reais(pagina):
    assert "github.com/GastonZinhow/lab-experimentacao-software" in pagina
    assert "O que esperávamos antes de simular" in pagina
    assert "Os dois testes rejeitam H₀" in pagina
    assert "Rejeita H₀" in pagina
    assert "só existe na versão em Streamlit" in pagina


def test_pagina_e_reproduzivel(pagina, tmp_path):
    arquivo = gerar_html(tmp_path / "dashboard.html")
    assert arquivo.read_text(encoding="utf-8") == pagina


def test_tema_claro_igual_ao_streamlit_sem_alterar_a_figura_original():
    import plotly.graph_objects as go

    from dashboard_html import FUNDO, TEXTO, aplicar_tema_claro

    figura = go.Figure(go.Bar(x=[1], y=[1]))
    clara = aplicar_tema_claro(figura)
    assert clara.layout.paper_bgcolor == FUNDO == "#FFFFFF"
    assert clara.layout.plot_bgcolor == FUNDO
    assert clara.layout.font.color == TEXTO == "#000000"
    assert figura.layout.paper_bgcolor is None


def test_pagina_usa_o_tema_claro(pagina):
    assert "color-scheme: light" in pagina
    assert "--fundo: #FFFFFF" in pagina

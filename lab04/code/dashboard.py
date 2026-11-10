"""Dashboard principal do Lab04.

Cada integrante implementa somente ``secoes/secao_<N>_<nome>.py`` e expõe
uma função ``render()``. Este arquivo descobre e renderiza essas seções na
ordem do enunciado, sem precisar ser alterado quando uma nova seção chegar.
"""

from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

import streamlit as st

PASTA_SECOES = Path(__file__).resolve().parent / "secoes"
REPOSITORIO_PADRAO = "https://github.com/GastonZinhow/lab-experimentacao-software"
DASHBOARD_LOCAL = "http://localhost:8501"
PROJETOS_PADRAO = f"{REPOSITORIO_PADRAO}/projects"


@dataclass(frozen=True)
class Secao:
    numero: int
    titulo: str


SECOES = (
    Secao(1, "Cenário"),
    Secao(2, "Os dados"),
    Secao(3, "Como os testes funcionam"),
    Secao(4, "Erro tipo I"),
    Secao(5, "Poder"),
    Secao(6, "Dados reais"),
    Secao(7, "Conclusão"),
)


def encontrar_arquivo(secao: Secao, pasta: Path = PASTA_SECOES) -> Path | None:
    """Encontra o arquivo de uma seção pelo número definido no enunciado."""
    arquivos = sorted(pasta.glob(f"secao_{secao.numero}_*.py"))
    if not arquivos:
        return None
    if len(arquivos) > 1:
        nomes = ", ".join(arquivo.name for arquivo in arquivos)
        raise RuntimeError(f"Há mais de um arquivo para esta seção: {nomes}")
    return arquivos[0]


def carregar_modulo(caminho: Path) -> ModuleType:
    """Carrega um módulo de seção diretamente do caminho encontrado."""
    nome_modulo = f"dashboard_secoes.{caminho.stem}"
    especificacao = importlib.util.spec_from_file_location(nome_modulo, caminho)
    if especificacao is None or especificacao.loader is None:
        raise ImportError(f"Não foi possível preparar a importação de {caminho.name}")

    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


def renderizar_secao(secao: Secao, pasta: Path = PASTA_SECOES) -> None:
    """Renderiza uma seção ou um aviso, preservando as demais seções."""
    try:
        caminho = encontrar_arquivo(secao, pasta)
        if caminho is None:
            st.header(f"{secao.numero}. {secao.titulo}")
            st.warning("🚧 Seção em construção.")
            return

        modulo = carregar_modulo(caminho)
        render = getattr(modulo, "render", None)
        if not callable(render):
            raise AttributeError(f"{caminho.name} precisa expor uma função render()")
        render()
    except Exception as erro:  # Uma seção com problema não deve derrubar as outras.
        st.header(f"{secao.numero}. {secao.titulo}")
        st.error(f"Não foi possível carregar esta seção: {erro}")


def mostrar_link(coluna, rotulo: str, url: str) -> None:
    """Mostra um botão quando há URL e mantém um espaço visível quando não há."""
    with coluna:
        if url:
            st.link_button(rotulo, url, use_container_width=True)
        else:
            st.info(f"{rotulo}: link a preencher")


def renderizar_cabecalho() -> None:
    """Renderiza o título e os links exigidos no topo do dashboard."""
    st.title("Testes de hipótese por dentro")
    st.caption("Pearson × Spearman · tamanho do módulo × número de defeitos")

    colunas = st.columns(3)
    dashboard_publicado = os.getenv("DASHBOARD_URL", "")
    mostrar_link(
        colunas[0],
        "Dashboard publicado" if dashboard_publicado else "Dashboard local",
        dashboard_publicado or DASHBOARD_LOCAL,
    )
    mostrar_link(
        colunas[1],
        "Repositório",
        os.getenv("REPOSITORY_URL", REPOSITORIO_PADRAO),
    )
    mostrar_link(
        colunas[2],
        "GitHub Projects",
        os.getenv("GITHUB_PROJECTS_URL", PROJETOS_PADRAO),
    )
    st.divider()


def main() -> None:
    st.set_page_config(
        page_title="Lab04 · Pearson × Spearman",
        page_icon="📊",
        layout="wide",
    )
    renderizar_cabecalho()
    for secao in SECOES:
        renderizar_secao(secao)
        if secao != SECOES[-1]:
            st.divider()


if __name__ == "__main__":
    main()

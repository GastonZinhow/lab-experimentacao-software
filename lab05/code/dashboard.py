"""Dashboard principal do Lab05: confiabilidade operacional do GitHub × GitLab.

Cada integrante implementa somente ``secoes/secao_<N>_<nome>.py`` e expõe uma
função ``render()``. Este arquivo descobre e renderiza essas seções na ordem
abaixo, sem precisar ser alterado quando uma nova seção chegar. Uma seção que
ainda não existe mostra "em construção"; uma seção com erro mostra o erro sem
derrubar as outras.

Para abrir (na raiz do repositório, para usar o tema do grupo)::

    python -m streamlit run lab05/code/dashboard.py
"""

from __future__ import annotations

import importlib.util
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

import streamlit as st

PASTA_CODIGO = Path(__file__).resolve().parent
PASTA_SECOES = PASTA_CODIGO / "secoes"
REPOSITORIO_PADRAO = "https://github.com/GastonZinhow/lab-experimentacao-software"
DASHBOARD_LOCAL = "http://localhost:8501"
PROJETOS_PADRAO = "https://github.com/users/GastonZinhow/projects"

if str(PASTA_CODIGO) not in sys.path:
    sys.path.insert(0, str(PASTA_CODIGO))


@dataclass(frozen=True)
class Secao:
    numero: int
    titulo: str


SECOES = (
    Secao(1, "Software"),
    Secao(2, "Pergunta e método"),
    Secao(3, "Dados e coleta"),
    Secao(4, "Frequência"),
    Secao(5, "Tempo de recuperação"),
    Secao(6, "Triangulação"),
    Secao(7, "Impacto"),
    Secao(8, "Ameaças e conclusão"),
)


def encontrar_arquivo(secao: Secao, pasta: Path = PASTA_SECOES) -> Path | None:
    """Encontra o arquivo ``secao_<N>_*.py`` de uma seção."""
    arquivos = sorted(pasta.glob(f"secao_{secao.numero}_*.py"))
    if not arquivos:
        return None
    if len(arquivos) > 1:
        nomes = ", ".join(arquivo.name for arquivo in arquivos)
        raise RuntimeError(f"Há mais de um arquivo para esta seção: {nomes}")
    return arquivos[0]


def carregar_modulo(caminho: Path) -> ModuleType:
    """Carrega um módulo de seção diretamente do arquivo."""
    nome_modulo = f"lab05_secoes.{caminho.stem}"
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
            st.warning("Seção em construção.", icon="🚧")
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
    with coluna:
        if url:
            st.link_button(rotulo, url, width="stretch")
        else:
            st.info(f"{rotulo}: link a preencher")


def renderizar_cabecalho() -> None:
    st.title("Confiabilidade operacional: GitHub × GitLab")
    st.caption(
        "Incidentes publicados nas páginas de status de GitHub.com e GitLab.com · "
        "nov/2025 a out/2026 (UTC) · somente componentes equivalentes"
    )

    colunas = st.columns(3)
    dashboard_publicado = os.getenv("DASHBOARD_URL", "")
    mostrar_link(
        colunas[0],
        "Dashboard publicado" if dashboard_publicado else "Dashboard local",
        dashboard_publicado or DASHBOARD_LOCAL,
    )
    mostrar_link(colunas[1], "Repositório", os.getenv("REPOSITORY_URL", REPOSITORIO_PADRAO))
    mostrar_link(
        colunas[2], "GitHub Projects", os.getenv("GITHUB_PROJECTS_URL", PROJETOS_PADRAO)
    )
    st.divider()


def main() -> None:
    st.set_page_config(
        page_title="Lab05 · GitHub × GitLab",
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

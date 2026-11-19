"""Seção 1 do dashboard: o software estudado e os três critérios do enunciado.

Também serve de exemplo do formato: um arquivo por seção, uma função
``render()`` que começa com ``st.header("<N>. <título>")``, textos em
constantes (fáceis de testar) e cores do ``dashboard_comum``.

Fonte dos números: ``lab05/docs/criterios.md`` (acesso em 19/11/2026).
"""

from __future__ import annotations

import streamlit as st

from dashboard_comum import CORES, JANELA_FIM, JANELA_INICIO, NOMES

DATA_ACESSO = "19/11/2026"

INTRODUCAO = (
    "Estudamos **o serviço em operação**, GitHub.com e GitLab.com, como um usuário "
    "o vê de fora: pelos incidentes que as próprias empresas publicam nas páginas de "
    "status. Não mineramos commits, issues nem pull requests de repositórios."
)

PLATAFORMAS = {
    "github": {
        "status": "https://www.githubstatus.com",
        "descricao": "Hospedagem de código, revisão (pull requests), CI/CD (Actions), pacotes e Pages.",
        "numeros": [
            ("Desenvolvedores", "225 mi+", "https://github.com/about"),
            ("Organizações", "4 mi+", "https://github.com/about"),
            (
                "Jobs do Actions (out/25–set/26)",
                "45,4 bi",
                "https://github.blog/news-insights/octoverse/octoverse-commits-pushes-reach-new-highs-in-2026-as-developers-build-with-agents/",
            ),
        ],
        "operacao": (
            "Incidente de Actions e Checks API em 09/11/2026, das 18:07 às 18:59 UTC "
            "([status](https://www.githubstatus.com/incidents/tp8cghg7tlc4))."
        ),
    },
    "gitlab": {
        "status": "https://status.gitlab.com",
        "descricao": "Plataforma DevSecOps: código, merge requests, CI/CD com runners, registries e Pages.",
        "numeros": [
            ("Usuários registrados", "50 mi+", "https://about.gitlab.com/company/"),
            ("Organizações", "100 mil+", "https://about.gitlab.com/jobs/"),
            (
                "Clientes com ARR > US$ 5 mil",
                "11.114",
                "https://ir.gitlab.com/financials/quarterly-results/default.aspx",
            ),
        ],
        "operacao": (
            "Versão 19.5 lançada em 15/10/2026 e investigação de erros do Gitaly em "
            "03/11/2026 ([status](https://status.gitlab.com/))."
        ),
    },
}

CRITERIOS = (
    "| Critério | GitHub.com | GitLab.com |\n"
    "|---|---|---|\n"
    "| **Real** | Produto, documentação e página de status oficiais | Produto, documentação e página de status oficiais |\n"
    "| **Em operação** | Incidentes publicados em nov/2026; 17,9 bi de pushes no último ano | Lançamento mensal (19.5); incidentes publicados em nov/2026 |\n"
    "| **Alto impacto** | 225 mi+ de desenvolvedores; 90% da Fortune 100 | 50 mi+ de usuários; 100 mil+ organizações |\n"
)

POR_QUE_AGORA = (
    "Em 2026 o GitHub teve meses turbulentos e uma reconstrução independente da "
    "disponibilidade divergiu dos percentuais da página oficial (*The Register*, "
    "12/06/2026). Por isso comparamos as duas plataformas com as **mesmas regras** e "
    "deixamos claro que medimos **incidentes publicados**, não todas as falhas."
)


def cabecalho_plataforma(plataforma: str) -> str:
    return (
        f"<h3 style='color:{CORES[plataforma]};margin-bottom:0'>"
        f"{NOMES[plataforma]}</h3>"
    )


def render() -> None:
    st.header("1. Software")
    st.markdown(INTRODUCAO)

    colunas = st.columns(2)
    for coluna, (plataforma, dados) in zip(colunas, PLATAFORMAS.items()):
        with coluna:
            st.markdown(cabecalho_plataforma(plataforma), unsafe_allow_html=True)
            st.caption(dados["descricao"])
            metricas = st.columns(len(dados["numeros"]))
            for metrica, (rotulo, valor, _) in zip(metricas, dados["numeros"]):
                metrica.metric(rotulo, valor)
            fontes = " · ".join(
                f"[{rotulo}]({url})" for rotulo, _, url in dados["numeros"]
            )
            st.caption(f"Fontes: {fontes} (acesso em {DATA_ACESSO})")
            st.markdown(f"**Em operação:** {dados['operacao']}")
            st.markdown(f"Página de status: <{dados['status']}>")

    st.subheader("Os três critérios do enunciado")
    st.markdown(CRITERIOS)
    st.caption(
        "Números publicados pelos próprios fornecedores; detalhes e links em "
        "`lab05/docs/criterios.md`."
    )

    st.subheader("Por que estudar agora")
    st.markdown(POR_QUE_AGORA)
    st.info(
        f"Janela do estudo: **{JANELA_INICIO}** a **{JANELA_FIM}** (12 meses fechados, UTC)."
    )

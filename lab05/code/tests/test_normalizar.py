"""Testes da etapa 02 (normalização e validação) com casos de borda, sem internet."""

import csv
import re
from pathlib import Path

import pytest

import run_all

PASTA_CODIGO = Path(__file__).resolve().parents[1]
etapa = run_all.carregar_etapa(PASTA_CODIGO / "etapas" / "02_normalizar.py")

MAPA = {
    ("github", "Actions"): "ci_cd",
    ("github", "Git Operations"): "git",
    ("github", "API Requests"): "api",
    ("github", "Copilot"): "fora_do_escopo",
    ("gitlab", "API"): "api",
}


def regra(tipo: str, padrao: str, categoria: str, plataforma: str = "ambas"):
    return etapa.RegraTitulo(plataforma, tipo, re.compile(padrao, re.IGNORECASE), categoria)


REGRAS = [
    regra("exclusiva", r"\bduo\b", "fora_do_escopo"),
    regra("especifica", r"\bgit\b", "git"),
    regra("especifica", r"pipelines?", "ci_cd"),
    regra("especifica", r"customers\.gitlab\.com", "fora_do_escopo"),
    regra("generica", r"(?<![\w.])gitlab\.com", "web", "gitlab"),
]


def bruto(**campos) -> dict:
    base = {
        "plataforma": "github",
        "id": "a1",
        "titulo": "Incident with Actions",
        "componentes_originais": "Actions",
        "impacto": "minor",
        "inicio_utc": "2026-03-01T10:00:00Z",
        "fim_utc": "2026-03-01T11:30:00Z",
        "fonte": "githubstatus",
        "url": "https://www.githubstatus.com/incidents/a1",
        "retroativo": False,
    }
    return {**base, **campos}


def normalizar(*brutos):
    return etapa.normalizar(list(brutos), MAPA, REGRAS)


# --------------------------------------------------------------------------- #
# Formato e mapa
# --------------------------------------------------------------------------- #


def test_incidente_comum_vai_para_o_formato_comum() -> None:
    linhas, relatorio = normalizar(bruto())

    assert linhas == [
        {
            "plataforma": "github",
            "id": "a1",
            "titulo": "Incident with Actions",
            "componentes_originais": "Actions",
            "componente_equivalente": "ci_cd",
            "impacto": "minor",
            "inicio_utc": "2026-03-01T10:00:00Z",
            "fim_utc": "2026-03-01T11:30:00Z",
            "duracao_min": "90",
            "fonte": "githubstatus",
            "url": "https://www.githubstatus.com/incidents/a1",
            "origem_componente": "publicado",
            "retroativo": "false",
            "termina_apos_janela": "false",
        }
    ]
    assert etapa.verificar(linhas) == []
    assert relatorio.sem_fim == []


def test_varios_componentes_contam_uma_vez_por_categoria() -> None:
    linhas, _ = normalizar(bruto(componentes_originais="API Requests;Actions;Copilot;Git Operations"))

    assert linhas[0]["componente_equivalente"] == "api;ci_cd;fora_do_escopo;git"


def test_componente_sem_mapeamento_e_listado() -> None:
    linhas, relatorio = normalizar(bruto(componentes_originais="Actions;Componente Novo"))

    assert linhas[0]["componente_equivalente"] == "ci_cd"
    assert relatorio.sem_mapeamento == {("github", "Componente Novo"): 1}


def test_so_componente_sem_mapeamento_vira_sem_componente() -> None:
    linhas, relatorio = normalizar(bruto(componentes_originais="Componente Novo"))

    assert linhas[0]["componente_equivalente"] == "sem_componente"
    assert linhas[0]["origem_componente"] == "publicado"
    assert relatorio.sem_mapeamento


# --------------------------------------------------------------------------- #
# Classificação pelo título
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("plataforma", "titulo", "esperado"),
    [
        ("gitlab", "Intermittent Git and CI/CD pipeline failures", "ci_cd;git"),
        ("gitlab", "Issues with GitLab Duo in merge requests pipelines", "fora_do_escopo"),
        ("gitlab", "Elevated 5xx Errors on GitLab.com", "web"),
        ("gitlab", "Pipelines failing on GitLab.com", "ci_cd"),
        ("gitlab", "404s on customers.gitlab.com", "fora_do_escopo"),
        ("gitlab", "Error loading GitLab.com and customers.gitlab.com", "fora_do_escopo;web"),
        ("github", "Elevated errors on GitLab.com", ""),
        ("gitlab", "Performance degradation in APAC", ""),
    ],
)
def test_categorias_pelo_titulo(plataforma: str, titulo: str, esperado: str) -> None:
    assert etapa.categorias_pelo_titulo(plataforma, titulo, REGRAS) == esperado


def test_sem_componente_publicado_usa_o_titulo() -> None:
    linhas, relatorio = normalizar(
        bruto(plataforma="gitlab", componentes_originais="", titulo="Git operation failed", impacto="")
    )

    assert linhas[0]["componente_equivalente"] == "git"
    assert linhas[0]["origem_componente"] == "titulo"
    assert len(relatorio.pelo_titulo) == 1


def test_sem_componente_e_sem_regra() -> None:
    linhas, relatorio = normalizar(bruto(componentes_originais="", titulo="Something odd"))

    assert linhas[0]["componente_equivalente"] == "sem_componente"
    assert linhas[0]["origem_componente"] == "nenhuma"
    assert len(relatorio.sem_componente) == 1


def test_titulo_nao_substitui_componente_publicado() -> None:
    linhas, _ = normalizar(bruto(componentes_originais="Actions", titulo="Git is down"))

    assert linhas[0]["componente_equivalente"] == "ci_cd"


# --------------------------------------------------------------------------- #
# Bordas da janela
# --------------------------------------------------------------------------- #


def test_inicio_exatamente_nas_bordas_entra() -> None:
    linhas, _ = normalizar(
        bruto(id="borda-ini", inicio_utc="2025-11-01T00:00:00Z", fim_utc="2025-11-01T00:10:00Z"),
        bruto(id="borda-fim", inicio_utc="2026-10-31T23:59:59Z", fim_utc="2026-11-01T00:09:59Z"),
    )

    assert [r["id"] for r in linhas] == ["borda-ini", "borda-fim"]
    assert etapa.verificar(linhas) == []


def test_comeca_antes_e_termina_dentro_fica_fora_mas_e_contado() -> None:
    linhas, relatorio = normalizar(
        bruto(inicio_utc="2025-10-31T23:00:00Z", fim_utc="2025-11-01T02:00:00Z")
    )

    assert linhas == []
    assert [r["id"] for r in relatorio.antes_da_janela] == ["a1"]


def test_comeca_e_termina_antes_some_sem_aviso() -> None:
    linhas, relatorio = normalizar(
        bruto(inicio_utc="2025-10-30T10:00:00Z", fim_utc="2025-10-30T11:00:00Z")
    )

    assert linhas == [] and relatorio.antes_da_janela == []


def test_comeca_dentro_e_termina_depois_mantem_duracao_inteira() -> None:
    linhas, relatorio = normalizar(
        bruto(inicio_utc="2026-10-31T22:00:00Z", fim_utc="2026-11-01T02:00:00Z")
    )

    assert linhas[0]["duracao_min"] == "240"
    assert linhas[0]["termina_apos_janela"] == "true"
    assert len(relatorio.termina_apos_janela) == 1


def test_comeca_depois_da_janela_fica_fora() -> None:
    linhas, relatorio = normalizar(
        bruto(inicio_utc="2026-11-01T00:00:00Z", fim_utc="2026-11-01T01:00:00Z")
    )

    assert linhas == []
    assert relatorio.depois_da_janela["github"] == 1


# --------------------------------------------------------------------------- #
# Fim ausente ou inválido e ids repetidos
# --------------------------------------------------------------------------- #


def test_sem_fim_entra_sem_duracao() -> None:
    linhas, relatorio = normalizar(bruto(fim_utc="", retroativo=True))

    assert linhas[0]["fim_utc"] == "" and linhas[0]["duracao_min"] == ""
    assert linhas[0]["retroativo"] == "true"
    assert len(relatorio.sem_fim) == 1
    assert etapa.verificar(linhas) == []


@pytest.mark.parametrize("fim", ["2026-03-01T10:00:00Z", "2026-03-01T09:00:00Z"])
def test_fim_igual_ou_antes_do_inicio_perde_a_duracao(fim: str) -> None:
    linhas, relatorio = normalizar(bruto(fim_utc=fim))

    assert linhas[0]["fim_utc"] == "" and linhas[0]["duracao_min"] == ""
    assert len(relatorio.fim_invalido) == 1
    assert etapa.verificar(linhas) == []


def test_id_repetido_fica_o_primeiro() -> None:
    linhas, relatorio = normalizar(bruto(titulo="primeiro"), bruto(titulo="segundo"))

    assert [r["titulo"] for r in linhas] == ["primeiro"]
    assert len(relatorio.repetidos) == 1


def test_mesmo_id_em_plataformas_diferentes_nao_e_repetido() -> None:
    linhas, relatorio = normalizar(
        bruto(), bruto(plataforma="gitlab", componentes_originais="API")
    )

    assert len(linhas) == 2 and relatorio.repetidos == []


def test_verificar_aponta_problemas() -> None:
    linha = normalizar(bruto())[0][0]
    ruins = [
        {**linha, "inicio_utc": "2027-01-01T00:00:00Z", "fim_utc": "2027-01-01T01:00:00Z"},
        {**linha, "id": "b", "fim_utc": "2026-03-01T09:00:00Z"},
        {**linha, "id": "c", "duracao_min": ""},
        {**linha, "id": "d", "plataforma": "bitbucket"},
    ]

    problemas = etapa.verificar(ruins)

    assert any("fora da janela" in p for p in problemas)
    assert any("fim_utc <= inicio_utc" in p for p in problemas)
    assert any("inconsistentes" in p for p in problemas)
    assert any("plataforma inválida" in p for p in problemas)


# --------------------------------------------------------------------------- #
# Arquivos reais versionados
# --------------------------------------------------------------------------- #


def test_regras_versionadas_usam_categorias_validas() -> None:
    regras = etapa.ler_regras()

    assert regras
    assert {r.tipo for r in regras} <= {"exclusiva", "especifica", "generica"}
    assert {r.plataforma for r in regras} <= {"ambas", "github", "gitlab"}
    assert {r.categoria for r in regras} <= set(etapa.CATEGORIAS)


def test_main_gera_csv_valido_com_os_dados_brutos(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(etapa, "ARQUIVO_SAIDA", tmp_path / "incidentes.csv")
    monkeypatch.setattr(etapa, "ARQUIVO_VALIDACAO", tmp_path / "validacao.md")

    etapa.main()

    with (tmp_path / "incidentes.csv").open(encoding="utf-8", newline="") as entrada:
        leitor = csv.DictReader(entrada)
        linhas = list(leitor)
    assert tuple(leitor.fieldnames[: len(etapa.COLUNAS)]) == etapa.COLUNAS
    assert {r["plataforma"] for r in linhas} == {"github", "gitlab"}
    assert etapa.verificar(linhas) == []
    assert "Validação dos incidentes" in (tmp_path / "validacao.md").read_text(encoding="utf-8")

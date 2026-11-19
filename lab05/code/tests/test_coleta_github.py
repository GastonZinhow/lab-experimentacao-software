"""Testes do coletor do GitHub com respostas reais salvas em 2026-11-19 (sem internet).

``tests/fixtures/github/`` tem a página 1 do histórico (set–nov/2026) e o JSON
de seis incidentes de outubro/2026, copiados de ``dados/brutos/github/``.
"""

import json
import shutil
from datetime import date
from pathlib import Path

import pytest

from coleta import github
from coleta._http import ClienteEducado, ErroColeta

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "github"


class SessaoProibida:
    headers: dict[str, str] = {}

    def get(self, url: str, timeout: int):
        raise AssertionError(f"O teste não pode acessar a internet: {url}")


@pytest.fixture
def cliente(tmp_path: Path) -> ClienteEducado:
    shutil.copytree(FIXTURES, tmp_path / "github")
    return ClienteEducado(tmp_path / "github", sessao=SessaoProibida())


def ler_fixture(codigo: str) -> dict:
    return json.loads((FIXTURES / "incidentes" / f"{codigo}.json").read_text(encoding="utf-8"))


def test_coletar_janela_com_respostas_salvas(cliente: ClienteEducado) -> None:
    incidentes = github.coletar("2026-10-05T00:00:00Z", "2026-10-07T23:59:59Z", cliente)

    assert [r["id"] for r in incidentes] == [
        "3q1yb5m7ltvb",
        "2kxnqcxcrr7f",
        "cjwszcf57bff",
        "djlmxz2zd0j7",
        "qpfv5p86dmrl",
    ]
    assert cliente.requisicoes == 0
    primeiro = incidentes[0]
    assert primeiro == {
        "plataforma": "github",
        "id": "3q1yb5m7ltvb",
        "titulo": "Incident with Actions",
        "componentes_originais": "Actions;Pages",
        "impacto": "critical",
        "inicio_utc": "2026-10-05T19:11:58Z",
        "fim_utc": "2026-10-05T22:49:42Z",
        "duracao_min": 217.74,
        "fonte": "githubstatus",
        "url": "https://www.githubstatus.com/incidents/3q1yb5m7ltvb",
        "status": "resolved",
        "retroativo": False,
        "manutencao": False,
    }


def test_coletar_respeita_a_borda_da_janela(cliente: ClienteEducado) -> None:
    incidentes = github.coletar("2026-10-05T23:00:00Z", "2026-10-06T23:59:59Z", cliente)

    assert [r["id"] for r in incidentes] == ["2kxnqcxcrr7f", "cjwszcf57bff"]


def test_inicio_e_o_primeiro_registro_publico_quando_started_at_foi_editado() -> None:
    # started_at foi gravado igual a resolved_at; o relatório mensal confirma ~71 min.
    registro = github.normalizar_incidente(ler_fixture("djlmxz2zd0j7"))

    assert registro["inicio_utc"] == "2026-10-07T15:14:45Z"
    assert registro["duracao_min"] == pytest.approx(70.47)


def test_incidente_retroativo_fica_sem_duracao() -> None:
    registro = github.normalizar_incidente(ler_fixture("dqn46wtvbdzv"))

    assert registro["retroativo"] is True
    assert registro["inicio_utc"] == "2026-10-01T02:00:00Z"
    assert registro["fim_utc"] == ""
    assert registro["duracao_min"] is None


@pytest.mark.parametrize(
    ("timestamp", "ano", "mes", "esperado"),
    [
        ("Aug <var data-var='date'>26</var>, <var data-var='time'>23:37</var> - Aug 27 UTC", 2026, 8, date(2026, 8, 26)),
        ("Dec <var data-var='date'>31</var>, <var data-var='time'>23:50</var> UTC", 2026, 1, date(2025, 12, 31)),
        ("sem data", 2026, 1, None),
    ],
)
def test_data_inicial_exibida(timestamp, ano, mes, esperado) -> None:
    assert github.data_inicial_exibida(timestamp, ano, mes) == esperado


def test_historico_baixado_em_meses_diferentes_e_rejeitado(tmp_path: Path) -> None:
    pasta = tmp_path / "github" / "historico"
    pasta.mkdir(parents=True)
    mes = {"name": "October", "year": 2026, "incidents": []}
    paginas = {
        1: {"start_time": "2026-09-01T00:00:00Z", "end_time": "2026-11-30T23:59:59Z", "months": [mes]},
        # Página 2 sobreposta à página 1: sinal de que foi baixada em outro mês.
        2: {"start_time": "2026-07-01T00:00:00Z", "end_time": "2026-09-30T23:59:59Z", "months": [mes]},
    }
    for numero, conteudo in paginas.items():
        (pasta / f"pagina_{numero:02d}.json").write_text(json.dumps(conteudo), encoding="utf-8")
    cliente = ClienteEducado(tmp_path / "github", sessao=SessaoProibida())

    with pytest.raises(ErroColeta, match="não são contíguas"):
        github.listar_incidentes(github.como_utc("2026-01-01"), github.como_utc("2026-10-31"), cliente)

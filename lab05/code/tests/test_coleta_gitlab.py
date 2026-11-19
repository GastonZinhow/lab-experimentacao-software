"""Testes do coletor do GitLab com uma resposta real salva (sem internet).

``tests/fixtures/gitlab/amostra.ics`` é um recorte do ``all.ics`` salvo pelo
navegador em 2026-11-19: o cabeçalho e seis VEVENT copiados sem alterar nenhum
byte (quatro incidentes de outubro/2026 e duas manutenções).
"""

import shutil
from pathlib import Path

import pytest

from coleta import gitlab
from coleta._http import CaminhoBloqueado, ClienteEducado

AMOSTRA = Path(__file__).resolve().parent / "fixtures" / "gitlab" / "amostra.ics"


class SessaoProibida:
    headers: dict[str, str] = {}

    def get(self, url: str, timeout: int):
        raise AssertionError(f"O teste não pode acessar a internet: {url}")


@pytest.fixture
def cliente(tmp_path: Path) -> ClienteEducado:
    shutil.copy(AMOSTRA, tmp_path / gitlab.ARQUIVO_ICAL)
    return ClienteEducado(tmp_path, sessao=SessaoProibida())


def eventos() -> dict[str, dict]:
    texto = AMOSTRA.read_text(encoding="utf-8")
    return {e["UID"][0].split("@")[0]: e for e in gitlab.ler_eventos(texto)}


def test_coletar_outubro_com_resposta_salva(cliente: ClienteEducado) -> None:
    incidentes = gitlab.coletar("2026-10-01T00:00:00Z", "2026-10-31T23:59:59Z", cliente)

    # A manutenção de 31/10 (Customers Portal) fica de fora.
    assert [r["id"] for r in incidentes] == ["000-mrwygx", "000-fgwh19", "0000y86d10", "000-svb5ts"]
    assert cliente.requisicoes == 0
    primeiro = incidentes[0]
    assert primeiro["plataforma"] == "gitlab"
    assert primeiro["titulo"] == "Job delays on saas-linux-small-amd64 hosted runners"
    assert primeiro["inicio_utc"] == "2026-10-07T16:51:44Z"
    assert primeiro["fim_utc"] == "2026-10-07T18:04:25Z"
    assert primeiro["duracao_min"] == pytest.approx(72.68)
    assert primeiro["fonte"] == "statusgitlab_ical"
    assert primeiro["issue_producao"] == (
        "https://gitlab.com/gitlab-com/gl-infra/production/-/work_items/23117"
    )
    # O iCal não tem esses campos; não inventamos valores.
    assert primeiro["componentes_originais"] == "" and primeiro["impacto"] == ""


def test_arquivo_manual_vai_para_o_manifesto(cliente: ClienteEducado) -> None:
    gitlab.coletar("2026-10-01T00:00:00Z", "2026-10-31T23:59:59Z", cliente)

    linhas = (cliente.pasta / "manifesto.csv").read_text(encoding="utf-8").splitlines()
    assert linhas[1].startswith(gitlab.URL_ICAL + ",")
    assert ",manual,all.ics," in linhas[1]


def test_linhas_dobradas_e_caracteres_escapados() -> None:
    manutencao = gitlab.normalizar_evento(eventos()["000-d1p19c"])

    assert "There may be brief, short-lived disruptions during the upgrade; however," in (
        manutencao["descricao"]
    )


@pytest.mark.parametrize(
    ("uid", "esperado"),
    [
        ("000-wa5j9n", True),   # 11:00:00–12:00:00, "Upcoming maintenance"
        ("000-d1p19c", True),   # 12:00:00–15:00:00, "Gitaly Storage Node Upgrade"
        ("000-mrwygx", False),  # 16:51:44
        ("000-svb5ts", False),  # 11:33:00: segundos 00, mas minuto fora do quarto de hora
    ],
)
def test_manutencao_e_reconhecida_pelo_horario_agendado(uid: str, esperado: bool) -> None:
    assert gitlab.eh_manutencao(eventos()[uid]) is esperado


def test_sem_arquivo_o_coletor_respeita_o_robots(tmp_path: Path) -> None:
    class SessaoRobots:
        headers: dict[str, str] = {}

        def get(self, url: str, timeout: int):
            assert url == "https://status.gitlab.com/robots.txt"

            class Resposta:
                status_code = 200
                content = b"User-agent: *\nDisallow: /pages/*\n"
                text = content.decode()

            return Resposta()

    cliente = ClienteEducado(tmp_path, sessao=SessaoRobots(), dormir=lambda _: None)

    with pytest.raises(CaminhoBloqueado):
        gitlab.coletar("2026-10-01", "2026-10-31", cliente)

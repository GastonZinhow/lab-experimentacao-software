"""Testes do cliente compartilhado pelos coletores. Nenhum acessa a internet."""

from pathlib import Path

import pytest

from coleta import _http
from coleta._http import CaminhoBloqueado, ClienteEducado, ErroColeta, RegrasRobots

ROBOTS_GITHUBSTATUS = "User-agent: *\nDisallow: /api/\nDisallow: /embed/\n"
ROBOTS_STATUS_GITLAB = (
    "User-agent: *\nDisallow: /pages/*\nDisallow: /user/*\n"
    "Disallow: /dashboard/*\nDisallow: /subscriber/*\n"
)


class Resposta:
    def __init__(self, status: int, conteudo: bytes = b"") -> None:
        self.status_code = status
        self.content = conteudo
        self.text = conteudo.decode("utf-8")


class SessaoFalsa:
    """Responde a partir de um dicionário ``url -> [respostas]`` e anota as chamadas."""

    def __init__(self, respostas: dict[str, list[Resposta]]) -> None:
        self.headers: dict[str, str] = {}
        self.respostas = respostas
        self.chamadas: list[str] = []

    def get(self, url: str, timeout: int) -> Resposta:
        self.chamadas.append(url)
        return self.respostas[url].pop(0)


class SessaoProibida:
    headers: dict[str, str] = {}

    def get(self, url: str, timeout: int):
        raise AssertionError(f"O teste não pode acessar a internet: {url}")


@pytest.fixture
def relogio(monkeypatch: pytest.MonkeyPatch):
    """Relógio falso: ``dormir`` avança o tempo em vez de esperar."""
    estado = {"agora": 1000.0, "dormidas": []}
    monkeypatch.setattr(ClienteEducado, "_ultima_requisicao", 0.0)

    def dormir(segundos: float) -> None:
        estado["dormidas"].append(segundos)
        estado["agora"] += segundos

    estado["dormir"] = dormir
    estado["relogio"] = lambda: estado["agora"]
    return estado


def criar_cliente(pasta: Path, sessao, relogio) -> ClienteEducado:
    return ClienteEducado(pasta, sessao=sessao, dormir=relogio["dormir"], relogio=relogio["relogio"])


@pytest.mark.parametrize(
    ("robots", "caminho", "esperado"),
    [
        (ROBOTS_GITHUBSTATUS, "/history.json?page=1", True),
        (ROBOTS_GITHUBSTATUS, "/incidents/abc123.json", True),
        (ROBOTS_GITHUBSTATUS, "/api/v2/incidents.json", False),
        (ROBOTS_STATUS_GITLAB, "/", True),
        (ROBOTS_STATUS_GITLAB, "/pages/history/5b36dc6502d06804c08349f7", False),
        (ROBOTS_STATUS_GITLAB, "/pages/5b36dc6502d06804c08349f7/calendar/all.ics", False),
        ("User-Agent: *\nDisallow: /users\nAllow: /users/sign_in\n", "/users/sign_in", True),
        ("User-Agent: *\nDisallow: /users\nAllow: /users/sign_in\n", "/users/fulano", False),
        ("User-Agent: *\nDisallow: /*/*.git$\n", "/grupo/projeto.git", False),
        ("User-Agent: *\nDisallow: /*/*.git$\n", "/grupo/projeto.github", True),
        ("User-agent: OutroRobo\nDisallow: /\n", "/qualquer", True),
    ],
)
def test_robots_entende_curingas_e_regra_mais_longa(robots, caminho, esperado):
    assert RegrasRobots.de_texto(robots).permite(caminho) is esperado


def test_obter_usa_cache_sem_acessar_a_internet(tmp_path: Path, relogio) -> None:
    (tmp_path / "pasta").mkdir()
    (tmp_path / "pasta" / "arquivo.json").write_bytes(b"{}")
    cliente = criar_cliente(tmp_path, SessaoProibida(), relogio)

    assert cliente.obter("https://exemplo.org/arquivo.json", "pasta/arquivo.json") == b"{}"
    assert cliente.requisicoes == 0
    assert not (tmp_path / "manifesto.csv").exists()


def test_obter_recusa_caminho_bloqueado_sem_baixar(tmp_path: Path, relogio) -> None:
    sessao = SessaoFalsa(
        {"https://status.gitlab.com/robots.txt": [Resposta(200, ROBOTS_STATUS_GITLAB.encode())]}
    )
    cliente = criar_cliente(tmp_path, sessao, relogio)

    with pytest.raises(CaminhoBloqueado, match="Salve o arquivo manualmente"):
        cliente.obter("https://status.gitlab.com/pages/x/calendar/all.ics", "all.ics")
    assert sessao.chamadas == ["https://status.gitlab.com/robots.txt"]


def test_obter_baixa_salva_registra_e_espera_entre_requisicoes(tmp_path: Path, relogio) -> None:
    sessao = SessaoFalsa(
        {
            "https://exemplo.org/robots.txt": [Resposta(200, b"User-agent: *\nDisallow: /api/\n")],
            "https://exemplo.org/a.json": [Resposta(200, b'{"a": 1}')],
        }
    )
    cliente = criar_cliente(tmp_path, sessao, relogio)

    assert cliente.obter("https://exemplo.org/a.json", "dados/a.json") == b'{"a": 1}'
    assert (tmp_path / "dados" / "a.json").read_bytes() == b'{"a": 1}'
    assert sessao.headers["User-Agent"] == _http.USER_AGENT
    # robots.txt + arquivo: a segunda requisição esperou o intervalo mínimo.
    assert relogio["dormidas"] == [pytest.approx(_http.INTERVALO_MINIMO_S)]
    linhas = (tmp_path / "manifesto.csv").read_text(encoding="utf-8").splitlines()
    assert linhas[0] == ",".join(_http.CAMPOS_MANIFESTO)
    assert linhas[2].startswith("https://exemplo.org/a.json,")
    resumo = _http.sha256(b'{"a": 1}')
    assert linhas[2].endswith(f",200,dados/a.json,{resumo}")


def test_erro_4xx_nao_e_repetido(tmp_path: Path, relogio) -> None:
    sessao = SessaoFalsa(
        {
            "https://exemplo.org/robots.txt": [Resposta(404)],
        }
    )
    cliente = criar_cliente(tmp_path, sessao, relogio)

    # robots.txt ausente (4xx) → tudo é tratado como bloqueado, por precaução.
    with pytest.raises(CaminhoBloqueado):
        cliente.obter("https://exemplo.org/a.json", "a.json")
    assert sessao.chamadas == ["https://exemplo.org/robots.txt"]


def test_erro_5xx_tem_uma_unica_nova_tentativa_depois_de_60s(tmp_path: Path, relogio) -> None:
    sessao = SessaoFalsa(
        {
            "https://exemplo.org/robots.txt": [Resposta(200, b"")],
            "https://exemplo.org/a.json": [Resposta(503), Resposta(503)],
        }
    )
    cliente = criar_cliente(tmp_path, sessao, relogio)

    with pytest.raises(ErroColeta, match="HTTP 503"):
        cliente.obter("https://exemplo.org/a.json", "a.json")
    assert sessao.chamadas.count("https://exemplo.org/a.json") == 2
    assert _http.ESPERA_NOVA_TENTATIVA_S in relogio["dormidas"]
    assert not (tmp_path / "a.json").exists()


def test_registrar_arquivo_manual_anota_uma_vez(tmp_path: Path, relogio) -> None:
    (tmp_path / "all.ics").write_bytes(b"BEGIN:VCALENDAR\r\nEND:VCALENDAR\r\n")
    cliente = criar_cliente(tmp_path, SessaoProibida(), relogio)

    cliente.registrar_arquivo_manual("https://status.gitlab.com/x/all.ics", "all.ics")
    cliente.registrar_arquivo_manual("https://status.gitlab.com/x/all.ics", "all.ics")

    linhas = (tmp_path / "manifesto.csv").read_text(encoding="utf-8").splitlines()
    assert len(linhas) == 2
    assert ",manual,all.ics," in linhas[1]

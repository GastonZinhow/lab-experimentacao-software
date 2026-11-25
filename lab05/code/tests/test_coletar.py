"""Testes da etapa 01 (coleta): o modo só cache nunca acessa a internet."""

import json
import shutil
from pathlib import Path

import pytest

import run_all
from coleta._http import ErroColeta

PASTA_CODIGO = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
etapa = run_all.carregar_etapa(PASTA_CODIGO / "etapas" / "01_coletar.py")


@pytest.fixture(autouse=True)
def sem_internet(monkeypatch) -> None:
    def proibido(*args, **kwargs):
        raise AssertionError("O teste não pode acessar a internet")

    monkeypatch.setattr("requests.Session.get", proibido)


def test_cliente_so_cache_le_arquivo_salvo(tmp_path: Path) -> None:
    (tmp_path / "gitlab").mkdir()
    (tmp_path / "gitlab" / "x.txt").write_bytes(b"ok")

    assert etapa.criar_cliente("gitlab", False, tmp_path).obter("https://exemplo", "x.txt") == b"ok"


def test_cliente_so_cache_para_quando_falta_arquivo(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(etapa, "PASTA_CODIGO", tmp_path)
    cliente = etapa.criar_cliente("github", False, tmp_path)

    with pytest.raises(ErroColeta, match="Modo só cache"):
        cliente.obter("https://www.githubstatus.com/history.json?page=1", "historico/pagina_01.json")
    assert cliente.requisicoes == 0


def test_coleta_so_cache_falha_sem_historico_completo(tmp_path: Path, monkeypatch) -> None:
    # A fixture só tem a página 1 do histórico (set–nov/2026): falta o resto da janela.
    monkeypatch.setattr(etapa, "PASTA_CODIGO", tmp_path)
    shutil.copytree(FIXTURES / "github", tmp_path / "github")

    with pytest.raises(ErroColeta, match="pagina_02"):
        etapa.coletar_tudo(baixar=False, pasta_brutos=tmp_path)


def test_data_da_coleta_vem_do_manifesto(tmp_path: Path) -> None:
    manifesto = tmp_path / "manifesto.csv"
    manifesto.write_text(
        "url,data_hora_utc,status_http,arquivo,sha256\n"
        "https://a/robots.txt,2026-11-19T10:00:00Z,200,,abc\n"
        "https://a/2,2026-11-24T10:00:00Z,200,b.json,def\n"
        "https://a/1,2026-11-19T10:00:01Z,200,a.json,abc\n",
        encoding="utf-8",
    )

    assert etapa.data_da_coleta(manifesto) == {
        "primeira_resposta_utc": "2026-11-19T10:00:01Z",
        "ultima_resposta_utc": "2026-11-24T10:00:00Z",
        "respostas_salvas": 2,
    }


def test_contar_por_mes_inclui_meses_vazios() -> None:
    contagem = etapa.contar_por_mes([{"inicio_utc": "2026-01-03T00:00:00Z"}] * 2)

    assert list(contagem) == etapa.MESES_JANELA
    assert len(contagem) == 12
    assert contagem["2026-01"] == 2 and sum(contagem.values()) == 2


def test_cache_versionado_reproduz_o_resumo_sem_internet() -> None:
    resumo = etapa.coletar_tudo(baixar=False)
    versionado = json.loads(etapa.ARQUIVO_RESUMO.read_text(encoding="utf-8"))

    assert resumo == versionado
    for plataforma in ("github", "gitlab"):
        dados = resumo["plataformas"][plataforma]
        assert dados["incidentes"] == sum(dados["por_mes"].values()) > 0

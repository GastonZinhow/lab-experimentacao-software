from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

import dashboard
import dashboard_comum
from dashboard import SECOES, Secao, encontrar_arquivo

PASTA_CODIGO = Path(__file__).resolve().parents[1]


def test_dashboard_abre_com_as_secoes_disponiveis_e_avisos_nas_ausentes() -> None:
    app = AppTest.from_file(str(PASTA_CODIGO / "dashboard.py"), default_timeout=60).run()

    assert not app.exception
    assert not app.error
    titulos = [f"{secao.numero}. {secao.titulo}" for secao in SECOES]
    assert [cabecalho.value for cabecalho in app.header] == titulos
    ausentes = [secao for secao in SECOES if encontrar_arquivo(secao) is None]
    avisos = [aviso for aviso in app.warning if aviso.value == "Seção em construção."]
    assert len(avisos) == len(ausentes)


def test_secoes_sao_as_oito_combinadas_e_em_ordem() -> None:
    assert [secao.numero for secao in SECOES] == list(range(1, 9))
    assert SECOES[0].titulo == "Software"
    assert SECOES[-1].titulo == "Ameaças e conclusão"


def test_secao_com_erro_nao_derruba_as_outras(tmp_path: Path) -> None:
    (tmp_path / "secao_1_quebrada.py").write_text(
        "def render():\n    raise ValueError('falha proposital')\n", encoding="utf-8"
    )
    (tmp_path / "secao_2_sem_render.py").write_text("X = 1\n", encoding="utf-8")
    script = (
        "import dashboard\n"
        "from pathlib import Path\n"
        f"pasta = Path({str(tmp_path)!r})\n"
        "dashboard.renderizar_secao(dashboard.Secao(1, 'Um'), pasta)\n"
        "dashboard.renderizar_secao(dashboard.Secao(2, 'Dois'), pasta)\n"
        "dashboard.renderizar_secao(dashboard.Secao(3, 'Três'), pasta)\n"
    )

    app = AppTest.from_string(script, default_timeout=30).run()

    assert not app.exception
    assert [cabecalho.value for cabecalho in app.header] == ["1. Um", "2. Dois", "3. Três"]
    assert "falha proposital" in app.error[0].value
    assert "precisa expor uma função render()" in app.error[1].value
    assert app.warning[0].value == "Seção em construção."


def test_dois_arquivos_para_a_mesma_secao_e_erro(tmp_path: Path) -> None:
    (tmp_path / "secao_1_a.py").write_text("", encoding="utf-8")
    (tmp_path / "secao_1_b.py").write_text("", encoding="utf-8")

    with pytest.raises(RuntimeError, match="mais de um arquivo"):
        encontrar_arquivo(Secao(1, "Um"), tmp_path)


def test_carregar_incidentes_usa_exemplo_enquanto_nao_ha_dados_reais(tmp_path: Path) -> None:
    tabela, eh_exemplo = dashboard_comum.carregar_incidentes(
        real=tmp_path / "nao_existe.csv"
    )

    assert eh_exemplo
    assert list(tabela.columns) == list(dashboard_comum.COLUNAS)
    assert str(tabela["inicio_utc"].dt.tz) == "UTC"


def test_carregar_incidentes_rejeita_formato_incompleto(tmp_path: Path) -> None:
    arquivo = tmp_path / "incidentes.csv"
    pd.DataFrame({"plataforma": ["github"], "id": ["1"]}).to_csv(arquivo, index=False)

    with pytest.raises(ValueError, match="Colunas ausentes"):
        dashboard_comum.carregar_incidentes(real=arquivo)


def test_cabecalho_tem_titulo_e_tres_links() -> None:
    script = "import dashboard\ndashboard.renderizar_cabecalho()\n"

    app = AppTest.from_string(script, default_timeout=30).run()

    assert not app.exception
    assert app.title[0].value == "Confiabilidade operacional: GitHub × GitLab"
    assert dashboard.REPOSITORIO_PADRAO.startswith("https://github.com/")

from streamlit.testing.v1 import AppTest

from secoes import secao_1_software as secao


def test_secao_1_renderiza_sem_erro() -> None:
    script = "from secoes import secao_1_software\nsecao_1_software.render()\n"

    app = AppTest.from_string(script, default_timeout=30).run()

    assert not app.exception
    assert app.header[0].value == "1. Software"
    rotulos = [metrica.label for metrica in app.metric]
    assert "Desenvolvedores" in rotulos and "Usuários registrados" in rotulos


def test_toda_metrica_tem_fonte_com_link() -> None:
    for dados in secao.PLATAFORMAS.values():
        for _, valor, url in dados["numeros"]:
            assert valor
            assert url.startswith("https://")


def test_cabecalho_usa_a_cor_combinada_de_cada_plataforma() -> None:
    assert "#6e40c9" in secao.cabecalho_plataforma("github")
    assert "#fc6d26" in secao.cabecalho_plataforma("gitlab")

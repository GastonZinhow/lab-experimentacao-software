from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_dashboard_abre_com_as_secoes_disponiveis_e_avisos_nas_ausentes():
    dashboard = Path(__file__).resolve().parents[1] / "dashboard.py"

    app = AppTest.from_file(str(dashboard), default_timeout=30).run()

    assert not app.exception
    assert [cabecalho.value for cabecalho in app.header] == [
        "1. Cenário",
        "2. Os dados",
        "3. Como os testes funcionam",
        "4. Erro tipo I",
        "5. Poder",
        "6. Dados reais",
        "7. Conclusão",
    ]
    assert len(app.warning) == 5
    # O AppTest separa o emoji usado como ícone do texto do alerta.
    assert all(aviso.value == "Seção em construção." for aviso in app.warning)

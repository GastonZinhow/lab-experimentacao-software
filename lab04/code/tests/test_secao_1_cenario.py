import pytest

pytest.importorskip("streamlit")

from secoes.secao_1_cenario import EXPECTATIVA, texto_origem


def test_origem_informa_amostra_populacao_e_variaveis():
    texto = texto_origem(30, 145)
    assert "30 classes entre 145" in texto
    assert "sumLOC_TOTAL" in texto and "NUMDEFECTS" in texto
    assert "promise.site.uottawa.ca" in texto


def test_expectativa_registrada_antes_de_simular_aparece_no_dashboard():
    assert "Spearman" in EXPECTATIVA
    assert "antes das simulações" in EXPECTATIVA

import pandas as pd
import pytest

pytest.importorskip("streamlit")

from analise_dados_reais import analisar, carregar_amostra
from secoes.secao_6_dados_reais import ler_resultado, tabela_secao_6, texto_secao_6


@pytest.fixture
def resultado():
    return ler_resultado()


def test_tabela_tem_estatistica_p_valor_efeito_e_conclusao(resultado):
    tabela = tabela_secao_6(resultado)
    assert len(tabela) == 4
    for coluna in ("Estatística (t)", "p-valor", "Tamanho do efeito", "Conclusão (α = 0,05)"):
        assert coluna in tabela.columns
    assert tabela["Tamanho do efeito"].iloc[0].startswith("r = 0,84")
    assert tabela["Tamanho do efeito"].iloc[1].startswith("ρ = 0,51")
    assert tabela["p-valor"].iloc[0] == "< 0,001"


def test_texto_usa_os_valores_do_csv_e_tem_de_duas_a_quatro_frases(resultado):
    texto = texto_secao_6(resultado)
    assert "r = 0,84" in texto and "ρ = 0,51" in texto and "0,58" in texto
    assert "Os dois testes rejeitam H₀" in texto
    assert 2 <= texto.count(". ") + 1 <= 4


def test_texto_muda_quando_nenhum_teste_rejeita(resultado):
    sem_rejeicao = resultado.assign(rejeita_h0=False)
    texto = texto_secao_6(sem_rejeicao)
    assert "Nenhum dos dois testes rejeita H₀" in texto
    assert "a decisão muda" in texto


def test_csv_lido_e_o_mesmo_da_analise(resultado):
    pd.testing.assert_frame_equal(resultado, analisar(carregar_amostra()), check_dtype=False, rtol=1e-9)


def test_sem_csv_devolve_tabela_vazia(tmp_path):
    assert ler_resultado(tmp_path / "inexistente.csv").empty

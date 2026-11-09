import pandas as pd
import pytest

pytest.importorskip("streamlit")
pytest.importorskip("plotly")

from secoes.secao_4_erro_tipo1 import CORES, classificar, figura_g3, ler_resultados, tabela_g3, texto_g3
from simulacao import COLUNAS_ERRO_TIPO1


def linhas(situacao, pearson, spearman, repeticoes=10_000):
    return [
        {"situacao": situacao, "teste": "pearson", "n": 30, "alfa": 0.05, "repeticoes": repeticoes,
         "proporcao_rejeicao": pearson},
        {"situacao": situacao, "teste": "spearman", "n": 30, "alfa": 0.05, "repeticoes": repeticoes,
         "proporcao_rejeicao": spearman},
    ]


@pytest.fixture
def pasta(tmp_path):
    pd.DataFrame(linhas("base", 0.0592, 0.0558)).to_csv(tmp_path / "erro_tipo1_base.csv", index=False)
    pd.DataFrame(linhas("outliers", 0.081, 0.051)).to_csv(tmp_path / "erro_tipo1_outliers.csv", index=False)
    pd.DataFrame([{"x": 1}]).to_csv(tmp_path / "poder_base.csv", index=False)
    return tmp_path


def test_le_todos_os_csvs_de_erro_tipo1_e_so_eles(pasta):
    tabela = ler_resultados(pasta)
    assert list(tabela.columns) == COLUNAS_ERRO_TIPO1
    assert list(tabela["situacao"]) == ["base", "base", "outliers", "outliers"]


def test_pasta_sem_resultados_devolve_tabela_vazia(tmp_path):
    assert ler_resultados(tmp_path).empty


def test_classifica_pela_margem_de_monte_carlo():
    tabela = classificar(pd.DataFrame(linhas("a", 0.0540, 0.0545) + linhas("b", 0.0450, 0.0600)))
    assert list(tabela["classificacao"]) == ["perto de α", "liberal", "conservador", "liberal"]


def test_g3_tem_titulo_eixos_legenda_cores_e_linha_em_5_por_cento(pasta):
    figura = figura_g3(classificar(ler_resultados(pasta)))
    assert "G3" in figura.layout.title.text
    assert "Situação" in figura.layout.xaxis.title.text
    assert "%" in figura.layout.yaxis.title.text
    barras = [serie for serie in figura.data if serie.type == "bar"]
    assert {serie.marker.color for serie in barras} == set(CORES.values())
    assert {serie.name for serie in barras} == {"Pearson", "Spearman"}
    assert any(forma.y0 == pytest.approx(5) and forma.y1 == pytest.approx(5) for forma in figura.layout.shapes)


def test_tabela_tem_uma_linha_por_teste_e_situacao(pasta):
    assert len(tabela_g3(classificar(ler_resultados(pasta)))) == 4


def test_texto_diz_qual_teste_se_desviou_e_em_que_sentido(pasta):
    texto = texto_g3(classificar(ler_resultados(pasta)))
    assert 2 <= texto.count(". ") + 1 <= 4
    assert "Pearson na situação outliers" in texto
    assert "liberal" in texto
    assert "8,10%" in texto


def test_texto_quando_ninguem_se_desvia():
    texto = texto_g3(classificar(pd.DataFrame(linhas("base", 0.0501, 0.0499))))
    assert "Nenhum teste se desviou" in texto
    assert 2 <= texto.count(". ") + 1 <= 4


def test_texto_nao_diz_que_spearman_ficou_mais_perto_quando_nao_ficou():
    texto = texto_g3(classificar(pd.DataFrame(linhas("base", 0.060, 0.070))))
    assert "fica mais perto de α" not in texto

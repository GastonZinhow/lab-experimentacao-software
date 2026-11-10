from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip("streamlit")
pytest.importorskip("plotly")

from dashboard import SECOES, encontrar_arquivo
from secoes import secao_5_poder
from secoes.secao_5_poder import CORES, figura_g4, ler_resultados, tabela_g4, texto_g4
from simulacao import COLUNAS_PODER


def linhas(situacao, valores):
    resultado = []
    for efeito, pearson, spearman in valores:
        for teste, proporcao in (("pearson", pearson), ("spearman", spearman)):
            resultado.append({
                "situacao": situacao,
                "teste": teste,
                "n": 30,
                "alfa": 0.05,
                "repeticoes": 10_000,
                "proporcao_rejeicao": proporcao,
                "efeito": efeito,
            })
    return resultado


@pytest.fixture
def pasta(tmp_path):
    pd.DataFrame(linhas("base", [
        (0.0, 0.05, 0.05),
        (0.1, 0.20, 0.10),
        (0.3, 0.40, 0.55),
        (0.5, 0.70, 0.90),
    ])).to_csv(tmp_path / "poder_base.csv", index=False)
    pd.DataFrame(linhas("nova", [
        (0.0, 0.05, 0.05),
        (0.1, 0.25, 0.15),
        (0.3, 0.60, 0.45),
        (0.5, 0.90, 0.75),
    ])).to_csv(tmp_path / "poder_nova.csv", index=False)
    pd.DataFrame([{"x": 1}]).to_csv(tmp_path / "erro_tipo1_base.csv", index=False)
    return tmp_path


def test_le_todos_os_csvs_de_poder_e_so_eles(pasta):
    tabela = ler_resultados(pasta)

    assert list(tabela.columns) == COLUNAS_PODER
    assert set(tabela["situacao"]) == {"base", "nova"}
    assert len(tabela) == 16


def test_pasta_sem_resultados_devolve_tabela_vazia(tmp_path):
    tabela = ler_resultados(tmp_path)

    assert tabela.empty
    assert list(tabela.columns) == COLUNAS_PODER


def test_g4_tem_paineis_eixos_legenda_cores_e_linhas_de_referencia(pasta):
    figura = figura_g4(ler_resultados(pasta))

    assert "G4" in figura.layout.title.text
    assert "efeito" in figura.layout.xaxis.title.text.lower()
    assert "adimensional" in figura.layout.xaxis.title.text.lower()
    assert "%" in figura.layout.yaxis.title.text
    curvas = [serie for serie in figura.data if serie.type == "scatter"]
    assert len(curvas) == 4
    assert {serie.line.color for serie in curvas} == set(CORES.values())
    assert {serie.name for serie in curvas} == {"Pearson", "Spearman"}
    assert {anotacao.text for anotacao in figura.layout.annotations} >= {"Situação: base", "Situação: nova"}
    referencias = {(forma.y0, forma.y1) for forma in figura.layout.shapes}
    assert any(y0 == pytest.approx(5) and y1 == pytest.approx(5) for y0, y1 in referencias)
    assert any(y0 == pytest.approx(80) and y1 == pytest.approx(80) for y0, y1 in referencias)


def test_texto_compara_vantagens_e_detecta_mudanca_de_lado(pasta):
    texto = texto_g4(ler_resultados(pasta))

    assert 2 <= texto.count(". ") + 1 <= 4
    assert "Pearson" in texto
    assert "Spearman" in texto
    assert "3 pontos percentuais" in texto
    assert "entre 0,10 e 0,30" in texto
    assert "em nova, não houve inversão" in texto


def test_tabela_tem_uma_linha_por_ponto_de_cada_curva(pasta):
    tabela = tabela_g4(ler_resultados(pasta))

    assert len(tabela) == 16
    assert set(tabela["Teste"]) == {"Pearson", "Spearman"}


def test_render_orienta_rodar_pipeline_quando_nao_ha_csv(tmp_path, monkeypatch):
    mensagens = []
    monkeypatch.setattr(secao_5_poder.st, "header", lambda *args, **kwargs: None)
    monkeypatch.setattr(secao_5_poder.st, "info", lambda mensagem: mensagens.append(mensagem))

    secao_5_poder.render(tmp_path)

    assert len(mensagens) == 1
    assert "run_all.py" in mensagens[0]


def test_dashboard_encontra_a_secao_5():
    secao = next(secao for secao in SECOES if secao.numero == 5)
    arquivo = encontrar_arquivo(secao)

    assert isinstance(arquivo, Path)
    assert arquivo.name == "secao_5_poder.py"

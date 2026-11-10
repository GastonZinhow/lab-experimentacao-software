from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip("streamlit")

from dashboard import DASHBOARD_LOCAL, PROJETOS_PADRAO, SECOES, encontrar_arquivo
from secoes import secao_7_conclusao
from secoes.secao_7_conclusao import carregar_resultados, resumir_conclusao


@pytest.fixture
def pasta(tmp_path):
    erros = {
        "base": (0.0592, 0.0558),
        "normal": (0.0535, 0.0541),
        "outliers": (0.0600, 0.0518),
    }
    poderes = {
        "base": (0.4227, 0.6360),
        "normal": (0.8269, 0.7752),
        "outliers": (0.2330, 0.5127),
    }
    for situacao, (pearson, spearman) in erros.items():
        pd.DataFrame([
            {"situacao": situacao, "teste": "pearson", "n": 30, "alfa": 0.05,
             "repeticoes": 10_000, "proporcao_rejeicao": pearson},
            {"situacao": situacao, "teste": "spearman", "n": 30, "alfa": 0.05,
             "repeticoes": 10_000, "proporcao_rejeicao": spearman},
        ]).to_csv(tmp_path / f"erro_tipo1_{situacao}.csv", index=False)
    for situacao, (pearson, spearman) in poderes.items():
        pd.DataFrame([
            {"situacao": situacao, "teste": "pearson", "n": 30, "alfa": 0.05,
             "repeticoes": 10_000, "proporcao_rejeicao": pearson, "efeito": 0.5},
            {"situacao": situacao, "teste": "spearman", "n": 30, "alfa": 0.05,
             "repeticoes": 10_000, "proporcao_rejeicao": spearman, "efeito": 0.5},
        ]).to_csv(tmp_path / f"poder_{situacao}.csv", index=False)
    return tmp_path


def test_conclusao_usa_resultados_finais_e_faz_recomendacao(pasta):
    erro_tipo1, poder = carregar_resultados(pasta)
    textos = resumir_conclusao(erro_tipo1, poder)

    assert "63,60%" in textos["expectativa"]
    assert "42,27%" in textos["expectativa"]
    assert "82,69%" in textos["contraste"]
    assert "51,27%" in textos["contraste"]
    assert "recomendamos Spearman" in textos["recomendacao"]
    assert "aproximadamente normais" in textos["mudanca"]
    assert "30 classes" in textos["limitacao"]


def test_render_orienta_rodar_pipeline_quando_faltam_resultados(tmp_path, monkeypatch):
    mensagens = []
    monkeypatch.setattr(secao_7_conclusao.st, "header", lambda *args, **kwargs: None)
    monkeypatch.setattr(secao_7_conclusao.st, "info", lambda mensagem: mensagens.append(mensagem))

    secao_7_conclusao.render(tmp_path)

    assert len(mensagens) == 1
    assert "run_all.py" in mensagens[0]


def test_dashboard_encontra_secao_7_e_tem_links_padrao():
    secao = next(secao for secao in SECOES if secao.numero == 7)
    arquivo = encontrar_arquivo(secao)

    assert isinstance(arquivo, Path)
    assert arquivo.name == "secao_7_conclusao.py"
    assert DASHBOARD_LOCAL == "http://localhost:8501"
    assert PROJETOS_PADRAO.endswith("/projects")

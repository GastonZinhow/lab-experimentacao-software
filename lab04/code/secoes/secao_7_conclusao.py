"""Seção 7 do dashboard: síntese das expectativas, resultados e recomendação."""
from pathlib import Path

import pandas as pd
import streamlit as st

from simulacao import PASTA_RESULTADOS


def _ler_padrao(pasta, padrao):
    arquivos = sorted(Path(pasta).glob(padrao))
    if not arquivos:
        return pd.DataFrame()
    return pd.concat([pd.read_csv(arquivo) for arquivo in arquivos], ignore_index=True)


def carregar_resultados(pasta=PASTA_RESULTADOS):
    """Lê os resultados finais usados na conclusão."""
    return _ler_padrao(pasta, "erro_tipo1_*.csv"), _ler_padrao(pasta, "poder_*.csv")


def _percentual(valor):
    return f"{100 * valor:.2f}%".replace(".", ",")


def _erro(erro_tipo1, situacao, teste):
    linha = erro_tipo1[(erro_tipo1["situacao"] == situacao) & (erro_tipo1["teste"] == teste)]
    return float(linha["proporcao_rejeicao"].iloc[0])


def _poder_maximo(poder, situacao, teste):
    linhas = poder[(poder["situacao"] == situacao) & (poder["teste"] == teste)]
    efeito = float(linhas["efeito"].max())
    valor = float(linhas.loc[linhas["efeito"] == efeito, "proporcao_rejeicao"].iloc[0])
    return efeito, valor


def resumir_conclusao(erro_tipo1, poder):
    """Produz os textos finais diretamente dos CSVs de G3 e G4."""
    efeito, base_pearson = _poder_maximo(poder, "base", "pearson")
    _, base_spearman = _poder_maximo(poder, "base", "spearman")
    _, normal_pearson = _poder_maximo(poder, "normal", "pearson")
    _, normal_spearman = _poder_maximo(poder, "normal", "spearman")
    _, outliers_pearson = _poder_maximo(poder, "outliers", "pearson")
    _, outliers_spearman = _poder_maximo(poder, "outliers", "spearman")
    erro_base_pearson = _erro(erro_tipo1, "base", "pearson")
    erro_base_spearman = _erro(erro_tipo1, "base", "spearman")

    return {
        "expectativa": (
            "Esperávamos que o Spearman fosse mais confiável nos dados assimétricos do KC1. A expectativa foi "
            f"confirmada principalmente nos efeitos maiores: na situação base e efeito {str(efeito).replace('.', ',')}, "
            f"o poder foi {_percentual(base_spearman)} no Spearman contra {_percentual(base_pearson)} no Pearson; "
            f"sob H₀, o Spearman também ficou mais perto de 5% ({_percentual(erro_base_spearman)} contra "
            f"{_percentual(erro_base_pearson)})."
        ),
        "contraste": (
            "O resultado não é uma vitória universal do Spearman. Na situação normal, onde a relação é linear e "
            f"os pressupostos do Pearson valem, o Pearson chegou a {_percentual(normal_pearson)} de poder contra "
            f"{_percentual(normal_spearman)}; com outliers independentes, o quadro se inverteu e o Spearman chegou a "
            f"{_percentual(outliers_spearman)} contra {_percentual(outliers_pearson)}."
        ),
        "recomendacao": (
            "Para dados como os do KC1 — assimétricos, com muitos empates em zero e módulos extremos — recomendamos "
            "Spearman como análise principal e Pearson como comparação de sensibilidade."
        ),
        "mudanca": (
            "A escolha mudaria para Pearson se os dados fossem aproximadamente normais, a associação fosse linear e "
            "não houvesse outliers influentes; também mudaria se o objetivo científico fosse medir especificamente a "
            "força de uma relação linear nos valores, e não apenas uma tendência monotônica."
        ),
        "limitacao": (
            "A principal limitação é externa: o gerador foi calibrado com apenas 30 classes de um único sistema. "
            "Os resultados mostram o comportamento dos testes neste cenário, mas não garantem a mesma vantagem em "
            "outros projetos, tamanhos de amostra ou processos de registro de defeitos."
        ),
    }


def render(pasta=PASTA_RESULTADOS):
    st.header("7. Conclusão")
    erro_tipo1, poder = carregar_resultados(pasta)
    if erro_tipo1.empty or poder.empty:
        st.info("Ainda faltam resultados para a conclusão. Rode `python lab04/code/run_all.py`.")
        return

    textos = resumir_conclusao(erro_tipo1, poder)
    st.subheader("O que esperávamos × o que encontramos")
    st.write(textos["expectativa"])
    st.write(textos["contraste"])
    st.subheader("Recomendação")
    st.success(textos["recomendacao"])
    st.subheader("Quando a escolha mudaria?")
    st.write(textos["mudanca"])
    st.caption(textos["limitacao"])

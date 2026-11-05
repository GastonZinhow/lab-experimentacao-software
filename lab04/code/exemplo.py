"""Conjunto simulado de exemplo, usado na interpretação dos testes e no G2."""
import numpy as np

from gerador import carregar_parametros, gerar
from testes import aplicar_testes

SITUACAO = "base"
N = 30  # mesmo tamanho da amostra real do KC1
SEMENTE = 42


def efeito_do_exemplo():
    """Efeito calibrado na amostra real: o exemplo imita uma nova coleta de 30 classes."""
    return carregar_parametros()["associacao"]["efeito_calibrado"]


def rodar_exemplo(gerar=gerar, aplicar_testes=aplicar_testes, efeito=None, n=N, semente=SEMENTE):
    """Gera o conjunto de exemplo com semente fixa e aplica os dois testes.

    `gerar` e `aplicar_testes` são parâmetros, como no combinado do grupo, para
    permitir trocar qualquer uma das peças sem mexer neste código.
    """
    efeito = efeito_do_exemplo() if efeito is None else efeito
    dados = gerar(SITUACAO, efeito, n, np.random.default_rng(semente))
    return dados, aplicar_testes(dados)

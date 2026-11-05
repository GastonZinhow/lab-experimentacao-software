"""Gerador dos dados simulados de LOC e nº de defeitos por módulo."""
import json
from functools import lru_cache

from dados_reais import ARQUIVO_PARAMETROS, amostrar_copula

SITUACOES = ("base",)


@lru_cache(maxsize=1)
def carregar_parametros():
    return json.loads(ARQUIVO_PARAMETROS.read_text(encoding="utf-8"))


def gerar(situacao, efeito, n, rng):
    """Devolve `n` módulos simulados com as chaves `loc` e `defeitos`.

    `efeito` é a força da associação, entre -1 e 1 (exclusive). Com `efeito = 0`
    as variáveis são independentes, ou seja, H₀ é verdadeira.
    """
    if situacao not in SITUACOES:
        raise ValueError(f"Situação desconhecida: {situacao!r}. Opções: {SITUACOES}")
    if not -1 < efeito < 1:
        raise ValueError(f"`efeito` deve ficar entre -1 e 1 (exclusive), recebido: {efeito}")

    parametros = carregar_parametros()
    loc, defeitos = amostrar_copula(
        parametros["loc"]["mu"],
        parametros["loc"]["sigma"],
        parametros["defeitos"]["media"],
        parametros["defeitos"]["k"],
        efeito,
        n,
        rng,
    )
    return {"loc": loc, "defeitos": defeitos}

"""Gerador dos dados simulados de LOC e nº de defeitos por módulo.

Situações (Q3):

- `base`: margens calibradas na amostra real do KC1 (LOC lognormal e defeitos
  binomial negativa), ligadas por uma cópula gaussiana. Já é muito assimétrica
  e tem muitos empates em zero defeito.
- `normal`: normal bivariada padrão, em que os pressupostos do teste de Pearson
  valem. É o ponto de comparação, em unidades padronizadas, sem significado de
  LOC ou de defeitos.
- `outliers`: a `base` com módulos atípicos. Cada valor de LOC e cada valor de
  defeitos, de forma independente, tem 5% de chance de ser empurrado 2 desvios
  para a cauda na escala latente (LOC cerca de 18 vezes maior; defeitos perto
  do percentil 98). Como a contaminação de uma variável não depende da outra,
  com `efeito = 0` as variáveis continuam independentes e H₀ continua verdadeira.
"""
import json
from functools import lru_cache

from dados_reais import ARQUIVO_PARAMETROS, normais_latentes, transformar_latentes

SITUACOES = ("base", "normal", "outliers")

PROPORCAO_OUTLIERS = 0.05
DESLOCAMENTO_OUTLIERS = 2.0


@lru_cache(maxsize=1)
def carregar_parametros():
    return json.loads(ARQUIVO_PARAMETROS.read_text(encoding="utf-8"))


def _margens_calibradas(z_loc, z_defeitos):
    parametros = carregar_parametros()
    return transformar_latentes(
        z_loc,
        z_defeitos,
        parametros["loc"]["mu"],
        parametros["loc"]["sigma"],
        parametros["defeitos"]["media"],
        parametros["defeitos"]["k"],
    )


def gerar(situacao, efeito, n, rng):
    """Devolve `n` módulos simulados com as chaves `loc` e `defeitos`.

    `efeito` é a força da associação, entre -1 e 1 (exclusive). Com `efeito = 0`
    as variáveis são independentes, ou seja, H₀ é verdadeira, em qualquer situação.
    """
    if situacao not in SITUACOES:
        raise ValueError(f"Situação desconhecida: {situacao!r}. Opções: {SITUACOES}")
    if not -1 < efeito < 1:
        raise ValueError(f"`efeito` deve ficar entre -1 e 1 (exclusive), recebido: {efeito}")

    z_loc, z_defeitos = normais_latentes(efeito, n, rng)
    if situacao == "normal":
        return {"loc": z_loc, "defeitos": z_defeitos}
    if situacao == "outliers":
        z_loc = z_loc + DESLOCAMENTO_OUTLIERS * (rng.random(n) < PROPORCAO_OUTLIERS)
        z_defeitos = z_defeitos + DESLOCAMENTO_OUTLIERS * (rng.random(n) < PROPORCAO_OUTLIERS)
    loc, defeitos = _margens_calibradas(z_loc, z_defeitos)
    return {"loc": loc, "defeitos": defeitos}

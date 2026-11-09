"""Testes de correlação de Pearson e de Spearman aplicados a um conjunto de módulos."""
import numpy as np
from scipy import stats

ALFA = 0.05
TESTES = ("pearson", "spearman")

# Limiares de Cohen (1988) para |r|, usados também para |ρ|.
LIMIARES_MAGNITUDE = ((0.1, "desprezível"), (0.3, "fraca"), (0.5, "moderada"), (np.inf, "forte"))


def aplicar_testes(dados):
    """Aplica os dois testes, bicaudais, a `dados["loc"]` × `dados["defeitos"]`.

    Devolve `{"pearson": {...}, "spearman": {...}}`, cada um com `coeficiente`
    (r ou ρ, que já é o tamanho do efeito) e `p_valor`.
    """
    loc = np.asarray(dados["loc"], dtype=float)
    defeitos = np.asarray(dados["defeitos"], dtype=float)
    if len(loc) != len(defeitos):
        raise ValueError("`loc` e `defeitos` precisam ter o mesmo tamanho")
    if len(loc) < 3:
        raise ValueError("São necessários pelo menos 3 módulos para testar a correlação")

    pearson = stats.pearsonr(loc, defeitos)
    spearman = stats.spearmanr(loc, defeitos)
    return {
        "pearson": {"coeficiente": float(pearson.statistic), "p_valor": float(pearson.pvalue)},
        "spearman": {"coeficiente": float(spearman.statistic), "p_valor": float(spearman.pvalue)},
    }


def _correlacao_por_linha(x, y):
    x = x - x.mean(axis=1, keepdims=True)
    y = y - y.mean(axis=1, keepdims=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        r = (x * y).sum(axis=1) / np.sqrt((x**2).sum(axis=1) * (y**2).sum(axis=1))
    return np.clip(r, -1.0, 1.0)


def _p_valor_bicaudal(coeficientes, n):
    with np.errstate(invalid="ignore", divide="ignore"):
        t = coeficientes * np.sqrt((n - 2) / ((1 - coeficientes) * (1 + coeficientes)))
    return 2 * stats.t.sf(np.abs(t), n - 2)


def aplicar_testes_em_lote(loc, defeitos):
    """Mesmo cálculo de `aplicar_testes`, para muitos conjuntos de uma vez.

    `loc` e `defeitos` têm forma (conjuntos, n): cada linha é um conjunto.
    Devolve o mesmo dicionário de `aplicar_testes`, com arrays no lugar de
    números. Os p-valores usam a t com n − 2 graus de liberdade, que é a conta
    exata do `pearsonr` e a mesma aproximação do `spearmanr`. Um conjunto com
    uma variável constante não tem correlação definida e recebe `nan`, como no SciPy.
    """
    loc = np.atleast_2d(np.asarray(loc, dtype=float))
    defeitos = np.atleast_2d(np.asarray(defeitos, dtype=float))
    if loc.shape != defeitos.shape:
        raise ValueError("`loc` e `defeitos` precisam ter a mesma forma")
    n = loc.shape[1]
    if n < 3:
        raise ValueError("São necessários pelo menos 3 módulos para testar a correlação")

    r = _correlacao_por_linha(loc, defeitos)
    rho = _correlacao_por_linha(stats.rankdata(loc, axis=1), stats.rankdata(defeitos, axis=1))
    return {
        "pearson": {"coeficiente": r, "p_valor": _p_valor_bicaudal(r, n)},
        "spearman": {"coeficiente": rho, "p_valor": _p_valor_bicaudal(rho, n)},
    }


def classificar_magnitude(coeficiente):
    """Classifica |r| ou |ρ| como desprezível, fraca, moderada ou forte (Cohen, 1988)."""
    absoluto = abs(coeficiente)
    return next(rotulo for limite, rotulo in LIMIARES_MAGNITUDE if absoluto < limite)


def estatistica_t(coeficiente, n):
    """Estatística t = r·√((n − 2) / (1 − r²)), que segue a t com n − 2 g.l. sob H₀."""
    return coeficiente * np.sqrt((n - 2) / (1 - coeficiente**2))


def resumir(resultados, alfa=ALFA):
    """Acrescenta a magnitude e a decisão (rejeita H₀ ou não) ao resultado de `aplicar_testes`."""
    return {
        teste: {
            **valores,
            "magnitude": classificar_magnitude(valores["coeficiente"]),
            "rejeita_h0": valores["p_valor"] < alfa,
        }
        for teste, valores in resultados.items()
    }

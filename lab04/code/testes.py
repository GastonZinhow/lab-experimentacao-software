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

"""Testes entre grupos e tamanhos de efeito da RQ06 (Issue #67)."""

from typing import Callable, Dict, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy.stats import bootstrap, kruskal, mannwhitneyu, spearmanr

ROTULOS_QUARTIS = ["Q1", "Q2", "Q3", "Q4"]
N_REAMOSTRAS = 2000
SEMENTE = 42


def epsilon_quadrado(h: float, n: int) -> float:
    """ε² = H / (n − 1) do Kruskal-Wallis, com n = total de observações."""
    if n < 2:
        raise ValueError("ε² exige pelo menos duas observações")
    return h / (n - 1)


def cliffs_delta(x: Sequence[float], y: Sequence[float]) -> float:
    """
    Cliff's delta δ = 2·U₁ / (n₁·n₂) − 1, com U₁ de mannwhitneyu(x, y).
    Positivo quando os valores de x tendem a ser maiores que os de y.
    """
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(x) == 0 or len(y) == 0:
        raise ValueError("Cliff's delta exige dois grupos não vazios")
    u1 = mannwhitneyu(x, y, alternative="two-sided").statistic
    return 2 * u1 / (len(x) * len(y)) - 1


def interpretar_cliffs_delta(delta: float) -> str:
    """Romano et al. (2006): |δ| < 0,147; < 0,33; < 0,474; ≥ 0,474."""
    d = abs(delta)
    if d < 0.147:
        return "desprezível"
    if d < 0.33:
        return "pequeno"
    if d < 0.474:
        return "médio"
    return "grande"


def interpretar_epsilon_quadrado(eps2: float) -> str:
    """Tomczak e Tomczak (2014): < 0,01; < 0,08; < 0,26; ≥ 0,26."""
    if eps2 < 0.01:
        return "desprezível"
    if eps2 < 0.08:
        return "pequeno"
    if eps2 < 0.26:
        return "médio"
    return "grande"


def quartis(serie: pd.Series) -> pd.Series:
    """Converte um fator numérico em grupos Q1 (menores) a Q4 (maiores)."""
    return pd.qcut(serie, 4, labels=ROTULOS_QUARTIS)


def intervalo_bootstrap(
    estatistica: Callable[..., float],
    amostras: Sequence[Sequence[float]],
    pareado: bool = False,
    n_reamostras: int = N_REAMOSTRAS,
    confianca: float = 0.95,
    semente: int = SEMENTE,
) -> Tuple[float, float]:
    """
    Intervalo de confiança percentil por bootstrap. Sem `pareado`, cada amostra
    é reamostrada separadamente (estratificado por grupo); com `pareado`, as
    amostras são reamostradas juntas, preservando os pares (x_i, y_i).
    """
    res = bootstrap(
        [np.asarray(a, dtype=float) for a in amostras], estatistica,
        paired=pareado, vectorized=False, n_resamples=n_reamostras,
        confidence_level=confianca, method="percentile",
        rng=np.random.default_rng(semente),
    )
    return float(res.confidence_interval.low), float(res.confidence_interval.high)


def ic_spearman(x: Sequence[float], y: Sequence[float], **kwargs) -> Tuple[float, float]:
    """IC de 95% do ρ de Spearman, reamostrando os repositórios (pares)."""
    return intervalo_bootstrap(lambda a, b: spearmanr(a, b).statistic, [x, y], pareado=True, **kwargs)


def ic_epsilon_quadrado(grupos: Sequence[Sequence[float]], **kwargs) -> Tuple[float, float]:
    """IC de 95% do ε² do Kruskal-Wallis, reamostrando dentro de cada grupo."""
    n = sum(len(g) for g in grupos)
    return intervalo_bootstrap(lambda *gs: epsilon_quadrado(kruskal(*gs).statistic, n), grupos, **kwargs)


def ic_cliffs_delta(x: Sequence[float], y: Sequence[float], **kwargs) -> Tuple[float, float]:
    """IC de 95% do Cliff's delta, reamostrando cada grupo separadamente."""
    return intervalo_bootstrap(cliffs_delta, [x, y], **kwargs)


def comparar_grupos(grupos: Dict[str, Sequence[float]]) -> Dict[str, object]:
    """
    Compara a distribuição de uma métrica entre grupos (valores ausentes já
    removidos). Com 3 ou mais grupos usa Kruskal-Wallis e ε²; com 2, usa
    Mann-Whitney bilateral e Cliff's delta (primeiro grupo contra o segundo).
    """
    nomes = [g for g, v in grupos.items() if len(v) > 0]
    valores = [np.asarray(grupos[g], dtype=float) for g in nomes]
    n = sum(len(v) for v in valores)
    if len(nomes) < 2:
        raise ValueError("A comparação exige pelo menos dois grupos não vazios")

    if len(nomes) == 2:
        res = mannwhitneyu(valores[0], valores[1], alternative="two-sided")
        efeito = cliffs_delta(valores[0], valores[1])
        return {
            "teste": "Mann-Whitney", "estatistica": float(res.statistic),
            "p": float(res.pvalue), "n": n, "grupos": len(nomes),
            "efeito": "Cliff's delta", "tamanho_efeito": efeito,
            "interpretacao": interpretar_cliffs_delta(efeito),
        }

    res = kruskal(*valores)
    efeito = epsilon_quadrado(res.statistic, n)
    return {
        "teste": "Kruskal-Wallis", "estatistica": float(res.statistic),
        "p": float(res.pvalue), "n": n, "grupos": len(nomes),
        "efeito": "ε²", "tamanho_efeito": efeito,
        "interpretacao": interpretar_epsilon_quadrado(efeito),
    }

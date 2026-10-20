"""Funções da análise de sensibilidade das classificações DORA (RQ07)."""

from typing import Iterable, Optional, Sequence

from sklearn.metrics import cohen_kappa_score

from metrics.classificacao import ELITE, HIGH, LOW, MEDIUM, categorias_repositorio


# A ordem precisa ser explícita: o padrão alfabético do sklearn colocaria Low
# entre High e Medium e produziria pesos incorretos para a escala ordinal.
ORDEM_CATEGORIAS = (ELITE, HIGH, MEDIUM, LOW)


def classificar_combinacao(
    deploy_frequency: Optional[float],
    lead_time_horas: Optional[float],
    cfr: Optional[float],
    tempo_recuperacao_horas: Optional[float],
):
    """Classifica as quatro métricas e a categoria geral de uma combinação."""
    return categorias_repositorio(
        deploy_frequency,
        lead_time_horas,
        cfr,
        tempo_recuperacao_horas,
    )


def comparar_classificacoes(
    classificacao_a: Sequence[Optional[str]] | Iterable[Optional[str]],
    classificacao_b: Sequence[Optional[str]] | Iterable[Optional[str]],
):
    """Calcula mudança e kappa linear entre duas classificações ordinais.

    Pares em que ao menos uma categoria está ausente ficam fora da comparação.
    """
    valores_a, valores_b = list(classificacao_a), list(classificacao_b)
    if len(valores_a) != len(valores_b):
        raise ValueError("As classificações precisam ter o mesmo tamanho")

    pares = [(a, b) for a, b in zip(valores_a, valores_b) if a is not None and b is not None]
    if not pares:
        return {
            "n_repositorios": 0,
            "n_mudaram": 0,
            "percentual_mudanca": None,
            "kappa_ponderado_linear": None,
            "n_mudancas_adjacentes": 0,
            "n_mudancas_distantes": 0,
        }

    a_validos, b_validos = zip(*pares)
    posicao = {categoria: i for i, categoria in enumerate(ORDEM_CATEGORIAS)}
    distancias = [abs(posicao[a] - posicao[b]) for a, b in pares]
    n_mudaram = sum(distancia > 0 for distancia in distancias)

    return {
        "n_repositorios": len(pares),
        "n_mudaram": n_mudaram,
        "percentual_mudanca": 100 * n_mudaram / len(pares),
        "kappa_ponderado_linear": float(
            cohen_kappa_score(
                a_validos,
                b_validos,
                labels=list(ORDEM_CATEGORIAS),
                weights="linear",
            )
        ),
        "n_mudancas_adjacentes": sum(distancia == 1 for distancia in distancias),
        "n_mudancas_distantes": sum(distancia >= 2 for distancia in distancias),
    }

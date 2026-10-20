"""Deployment rework rate (RQ08, Issue #69)."""

from typing import Optional


def calcular_rework_rate(
    releases_corretivas: Optional[int], total_releases: Optional[int]
) -> Optional[float]:
    """Proporção de releases publicadas classificadas como corretivas.

    Retorna ``None`` quando não há releases no denominador. As contagens são
    validadas para impedir taxas negativas ou acima de 100%.
    """
    if releases_corretivas is None or total_releases is None or total_releases == 0:
        return None
    if total_releases < 0 or releases_corretivas < 0 or releases_corretivas > total_releases:
        raise ValueError("Contagens de releases inválidas para a rework rate")
    return releases_corretivas / total_releases

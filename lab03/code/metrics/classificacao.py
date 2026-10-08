import math
from statistics import median
from typing import Optional

ELITE, HIGH, MEDIUM, LOW = "Elite", "High", "Medium", "Low"
NOTAS = {ELITE: 4, HIGH: 3, MEDIUM: 2, LOW: 1}
CATEGORIA_POR_NOTA = {nota: cat for cat, nota in NOTAS.items()}

# "1 deploy por mês" expresso em deploys por semana (12 meses ≈ 52,18 semanas)
UM_POR_MES_EM_SEMANAS = 12 / (365.25 / 7)


def classificar_deploy_frequency(releases_por_semana: Optional[float]) -> Optional[str]:
    """Elite ≥ 7/sem; High ≥ 1/sem; Medium ≥ 1/mês; Low < 1/mês."""
    if releases_por_semana is None:
        return None
    if releases_por_semana >= 7:
        return ELITE
    if releases_por_semana >= 1:
        return HIGH
    if releases_por_semana >= UM_POR_MES_EM_SEMANAS:
        return MEDIUM
    return LOW


def classificar_lead_time(horas: Optional[float]) -> Optional[str]:
    """Elite < 1 dia; High < 1 semana; Medium < 30 dias; Low ≥ 30 dias."""
    if horas is None:
        return None
    if horas < 24:
        return ELITE
    if horas < 7 * 24:
        return HIGH
    if horas < 30 * 24:
        return MEDIUM
    return LOW


def classificar_cfr(taxa: Optional[float]) -> Optional[str]:
    """CFR como fração (0 a 1). Elite ≤ 15%; High ≤ 30%; Medium ≤ 45%; Low > 45%."""
    if taxa is None:
        return None
    if taxa <= 0.15:
        return ELITE
    if taxa <= 0.30:
        return HIGH
    if taxa <= 0.45:
        return MEDIUM
    return LOW


def classificar_tempo_recuperacao(horas: Optional[float]) -> Optional[str]:
    """Elite < 1 hora; High < 1 dia; Medium < 1 semana; Low ≥ 1 semana."""
    if horas is None:
        return None
    if horas < 1:
        return ELITE
    if horas < 24:
        return HIGH
    if horas < 7 * 24:
        return MEDIUM
    return LOW


def classificacao_geral(*categorias: Optional[str]) -> Optional[str]:
    """
    Categoria geral do repositório: mediana das notas (Elite=4, High=3, Medium=2,
    Low=1), arredondada para baixo. Métricas sem valor (None) não entram na mediana;
    retorna None se nenhuma métrica tiver valor.
    Ex.: (Elite, High, High, Low) → notas (4, 3, 3, 1) → mediana 3 → High.
    """
    notas = [NOTAS[c] for c in categorias if c is not None]
    if not notas:
        return None
    return CATEGORIA_POR_NOTA[math.floor(median(notas))]


def classificar_repositorio(
    deploy_frequency: Optional[float],
    lead_time_horas: Optional[float],
    cfr: Optional[float],
    tempo_recuperacao_horas: Optional[float],
) -> Optional[str]:
    """Atalho: classifica as quatro métricas e devolve a categoria geral."""
    return classificacao_geral(
        classificar_deploy_frequency(deploy_frequency),
        classificar_lead_time(lead_time_horas),
        classificar_cfr(cfr),
        classificar_tempo_recuperacao(tempo_recuperacao_horas),
    )

import pytest

from metrics.classificacao import (
    ELITE, HIGH, MEDIUM, LOW,
    UM_POR_MES_EM_SEMANAS,
    classificacao_geral,
    classificar_cfr,
    classificar_deploy_frequency,
    classificar_lead_time,
    classificar_repositorio,
    classificar_tempo_recuperacao,
)

DIA = 24.0
SEMANA = 7 * DIA


# ==========================================
# Faixas por métrica, incluindo valores exatamente nos limites
# ==========================================

@pytest.mark.parametrize("valor, esperado", [
    (10.0, ELITE),
    (7.0, ELITE),                         # limite: ≥ 7 por semana
    (6.99, HIGH),
    (1.0, HIGH),                          # limite: ≥ 1 por semana
    (0.99, MEDIUM),
    (UM_POR_MES_EM_SEMANAS, MEDIUM),      # limite: ≥ 1 por mês
    (UM_POR_MES_EM_SEMANAS - 1e-9, LOW),
    (0.0, LOW),
])
def test_classificar_deploy_frequency(valor, esperado):
    assert classificar_deploy_frequency(valor) == esperado


@pytest.mark.parametrize("horas, esperado", [
    (0.0, ELITE),
    (DIA - 0.01, ELITE),
    (DIA, HIGH),                 # limite: 1 dia já é High
    (SEMANA - 0.01, HIGH),
    (SEMANA, MEDIUM),            # limite: 1 semana já é Medium
    (30 * DIA - 0.01, MEDIUM),
    (30 * DIA, LOW),             # limite: 30 dias já é Low
    (400 * DIA, LOW),
])
def test_classificar_lead_time(horas, esperado):
    assert classificar_lead_time(horas) == esperado


@pytest.mark.parametrize("taxa, esperado", [
    (0.0, ELITE),
    (0.15, ELITE),       # limite: ≤ 15%
    (0.1501, HIGH),
    (0.30, HIGH),        # limite: ≤ 30%
    (3 / 10, HIGH),
    (0.3001, MEDIUM),
    (0.45, MEDIUM),      # limite: ≤ 45%
    (9 / 20, MEDIUM),
    (0.4501, LOW),
    (1.0, LOW),
])
def test_classificar_cfr(taxa, esperado):
    assert classificar_cfr(taxa) == esperado


@pytest.mark.parametrize("horas, esperado", [
    (0.5, ELITE),
    (1.0, HIGH),           # limite: 1 hora já é High
    (DIA - 0.01, HIGH),
    (DIA, MEDIUM),         # limite: 1 dia já é Medium
    (SEMANA - 0.01, MEDIUM),
    (SEMANA, LOW),         # limite: 1 semana já é Low
])
def test_classificar_tempo_recuperacao(horas, esperado):
    assert classificar_tempo_recuperacao(horas) == esperado


@pytest.mark.parametrize("funcao", [
    classificar_deploy_frequency, classificar_lead_time, classificar_cfr, classificar_tempo_recuperacao,
])
def test_metrica_ausente_nao_e_classificada(funcao):
    assert funcao(None) is None


# ==========================================
# Classificação geral
# ==========================================

def test_classificacao_geral_exemplo_enunciado():
    """Notas (4, 3, 3, 1) → mediana 3 → High."""
    assert classificacao_geral(ELITE, HIGH, HIGH, LOW) == HIGH


def test_classificacao_geral_arredonda_mediana_para_baixo():
    # (4, 4, 3, 3) → mediana 3,5 → 3 (High)
    assert classificacao_geral(ELITE, ELITE, HIGH, HIGH) == HIGH
    # (2, 2, 1, 1) → mediana 1,5 → 1 (Low)
    assert classificacao_geral(MEDIUM, MEDIUM, LOW, LOW) == LOW
    # (4, 4, 4, 1) → mediana 4 → Elite
    assert classificacao_geral(ELITE, ELITE, ELITE, LOW) == ELITE


def test_classificacao_geral_ignora_metricas_ausentes():
    # (4, 2, 1) → mediana 2 → Medium
    assert classificacao_geral(ELITE, None, MEDIUM, LOW) == MEDIUM
    assert classificacao_geral(None, None, None, None) is None


def test_classificar_repositorio_ponta_a_ponta():
    # DF 2/sem (High), LT 12h (Elite), CFR 20% (High), MTTR 10 dias (Low) → (3,4,3,1) → 3 → High
    assert classificar_repositorio(2.0, 12.0, 0.20, 10 * DIA) == HIGH

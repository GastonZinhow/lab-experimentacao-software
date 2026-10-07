import pytest
from metrics.cfr import calcular_cfr_a
from metrics.recovery import calcular_tempo_recuperacao

# ==========================================
# Testes de CFR (a)
# ==========================================

def test_cfr_a_calculo_basico():
    runs = [
        {"conclusion": "success"},
        {"conclusion": "failure"},
        {"conclusion": "cancelled"},  # Deve ignorar
        {"conclusion": "success"}
    ]
    # 1 falha / (2 sucessos + 1 falha) = 1/3 ≈ 0.3333
    assert calcular_cfr_a(runs) == pytest.approx(1 / 3)

def test_cfr_a_apenas_sucessos():
    runs = [{"conclusion": "success"}, {"conclusion": "success"}]
    assert calcular_cfr_a(runs) == 0.0

def test_cfr_a_apenas_falhas():
    runs = [{"conclusion": "failure"}, {"conclusion": "timed_out"}]
    assert calcular_cfr_a(runs) == 1.0

def test_cfr_a_sem_runs_validos():
    runs = [{"conclusion": "cancelled"}, {"conclusion": "skipped"}]
    assert calcular_cfr_a(runs) is None

def test_cfr_a_lista_vazia():
    assert calcular_cfr_a([]) is None


# ==========================================
# Testes de Tempo de Recuperação
# ==========================================

def test_recuperacao_exemplo_enunciado():
    """
    Exemplo do edital:
    09:00 success
    10:00 failure <- inicio
    10:30 failure
    11:15 success <- terminou 11:20
    Recuperação: 11:20 - 10:00 = 1h20 (1.3333h)
    """
    runs = [
        {"workflow_id": 1, "run_started_at": "2024-05-10T09:00:00Z", "updated_at": "2024-05-10T09:05:00Z", "conclusion": "success"},
        {"workflow_id": 1, "run_started_at": "2024-05-10T10:00:00Z", "updated_at": "2024-05-10T10:10:00Z", "conclusion": "failure"},
        {"workflow_id": 1, "run_started_at": "2024-05-10T10:30:00Z", "updated_at": "2024-05-10T10:40:00Z", "conclusion": "failure"},
        {"workflow_id": 1, "run_started_at": "2024-05-10T11:15:00Z", "updated_at": "2024-05-10T11:20:00Z", "conclusion": "success"}
    ]
    mediana, censura = calcular_tempo_recuperacao(runs)
    assert mediana == pytest.approx(1.3333, rel=1e-3)
    assert censura == 0.0

def test_recuperacao_caso_borda_cancelled_no_meio():
    """
    Garante que uma execução intermediária cancelada não interrompe
    nem impede o término do episódio de recuperação.
    """
    runs = [
        {"workflow_id": 1, "run_started_at": "2024-05-10T10:00:00Z", "updated_at": "2024-05-10T10:10:00Z", "conclusion": "failure"},
        {"workflow_id": 1, "run_started_at": "2024-05-10T10:20:00Z", "updated_at": "2024-05-10T10:25:00Z", "conclusion": "cancelled"},
        {"workflow_id": 1, "run_started_at": "2024-05-10T11:00:00Z", "updated_at": "2024-05-10T11:00:00Z", "conclusion": "success"}
    ]
    mediana, censura = calcular_tempo_recuperacao(runs)
    assert mediana == pytest.approx(1.0)
    assert censura == 0.0

def test_recuperacao_caso_borda_falha_nunca_recuperada_censura():
    """
    Falha que encerra a janela sem nenhum sucesso posterior deve ser marcada como censurada.
    """
    runs = [
        {"workflow_id": 1, "run_started_at": "2024-05-10T10:00:00Z", "updated_at": "2024-05-10T10:10:00Z", "conclusion": "failure"},
        {"workflow_id": 1, "run_started_at": "2024-05-10T10:30:00Z", "updated_at": "2024-05-10T10:40:00Z", "conclusion": "failure"}
    ]
    mediana, censura = calcular_tempo_recuperacao(runs)
    assert mediana is None
    assert censura == 1.0

def test_recuperacao_caso_borda_dois_workflows_intercalados():
    """
    Verifica se a intercalação de execuções de workflows diferentes não contamina os episódios.
    """
    runs = [
        # WF 1 falha às 10:00
        {"workflow_id": 1, "run_started_at": "2024-05-10T10:00:00Z", "updated_at": "2024-05-10T10:10:00Z", "conclusion": "failure"},
        # WF 2 roda e tem sucesso às 10:15 (não deve fechar o episódio do WF 1)
        {"workflow_id": 2, "run_started_at": "2024-05-10T10:05:00Z", "updated_at": "2024-05-10T10:15:00Z", "conclusion": "success"},
        # WF 1 recupera às 12:00 (duração = 2.0h)
        {"workflow_id": 1, "run_started_at": "2024-05-10T11:50:00Z", "updated_at": "2024-05-10T12:00:00Z", "conclusion": "success"}
    ]
    mediana, censura = calcular_tempo_recuperacao(runs)
    assert mediana == pytest.approx(2.0)
    assert censura == 0.0

def test_recuperacao_sem_episodios():
    runs = [
        {"workflow_id": 1, "run_started_at": "2024-05-10T09:00:00Z", "updated_at": "2024-05-10T09:10:00Z", "conclusion": "success"}
    ]
    mediana, censura = calcular_tempo_recuperacao(runs)
    assert mediana is None
    assert censura == 0.0
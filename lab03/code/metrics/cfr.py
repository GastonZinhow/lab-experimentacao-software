from typing import List, Dict, Any, Optional

def calcular_cfr_a(runs: List[Dict[str, Any]]) -> Optional[float]:
    """
    Calcula o Change Failure Rate (CFR) - Variante (a) Proxy de CI.
    Fórmula: nº de falhas ÷ (nº de falhas + nº de sucessos)
    Status considerados:
      - sucesso: conclusion == 'success'
      - falha: conclusion in ['failure', 'timed_out', 'startup_failure']
      - ignorar: 'cancelled', 'skipped', 'neutral', etc.
    Retorna float entre 0.0 e 1.0, ou None se não houver execuções válidas.
    """
    sucessos = 0
    falhas = 0

    for run in runs:
        # Dá suporte ao campo já mapeado ou ao campo bruto
        status = run.get("status_classificacao")
        conclusion = run.get("conclusion_original", run.get("conclusion"))

        if status == "sucesso" or conclusion == "success":
            sucessos += 1
        elif status == "falha" or conclusion in ["failure", "timed_out", "startup_failure"]:
            falhas += 1

    total_validos = sucessos + falhas
    if total_validos == 0:
        return None

    return falhas / total_validos
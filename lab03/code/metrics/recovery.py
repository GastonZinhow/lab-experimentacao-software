from datetime import datetime
from statistics import median
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict

def _parse_iso(dt_str: str) -> datetime:
    """Converte strings ISO-8601 em datetime UTC ciente de fuso."""
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))

def _normalizar_status(run: Dict[str, Any]) -> str:
    status = run.get("status_classificacao")
    if status:
        return status
    conc = run.get("conclusion_original", run.get("conclusion"))
    if conc == "success":
        return "sucesso"
    if conc in ["failure", "timed_out", "startup_failure"]:
        return "falha"
    return "ignorar"

def calcular_tempo_recuperacao(runs: List[Dict[str, Any]]) -> Tuple[Optional[float], float]:
    """
    Calcula:
      1. Mediana do tempo de recuperação (em horas) dos episódios concluídos.
      2. Proporção de episódios censurados (iniciados e não recuperados dentro da janela).
    Retorna: (mediana_horas, proporcao_censurados)
    """
    # Agrupa por workflow_id descartando execuções com status "ignorar"
    workflows = defaultdict(list)
    for r in runs:
        status_norm = _normalizar_status(r)
        if status_norm in ["sucesso", "falha"]:
            workflows[r["workflow_id"]].append({**r, "_status": status_norm})

    duracoes_horas: List[float] = []
    total_episodios = 0
    episodios_censurados = 0

    for wf_id, wf_runs in workflows.items():
        # Ordena cronologicamente por run_started_at
        wf_runs.sort(key=lambda x: _parse_iso(x["run_started_at"]))

        in_episode = False
        falha_inicio_dt: Optional[datetime] = None

        for r in wf_runs:
            status = r["_status"]

            if not in_episode:
                if status == "falha":
                    in_episode = True
                    falha_inicio_dt = _parse_iso(r["run_started_at"])
                    total_episodios += 1
            else:
                if status == "sucesso":
                    fim_dt = _parse_iso(r["updated_at"])
                    diff_hours = (fim_dt - falha_inicio_dt).total_seconds() / 3600.0
                    duracoes_horas.append(diff_hours)
                    in_episode = False
                    falha_inicio_dt = None

        # Se terminou a lista de runs do workflow ainda em episódio de falha -> Censurado
        if in_episode:
            episodios_censurados += 1

    prop_censurados = (episodios_censurados / total_episodios) if total_episodios > 0 else 0.0
    mediana_horas = median(duracoes_horas) if duracoes_horas else None

    return mediana_horas, prop_censurados
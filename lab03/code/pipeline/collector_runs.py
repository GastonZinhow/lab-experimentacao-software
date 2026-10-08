from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Any
from pipeline.client import GitHubClient

SUCCESS_SET = {"success"}
FAILURE_SET = {"failure", "timed_out", "startup_failure"}
IGNORE_SET = {"cancelled", "skipped", "neutral", "action_required", "stale", None, ""}

# Campos de cada run guardados no cache: a resposta completa tem ~17 KB por
# run (repositório, commit, autor...) e levou o cache a vários GB.
RUN_FIELDS = (
    "id", "workflow_id", "name", "event", "head_branch", "head_sha", "status",
    "conclusion", "run_attempt", "created_at", "run_started_at", "updated_at",
)


def slim_run(run: Dict[str, Any]) -> Dict[str, Any]:
    return {k: run.get(k) for k in RUN_FIELDS}


def classify_conclusion(conclusion: str) -> str:
    if conclusion in SUCCESS_SET:
        return "sucesso"
    if conclusion in FAILURE_SET:
        return "falha"
    return "ignorar"

def fetch_runs_range(client: GitHubClient, owner: str, repo: str, branch: str, start_dt: datetime, end_dt: datetime) -> List[Dict[str, Any]]:
    date_format = "%Y-%m-%d"
    created_str = f"{start_dt.strftime(date_format)}..{end_dt.strftime(date_format)}"
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
    params = {
        "branch": branch,
        "event": "push",
        "created": created_str,
        "per_page": 100
    }

    # Sonda com per_page=1 via cache: numa nova execução o total do mês
    # já está em disco e só as páginas ainda não baixadas vão para a API.
    data, _ = client.get_json(url, params={**params, "per_page": 1})
    total_count = data.get("total_count", 0)

    if total_count == 0:
        return []

    if total_count >= 1000:
        if end_dt.date() > start_dt.date():
            print(f"  [Aviso] Intervalo {created_str} atingiu teto ({total_count}). Subdividindo...")
            mid_dt = start_dt + (end_dt - start_dt) / 2
            return (fetch_runs_range(client, owner, repo, branch, start_dt, mid_dt) +
                    fetch_runs_range(client, owner, repo, branch, mid_dt + timedelta(days=1), end_dt))
        # Um único dia com mais de 1.000 runs: a API só devolve os 1.000 primeiros.
        print(f"  [Aviso] {owner}/{repo} {created_str}: {total_count} runs em um dia; "
              f"apenas 1000 disponiveis pela API")

    return client.paginate(url, params=params, transform_item=slim_run)

def collect_repo_runs(client: GitHubClient, owner: str, repo: str, branch: str, start_date: str, end_date: str) -> pd.DataFrame:
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    print(f"\n[Coletando] {owner}/{repo} (branch: {branch}) de {start_date} a {end_date}...")
    all_runs = []
    curr = start_dt

    while curr < end_dt:
        next_month = (curr.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        sub_end = min(next_month, end_dt)
        
        runs = fetch_runs_range(client, owner, repo, branch, curr, sub_end)
        all_runs.extend(runs)
        print(f"  -> {curr.strftime('%Y-%m-%d')} a {sub_end.strftime('%Y-%m-%d')}: {len(runs)} runs")
        
        curr = sub_end + timedelta(days=1)

    records = []
    for r in all_runs:
        conclusion_raw = r.get("conclusion")
        records.append({
            "repo": f"{owner}/{repo}",
            "run_id": r.get("id"),
            "workflow_id": r.get("workflow_id"),
            "run_started_at": r.get("run_started_at"),
            "updated_at": r.get("updated_at"),
            "conclusion_original": conclusion_raw,
            "status_classificacao": classify_conclusion(conclusion_raw)
        })

    df = pd.DataFrame(records)
    if not df.empty:
        df = df.drop_duplicates(subset=["run_id"])
    print(f"[Concluído] {owner}/{repo}: {len(df)} runs únicos extraídos.")
    return df
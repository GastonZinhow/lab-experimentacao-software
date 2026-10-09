from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

import pandas as pd

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

DATE_FORMAT = "%Y-%m-%d"
TETO_API = 1000  # a API só devolve os 1.000 primeiros resultados de uma consulta


def slim_run(run: Dict[str, Any]) -> Dict[str, Any]:
    return {k: run.get(k) for k in RUN_FIELDS}


def classify_conclusion(conclusion: str) -> str:
    if conclusion in SUCCESS_SET:
        return "sucesso"
    if conclusion in FAILURE_SET:
        return "falha"
    return "ignorar"


def _runs_url(owner: str, repo: str) -> str:
    return f"https://api.github.com/repos/{owner}/{repo}/actions/runs"


def _runs_params(branch: str, start_dt: datetime, end_dt: datetime) -> Dict[str, Any]:
    return {
        "branch": branch,
        "event": "push",
        "created": f"{start_dt.strftime(DATE_FORMAT)}..{end_dt.strftime(DATE_FORMAT)}",
        "per_page": 100,
    }


def _total_count(
    client: GitHubClient, owner: str, repo: str, branch: str,
    start_dt: datetime, end_dt: datetime,
) -> int:
    """
    Total de runs (push, branch, intervalo) com UMA chamada (per_page=1).
    Guarda só o total no cache; entradas antigas (resposta bruta) continuam
    funcionando, pois só `total_count` é lido.
    """
    params = {**_runs_params(branch, start_dt, end_dt), "per_page": 1}
    data, _ = client.get_json(
        _runs_url(owner, repo),
        params=params,
        transform=lambda d: {"total_count": d.get("total_count", 0)},
    )
    return data.get("total_count", 0)


def contar_runs_janela(
    client: GitHubClient, owner: str, repo: str, branch: str,
    start_date: str, end_date: str,
) -> int:
    """
    Limite superior das runs válidas da janela, com 1 chamada: conta TODAS as
    runs (qualquer conclusão) com os mesmos filtros da coleta. Se já for menor
    que `min_runs`, o repositório pode ser descartado sem baixar nada.
    """
    start_dt = datetime.strptime(start_date, DATE_FORMAT)
    end_dt = datetime.strptime(end_date, DATE_FORMAT)
    return _total_count(client, owner, repo, branch, start_dt, end_dt)


def fetch_runs_range(
    client: GitHubClient, owner: str, repo: str, branch: str,
    start_dt: datetime, end_dt: datetime,
) -> List[Dict[str, Any]]:
    created_str = f"{start_dt.strftime(DATE_FORMAT)}..{end_dt.strftime(DATE_FORMAT)}"
    url = _runs_url(owner, repo)
    params = _runs_params(branch, start_dt, end_dt)

    total_count = _total_count(client, owner, repo, branch, start_dt, end_dt)
    if total_count == 0:
        return []

    if total_count >= TETO_API:
        if (end_dt - start_dt).days > 1:
            print(f"  [Aviso] Intervalo {created_str} atingiu teto ({total_count}). Subdividindo...")
            mid_dt = start_dt + (end_dt - start_dt) / 2
            return (
                fetch_runs_range(client, owner, repo, branch, start_dt, mid_dt)
                + fetch_runs_range(client, owner, repo, branch, mid_dt + timedelta(days=1), end_dt)
            )
        if end_dt.date() > start_dt.date():
            # Intervalo curto demais para dividir ao meio: consulta dia a dia.
            print(f"  [Aviso] Intervalo {created_str} atingiu teto ({total_count}). Dividindo por dia...")
            n_days = (end_dt.date() - start_dt.date()).days
            runs: List[Dict[str, Any]] = []
            for i in range(n_days + 1):
                day = datetime.combine(start_dt.date() + timedelta(days=i), datetime.min.time())
                runs += fetch_runs_range(client, owner, repo, branch, day, day)
            return runs
        # Um único dia com mais de 1.000 runs: a API só devolve os 1.000 primeiros.
        print(f"  [Aviso] {owner}/{repo} {created_str}: {total_count} runs em um dia; "
              f"apenas {TETO_API} disponiveis pela API")

    return client.paginate(url, params=params, transform_item=slim_run)


def _faixas_mensais(start_dt: datetime, end_dt: datetime) -> List[Tuple[datetime, datetime]]:
    faixas = []
    curr = start_dt
    while curr < end_dt:
        next_month = (curr.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        sub_end = min(next_month, end_dt)
        faixas.append((curr, sub_end))
        curr = sub_end + timedelta(days=1)
    return faixas


def collect_repo_runs(
    client: GitHubClient, owner: str, repo: str, branch: str,
    start_date: str, end_date: str,
    particionar_por_mes: bool = False,
) -> pd.DataFrame:
    """
    Coleta as runs do repositório na janela.

    Por padrão consulta a janela inteira de uma vez (1 sondagem + ceil(n/100)
    páginas) e só subdivide quando a API bate no teto de 1.000 resultados.
    `particionar_por_mes=True` reproduz a coleta antiga mês a mês, útil para
    reaproveitar um cache já populado por ela (as URLs são as mesmas).
    """
    start_dt = datetime.strptime(start_date, DATE_FORMAT)
    end_dt = datetime.strptime(end_date, DATE_FORMAT)

    print(f"\n[Coletando] {owner}/{repo} (branch: {branch}) de {start_date} a {end_date}...")
    faixas = _faixas_mensais(start_dt, end_dt) if particionar_por_mes else [(start_dt, end_dt)]

    all_runs: List[Dict[str, Any]] = []
    for ini, fim in faixas:
        runs = fetch_runs_range(client, owner, repo, branch, ini, fim)
        all_runs.extend(runs)
        if particionar_por_mes:
            print(f"  -> {ini.strftime(DATE_FORMAT)} a {fim.strftime(DATE_FORMAT)}: {len(runs)} runs")

    nome = f"{owner}/{repo}"
    records = [
        {
            "repo": nome,
            "run_id": r.get("id"),
            "workflow_id": r.get("workflow_id"),
            "run_started_at": r.get("run_started_at"),
            "updated_at": r.get("updated_at"),
            "conclusion_original": r.get("conclusion"),
            "status_classificacao": classify_conclusion(r.get("conclusion")),
        }
        for r in all_runs
    ]

    df = pd.DataFrame(records)
    if not df.empty:
        df = df.drop_duplicates(subset=["run_id"])
    print(f"[Concluído] {nome}: {len(df)} runs únicos extraídos.")
    return df
"""
Conferência da coleta (Issue #52): para 2 repositórios da amostra, recalcula
o nº de releases e de workflow runs válidos na janela por um caminho
independente do pipeline e gera `data/conferencia.md`.

- Sem cache: tudo é baixado de novo da API.
- Releases: lista completa, filtrada aqui mesmo (não usa selection.py).
- Runs: em vez de baixar e classificar cada run, pede à API só o
  `total_count` filtrado por `status=<conclusion>`, mês a mês.

Repositórios conferidos: o de menos e o de mais runs válidos da amostra
(o mais perto do corte de inclusão e o que mais exercita a paginação).

Uso: python conferencia.py --config config.yaml
"""
import argparse
import os
import sys
from datetime import date, datetime, timedelta

import pandas as pd
from pipeline.config import load_config

from pipeline.client import GitHubClient

API = "https://api.github.com"
FAILURE = ["failure", "timed_out", "startup_failure"]


def month_ranges(start: date, end: date):
    curr = start
    while curr <= end:
        month_end = (curr.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        yield curr, min(month_end, end)
        curr = month_end + timedelta(days=1)


def count_releases(client, full_name, start, end):
    releases = client.paginate(f"{API}/repos/{full_name}/releases", params={"per_page": 100})
    in_window = [
        r for r in releases
        if not r["draft"] and r["published_at"] and start <= r["published_at"][:10] <= end
    ]
    n_pre = sum(1 for r in in_window if r["prerelease"])
    return len(in_window) - n_pre, n_pre


def count_runs(client, full_name, branch, start, end):
    totals = {}
    for conclusion in ["success"] + FAILURE:
        total = 0
        for m_start, m_end in month_ranges(start, end):
            data, _ = client.get_json(
                f"{API}/repos/{full_name}/actions/runs",
                params={
                    "branch": branch, "event": "push", "status": conclusion,
                    "created": f"{m_start.isoformat()}..{m_end.isoformat()}",
                    "per_page": 1,
                },
            )
            total += data.get("total_count", 0)
        totals[conclusion] = total
    return totals


def main():
    parser = argparse.ArgumentParser(description="Conferência independente da coleta")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    cfg = load_config(args.config)

    out_dir = cfg.get("output_dir", "data")
    start, end = cfg["window"]["start"], cfg["window"]["end"]
    meta_path = os.path.join(out_dir, "metadados.csv")
    if not os.path.exists(meta_path):
        sys.exit(f"{meta_path} não existe: rode antes `python -m pipeline --config config.yaml`.")
    meta = pd.read_csv(meta_path)
    meta = meta.sort_values("n_runs_validos_janela")
    chosen = [meta.iloc[0], meta.iloc[-1]]

    client = GitHubClient(cache=None, max_retries=cfg.get("max_retries", 5))
    s_date = datetime.strptime(start, "%Y-%m-%d").date()
    e_date = datetime.strptime(end, "%Y-%m-%d").date()

    lines = [
        "# Conferência da coleta (Issue #52)",
        "",
        f"Gerado em {date.today().isoformat()} por `python conferencia.py --config config.yaml`.",
        f"Janela: {start} a {end}. Os valores \"conferência\" foram baixados de novo da API,",
        "sem cache, por um caminho diferente do pipeline (releases filtradas neste script;",
        "runs contados pelo `total_count` com filtro `status`, mês a mês).",
        "",
        "| Repositório | Medida | Pipeline (`metadados.csv`) | Conferência | Confere? |",
        "|---|---|---|---|---|",
    ]
    all_ok = True
    for row in chosen:
        name, branch = row["full_name"], row["default_branch"]
        print(f"[Conferência] {name} ({branch})")
        n_rel, n_pre = count_releases(client, name, start, end)
        runs = count_runs(client, name, branch, s_date, e_date)
        n_valid = runs["success"] + sum(runs[c] for c in FAILURE)
        checks = [
            ("releases", row["n_releases_janela"], n_rel),
            ("pré-releases", row["n_prereleases_janela"], n_pre),
            ("runs válidos", row["n_runs_validos_janela"], n_valid),
        ]
        for medida, esperado, obtido in checks:
            ok = int(esperado) == int(obtido)
            all_ok &= ok
            lines.append(f"| {name} | {medida} | {int(esperado)} | {obtido} | {'sim' if ok else '**não**'} |")
        lines.append(
            f"| {name} | runs por conclusion | – | "
            + ", ".join(f"{c}: {n}" for c, n in runs.items())
            + " | – |"
        )

    lines += [
        "",
        "## Conferência visual (opcional)",
        "",
        "Para conferir pela interface do GitHub, abra:",
        "",
    ]
    for row in chosen:
        name, branch = row["full_name"], row["default_branch"]
        lines += [
            f"- **{name}**",
            f"  - releases: https://github.com/{name}/releases",
            f"  - runs: https://github.com/{name}/actions?query="
            f"branch%3A{branch}+event%3Apush+created%3A{start}..{end}+is%3Asuccess "
            "(troque `is:success` por `is:failure`)",
        ]

    path = os.path.join(out_dir, "conferencia.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nSalvo em {path}")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()

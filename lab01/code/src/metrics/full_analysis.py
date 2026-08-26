"""
Analise completa das RQ01-RQ06 sobre os 1000 repositorios coletados (issue: Analisar resultados das RQs 01 a 06), com geração dos
gráficos usados na secao 4.2 do relatorio final (issue: Implementar
visualizacoes dos resultados).

Não inclui a RQ07 (bonus) e fica para quem pegar essa issue.****

Roda sobre data/raw/top_1000_repositories.csv.
"""
import csv
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CODE_DIR = Path(__file__).resolve().parents[2]
CSV_PATH = CODE_DIR / "data" / "raw" / "top_1000_repositories.csv"
CHARTS_DIR = CODE_DIR / "data" / "processed" / "charts"
RESULTS_PATH = CODE_DIR / "data" / "processed" / "full_analysis_results.json"

# Fonte: TIOBE Index: https://www.tiobe.com/tiobe-index/
POPULAR_LANGUAGES = {
    "Python", "C", "C++", "Java", "C#", "JavaScript",
    "Visual Basic", "SQL", "R", "Rust",
}

BLUE = "#2a78d6"
ORANGE = "#eb6834"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
MUTED = "#898781"
INK = "#0b0b0b"
SURFACE = "#fcfcfb"


def load_repositories():
    with open(CSV_PATH, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")
        return list(reader)


def parse_dt(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def enrich(repositories):
    now = datetime.now(timezone.utc)

    for repo in repositories:
        created_at = parse_dt(repo.get("created_at"))
        pushed_at = parse_dt(repo.get("pushed_at"))

        repo["_age_years"] = round((now - created_at).days / 365.25, 2) if created_at else None
        repo["_days_since_update"] = (now - pushed_at).days if pushed_at else None

        repo["_merged_prs"] = int(repo.get("merged_pull_requests_count") or 0)

        total_issues = int(repo.get("issues_count") or 0)
        closed_issues = int(repo.get("closed_issues_count") or 0)
        repo["_issue_close_ratio"] = round(closed_issues / total_issues * 100, 2) if total_issues > 0 else None

        repo["_releases_count"] = int(repo.get("releases_count") or 0)
        repo["_releases_capped"] = repo["_releases_count"] >= 1000

        language = repo.get("primary_language") or None
        repo["_language"] = language
        repo["_is_popular_language"] = (language in POPULAR_LANGUAGES) if language else None

    return repositories


def distribution(values):
    values = [v for v in values if v is not None]
    if not values:
        return None
    dist = {
        "n": len(values),
        "min": min(values),
        "max": max(values),
        "mean": round(statistics.mean(values), 2),
        "median": round(statistics.median(values), 2),
    }
    dist["stdev"] = round(statistics.stdev(values), 2) if len(values) > 1 else 0
    return dist


def analyze_rq01(repos):
    return distribution([r["_age_years"] for r in repos])


def analyze_rq02(repos):
    return distribution([r["_merged_prs"] for r in repos])


def analyze_rq03(repos):
    all_dist = distribution([r["_releases_count"] for r in repos])
    uncapped = [r["_releases_count"] for r in repos if not r["_releases_capped"]]
    n_capped = sum(1 for r in repos if r["_releases_capped"])
    return {
        "all": all_dist,
        "excluding_capped": distribution(uncapped),
        "n_capped": n_capped,
    }


def analyze_rq04(repos):
    return distribution([r["_days_since_update"] for r in repos])


def analyze_rq05(repos):
    with_language = [r for r in repos if r["_language"] is not None]
    popular = [r for r in with_language if r["_is_popular_language"]]
    return {
        "total": len(repos),
        "no_language": len(repos) - len(with_language),
        "considered": len(with_language),
        "popular": len(popular),
        "not_popular": len(with_language) - len(popular),
        "popular_pct": round(len(popular) / len(with_language) * 100, 2) if with_language else None,
    }


def analyze_rq06(repos):
    return distribution([r["_issue_close_ratio"] for r in repos if r["_issue_close_ratio"] is not None])


def style_axes(ax):
    ax.set_facecolor(SURFACE)
    ax.figure.set_facecolor(SURFACE)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(AXIS)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def save_histogram(values, median, title, xlabel, filename, bins=40, clip_percentile=98):
    values = [v for v in values if v is not None]
    upper = statistics.quantiles(values, n=100)[clip_percentile - 1] if len(values) >= 100 else max(values)

    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=150)
    ax.hist([v for v in values if v <= upper], bins=bins, color=BLUE, edgecolor=SURFACE, linewidth=0.5)
    ax.axvline(median, color=INK, linewidth=1.5, linestyle="--")
    ax.text(median, ax.get_ylim()[1] * 0.95, f" mediana = {median}", color=INK, fontsize=9, va="top")

    ax.set_title(title, color=INK, fontsize=11, loc="left", pad=12)
    ax.set_xlabel(xlabel, color=MUTED, fontsize=9)
    ax.set_ylabel("Número de repositórios", color=MUTED, fontsize=9)
    style_axes(ax)

    fig.tight_layout()
    fig.savefig(CHARTS_DIR / filename, facecolor=SURFACE)
    plt.close(fig)


def save_two_bar(labels, values, title, ylabel, filename, value_fmt="{:.1f}"):
    fig, ax = plt.subplots(figsize=(5, 4.2), dpi=150)
    colors = [BLUE, ORANGE]
    bars = ax.bar(labels, values, color=colors[: len(labels)], width=0.55)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height(),
            value_fmt.format(value), ha="center", va="bottom",
            color=INK, fontsize=10,
        )

    ax.set_title(title, color=INK, fontsize=11, loc="left", pad=12)
    ax.set_ylabel(ylabel, color=MUTED, fontsize=9)
    style_axes(ax)
    ax.set_ylim(0, max(values) * 1.2)

    fig.tight_layout()
    fig.savefig(CHARTS_DIR / filename, facecolor=SURFACE)
    plt.close(fig)


def generate_charts(repos, rq01, rq02, rq03, rq04, rq05, rq06):
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    save_histogram(
        [r["_age_years"] for r in repos], rq01["median"],
        "RQ01 — Idade dos repositórios populares",
        "Idade (anos)", "rq01_idade.png",
    )
    save_histogram(
        [r["_merged_prs"] for r in repos], rq02["median"],
        "RQ02 — Total de pull requests aceitas",
        "Pull requests aceitas (mescladas)", "rq02_pr_merge_ratio.png", clip_percentile=90,
    )
    save_histogram(
        [r["_releases_count"] for r in repos], rq03["all"]["median"],
        "RQ03 — Total de releases por repositório",
        "Total de releases", "rq03_releases.png", clip_percentile=90,
    )
    save_histogram(
        [r["_days_since_update"] for r in repos], rq04["median"],
        "RQ04 — Dias desde a última atualização",
        "Dias desde o último push", "rq04_dias_desde_update.png", clip_percentile=90,
    )
    save_two_bar(
        ["Linguagem popular\n(TIOBE top 10)", "Outras linguagens"],
        [rq05["popular"], rq05["not_popular"]],
        "RQ05 — Repositórios por grupo de linguagem",
        "Número de repositórios", "rq05_linguagem.png", value_fmt="{:.0f}",
    )
    save_histogram(
        [r["_issue_close_ratio"] for r in repos if r["_issue_close_ratio"] is not None], rq06["median"],
        "RQ06 — Percentual de issues fechadas",
        "Issues fechadas / issues totais (%)", "rq06_issue_close_ratio.png",
    )


def main():
    repos = enrich(load_repositories())

    results = {
        "rq01_idade": analyze_rq01(repos),
        "rq02_pr_merge_ratio": analyze_rq02(repos),
        "rq03_releases": analyze_rq03(repos),
        "rq04_dias_desde_update": analyze_rq04(repos),
        "rq05_linguagem": analyze_rq05(repos),
        "rq06_issue_close_ratio": analyze_rq06(repos),
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)

    generate_charts(
        repos,
        results["rq01_idade"], results["rq02_pr_merge_ratio"], results["rq03_releases"],
        results["rq04_dias_desde_update"], results["rq05_linguagem"], results["rq06_issue_close_ratio"],
    )

    print(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\nResultados salvos em: {RESULTS_PATH}")
    print(f"Gráficos salvos em: {CHARTS_DIR}")


if __name__ == "__main__":
    main()

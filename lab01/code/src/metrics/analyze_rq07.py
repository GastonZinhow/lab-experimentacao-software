import csv
import statistics
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# Mesma fonte/lista da RQ05 (TIOBE Index, top 10, agosto/2026)
# Manter em sincronia com POPULAR_LANGUAGES em analyze_rq05_rq06.py
POPULAR_LANGUAGES = {
    "Python",
    "C",
    "C++",
    "Java",
    "C#",
    "JavaScript",
    "Visual Basic",
    "SQL",
    "R",
    "Rust",
}

MIN_REPOS_PER_LANGUAGE = 2

CHARTS_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "charts"

# Mesma paleta usada em full_analysis.py, para os graficos ficarem consistentes
BLUE = "#2a78d6"
ORANGE = "#eb6834"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
MUTED = "#898781"
INK = "#0b0b0b"
SURFACE = "#fcfcfb"


def days_since_update(pushed_at):
    if not pushed_at:
        return None
    pushed_dt = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - pushed_dt).days


def merged_pr_ratio(repo):
    total = int(repo.get("pull_requests_count") or 0)
    merged = int(repo.get("merged_pull_requests_count") or 0)
    return round((merged / total) * 100, 2) if total > 0 else None


def group_by_language(repositories):
    groups = {}

    for repo in repositories:
        language = repo.get("primary_language")

        if not language:
            continue

        groups.setdefault(language, []).append(repo)

    return groups


def group_metrics(repositories):
    ratios = [r for r in (merged_pr_ratio(repo) for repo in repositories) if r is not None]
    releases = [int(repo.get("releases_count") or 0) for repo in repositories]
    updates = [d for d in (days_since_update(repo.get("pushed_at")) for repo in repositories) if d is not None]

    return {
        "n": len(repositories),
        "pr_merge_ratio_median": round(statistics.median(ratios), 2) if ratios else None,
        "releases_median": statistics.median(releases) if releases else None,
        "days_since_update_median": statistics.median(updates) if updates else None,
    }


def print_group_metrics(label, repositories):
    metrics = group_metrics(repositories)

    print(f"{label} (n={metrics['n']})")
    print(f"  - Mediana % PRs aceitas: {metrics['pr_merge_ratio_median']}%")
    print(f"  - Mediana de releases: {metrics['releases_median']}")
    print(f"  - Mediana de dias desde ultimo push: {metrics['days_since_update_median']}")


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


def save_two_bar(values, title, ylabel, filename, value_fmt="{:.1f}"):
    labels = ["Linguagem popular\n(TIOBE top 10)", "Outras linguagens"]

    fig, ax = plt.subplots(figsize=(5, 4.2), dpi=150)
    bars = ax.bar(labels, values, color=[BLUE, ORANGE], width=0.55)

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
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(CHARTS_DIR / filename, facecolor=SURFACE)
    plt.close(fig)


def generate_charts(populares_metrics, nao_populares_metrics):
    save_two_bar(
        [populares_metrics["pr_merge_ratio_median"], nao_populares_metrics["pr_merge_ratio_median"]],
        "RQ07 — Mediana de PRs aceitas (%) por grupo de linguagem",
        "PRs aceitas / PRs totais (%)", "rq07_pr_merge_ratio.png",
    )
    save_two_bar(
        [populares_metrics["releases_median"], nao_populares_metrics["releases_median"]],
        "RQ07 — Mediana de releases por grupo de linguagem",
        "Total de releases", "rq07_releases.png", value_fmt="{:.0f}",
    )
    save_two_bar(
        [populares_metrics["days_since_update_median"], nao_populares_metrics["days_since_update_median"]],
        "RQ07 — Mediana de dias desde a última atualização por grupo",
        "Dias desde o último push", "rq07_dias_desde_update.png", value_fmt="{:.0f}",
    )


def analyze_rq07(csv_path):
    with open(csv_path, "r", encoding="utf-8", newline="") as file:
        repositories = list(csv.DictReader(file, delimiter=";"))

    print("== Analise RQ07 (bonus) ==\n")

    print("-- 1-4. Metricas separadas por linguagem primaria --\n")
    language_groups = group_by_language(repositories)
    languages_ordenadas = sorted(language_groups.items(), key=lambda item: len(item[1]), reverse=True)

    ignoradas = []

    for language, repos in languages_ordenadas:
        if len(repos) < MIN_REPOS_PER_LANGUAGE:
            ignoradas.append(language)
            continue

        print_group_metrics(language, repos)
        print()

    if ignoradas:
        print(
            f"(linguagens com menos de {MIN_REPOS_PER_LANGUAGE} repositorios, "
            f"ignoradas na comparacao individual: {', '.join(ignoradas)})\n"
        )

    print("-- 5. Discussao: linguagens populares (TIOBE top 10) vs demais --\n")

    populares = [r for r in repositories if r.get("primary_language") in POPULAR_LANGUAGES]
    nao_populares = [
        r for r in repositories
        if r.get("primary_language") and r.get("primary_language") not in POPULAR_LANGUAGES
    ]

    print_group_metrics("Linguagens populares (TIOBE top 10)", populares)
    print()
    print_group_metrics("Linguagens NAO populares", nao_populares)

    generate_charts(group_metrics(populares), group_metrics(nao_populares))
    print(f"\nGraficos salvos em: {CHARTS_DIR}")


if __name__ == "__main__":
    from pathlib import Path

    data_path = Path(__file__).resolve().parents[2] / "data" / "raw" / "top_1000_repositories.csv"
    analyze_rq07(str(data_path))

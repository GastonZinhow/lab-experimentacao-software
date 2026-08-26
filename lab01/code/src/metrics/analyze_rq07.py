import csv
import statistics
from datetime import datetime, timezone


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


def print_group_metrics(label, repositories):
    ratios = [r for r in (merged_pr_ratio(repo) for repo in repositories) if r is not None]
    releases = [int(repo.get("releases_count") or 0) for repo in repositories]
    updates = [d for d in (days_since_update(repo.get("pushed_at")) for repo in repositories) if d is not None]

    print(f"{label} (n={len(repositories)})")
    print(f"  - Mediana % PRs aceitas: {round(statistics.median(ratios), 2) if ratios else None}% (n={len(ratios)})")
    print(f"  - Mediana de releases: {statistics.median(releases) if releases else None}")
    print(f"  - Mediana de dias desde ultimo push: {statistics.median(updates) if updates else None}")


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


if __name__ == "__main__":
    from pathlib import Path

    data_path = Path(__file__).resolve().parents[2] / "data" / "raw" / "top_1000_repositories.csv"
    analyze_rq07(str(data_path))

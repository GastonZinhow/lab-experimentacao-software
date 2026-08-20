import csv
import statistics
from datetime import datetime, timezone


NUMERIC_FIELDS = [
    "stars",
    "releases_count",
    "pull_requests_count",
    "merged_pull_requests_count",
    "issues_count",
    "closed_issues_count",
]

ALL_FIELDS = [
    "name",
    "owner",
    "url",
    "created_at",
    "stars",
    "releases_count",
    "pushed_at",
    "pull_requests_count",
    "merged_pull_requests_count",
    "primary_language",
    "issues_count",
    "closed_issues_count",
]


def load_repositories(csv_path, delimiter=";"):
    with open(csv_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        return list(reader)


def parse_datetime(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def enrich_derived_fields(repositories):
    now = datetime.now(timezone.utc)

    for repo in repositories:
        created_at = parse_datetime(repo.get("created_at"))
        pushed_at = parse_datetime(repo.get("pushed_at"))

        repo["_age_days"] = (now - created_at).days if created_at else None
        repo["_days_since_update"] = (now - pushed_at).days if pushed_at else None
        repo["_created_at_dt"] = created_at
        repo["_pushed_at_dt"] = pushed_at

    return repositories


def check_missing_values(repositories):
    total = len(repositories)
    missing = {field: 0 for field in ALL_FIELDS}

    for repo in repositories:
        for field in ALL_FIELDS:
            if repo.get(field) in (None, ""):
                missing[field] += 1

    return total, missing


def check_duplicates(repositories):
    seen = {}
    duplicates = []

    for repo in repositories:
        key = f"{repo.get('owner')}/{repo.get('name')}"

        if key in seen:
            duplicates.append(key)
        else:
            seen[key] = True

    return duplicates


def check_logical_inconsistencies(repositories):
    problems = []

    for repo in repositories:
        repo_name = f"{repo.get('owner')}/{repo.get('name')}"

        closed_issues = int(repo.get("closed_issues_count") or 0)
        total_issues = int(repo.get("issues_count") or 0)
        merged_prs = int(repo.get("merged_pull_requests_count") or 0)
        total_prs = int(repo.get("pull_requests_count") or 0)
        stars = int(repo.get("stars") or 0)

        if closed_issues > total_issues:
            problems.append(
                f"{repo_name}: closed_issues_count ({closed_issues}) > issues_count ({total_issues})"
            )

        if merged_prs > total_prs:
            problems.append(
                f"{repo_name}: merged_pull_requests_count ({merged_prs}) > pull_requests_count ({total_prs})"
            )

        if stars <= 0:
            problems.append(f"{repo_name}: stars <= 0 ({stars})")

        created_at = repo.get("_created_at_dt")
        pushed_at = repo.get("_pushed_at_dt")

        if created_at and pushed_at and pushed_at < created_at:
            problems.append(
                f"{repo_name}: pushed_at ({pushed_at.date()}) anterior ao created_at ({created_at.date()})"
            )

    return problems


def compute_distribution(values):
    if not values:
        return None

    distribution = {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": round(statistics.mean(values), 2),
        "median": round(statistics.median(values), 2),
    }

    if len(values) > 1:
        distribution["stdev"] = round(statistics.stdev(values), 2)
    else:
        distribution["stdev"] = 0

    return distribution


def find_outliers(repositories, field, values_by_repo):
    values = [v for _, v in values_by_repo]

    if len(values) < 4:
        return [], None, None

    quartiles = statistics.quantiles(values, n=4, method="inclusive")
    q1, q3 = quartiles[0], quartiles[2]
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = [
        (repo_name, value)
        for repo_name, value in values_by_repo
        if value < lower_bound or value > upper_bound
    ]
    outliers.sort(key=lambda item: item[1], reverse=True)

    return outliers, lower_bound, upper_bound


def validate_data_consistency(csv_path, delimiter=";"):
    repositories = load_repositories(csv_path, delimiter=delimiter)
    repositories = enrich_derived_fields(repositories)

    print("== Validacao de consistencia dos dados (issue #8) ==\n")

    total, missing = check_missing_values(repositories)
    print(f"Total de repositorios carregados: {total}\n")

    print("-- Valores ausentes por campo --")
    for field, missing_count in missing.items():
        percentage = round((missing_count / total) * 100, 2) if total else 0
        print(f"  - {field}: {missing_count} ({percentage}%)")
    print()

    duplicates = check_duplicates(repositories)
    print(f"-- Repositorios duplicados: {len(duplicates)} --")
    for duplicate in duplicates:
        print(f"  - {duplicate}")
    print()

    problems = check_logical_inconsistencies(repositories)
    print(f"-- Inconsistencias logicas encontradas: {len(problems)} --")
    for problem in problems[:20]:
        print(f"  - {problem}")
    if len(problems) > 20:
        print(f"  ... e mais {len(problems) - 20} ocorrencias")
    print()

    print("-- Distribuicoes e outliers por metrica --")

    metrics_to_check = NUMERIC_FIELDS + ["_age_days", "_days_since_update"]

    for field in metrics_to_check:
        values_by_repo = [
            (f"{repo.get('owner')}/{repo.get('name')}", repo[field])
            for repo in repositories
            if repo.get(field) is not None
        ]
        values_by_repo = [
            (name, int(value) if field != "_age_days" and field != "_days_since_update" else value)
            for name, value in values_by_repo
        ]

        values = [v for _, v in values_by_repo]
        distribution = compute_distribution(values)

        label = field.lstrip("_")
        print(f"\n{label}:")

        if not distribution:
            print("  Sem dados suficientes para calcular a distribuicao.")
            continue

        print(f"  count={distribution['count']} min={distribution['min']} "
              f"max={distribution['max']} mean={distribution['mean']} "
              f"median={distribution['median']} stdev={distribution['stdev']}")

        outliers, lower_bound, upper_bound = find_outliers(repositories, field, values_by_repo)

        if lower_bound is None:
            print("  Repositorios insuficientes para deteccao de outliers (IQR).")
            continue

        print(f"  Limite IQR: [{round(lower_bound, 2)}, {round(upper_bound, 2)}]")
        print(f"  Outliers detectados: {len(outliers)}")

        for repo_name, value in outliers[:5]:
            print(f"    - {repo_name}: {value}")

    print("\n== Fim da validacao ==")


if __name__ == "__main__":
    validate_data_consistency("data/raw/top_1000_repositories.csv")

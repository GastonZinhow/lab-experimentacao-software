from datetime import datetime, timezone
import json


REPOSITORIES_FOR_ANALYSIS = {
    "vercel/next.js",
    "excalidraw/excalidraw",
    "kubernetes/kubernetes",
    "Hack-with-Github/Awesome-Hacking",
    "mrdoob/three.js",
    "sst/opencode",
    "yt-dlp/yt-dlp",
    "huggingface/transformers",
}


def calculate_age_years(created_at):
    created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)

    age_days = (now - created_dt).days

    return round(age_days / 365.25, 2)


def analyze_rq01_rq02(json_path):
    with open(json_path, "r", encoding="utf-8") as file:
        repositories = json.load(file)

    selected_repositories = []

    for repo in repositories:
        repo_name = f"{repo.get('owner')}/{repo.get('name')}"

        if repo_name in REPOSITORIES_FOR_ANALYSIS:
            selected_repositories.append(repo)

    print("== Analise RQ01 e RQ02 ==\n")

    for repo in selected_repositories:
        repo_name = f"{repo.get('owner')}/{repo.get('name')}"

        created_at = repo.get("created_at")
        age_years = None

        if created_at:
            age_years = calculate_age_years(created_at)

        merged_pull_requests = repo.get("merged_pull_requests_count", 0)
        total_pull_requests = repo.get("pull_requests_count", 0)

        merged_pr_ratio = 0

        if total_pull_requests > 0:
            merged_pr_ratio = round(
                (merged_pull_requests / total_pull_requests) * 100,
                2
            )

        print(f"Repositorio: {repo_name}")
        print(f"  - RQ01 - Data de criacao: {created_at}")
        print(f"  - RQ01 - Idade aproximada: {age_years} anos")
        print(f"  - RQ02 - Total de pull requests: {total_pull_requests}")
        print(f"  - RQ02 - Pull requests aceitas/merged: {merged_pull_requests}")
        print(f"  - RQ02 - Percentual de PRs merged: {merged_pr_ratio}%\n")

    print(f"Total de repositorios analisados: {len(selected_repositories)}")


if __name__ == "__main__":
    analyze_rq01_rq02("../../data/raw/top_100_repositories.json")
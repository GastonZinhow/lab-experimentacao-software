import json
from pathlib import Path

from src.config import get_github_token
from src.collectors.repository_collector import collect_top_repositories


def main():
    token = get_github_token()

    repositories = collect_top_repositories(token, total_repositories=100, page_size=10)

    output_path = Path("data/raw/top_100_repositories.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(repositories, file, ensure_ascii=False, indent=2)

    print(f"{len(repositories)} repositórios foram salvos em {output_path}")


if __name__ == "__main__":
    main()
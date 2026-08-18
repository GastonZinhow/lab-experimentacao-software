from pathlib import Path

from src.config import get_github_token
from src.collectors.repository_collector import collect_top_repositories
from src.exporters.repository_exporter import RepositoryExporter


def main():
    token = get_github_token()

    repositories = collect_top_repositories(token, total_repositories=1000, page_size=10)

    #json_output_path = Path("data/raw/top_1000_repositories.json")
    csv_output_path = Path("data/raw/top_1000_repositories.csv")
    exporter = RepositoryExporter(repositories)

    #exporter.export_json(json_output_path)
    exporter.export_csv(csv_output_path, delimiter=";")

    #print(f"{len(repositories)} repositórios foram salvos em {json_output_path}")
    print(f"{len(repositories)} repositories saved at {csv_output_path}")
    print("CSV generated with UTF-8 enconding and separator: ';'.")
    print("Missing data by field:")

    for field, missing_count in exporter.count_missing_values().items():
        print(f"  - {field}: {missing_count}")


if __name__ == "__main__":
    main()

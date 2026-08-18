import csv
import json


class RepositoryExporter:
    fields = [
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

    def __init__(self, repositories):
        self.repositories = repositories

    def export_json(self, output_path):
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(self.repositories, file, ensure_ascii=False, indent=2)

    def export_csv(self, output_path, delimiter=","):
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=self.fields,
                delimiter=delimiter,
            )
            writer.writeheader()
            writer.writerows(self.repositories)

    def count_missing_values(self):
        return {
            field: sum(
                repository.get(field) in (None, "")
                for repository in self.repositories
            )
            for field in self.fields
        }

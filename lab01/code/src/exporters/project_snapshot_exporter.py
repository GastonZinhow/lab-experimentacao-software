import csv


class ProjectSnapshotExporter:
    fields = [
        "issue_number",
        "title",
        "url",
        "assignees",
        "status",
        "sprint",
    ]

    def __init__(self, items, sprint_label):
        self.items = items
        self.sprint_label = sprint_label

    def export_csv(self, output_path, delimiter=","):
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=self.fields,
                delimiter=delimiter,
            )
            writer.writeheader()

            for item in self.items:
                row = dict(item)
                row["sprint"] = self.sprint_label
                writer.writerow(row)

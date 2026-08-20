import sys
from pathlib import Path

from src.config import get_github_token
from src.collectors.project_collector import collect_project_items
from src.exporters.project_snapshot_exporter import ProjectSnapshotExporter


PROJECT_OWNER = "GastonZinhow"
PROJECT_NUMBER = 3


def main():
    if len(sys.argv) != 2:
        print("Uso: python export_project_snapshot.py <SPRINT_LABEL>")
        print("Exemplo: python export_project_snapshot.py Lab01S03")
        sys.exit(1)

    sprint_label = sys.argv[1]

    token = get_github_token()

    items = collect_project_items(token, PROJECT_OWNER, PROJECT_NUMBER)

    exporter = ProjectSnapshotExporter(items, sprint_label)
    output_path = Path(f"data/snapshots/{sprint_label.lower()}_project_snapshot.csv")
    exporter.export_csv(output_path)

    print(f"{len(items)} itens do Project exportados para {output_path}")


if __name__ == "__main__":
    main()

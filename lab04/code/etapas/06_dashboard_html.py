"""Etapa 6: gera a versão estática do dashboard em `lab04/dashboard.html`."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dashboard_html import gerar_html


def main():
    arquivo = gerar_html()
    print(f"Dashboard em HTML: {arquivo} ({arquivo.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()

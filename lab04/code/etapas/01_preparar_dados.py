"""Etapa 1: sorteia a amostra real e calibra os parâmetros do gerador."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dados_reais import preparar


def main():
    amostra, parametros = preparar()
    print(f"Amostra: {len(amostra)} módulos | efeito calibrado: {parametros['associacao']['efeito_calibrado']:.3f}")


if __name__ == "__main__":
    main()

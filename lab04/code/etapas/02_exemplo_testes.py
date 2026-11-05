"""Etapa 2: aplica Pearson e Spearman ao conjunto simulado de exemplo e salva o resultado."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from exemplo import N, SEMENTE, SITUACAO, efeito_do_exemplo, rodar_exemplo
from testes import ALFA, resumir

ARQUIVO_SAIDA = Path(__file__).resolve().parents[1] / "resultados" / "exemplo_testes.json"


def main():
    _, resultados = rodar_exemplo()
    saida = {
        "situacao": SITUACAO, "n": N, "efeito": efeito_do_exemplo(), "semente": SEMENTE, "alfa": ALFA,
        "testes": resumir(resultados),
    }
    ARQUIVO_SAIDA.parent.mkdir(exist_ok=True)
    ARQUIVO_SAIDA.write_text(json.dumps(saida, indent=2, ensure_ascii=False), encoding="utf-8")
    for teste, valores in saida["testes"].items():
        decisao = "rejeita H0" if valores["rejeita_h0"] else "não rejeita H0"
        print(f"{teste:>8}: coeficiente = {valores['coeficiente']:.3f} ({valores['magnitude']}), "
              f"p = {valores['p_valor']:.4f} -> {decisao}")


if __name__ == "__main__":
    main()

"""Etapa 5: Pearson e Spearman aplicados à amostra real do KC1."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analise_dados_reais import ARQUIVO_RESULTADO, analisar, carregar_amostra


def main(arquivo_saida=ARQUIVO_RESULTADO):
    """Salva `resultados/dados_reais.csv`."""
    tabela = analisar(carregar_amostra())
    Path(arquivo_saida).parent.mkdir(exist_ok=True)
    tabela.to_csv(arquivo_saida, index=False)
    for linha in tabela.itertuples():
        decisao = "rejeita H0" if linha.rejeita_h0 else "não rejeita H0"
        print(f"{linha.conjunto:>16} | {linha.teste:>8}: coeficiente = {linha.coeficiente:.3f} "
              f"[{linha.ic95_inferior:.2f}; {linha.ic95_superior:.2f}], p = {linha.p_valor:.2g} -> {decisao}")


if __name__ == "__main__":
    main()

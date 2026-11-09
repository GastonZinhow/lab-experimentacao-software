"""Etapa 3: erro tipo I de Pearson e Spearman em cada situação simulada (Q1 e Q3)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gerador import SITUACOES, gerar
from simulacao import PASTA_RESULTADOS, arquivo_erro_tipo1, simular_erro_tipo1


def main(gerar=gerar, situacoes=SITUACOES, pasta=PASTA_RESULTADOS, **opcoes):
    """Salva `resultados/erro_tipo1_<situacao>.csv` para cada situação de `SITUACOES`."""
    Path(pasta).mkdir(exist_ok=True)
    for situacao in situacoes:
        tabela = simular_erro_tipo1(situacao, gerar=gerar, **opcoes)
        tabela.to_csv(arquivo_erro_tipo1(situacao, pasta), index=False)
        resumo = ", ".join(f"{linha.teste} = {100 * linha.proporcao_rejeicao:.2f}%" for linha in tabela.itertuples())
        print(f"Erro tipo I ({situacao}): {resumo}")


if __name__ == "__main__":
    main()

"""Etapa 4: poder de Pearson e Spearman por efeito e situação (Q2 e Q3)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gerador import SITUACOES, gerar
from simulacao import PASTA_RESULTADOS, arquivo_poder, simular_poder
from testes import aplicar_testes_em_lote


def main(gerar=gerar, aplicar_testes_em_lote=aplicar_testes_em_lote,
         situacoes=SITUACOES, pasta=PASTA_RESULTADOS, **opcoes):
    """Salva `resultados/poder_<situacao>.csv` para cada situação."""
    Path(pasta).mkdir(exist_ok=True)
    for situacao in situacoes:
        tabela = simular_poder(
            situacao,
            gerar=gerar,
            aplicar_testes_em_lote=aplicar_testes_em_lote,
            **opcoes,
        )
        tabela.to_csv(arquivo_poder(situacao, pasta), index=False)
        resumo = ", ".join(
            f"efeito {linha.efeito:g}/{linha.teste} = {100 * linha.proporcao_rejeicao:.2f}%"
            for linha in tabela.itertuples()
        )
        print(f"Poder ({situacao}): {resumo}")


if __name__ == "__main__":
    main()

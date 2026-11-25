"""Etapa 01: coleta dos incidentes das duas plataformas na janela do estudo.

Chama os coletores do GitHub e do GitLab para ``2025-11-01T00:00:00Z`` a
``2026-10-31T23:59:59Z`` e grava um resumo em ``dados/brutos/resumo_coleta.json``
(data da coleta tirada dos manifestos e total de incidentes por mês).

Por padrão a etapa **só usa o cache** (``dados/brutos/<plataforma>/``): se faltar
algum arquivo, ela para com erro em vez de acessar a internet. É assim que o
comando único (``run_all.py``) e o CI a executam. Para baixar o que falta,
seguindo as regras do plano de coleta (1 req/s, robots.txt, User-Agent genérico)::

    python lab05/code/etapas/01_coletar.py --baixar
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

PASTA_CODIGO = Path(__file__).resolve().parents[1]
if str(PASTA_CODIGO) not in sys.path:
    sys.path.insert(0, str(PASTA_CODIGO))

from coleta import github, gitlab  # noqa: E402
from coleta._http import ClienteEducado, ErroColeta  # noqa: E402

JANELA_INICIO = "2025-11-01T00:00:00Z"
JANELA_FIM = "2026-10-31T23:59:59Z"
PASTA_BRUTOS = PASTA_CODIGO / "dados" / "brutos"
ARQUIVO_RESUMO = PASTA_BRUTOS / "resumo_coleta.json"
MESES_JANELA = [f"2025-{m:02d}" for m in (11, 12)] + [f"2026-{m:02d}" for m in range(1, 11)]
COLETORES = {"github": github, "gitlab": gitlab}


class ClienteSoCache(ClienteEducado):
    """Cliente que nunca acessa a internet: só devolve arquivos já salvos."""

    def obter(self, url: str, arquivo: str) -> bytes:
        destino = self.pasta / arquivo
        if not destino.exists():
            raise ErroColeta(
                f"Modo só cache: falta {destino.relative_to(PASTA_CODIGO).as_posix()} "
                f"({url}). Rode 'python etapas/01_coletar.py --baixar' com internet."
            )
        return destino.read_bytes()


def criar_cliente(plataforma: str, baixar: bool, pasta_brutos: Path = PASTA_BRUTOS) -> ClienteEducado:
    classe = ClienteEducado if baixar else ClienteSoCache
    return classe(pasta_brutos / plataforma)


def data_da_coleta(manifesto: Path) -> dict[str, str]:
    """Primeira e última resposta salva no manifesto (quando a coleta foi feita)."""
    if not manifesto.exists():
        return {"primeira_resposta_utc": "", "ultima_resposta_utc": "", "respostas_salvas": 0}
    with manifesto.open(encoding="utf-8", newline="") as entrada:
        datas = sorted(
            linha["data_hora_utc"] for linha in csv.DictReader(entrada) if linha["arquivo"]
        )
    return {
        "primeira_resposta_utc": datas[0] if datas else "",
        "ultima_resposta_utc": datas[-1] if datas else "",
        "respostas_salvas": len(datas),
    }


def contar_por_mes(incidentes: list[dict]) -> dict[str, int]:
    contagem = Counter(r["inicio_utc"][:7] for r in incidentes)
    return {mes: contagem.get(mes, 0) for mes in MESES_JANELA}


def coletar_tudo(baixar: bool = False, pasta_brutos: Path = PASTA_BRUTOS) -> dict:
    resumo = {"janela": {"inicio_utc": JANELA_INICIO, "fim_utc": JANELA_FIM}, "plataformas": {}}
    for plataforma, coletor in COLETORES.items():
        cliente = criar_cliente(plataforma, baixar, pasta_brutos)
        incidentes = coletor.coletar(JANELA_INICIO, JANELA_FIM, cliente)
        resumo["plataformas"][plataforma] = {
            "fonte": coletor.FONTE,
            "coleta": data_da_coleta(cliente.pasta / "manifesto.csv"),
            "incidentes": len(incidentes),
            "por_mes": contar_por_mes(incidentes),
        }
        print(f"{plataforma}: {len(incidentes)} incidentes ({cliente.requisicoes} requisições)")
    return resumo


def main(baixar: bool = False) -> None:
    resumo = coletar_tudo(baixar)
    ARQUIVO_RESUMO.write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"Resumo salvo em {ARQUIVO_RESUMO.relative_to(PASTA_CODIGO).as_posix()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--baixar",
        action="store_true",
        help="permite acessar a internet para baixar o que falta no cache",
    )
    main(baixar=parser.parse_args().baixar)

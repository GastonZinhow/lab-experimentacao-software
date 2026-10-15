"""
Avaliação da heurística de release corretiva frente à amostra-ouro (Issue #61).

Compara a saída de metrics.corretiva com o rótulo `corretiva` de uma planilha
de referência (por padrão, rotulos_consenso.csv) e calcula precisão, recall e
F1 com sklearn.metrics.precision_recall_fscore_support, tendo "corretiva = sim"
como classe positiva. Grava os erros (falsos positivos e negativos) em
erros_heuristica_<versao>.csv para orientar a próxima versão.

Os commits de cada release vêm de um CSV no formato de commits_por_release.csv
(colunas repo, tag_name, mensagem). Por padrão, usa commits_amostra_ouro.csv,
com os commits `tag_anterior..tag_name` das 300 releases da amostra-ouro. As
release notes (usadas a partir da v3) vêm de notas_amostra_ouro.csv (colunas
full_name, tag_name, notas).

Uso:
    python -m rotulagem.avaliacao --config config.yaml
    python -m rotulagem.avaliacao --config config.yaml --versao v1 --referencia rotulos_luisa.csv
"""
import argparse
import os
import sys
from typing import Dict, List, Optional

import pandas as pd
from sklearn.metrics import precision_recall_fscore_support

from metrics.corretiva import VERSAO_ATUAL, VERSOES, tem_commit_corretivo, tipo_incremento
from pipeline.config import load_config
from rotulagem.concordancia import ARQUIVO_CONSENSO, normalizar

ARQUIVO_COMMITS = "commits_amostra_ouro.csv"
ARQUIVO_NOTAS = "notas_amostra_ouro.csv"


def metricas(y_true: List[bool], y_pred: List[bool]) -> Dict[str, float]:
    """Precisão, recall e F1 da classe positiva (corretiva), mais a matriz de confusão."""
    p, r, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", pos_label=True, zero_division=0
    )
    vp = sum(t and p_ for t, p_ in zip(y_true, y_pred))
    fp = sum(p_ and not t for t, p_ in zip(y_true, y_pred))
    fn = sum(t and not p_ for t, p_ in zip(y_true, y_pred))
    return {
        "precisao": float(p),
        "recall": float(r),
        "f1": float(f1),
        "vp": vp,
        "fp": fp,
        "fn": fn,
        "vn": len(y_true) - vp - fp - fn,
        "n": len(y_true),
    }


def mensagens_por_release(commits: pd.DataFrame) -> Dict[tuple, List[str]]:
    if commits.empty:
        return {}
    return {
        (repo, tag): grupo["mensagem"].tolist()
        for (repo, tag), grupo in commits.groupby(["repo", "tag_name"])
    }


def avaliar(
    referencia: pd.DataFrame,
    planilha: pd.DataFrame,
    commits: pd.DataFrame,
    versao: str = VERSAO_ATUAL,
    notas: Optional[pd.DataFrame] = None,
) -> tuple:
    """
    Aplica a heurística `versao` às releases da referência e devolve
    (métricas, tabela por release com rótulo, previsão e pistas do erro).
    Itens da referência sem rótulo de corretiva são ignorados.
    """
    classificar = VERSOES[versao]
    msgs = mensagens_por_release(commits)
    anteriores = dict(zip(zip(planilha["full_name"], planilha["tag_name"]), planilha["tag_anterior"]))
    textos = (
        {} if notas is None
        else dict(zip(zip(notas["full_name"], notas["tag_name"]), notas["notas"]))
    )

    linhas = []
    for _, r in referencia.iterrows():
        rotulo = normalizar(r["corretiva"])
        if rotulo not in ("sim", "nao"):
            continue
        chave = (r["full_name"], r["tag_name"])
        anterior: Optional[str] = anteriores.get(chave) or None
        mensagens = msgs.get(chave, [])
        linhas.append({
            "item": r.get("item"),
            "full_name": r["full_name"],
            "tag_name": r["tag_name"],
            "tag_anterior": anterior,
            "incremento": tipo_incremento(anterior, r["tag_name"]) or "fora_semver_ou_nao_cresce",
            "n_commits": len(mensagens),
            "commit_corretivo_v1": tem_commit_corretivo(mensagens),
            "rotulo": rotulo == "sim",
            "previsto": bool(classificar(r["tag_name"], anterior, mensagens, textos.get(chave) or None)),
        })
    tabela = pd.DataFrame(linhas)
    if tabela.empty:
        raise ValueError("A referência não tem nenhum rótulo de corretiva.")
    res = metricas(tabela["rotulo"].tolist(), tabela["previsto"].tolist())
    tabela["erro"] = tabela.apply(
        lambda x: "" if x["rotulo"] == x["previsto"] else ("FP" if x["previsto"] else "FN"), axis=1
    )
    return res, tabela


def formatar(versao: str, res: Dict[str, float]) -> str:
    return (
        f"{versao}: P = {res['precisao']:.3f} | R = {res['recall']:.3f} | F1 = {res['f1']:.3f} "
        f"(VP {res['vp']}, FP {res['fp']}, FN {res['fn']}, VN {res['vn']}; n = {res['n']})"
    )


def main():
    parser = argparse.ArgumentParser(description="P/R/F1 da heurística corretiva (#61)")
    parser.add_argument("--config", required=True)
    parser.add_argument("--versao", default=VERSAO_ATUAL, choices=sorted(VERSOES),
                        help="versão da heurística (padrão: a atual)")
    parser.add_argument("--todas", action="store_true", help="avalia todas as versões")
    parser.add_argument("--referencia", default=ARQUIVO_CONSENSO,
                        help="planilha de referência na pasta de validação")
    parser.add_argument("--commits", default=ARQUIVO_COMMITS,
                        help="CSV de commits (repo, tag_name, mensagem) na pasta de validação")
    parser.add_argument("--notas", default=ARQUIVO_NOTAS,
                        help="CSV de release notes (full_name, tag_name, notas) na pasta de validação")
    args = parser.parse_args()

    cfg = load_config(args.config)
    pasta = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(args.config)), cfg["validation"]["dir"])
    )
    caminho_ref = os.path.join(pasta, args.referencia)
    if not os.path.exists(caminho_ref):
        sys.exit(f"Referência não encontrada: {caminho_ref} (rode rotulagem.concordancia antes).")

    ler = lambda nome: pd.read_csv(os.path.join(pasta, nome), dtype=str, keep_default_na=False)
    referencia, planilha, commits = ler(args.referencia), ler("planilha_rotulagem.csv"), ler(args.commits)
    notas = ler(args.notas) if os.path.exists(os.path.join(pasta, args.notas)) else None
    print(f"[Avaliação] referência: {args.referencia} | commits: {args.commits} | notas: "
          f"{args.notas if notas is not None else 'nenhuma'}")

    for versao in sorted(VERSOES) if args.todas else [args.versao]:
        res, tabela = avaliar(referencia, planilha, commits, versao, notas)
        print(formatar(versao, res))
        erros = tabela[tabela["erro"] != ""]
        nome = f"erros_heuristica_{versao}.csv"
        erros.to_csv(os.path.join(pasta, nome), index=False)
        print(f"  {len(erros)} erros em {nome}")


if __name__ == "__main__":
    main()

"""
Concordância e consenso da amostra-ouro (Issue #59, seção 6 do enunciado).

1. Lê os `rotulos_<avaliador>.csv` de `validation.dir` e confere se estão
   completos (sem células vazias, valores válidos, rótulos de repositório iguais
   nas 5 linhas do mesmo repositório).
2. Calcula o kappa de Fleiss em cada dimensão (`aggregate_raters` +
   `fleiss_kappa`) e o interpreta pela escala de Landis & Koch (1977).
3. Lista os itens sem unanimidade em `divergencias.csv` (pauta da reunião).
4. Gera `rotulos_consenso.csv` pelo protocolo de `docs/protocolo_consenso.md`:
   maioria simples; empates 1-1-1 e revisões decididos em reunião e
   registrados em `decisoes_reuniao.csv`.

Uso: python -m rotulagem.concordancia --config config.yaml
"""
import argparse
import glob
import os
import sys
import unicodedata
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from statsmodels.stats.inter_rater import aggregate_raters, fleiss_kappa

from pipeline.config import load_config

# Valores aceitos em cada dimensão (comparados sem acento e em minúsculas)
CATEGORIAS: Dict[str, List[str]] = {
    "tipo_projeto": ["biblioteca", "aplicacao", "cli", "outro"],
    "entregas_reais": ["sim", "nao", "incerto"],
    "corretiva": ["sim", "nao"],
}
# Dimensões rotuladas por repositório (as demais, por release)
POR_REPOSITORIO = {"tipo_projeto", "entregas_reais"}

ARQUIVO_CONSENSO = "rotulos_consenso.csv"
ARQUIVO_DECISOES = "decisoes_reuniao.csv"

# Landis & Koch (1977): limite superior de cada faixa
LANDIS_KOCH = [
    (0.0, "pobre"),
    (0.20, "leve"),
    (0.40, "razoável"),
    (0.60, "moderada"),
    (0.80, "substancial"),
    (1.0, "quase perfeita"),
]


def normalizar(valor) -> str:
    if valor is None or (isinstance(valor, float) and np.isnan(valor)):
        return ""
    texto = unicodedata.normalize("NFKD", str(valor)).encode("ascii", "ignore").decode()
    return texto.strip().lower()


def interpretar(kappa: float) -> str:
    if np.isnan(kappa):
        return "indefinido"
    if kappa < 0:
        return "pobre"
    for limite, rotulo in LANDIS_KOCH[1:]:
        if kappa <= limite:
            return rotulo
    return LANDIS_KOCH[-1][1]


# ---------------------------------------------------------------------------
# Leitura e conferência
# ---------------------------------------------------------------------------

def carregar_rotulos(pasta: str) -> Dict[str, pd.DataFrame]:
    """{avaliador: planilha}, a partir de rotulos_<avaliador>.csv."""
    rotulos = {}
    for caminho in sorted(glob.glob(os.path.join(pasta, "rotulos_*.csv"))):
        nome = os.path.basename(caminho)[len("rotulos_"):-len(".csv")]
        if nome == "consenso":
            continue
        df = pd.read_csv(caminho, dtype=str, keep_default_na=False)
        for dim in CATEGORIAS:
            df[dim] = df[dim].map(normalizar)
        rotulos[nome] = df
    return rotulos


def conferir(df: pd.DataFrame, planilha: pd.DataFrame) -> List[str]:
    """Problemas que impedem o cálculo: itens faltando, vazios, inválidos."""
    problemas = []
    chave = ["full_name", "tag_name"]
    esperado = set(map(tuple, planilha[chave].values))
    presente = set(map(tuple, df[chave].values))
    for full_name, tag in sorted(esperado - presente):
        problemas.append(f"faltando {full_name} {tag}")
    for full_name, tag in sorted(presente - esperado):
        problemas.append(f"item fora do sorteio {full_name} {tag}")

    for dim, validos in CATEGORIAS.items():
        for _, linha in df.iterrows():
            valor = linha[dim]
            if valor == "":
                problemas.append(f"{dim} vazio em {linha['full_name']} {linha['tag_name']}")
            elif valor not in validos:
                problemas.append(
                    f"{dim}='{valor}' inválido em {linha['full_name']} {linha['tag_name']} "
                    f"(use {', '.join(validos)})"
                )
    for dim in POR_REPOSITORIO:
        distintos = df.groupby("full_name")[dim].nunique()
        for full_name in distintos[distintos > 1].index:
            problemas.append(f"{dim} diferente entre as releases de {full_name}")
    return problemas


# ---------------------------------------------------------------------------
# Kappa de Fleiss
# ---------------------------------------------------------------------------

def matriz(rotulos: Dict[str, pd.DataFrame], dim: str) -> pd.DataFrame:
    """Itens x avaliadores. Itens = repositórios ou releases, conforme a dimensão."""
    chave = ["full_name"] if dim in POR_REPOSITORIO else ["full_name", "tag_name"]
    colunas = []
    for avaliador, df in rotulos.items():
        serie = df.drop_duplicates(chave).set_index(chave)[dim].rename(avaliador)
        colunas.append(serie)
    return pd.concat(colunas, axis=1).sort_index()


def kappa_fleiss(m: pd.DataFrame, categorias: List[str]) -> float:
    codigos = m.apply(lambda col: col.map({c: i for i, c in enumerate(categorias)}))
    tabela, _ = aggregate_raters(codigos.to_numpy(dtype=int), n_cat=len(categorias))
    with np.errstate(divide="ignore", invalid="ignore"):
        return float(fleiss_kappa(tabela, method="fleiss"))


def resumo_kappa(rotulos: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    linhas = []
    for dim, categorias in CATEGORIAS.items():
        m = matriz(rotulos, dim)
        k = kappa_fleiss(m, categorias)
        unanimes = int((m.nunique(axis=1) == 1).sum())
        linhas.append({
            "dimensao": dim,
            "itens": len(m),
            "avaliadores": m.shape[1],
            "kappa_fleiss": round(k, 4),
            "interpretacao": interpretar(k),
            "concordancia_unanime": round(unanimes / len(m), 4),
        })
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# Divergências e consenso
# ---------------------------------------------------------------------------

def divergencias(rotulos: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Itens sem unanimidade, com o rótulo de cada avaliador."""
    partes = []
    for dim in CATEGORIAS:
        m = matriz(rotulos, dim)
        divergentes = m[m.nunique(axis=1) > 1]
        div = divergentes.reset_index()
        if "tag_name" not in div:
            div.insert(1, "tag_name", "")
        div.insert(0, "dimensao", dim)
        div["empate"] = [maioria(valores) is None for _, valores in divergentes.iterrows()]
        partes.append(div)
    return pd.concat(partes, ignore_index=True)


def maioria(valores: pd.Series) -> Optional[str]:
    contagem = valores.value_counts()
    if contagem.iloc[0] * 2 > len(valores):
        return contagem.index[0]
    return None


def consenso(
    rotulos: Dict[str, pd.DataFrame], planilha: pd.DataFrame, decisoes: pd.DataFrame
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Rótulo de consenso por item: decisão da reunião, se houver; senão maioria.
    Retorna (planilha de consenso, itens ainda sem decisão).
    """
    decididos = {
        (d["dimensao"], d["full_name"], d.get("tag_name", "") or ""): normalizar(d["rotulo"])
        for _, d in decisoes.iterrows()
    }
    out = planilha[["item", "full_name", "tag_name", "release_url"]].copy()
    pendentes = []
    for dim in CATEGORIAS:
        m = matriz(rotulos, dim)
        rotulo_item, origem_item = {}, {}
        for idx, valores in m.iterrows():
            full_name, tag = (idx, "") if dim in POR_REPOSITORIO else idx
            chave = (dim, full_name, tag)
            if chave in decididos:
                rotulo_item[(full_name, tag)] = decididos[chave]
                origem_item[(full_name, tag)] = "reuniao"
                continue
            voto = maioria(valores)
            if voto is None:
                pendentes.append(f"{dim} {full_name} {tag}".strip())
            rotulo_item[(full_name, tag)] = voto or ""
            origem_item[(full_name, tag)] = (
                "unanime" if valores.nunique() == 1 else "maioria" if voto else "empate"
            )
        chave_linha = (
            out["full_name"].map(lambda f: (f, ""))
            if dim in POR_REPOSITORIO
            else pd.Series(list(zip(out["full_name"], out["tag_name"])), index=out.index)
        )
        out[dim] = chave_linha.map(rotulo_item)
        out[f"origem_{dim}"] = chave_linha.map(origem_item)
    return out, pendentes


def main():
    parser = argparse.ArgumentParser(description="Kappa de Fleiss e consenso (#59)")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg = load_config(args.config)
    pasta = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(args.config)), cfg["validation"]["dir"])
    )
    planilha = pd.read_csv(os.path.join(pasta, "planilha_rotulagem.csv"), dtype=str, keep_default_na=False)
    rotulos = carregar_rotulos(pasta)
    print(f"[Rótulos] avaliadores: {', '.join(rotulos) or 'nenhum'}")

    problemas = {nome: conferir(df, planilha) for nome, df in rotulos.items()}
    for nome, lista in problemas.items():
        for p in lista[:20]:
            print(f"  [{nome}] {p}")
        if len(lista) > 20:
            print(f"  [{nome}] ... e mais {len(lista) - 20} problemas")
    if any(problemas.values()):
        sys.exit("Corrija as planilhas acima antes de calcular o kappa.")
    if len(rotulos) < 3:
        sys.exit("O kappa de Fleiss da seção 6 pede as planilhas dos três avaliadores.")

    kappas = resumo_kappa(rotulos)
    kappas.to_csv(os.path.join(pasta, "kappa_fleiss.csv"), index=False)
    print("\nKappa de Fleiss:")
    print(kappas.to_string(index=False))

    div = divergencias(rotulos)
    div.to_csv(os.path.join(pasta, "divergencias.csv"), index=False)
    print(f"\n{len(div)} itens divergentes ({int(div['empate'].sum())} empates 1-1-1) em divergencias.csv")

    caminho_decisoes = os.path.join(pasta, ARQUIVO_DECISOES)
    decisoes = (
        pd.read_csv(caminho_decisoes, dtype=str, keep_default_na=False)
        if os.path.exists(caminho_decisoes)
        else pd.DataFrame(columns=["dimensao", "full_name", "tag_name", "rotulo", "justificativa"])
    )
    resultado, pendentes = consenso(rotulos, planilha, decisoes)
    if pendentes:
        print(f"\n{len(pendentes)} empates aguardando a reunião ({ARQUIVO_DECISOES}):")
        for p in pendentes:
            print(f"  {p}")
        sys.exit(1)
    resultado.to_csv(os.path.join(pasta, ARQUIVO_CONSENSO), index=False)
    print(f"\nConsenso gravado em {ARQUIVO_CONSENSO} ({len(resultado)} releases).")


if __name__ == "__main__":
    main()

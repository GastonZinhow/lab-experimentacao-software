"""Etapa 03: estatística descritiva dos incidentes comparáveis.

As tabelas usam apenas categorias equivalentes presentes no mapa das duas
plataformas. Um incidente multicomponente conta uma vez no total da plataforma
e uma vez em cada categoria afetada. Durações ausentes não são imputadas.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go


PASTA_CODIGO = Path(__file__).resolve().parents[1]
ARQUIVO_INCIDENTES = PASTA_CODIGO / "dados" / "processados" / "incidentes.csv"
ARQUIVO_EXEMPLO = PASTA_CODIGO / "dados" / "processados" / "exemplo_incidentes.csv"
ARQUIVO_MAPA = PASTA_CODIGO / "dados" / "mapa_componentes.csv"
PASTA_RESULTADOS = PASTA_CODIGO / "resultados"
ARQUIVO_SAIDA = PASTA_RESULTADOS / "tabelas" / "descritiva.csv"
PASTA_FIGURAS = PASTA_RESULTADOS / "figuras"

PLATAFORMAS = ("github", "gitlab")
CORES = {"github": "#6e40c9", "gitlab": "#fc6d26"}
NOMES = {"github": "GitHub.com", "gitlab": "GitLab.com"}
MESES = pd.period_range("2025-11", "2026-10", freq="M").astype(str).tolist()
COLUNAS_SAIDA = (
    "metrica", "plataforma", "mes", "componente_equivalente", "impacto",
    "n", "valor", "proporcao", "mediana", "q1", "q3", "iqr",
    "minimo", "maximo", "media", "p90", "variancia", "dispersao",
    "unidade", "observacao",
)


def categorias_comparaveis(arquivo_mapa: Path = ARQUIVO_MAPA) -> list[str]:
    mapa = pd.read_csv(arquivo_mapa)
    conjuntos = [
        set(mapa.loc[mapa["plataforma"] == plataforma, "componente_equivalente"])
        for plataforma in PLATAFORMAS
    ]
    return sorted(set.intersection(*conjuntos) - {"fora_do_escopo"})


def carregar_incidentes(
    real: Path = ARQUIVO_INCIDENTES, exemplo: Path = ARQUIVO_EXEMPLO
) -> pd.DataFrame:
    arquivo = real if real.exists() else exemplo
    dados = pd.read_csv(arquivo, dtype={"id": str})
    dados["inicio_utc"] = pd.to_datetime(dados["inicio_utc"], utc=True, errors="coerce")
    dados["fim_utc"] = pd.to_datetime(dados["fim_utc"], utc=True, errors="coerce")
    dados["duracao_min"] = pd.to_numeric(dados["duracao_min"], errors="coerce")
    return dados


def preparar_amostra(
    dados: pd.DataFrame, categorias: list[str]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devolve incidentes únicos e a visão explodida por categoria."""
    explodida = dados.copy()
    explodida["componente_equivalente"] = (
        explodida["componente_equivalente"].fillna("").str.split(";")
    )
    explodida = explodida.explode("componente_equivalente")
    explodida = explodida[explodida["componente_equivalente"].isin(categorias)]
    explodida = explodida.drop_duplicates(
        ["plataforma", "id", "componente_equivalente"]
    ).copy()
    unicos = (
        dados.merge(
            explodida[["plataforma", "id"]].drop_duplicates(),
            on=["plataforma", "id"], how="inner",
        )
        .drop_duplicates(["plataforma", "id"])
        .copy()
    )
    unicos["mes"] = unicos["inicio_utc"].dt.strftime("%Y-%m")
    explodida["mes"] = explodida["inicio_utc"].dt.strftime("%Y-%m")
    return unicos, explodida


def _vazio(**valores: object) -> dict[str, object]:
    linha = {coluna: "" for coluna in COLUNAS_SAIDA}
    linha.update(valores)
    return linha


def _resumo(valores: pd.Series) -> dict[str, object]:
    valores = pd.to_numeric(valores, errors="coerce").dropna()
    if valores.empty:
        return {chave: "" for chave in ("mediana", "q1", "q3", "iqr", "minimo", "maximo", "media", "p90")}
    q1 = float(valores.quantile(0.25))
    q3 = float(valores.quantile(0.75))
    return {
        "mediana": float(valores.median()), "q1": q1, "q3": q3,
        "iqr": q3 - q1, "minimo": float(valores.min()),
        "maximo": float(valores.max()), "media": float(valores.mean()),
        "p90": float(valores.quantile(0.90)),
    }


def frequencias(
    unicos: pd.DataFrame, explodida: pd.DataFrame, categorias: list[str]
) -> list[dict[str, object]]:
    linhas: list[dict[str, object]] = []
    totais = unicos.groupby(["plataforma", "mes"])["id"].nunique()
    por_componente = explodida.groupby(
        ["plataforma", "mes", "componente_equivalente"]
    )["id"].nunique()
    for plataforma in PLATAFORMAS:
        valores_mensais = []
        for mes in MESES:
            valor = int(totais.get((plataforma, mes), 0))
            valores_mensais.append(valor)
            linhas.append(_vazio(
                metrica="frequencia_mensal", plataforma=plataforma, mes=mes,
                n=valor, valor=valor, unidade="incidentes",
                observacao="Incidente conta uma vez no total da plataforma.",
            ))
            for componente in categorias:
                valor = int(por_componente.get((plataforma, mes, componente), 0))
                linhas.append(_vazio(
                    metrica="frequencia_mensal_componente", plataforma=plataforma,
                    mes=mes, componente_equivalente=componente, n=valor,
                    valor=valor, unidade="incidentes",
                    observacao="Multicomponente conta uma vez em cada categoria.",
                ))
        serie = pd.Series(valores_mensais, dtype=float)
        media = float(serie.mean())
        linhas.append(_vazio(
            metrica="frequencia_resumo", plataforma=plataforma, n=len(serie),
            valor=int(serie.sum()), variancia=float(serie.var(ddof=1)),
            dispersao=float(serie.var(ddof=1) / media) if media else "",
            unidade="incidentes/mês", observacao=(
                "Valor é o total; dispersão é variância amostral dividida pela média."
            ), **_resumo(serie),
        ))
    return linhas


def duracoes(unicos: pd.DataFrame) -> list[dict[str, object]]:
    linhas = []
    for plataforma in PLATAFORMAS:
        valores = unicos.loc[unicos["plataforma"] == plataforma, "duracao_min"].dropna()
        linhas.append(_vazio(
            metrica="duracao", plataforma=plataforma, n=len(valores),
            unidade="minutos", observacao="Média é apoio; mediana e IQR são o resumo principal.",
            **_resumo(valores),
        ))
    return linhas


def _intervalos(grupo: pd.DataFrame) -> pd.Series:
    ordenado = grupo.sort_values(["inicio_utc", "fim_utc", "id"])
    anterior = ordenado["fim_utc"].shift(1)
    minutos = (ordenado["inicio_utc"] - anterior).dt.total_seconds() / 60
    return minutos.dropna().clip(lower=0)


def mtbf(
    unicos: pd.DataFrame, explodida: pd.DataFrame, categorias: list[str]
) -> list[dict[str, object]]:
    linhas = []
    for plataforma in PLATAFORMAS:
        grupos = [("todos", unicos[unicos["plataforma"] == plataforma])]
        grupos.extend(
            (categoria, explodida[
                (explodida["plataforma"] == plataforma)
                & (explodida["componente_equivalente"] == categoria)
            ])
            for categoria in categorias
        )
        for componente, grupo in grupos:
            valores = _intervalos(grupo)
            linhas.append(_vazio(
                metrica="mtbf_proxy", plataforma=plataforma,
                componente_equivalente=componente, n=len(valores),
                valor=float(valores.mean()) if len(valores) else "",
                unidade="minutos", observacao=(
                    "Tempo operacional entre fim e próximo início; sobreposição vira zero."
                ), **_resumo(valores),
            ))
    return linhas


def impactos(unicos: pd.DataFrame) -> list[dict[str, object]]:
    linhas = []
    for plataforma in PLATAFORMAS:
        valores = unicos.loc[unicos["plataforma"] == plataforma, "impacto"]
        valores = valores.fillna("").replace("", "nao_informado")
        contagens = valores.value_counts().sort_index()
        total = int(contagens.sum())
        for impacto, quantidade in contagens.items():
            linhas.append(_vazio(
                metrica="distribuicao_impacto", plataforma=plataforma,
                impacto=impacto, n=int(quantidade), valor=int(quantidade),
                proporcao=float(quantidade / total) if total else "",
                unidade="incidentes", observacao="Classes preservadas como publicadas.",
            ))
    return linhas


def calcular_descritiva(
    dados: pd.DataFrame, categorias: list[str]
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    unicos, explodida = preparar_amostra(dados, categorias)
    linhas = (
        frequencias(unicos, explodida, categorias)
        + duracoes(unicos)
        + mtbf(unicos, explodida, categorias)
        + impactos(unicos)
    )
    tabela = pd.DataFrame(linhas, columns=COLUNAS_SAIDA)
    return tabela, unicos, explodida


def _salvar_figura(figura: go.Figure, caminho: Path, identificador: str) -> None:
    caminho.write_text(
        figura.to_html(
            full_html=True, include_plotlyjs="cdn", div_id=identificador,
            config={"displaylogo": False, "responsive": True},
        ), encoding="utf-8", newline="\n",
    )


def gerar_figuras(
    tabela: pd.DataFrame, unicos: pd.DataFrame, explodida: pd.DataFrame,
    categorias: list[str], pasta: Path = PASTA_FIGURAS,
) -> None:
    pasta.mkdir(parents=True, exist_ok=True)
    mensal = tabela[tabela["metrica"] == "frequencia_mensal"]
    serie = go.Figure()
    for plataforma in PLATAFORMAS:
        parte = mensal[mensal["plataforma"] == plataforma]
        serie.add_bar(
            x=parte["mes"], y=parte["valor"], name=NOMES[plataforma],
            marker_color=CORES[plataforma],
        )
    serie.update_layout(
        title="Incidentes publicados por mês", xaxis_title="Mês (UTC)",
        yaxis_title="Número de incidentes", legend_title="Plataforma",
        barmode="group", template="plotly_white",
    )
    _salvar_figura(serie, pasta / "serie_mensal.html", "serie-mensal")

    violino = go.Figure()
    for plataforma in PLATAFORMAS:
        valores = unicos.loc[
            (unicos["plataforma"] == plataforma) & (unicos["duracao_min"] > 0),
            "duracao_min",
        ]
        violino.add_trace(go.Violin(
            y=valores, name=NOMES[plataforma], line_color=CORES[plataforma],
            box_visible=True, meanline_visible=True, points="all", jitter=0.25,
        ))
    violino.update_layout(
        title="Distribuição da duração dos incidentes", xaxis_title="Plataforma",
        yaxis_title="Duração (minutos, escala log)", yaxis_type="log",
        legend_title="Plataforma", template="plotly_white",
    )
    _salvar_figura(violino, pasta / "duracao_violino.html", "duracao-violino")

    barras = go.Figure()
    contagens = explodida.groupby(
        ["plataforma", "componente_equivalente"]
    )["id"].nunique()
    for plataforma in PLATAFORMAS:
        barras.add_bar(
            x=categorias,
            y=[int(contagens.get((plataforma, categoria), 0)) for categoria in categorias],
            name=NOMES[plataforma], marker_color=CORES[plataforma],
        )
    barras.update_layout(
        title="Incidentes por componente equivalente", xaxis_title="Componente equivalente",
        yaxis_title="Número de incidentes", legend_title="Plataforma",
        barmode="group", template="plotly_white",
    )
    _salvar_figura(barras, pasta / "incidentes_componente.html", "incidentes-componente")


def main() -> None:
    categorias = categorias_comparaveis()
    tabela, unicos, explodida = calcular_descritiva(carregar_incidentes(), categorias)
    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(ARQUIVO_SAIDA, index=False, lineterminator="\n", float_format="%.4f")
    gerar_figuras(tabela, unicos, explodida, categorias)
    totais = unicos.groupby("plataforma")["id"].nunique().to_dict()
    print(
        "Descritiva: "
        + ", ".join(f"{plataforma}={totais.get(plataforma, 0)}" for plataforma in PLATAFORMAS)
        + " incidentes comparáveis."
    )


if __name__ == "__main__":
    main()

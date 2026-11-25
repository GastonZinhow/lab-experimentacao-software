"""Etapa 03: estatística descritiva dos incidentes comparáveis.

As tabelas usam apenas categorias equivalentes presentes no mapa das duas
plataformas. Um incidente multicomponente conta uma vez no total da plataforma
e uma vez em cada categoria afetada. Durações ausentes não são imputadas.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.offline


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
    config = {
        "displaylogo": False,
        "responsive": True,
        "scrollZoom": True,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        "toImageButtonOptions": {"filename": identificador, "scale": 2},
    }
    caminho.write_text(
        figura.to_html(
            full_html=True, include_plotlyjs="cdn", div_id=identificador,
            config=config,
        ), encoding="utf-8", newline="\n",
    )


def _estilo_comum(figura: go.Figure) -> None:
    figura.update_layout(
        template="plotly_white", height=540,
        margin={"l": 70, "r": 35, "t": 105, "b": 70},
        font={"family": "Inter, Segoe UI, sans-serif", "color": "#172033"},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(248,250,252,.72)",
        hoverlabel={"bgcolor": "white", "font_size": 13, "font_family": "Inter, Segoe UI, sans-serif"},
        legend={
            "orientation": "h", "yanchor": "bottom", "y": 1.04,
            "xanchor": "right", "x": 1, "title_text": "",
        },
        title={"x": 0, "xanchor": "left", "font": {"size": 22}},
    )
    figura.update_xaxes(showgrid=False, zeroline=False, linecolor="#d8deea")
    figura.update_yaxes(gridcolor="#e8ecf3", zeroline=False, linecolor="#d8deea")


def construir_figuras(
    tabela: pd.DataFrame, unicos: pd.DataFrame, explodida: pd.DataFrame,
    categorias: list[str],
) -> list[tuple[str, str, str, go.Figure]]:
    mensal = tabela[tabela["metrica"] == "frequencia_mensal"]
    serie = go.Figure()
    valores_serie: list[list[float]] = []
    acumulados: list[list[float]] = []
    for plataforma in PLATAFORMAS:
        parte = mensal[mensal["plataforma"] == plataforma]
        valores = parte["valor"].astype(float).tolist()
        valores_serie.append(valores)
        acumulados.append(pd.Series(valores).cumsum().tolist())
        serie.add_bar(
            x=parte["mes"], y=valores, name=NOMES[plataforma],
            marker={"color": CORES[plataforma], "line": {"color": "white", "width": 1}},
            hovertemplate=(
                f"<b>{NOMES[plataforma]}</b><br>Mês: %{{x}}"
                "<br>Incidentes: %{y:.0f}<extra></extra>"
            ),
        )
    serie.update_layout(
        title={"text": "Incidentes publicados por mês<sup> categorias comparáveis</sup>"},
        xaxis_title="Mês de início (UTC)", yaxis_title="Número de incidentes",
        barmode="group", hovermode="x unified",
        updatemenus=[{
            "type": "buttons", "direction": "right", "x": 0, "y": 1.19,
            "showactive": True, "active": 0,
            "buttons": [
                {"label": "Mensal", "method": "update", "args": [
                    {"y": valores_serie}, {"yaxis.title.text": "Número de incidentes"},
                ]},
                {"label": "Acumulado", "method": "update", "args": [
                    {"y": acumulados}, {"yaxis.title.text": "Incidentes acumulados"},
                ]},
            ],
        }],
    )
    _estilo_comum(serie)

    violino = go.Figure()
    for plataforma in PLATAFORMAS:
        parte = unicos.loc[
            (unicos["plataforma"] == plataforma) & (unicos["duracao_min"] > 0),
            ["duracao_min", "titulo", "inicio_utc", "componente_equivalente"],
        ].copy()
        parte["inicio"] = parte["inicio_utc"].dt.strftime("%d/%m/%Y %H:%M UTC")
        violino.add_trace(go.Violin(
            y=parte["duracao_min"], name=NOMES[plataforma], line_color=CORES[plataforma],
            fillcolor=CORES[plataforma], opacity=0.62,
            box_visible=True, meanline_visible=True, points="all", jitter=0.25,
            pointpos=0, customdata=parte[["titulo", "inicio", "componente_equivalente"]],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>Duração: %{y:.1f} min"
                "<br>Início: %{customdata[1]}<br>Componentes: %{customdata[2]}"
                "<extra></extra>"
            ),
        ))
    violino.update_layout(
        title={"text": "Distribuição da duração<sup> pontos = incidentes individuais</sup>"},
        xaxis_title="Plataforma",
        yaxis_title="Duração (minutos, escala log)", yaxis_type="log",
        violinmode="group",
        updatemenus=[{
            "type": "buttons", "direction": "right", "x": 0, "y": 1.19,
            "showactive": True, "active": 0,
            "buttons": [
                {"label": "Escala log", "method": "relayout", "args": [{
                    "yaxis.type": "log", "yaxis.title.text": "Duração (minutos, escala log)",
                }]},
                {"label": "Escala linear", "method": "relayout", "args": [{
                    "yaxis.type": "linear", "yaxis.title.text": "Duração (minutos)",
                }]},
            ],
        }],
    )
    _estilo_comum(violino)

    barras = go.Figure()
    contagens = explodida.groupby(
        ["plataforma", "componente_equivalente"]
    )["id"].nunique()
    valores_componentes: list[list[float]] = []
    percentuais: list[list[float]] = []
    for plataforma in PLATAFORMAS:
        valores = [int(contagens.get((plataforma, categoria), 0)) for categoria in categorias]
        total = int(explodida.loc[explodida["plataforma"] == plataforma, "id"].nunique())
        valores_componentes.append(valores)
        percentuais.append([100 * valor / total if total else 0 for valor in valores])
        barras.add_bar(
            x=categorias, y=valores, name=NOMES[plataforma],
            marker={"color": CORES[plataforma], "line": {"color": "white", "width": 1}},
            text=valores, textposition="outside", cliponaxis=False,
            hovertemplate=(
                f"<b>{NOMES[plataforma]}</b><br>Componente: %{{x}}"
                "<br>Incidentes: %{y:.0f}<extra></extra>"
            ),
        )
    barras.update_layout(
        title={"text": "Incidentes por componente equivalente<sup> multicomponente aparece em cada categoria</sup>"},
        xaxis_title="Componente equivalente", yaxis_title="Número de incidentes",
        barmode="group",
        updatemenus=[{
            "type": "buttons", "direction": "right", "x": 0, "y": 1.19,
            "showactive": True, "active": 0,
            "buttons": [
                {"label": "Quantidade", "method": "update", "args": [
                    {"y": valores_componentes, "text": valores_componentes},
                    {"yaxis.title.text": "Número de incidentes", "yaxis.ticksuffix": ""},
                ]},
                {"label": "% da plataforma", "method": "update", "args": [
                    {"y": percentuais, "text": [[f"{v:.1f}%" for v in linha] for linha in percentuais]},
                    {"yaxis.title.text": "Incidentes da plataforma (%)", "yaxis.ticksuffix": "%"},
                ]},
            ],
        }],
    )
    _estilo_comum(barras)
    return [
        ("Frequência mensal", "Como os incidentes se distribuíram ao longo dos 12 meses.", "serie-mensal", serie),
        ("Tempo de recuperação", "Distribuição completa, quartis, média e casos extremos.", "duracao-violino", violino),
        ("Componentes afetados", "Onde os incidentes comparáveis se concentraram.", "incidentes-componente", barras),
    ]


def _salvar_painel(
    figuras: list[tuple[str, str, str, go.Figure]], tabela: pd.DataFrame,
    caminho: Path,
) -> None:
    config = {
        "displaylogo": False, "responsive": True, "scrollZoom": True,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    }
    slides = []
    botoes = []
    pontos = []
    for indice, (titulo, descricao, identificador, figura) in enumerate(figuras):
        grafico = figura.to_html(
            full_html=False, include_plotlyjs=False, div_id=f"painel-{identificador}",
            config=config,
        )
        ativo = " active" if indice == 0 else ""
        slides.append(
            f'<section class="slide{ativo}" data-index="{indice}" aria-label="{escape(titulo)}">'
            f'<div class="slide-heading"><div><span class="eyebrow">VISUAL {indice + 1}</span>'
            f'<h2>{escape(titulo)}</h2><p>{escape(descricao)}</p></div></div>{grafico}</section>'
        )
        botoes.append(
            f'<button class="tab{ativo}" data-go="{indice}" type="button">{escape(titulo)}</button>'
        )
        pontos.append(
            f'<button class="dot{ativo}" data-go="{indice}" type="button" aria-label="Ir ao gráfico {indice + 1}"></button>'
        )

    resumo = tabela[tabela["metrica"] == "frequencia_resumo"].set_index("plataforma")
    duracao = tabela[tabela["metrica"] == "duracao"].set_index("plataforma")
    total_github = int(resumo.loc["github", "valor"])
    total_gitlab = int(resumo.loc["gitlab", "valor"])
    mediana_github = float(duracao.loc["github", "mediana"])
    mediana_gitlab = float(duracao.loc["gitlab", "mediana"])
    conteudo = "".join(slides)
    navegacao = "".join(botoes)
    indicadores = "".join(pontos)
    pagina = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Confiabilidade operacional · GitHub × GitLab</title>
  <script src="https://cdn.plot.ly/plotly-{plotly.offline.get_plotlyjs_version()}.min.js"></script>
  <style>
    :root {{ --ink:#172033; --muted:#667085; --line:#dde3ee; --card:rgba(255,255,255,.86); --purple:#6e40c9; --orange:#fc6d26; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; min-height:100vh; color:var(--ink); font-family:Inter,"Segoe UI",sans-serif;
      background:radial-gradient(circle at 8% 4%,#eee8ff 0,transparent 30%),radial-gradient(circle at 92% 10%,#fff0e8 0,transparent 28%),#f5f7fb; }}
    .shell {{ width:min(1240px,calc(100% - 32px)); margin:auto; padding:28px 0 38px; }}
    header {{ display:grid; grid-template-columns:1fr auto; gap:24px; align-items:end; margin-bottom:22px; }}
    .kicker,.eyebrow {{ color:var(--purple); font-weight:800; letter-spacing:.13em; font-size:11px; }}
    h1 {{ margin:7px 0 6px; font-size:clamp(28px,4vw,46px); letter-spacing:-.04em; }}
    header p,.slide-heading p {{ margin:0; color:var(--muted); line-height:1.55; }}
    .keys {{ color:var(--muted); font-size:13px; padding:10px 13px; border:1px solid var(--line); border-radius:12px; background:#fff; white-space:nowrap; }}
    kbd {{ padding:2px 7px; border:1px solid #cbd3df; border-bottom-width:2px; border-radius:6px; background:#f8fafc; color:var(--ink); }}
    .kpis {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:16px; }}
    .kpi {{ padding:15px 17px; border:1px solid var(--line); border-radius:16px; background:var(--card); box-shadow:0 8px 30px rgba(20,30,55,.04); }}
    .kpi span {{ color:var(--muted); font-size:12px; }} .kpi strong {{ display:block; margin-top:4px; font-size:22px; }}
    .purple {{ color:var(--purple); }} .orange {{ color:var(--orange); }}
    .tabs {{ display:flex; gap:8px; overflow:auto; padding:4px 2px 12px; }}
    .tab {{ border:1px solid var(--line); background:rgba(255,255,255,.68); color:var(--muted); padding:10px 14px; border-radius:999px; cursor:pointer; font-weight:650; white-space:nowrap; }}
    .tab:hover,.tab.active {{ background:var(--ink); color:#fff; border-color:var(--ink); }}
    .stage {{ position:relative; border:1px solid var(--line); border-radius:24px; background:var(--card); box-shadow:0 20px 60px rgba(25,32,50,.09); overflow:hidden; }}
    .slide {{ display:none; padding:22px 24px 8px; animation:enter .28s ease-out; }} .slide.active {{ display:block; }}
    @keyframes enter {{ from {{ opacity:0; transform:translateX(16px); }} to {{ opacity:1; transform:none; }} }}
    .slide-heading h2 {{ margin:4px 0 3px; font-size:21px; }}
    .controls {{ display:flex; align-items:center; justify-content:center; gap:12px; margin-top:15px; }}
    .arrow {{ width:44px; height:44px; border-radius:50%; border:1px solid var(--line); background:#fff; color:var(--ink); cursor:pointer; font-size:22px; }}
    .arrow:hover {{ transform:translateY(-2px); box-shadow:0 8px 20px rgba(20,30,55,.12); }}
    .dots {{ display:flex; gap:7px; }} .dot {{ width:8px; height:8px; padding:0; border:0; border-radius:9px; background:#cbd3df; cursor:pointer; transition:.2s; }}
    .dot.active {{ width:26px; background:var(--purple); }} .counter {{ min-width:42px; color:var(--muted); font-size:13px; }}
    .hint {{ text-align:center; color:var(--muted); font-size:12px; margin:12px 0 0; }}
    @media(max-width:760px) {{ header {{ grid-template-columns:1fr; }} .keys {{ display:none; }} .kpis {{ grid-template-columns:1fr 1fr; }} .slide {{ padding:18px 8px 4px; }} }}
  </style>
</head>
<body><main class="shell">
  <header><div><span class="kicker">LAB05 · ESTATÍSTICA DESCRITIVA</span><h1>Confiabilidade operacional</h1>
    <p>Incidentes publicados entre nov/2025 e out/2026 · componentes equivalentes.</p></div>
    <div class="keys"><kbd>←</kbd> <kbd>→</kbd> para trocar de gráfico</div></header>
  <section class="kpis" aria-label="Resumo"><div class="kpi"><span>Incidentes GitHub</span><strong class="purple">{total_github}</strong></div>
    <div class="kpi"><span>Incidentes GitLab</span><strong class="orange">{total_gitlab}</strong></div>
    <div class="kpi"><span>Duração mediana GitHub</span><strong>{mediana_github:.1f} min</strong></div>
    <div class="kpi"><span>Duração mediana GitLab</span><strong>{mediana_gitlab:.1f} min</strong></div></section>
  <nav class="tabs" aria-label="Escolher visual">{navegacao}</nav>
  <div class="stage" aria-live="polite">{conteudo}</div>
  <div class="controls"><button class="arrow" id="prev" aria-label="Gráfico anterior">←</button><div class="dots">{indicadores}</div>
    <span class="counter" id="counter">1 / {len(figuras)}</span><button class="arrow" id="next" aria-label="Próximo gráfico">→</button></div>
  <p class="hint">Passe o mouse para ver detalhes · clique na legenda para ocultar uma plataforma · use os botões dentro de cada gráfico.</p>
</main><script>
  const slides=[...document.querySelectorAll('.slide')], tabs=[...document.querySelectorAll('.tab')], dots=[...document.querySelectorAll('.dot')]; let current=0;
  function show(index) {{ current=(index+slides.length)%slides.length; slides.forEach((el,i)=>el.classList.toggle('active',i===current));
    tabs.forEach((el,i)=>el.classList.toggle('active',i===current)); dots.forEach((el,i)=>el.classList.toggle('active',i===current));
    document.getElementById('counter').textContent=`${{current+1}} / ${{slides.length}}`; const plot=slides[current].querySelector('.plotly-graph-div'); if(plot) requestAnimationFrame(()=>Plotly.Plots.resize(plot)); }}
  document.querySelectorAll('[data-go]').forEach(el=>el.addEventListener('click',()=>show(Number(el.dataset.go))));
  document.getElementById('prev').addEventListener('click',()=>show(current-1)); document.getElementById('next').addEventListener('click',()=>show(current+1));
  document.addEventListener('keydown',event=>{{ if(event.key==='ArrowLeft') show(current-1); if(event.key==='ArrowRight') show(current+1); }});
  let startX=null; document.querySelector('.stage').addEventListener('touchstart',e=>startX=e.touches[0].clientX,{{passive:true}});
  document.querySelector('.stage').addEventListener('touchend',e=>{{ if(startX===null)return; const dx=e.changedTouches[0].clientX-startX; if(Math.abs(dx)>55) show(current+(dx<0?1:-1)); startX=null; }},{{passive:true}});
  show(0);
</script></body></html>"""
    caminho.write_text(pagina, encoding="utf-8", newline="\n")


def gerar_figuras(
    tabela: pd.DataFrame, unicos: pd.DataFrame, explodida: pd.DataFrame,
    categorias: list[str], pasta: Path = PASTA_FIGURAS,
) -> None:
    pasta.mkdir(parents=True, exist_ok=True)
    figuras = construir_figuras(tabela, unicos, explodida, categorias)
    for _, _, identificador, figura in figuras:
        _salvar_figura(figura, pasta / f"{identificador.replace('-', '_')}.html", identificador)
    _salvar_painel(figuras, tabela, pasta / "painel_descritiva.html")


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

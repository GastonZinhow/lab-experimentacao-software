"""
Dashboard de visualizacao do experimento (LAB02, issue #45).

Cobre o Passo 6 do enunciado: importa os dados do experimento e gera
graficos comparando os tratamentos `IA` e `Manual` em tempo (RQ1), taxa de
sucesso (RQ2) e metricas estaticas (RQ3).

Entradas (lidas a cada execucao, entao basta rodar de novo quando novos
trials forem registrados):

    data/raw/trials.csv                  -> RQ1 e RQ2 (register_trial.py)
    data/processed/ck/<run_id>/*.csv     -> RQ3, WMC e LOC (run_static_metrics.ps1)
    data/processed/cpd-<run_id>.xml      -> RQ3, duplicacao (PMD CPD)

Saidas em data/processed/charts:

    rq1_tempo_por_tratamento.png
    rq1_tempo_por_kata.png
    rq2_taxa_sucesso.png
    rq3_metricas_estaticas.png
    dashboard.png                        (visao consolidada das tres RQs)

Uso:

    python scripts/dashboard.py
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Patch, Rectangle  # noqa: E402
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator  # noqa: E402
from matplotlib.transforms import IdentityTransform, blended_transform_factory  # noqa: E402

CODE_DIR = Path(__file__).resolve().parent.parent
TRIALS_CSV = CODE_DIR / "data" / "raw" / "trials.csv"
PROCESSED_DIR = CODE_DIR / "data" / "processed"
CK_DIR = PROCESSED_DIR / "ck"
CHARTS_DIR = PROCESSED_DIR / "charts"

TIMEBOX_MIN = 35

KATAS = {
    "K01": ("Is Subsequence", "Fácil"),
    "K02": ("Find if Path Exists in Graph", "Fácil"),
    "K03": ("House Robber", "Média"),
    "K04": ("Flower Planting With No Adjacent", "Média"),
    "K05": ("Longest Cycle in a Graph", "Difícil"),
    "K06": ("N-Queens II", "Difícil"),
}

TRATAMENTOS = ["IA", "Manual"]
ROTULOS = {"IA": "Com IA (Copilot)", "Manual": "Manual"}

# ---------------------------------------------------------------------------
# Estilo: paleta categorica validada (slots 1 e 2) + tinta neutra para texto
# ---------------------------------------------------------------------------

COR = {"IA": "#2a78d6", "Manual": "#eb6834"}
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
CRITICAL = "#d03b3b"
TILE_BORDER = "#e6e5df"

DPI = 200
PX = DPI / 100  # pixels de tela por "pixel logico" (imagens em 2x)


def pt(px):
    """Converte pixels logicos em pontos (largura de linha / tamanho de marcador)."""
    return px * 0.72


def fonte_disponivel(preferidas=("Segoe UI", "Inter", "Helvetica Neue", "Arial")):
    instaladas = {f.name for f in font_manager.fontManager.ttflist}
    return next((f for f in preferidas if f in instaladas), "DejaVu Sans")


plt.rcParams.update({
    "font.family": fonte_disponivel(),
    "font.size": 9.5,
    "text.color": INK,
    "axes.edgecolor": BASELINE,
    "axes.labelcolor": INK_2,
    "axes.facecolor": SURFACE,
    "figure.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelcolor": MUTED,
    "ytick.labelcolor": MUTED,
    "xtick.major.size": 0,
    "ytick.major.size": 0,
    "axes.unicode_minus": False,
})


def fmt(valor, casas=1):
    """Numero no formato pt-BR (virgula decimal, ponto de milhar)."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def fmt_min(valor):
    return f"{fmt(valor, 1)} min"


# ---------------------------------------------------------------------------
# Carga dos dados
# ---------------------------------------------------------------------------


def nome_participante(bruto):
    return re.split(r"[_\-\s]", str(bruto).strip())[0].capitalize()


def carregar_trials():
    df = pd.read_csv(TRIALS_CSV)
    df["participante"] = df["integrante"].map(nome_participante)
    df["kata"] = df["kata"].str.upper()
    df["tempo_min"] = df["tempo_segundos"].astype(float) / 60
    df["censurado"] = df["censurado"].astype(str).str.lower() == "true"
    df["testes_falhando"] = df["testes_total"] - df["testes_passando"]
    return df


def duplicacao_cpd(run_id):
    """% de tokens duplicados segundo o PMD CPD (0 se nao houver duplicacao)."""
    xml_path = PROCESSED_DIR / "cpd" / f"cpd-{run_id}.xml"
    if not xml_path.exists():
        return float("nan")
    raiz = ET.parse(xml_path).getroot()
    ns = {"c": raiz.tag.split("}")[0].strip("{")} if raiz.tag.startswith("{") else {}
    pref = "c:" if ns else ""
    total = sum(int(f.get("totalNumberOfTokens", 0)) for f in raiz.findall(f"{pref}file", ns))
    duplicados = 0
    for dup in raiz.findall(f"{pref}duplication", ns):
        ocorrencias = len(dup.findall(f"{pref}file", ns))
        duplicados += int(dup.get("tokens", 0)) * max(ocorrencias - 1, 0)
    return 100 * duplicados / total if total else 0.0


def carregar_metricas_estaticas():
    linhas = []
    for pasta in sorted(CK_DIR.glob("*")):
        m = re.match(r"^(.*)-(k\d+)-(ia|manual)$", pasta.name, re.IGNORECASE)
        if not m or not (pasta / "class.csv").exists():
            continue
        classes = pd.read_csv(pasta / "class.csv")
        metodos = pd.read_csv(pasta / "method.csv")
        wmc = classes["wmc"].sum()
        loc = classes["loc"].sum()
        linhas.append({
            "participante": nome_participante(m.group(1)),
            "kata": m.group(2).upper(),
            "tratamento": "IA" if m.group(3).lower() == "ia" else "Manual",
            "wmc": wmc,
            "loc": loc,
            "metodos": len(metodos),
            "wmc_por_loc": wmc / loc if loc else float("nan"),
            "duplicacao_pct": duplicacao_cpd(pasta.name),
        })
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# Primitivas de desenho (marcas com cantos arredondados em pixels reais)
# ---------------------------------------------------------------------------


def eixos(fig, esq, topo, larg, alt):
    """Cria eixos posicionados em polegadas a partir do canto superior esquerdo."""
    w, h = fig.get_size_inches()
    return fig.add_axes([esq / w, 1 - (topo + alt) / h, larg / w, alt / h])


def texto(fig, x, y_topo, s, **kw):
    w, h = fig.get_size_inches()
    kw.setdefault("va", "top")
    return fig.text(x / w, 1 - y_topo / h, s, **kw)


def cabecalho(fig, x, y, titulo, subtitulo=None, tamanho=15):
    texto(fig, x, y, titulo, fontsize=tamanho, fontweight="semibold", color=INK)
    if subtitulo:
        texto(fig, x, y + tamanho / 72 * 1.55, subtitulo, fontsize=10, color=INK_2, linespacing=1.45)


def rodape(fig, s):
    texto(fig, 0.45, fig.get_size_inches()[1] - 0.28, s, fontsize=8, color=MUTED)


def estilo_eixos(ax, grade="x"):
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.spines["bottom"].set_linewidth(pt(1))
    ax.grid(axis=grade, color=GRID, linewidth=pt(1), linestyle="-")
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", labelsize=8.5, pad=6)


def barra_h(ax, y, x0, x1, cor, espessura_px=24, raio_px=4, arredondar_base=False, zorder=3):
    """Barra horizontal com a ponta de dados arredondada e a base reta."""
    X0, Y = ax.transData.transform((x0, y))
    X1, _ = ax.transData.transform((x1, y))
    largura, altura = X1 - X0, espessura_px * PX
    if largura <= 0:
        return
    r = min(raio_px * PX, largura / 2, altura / 2)
    comum = dict(transform=IdentityTransform(), facecolor=cor, edgecolor="none", zorder=zorder, clip_on=False)
    ax.add_artist(FancyBboxPatch((X0, Y - altura / 2), largura, altura,
                                 boxstyle=f"round,pad=0,rounding_size={r}", **comum))
    if not arredondar_base:
        ax.add_artist(Rectangle((X0, Y - altura / 2), max(largura - r, 0), altura, **comum))


def faixa(ax, y, x0, x1, cor, altura_px, alpha, raio_px=4):
    X0, Y = ax.transData.transform((x0, y))
    X1, _ = ax.transData.transform((x1, y))
    altura = altura_px * PX
    ax.add_artist(FancyBboxPatch((X0, Y - altura / 2), X1 - X0, altura,
                                 boxstyle=f"round,pad=0,rounding_size={raio_px * PX}",
                                 transform=IdentityTransform(), facecolor=cor, alpha=alpha,
                                 edgecolor="none", zorder=1, clip_on=False))


def pontos(ax, xs, ys, cor, zorder=4):
    ax.plot(xs, ys, linestyle="none", marker="o", markersize=pt(11), markerfacecolor=cor,
            markeredgecolor=SURFACE, markeredgewidth=pt(2), zorder=zorder, clip_on=False)


def eixo_tempo_log(ax):
    ax.set_xscale("log")
    ax.set_xlim(0.3, 48)
    ticks = [0.5, 1, 2, 5, 10, 20, 35]
    ax.xaxis.set_major_locator(FixedLocator(ticks))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt(v, 1 if v < 1 else 0)))


def linha_timebox(ax, y_texto):
    ax.plot([TIMEBOX_MIN] * 2, [ax.get_ylim()[0], y_texto - 0.05], color=BASELINE,
            linewidth=pt(1), zorder=1)
    ax.text(TIMEBOX_MIN, y_texto, "time-box\n35 min", ha="center", va="bottom",
            fontsize=8, color=MUTED, linespacing=1.2)


def legenda_tratamentos(ax, y=1.02, x=0.0):
    alcas = [Line2D([], [], linestyle="none", marker="o", markersize=pt(11), markerfacecolor=COR[t],
                    markeredgecolor=SURFACE, markeredgewidth=pt(2), label=ROTULOS[t]) for t in TRATAMENTOS]
    ax.legend(handles=alcas, loc="lower left", bbox_to_anchor=(x, y), ncol=2, frameon=False,
              fontsize=9, labelcolor=INK_2, handletextpad=0.3, columnspacing=1.6, borderaxespad=0)


def mediana_iqr(serie):
    return serie.median(), serie.quantile(0.25), serie.quantile(0.75)


# ---------------------------------------------------------------------------
# RQ1 - tempo
# ---------------------------------------------------------------------------


def desenhar_tempo_por_tratamento(ax, trials):
    estilo_eixos(ax, grade="x")
    eixo_tempo_log(ax)
    ax.set_ylim(-0.7, 1.75)
    ax.set_yticks([])
    ax.set_xlabel("Tempo até passar em todos os testes (min, escala logarítmica)", fontsize=8.5,
                  color=MUTED, labelpad=8)
    linha_timebox(ax, 1.42)

    posicoes = {"IA": 1, "Manual": 0}
    rotulo_x = blended_transform_factory(ax.transAxes, ax.transData)
    for trat, y in posicoes.items():
        tempos = trials.loc[trials["tratamento"] == trat, "tempo_min"].sort_values()
        if tempos.empty:
            continue
        med, q1, q3 = mediana_iqr(tempos)
        faixa(ax, y, q1, q3, COR[trat], altura_px=34, alpha=0.14)
        ax.plot([med, med], [y - 0.26, y + 0.26], color=INK, linewidth=pt(2), zorder=5,
                solid_capstyle="butt")
        deslocamentos = [(-0.09 if i % 2 == 0 else 0.09) for i in range(len(tempos))]
        pontos(ax, tempos.values, [y + d for d in deslocamentos], COR[trat])
        ax.text(med, y + 0.34, f"mediana {fmt_min(med)}", ha="center", va="bottom",
                fontsize=8.5, color=INK, fontweight="semibold")

        n = len(tempos)
        censurados = int(trials.loc[trials["tratamento"] == trat, "censurado"].sum())
        ax.text(-0.02, y + 0.07, ROTULOS[trat], transform=rotulo_x, ha="right", va="bottom",
                fontsize=9.5, color=INK, fontweight="semibold")
        ax.text(-0.02, y - 0.03, f"{n} trials · {censurados} censurados", transform=rotulo_x,
                ha="right", va="top", fontsize=8, color=MUTED)

    alcas = [
        Line2D([], [], linestyle="none", marker="o", markersize=pt(9), markerfacecolor=MUTED,
               markeredgecolor=SURFACE, label="trial"),
        Line2D([], [], color=INK, linewidth=pt(2), label="mediana"),
        Patch(facecolor=MUTED, alpha=0.25, edgecolor="none", label="intervalo interquartil (Q1–Q3)"),
    ]
    ax.legend(handles=alcas, loc="lower right", bbox_to_anchor=(1.0, 1.03), ncol=3, frameon=False,
              fontsize=8.5, labelcolor=INK_2, handletextpad=0.4, columnspacing=1.4, borderaxespad=0)


def desenhar_tempo_por_kata(ax, trials):
    estilo_eixos(ax, grade="x")
    eixo_tempo_log(ax)
    katas = sorted(trials["kata"].unique())
    n = len(katas)
    ax.set_ylim(-0.6, n - 0.4)
    ax.set_yticks([])
    ax.set_xlabel("Tempo até passar em todos os testes (min, escala logarítmica)", fontsize=8.5,
                  color=MUTED, labelpad=8)
    ax.plot([TIMEBOX_MIN] * 2, [-0.6, n - 0.5], color=BASELINE, linewidth=pt(1), zorder=1)
    ax.text(TIMEBOX_MIN, n - 0.45, "time-box", ha="center", va="bottom", fontsize=8, color=MUTED)

    medianas = trials.groupby(["kata", "tratamento"])["tempo_min"].median().unstack()
    rot = blended_transform_factory(ax.transAxes, ax.transData)
    ax.text(1.035, n - 0.45, "Manual ÷ IA", transform=rot, ha="left", va="bottom", fontsize=8, color=MUTED)

    for i, kata in enumerate(katas):
        y = n - 1 - i
        ia = medianas.loc[kata].get("IA")
        manual = medianas.loc[kata].get("Manual")
        if pd.notna(ia) and pd.notna(manual):
            ax.plot([ia, manual], [y, y], color=BASELINE, linewidth=pt(2), zorder=2, solid_capstyle="round")
            ax.text(1.035, y, f"{fmt(manual / ia, 1)}×", transform=rot, ha="left", va="center",
                    fontsize=10, color=INK, fontweight="semibold")
        for trat, valor in (("IA", ia), ("Manual", manual)):
            if pd.notna(valor):
                pontos(ax, [valor], [y], COR[trat])

        nome, dificuldade = KATAS.get(kata, (kata, ""))
        quem = trials[trials["kata"] == kata].sort_values("tratamento")
        detalhe = " · ".join(f"{t}: {', '.join(g['participante'])}" for t, g in quem.groupby("tratamento"))
        ax.text(-0.02, y + 0.05, f"{kata}  {nome}", transform=rot, ha="right", va="bottom",
                fontsize=9.5, color=INK, fontweight="semibold")
        ax.text(-0.02, y - 0.02, f"{dificuldade} · {detalhe}", transform=rot, ha="right", va="top",
                fontsize=8, color=MUTED)

    legenda_tratamentos(ax, y=1.03)


# ---------------------------------------------------------------------------
# RQ2 - taxa de sucesso
# ---------------------------------------------------------------------------


def desenhar_taxa_sucesso(ax, trials):
    estilo_eixos(ax, grade="x")
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.6, 1.6)
    ax.set_yticks([])
    ax.xaxis.set_major_locator(FixedLocator([0, 25, 50, 75, 100]))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.set_xlabel("Testes de aceitação passando ao final do trial (soma de todos os trials)",
                  fontsize=8.5, color=MUTED, labelpad=8)
    rot = blended_transform_factory(ax.transAxes, ax.transData)

    for trat, y in (("IA", 1), ("Manual", 0)):
        grupo = trials[trials["tratamento"] == trat]
        if grupo.empty:
            continue
        passando, total = grupo["testes_passando"].sum(), grupo["testes_total"].sum()
        pct = 100 * passando / total
        barra_h(ax, y, 0, pct, COR[trat], arredondar_base=pct < 100)
        if pct < 100:
            # 2px de respiro entre a parte passando e a parte falhando
            X, _ = ax.transData.transform((pct, y))
            inicio = ax.transData.inverted().transform((X + 2 * PX, 0))[0]
            barra_h(ax, y, inicio, 100, CRITICAL)
        ax.text(1.02, y + 0.04, f"{fmt(pct, 0)}%", transform=rot, ha="left", va="bottom",
                fontsize=11, color=INK, fontweight="semibold")
        ax.text(1.02, y - 0.02, f"{passando} de {total} testes", transform=rot, ha="left", va="top",
                fontsize=8, color=MUTED)
        censurados = int(grupo["censurado"].sum())
        ax.text(-0.02, y + 0.04, ROTULOS[trat], transform=rot, ha="right", va="bottom",
                fontsize=9.5, color=INK, fontweight="semibold")
        ax.text(-0.02, y - 0.02, f"{len(grupo)} trials · {censurados} censurados", transform=rot,
                ha="right", va="top", fontsize=8, color=MUTED)

    falhando = int(trials["testes_falhando"].sum())
    if falhando:
        alcas = [Patch(facecolor=CRITICAL, label="testes falhando")]
        ax.legend(handles=alcas, loc="lower right", bbox_to_anchor=(1.0, 1.03), frameon=False,
                  fontsize=8.5, labelcolor=INK_2, borderaxespad=0)


# ---------------------------------------------------------------------------
# RQ3 - metricas estaticas
# ---------------------------------------------------------------------------

PAINEIS_RQ3 = [
    ("wmc", "Complexidade ciclomática", "WMC · soma de McCabe por classe (CK)", 0),
    ("loc", "Linhas de código", "LOC da classe Solution (CK) · controle", 0),
    ("wmc_por_loc", "Complexidade por linha", "WMC ÷ LOC", 2),
]


def escala_bonita(valor, max_divisoes=5):
    """Passo "redondo" e teto do eixo para que os ticks caiam em numeros limpos."""
    if valor <= 0:
        return 1, 1
    for passo in (0.05, 0.1, 0.2, 0.25, 0.5, 1, 2, 2.5, 5, 10, 20, 25, 50, 100, 200, 250, 500):
        divisoes = -(-valor // passo)
        if divisoes <= max_divisoes:
            return passo, passo * divisoes
    return valor / max_divisoes, valor


def deslocamentos_beeswarm(ax, valores, diametro_px=12):
    """Deslocamento horizontal (em dados) de cada ponto para que nenhum se sobreponha.

    Cada ponto vai para a posicao livre mais proxima do centro, testando
    colisao em pixels com os pontos ja posicionados.
    """
    caixa = ax.get_window_extent()
    (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
    px_x = caixa.width / (x1 - x0)
    px_y = caixa.height / (y1 - y0)
    d = diametro_px * PX
    colocados = []
    deslocamentos = []
    for v in valores:
        y = v * px_y
        candidatos = [0.0]
        for k in range(1, 20):
            candidatos += [k * d / 2, -k * d / 2]
        for c in candidatos:
            if all((c - cx) ** 2 + (y - cy) ** 2 >= d ** 2 for cx, cy in colocados):
                colocados.append((c, y))
                deslocamentos.append(c / px_x)
                break
    return deslocamentos


def desenhar_painel_rq3(ax, estaticas, coluna, casas):
    estilo_eixos(ax, grade="y")
    ax.set_xlim(-0.6, 1.6)
    passo, topo = escala_bonita(estaticas[coluna].max() * 1.08)
    ax.set_ylim(0, topo)
    ax.yaxis.set_major_locator(FixedLocator([passo * i for i in range(int(round(topo / passo)) + 1)]))
    casas_eixo = 0 if passo >= 1 else (1 if passo * 10 == int(passo * 10) else 2)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt(v, casas_eixo)))
    ax.set_xticks([0, 1])
    ax.set_xticklabels([ROTULOS[t] for t in TRATAMENTOS], fontsize=8.5, color=INK_2)

    for x, trat in enumerate(TRATAMENTOS):
        valores = estaticas.loc[estaticas["tratamento"] == trat, coluna].sort_values().reset_index(drop=True)
        if valores.empty:
            continue
        xs = [x + d for d in deslocamentos_beeswarm(ax, valores)]
        ys = list(valores)
        meia = max(abs(xi - x) for xi in xs) + 0.14
        med = valores.median()
        ax.plot([x - meia, x + meia], [med, med], color=INK, linewidth=pt(2), zorder=3,
                solid_capstyle="butt")
        pontos(ax, xs, ys, COR[trat])
        ax.text(x + meia + 0.05, med, fmt(med, casas), ha="left", va="center", fontsize=9,
                color=INK, fontweight="semibold",
                bbox=dict(boxstyle="round,pad=0.15", facecolor=SURFACE, edgecolor="none"))


def desenhar_tile_duplicacao(fig, esq, topo, larg, alt, estaticas):
    w, h = fig.get_size_inches()
    ax = eixos(fig, esq, topo, larg, alt)
    ax.set_axis_off()
    ax.add_patch(FancyBboxPatch((0.01, 0.01), 0.98, 0.98, boxstyle="round,pad=0,rounding_size=0.04",
                                transform=ax.transAxes, facecolor=SURFACE, edgecolor=TILE_BORDER,
                                linewidth=pt(1)))
    ax.text(0.09, 0.9, "Duplicação de código", transform=ax.transAxes, fontsize=10.5,
            fontweight="semibold", color=INK, va="top")
    ax.text(0.09, 0.8, "% de tokens duplicados (PMD CPD)", transform=ax.transAxes, fontsize=8.5,
            color=MUTED, va="top")
    for i, trat in enumerate(TRATAMENTOS):
        valores = estaticas.loc[estaticas["tratamento"] == trat, "duplicacao_pct"].dropna()
        y = 0.56 - i * 0.3
        ax.plot([0.1], [y], marker="o", markersize=pt(11), markerfacecolor=COR[trat],
                markeredgecolor=SURFACE, transform=ax.transAxes)
        ax.text(0.17, y, ROTULOS[trat], transform=ax.transAxes, fontsize=9, color=INK_2, va="center")
        valor = f"{fmt(valores.median(), 0)}%" if not valores.empty else "–"
        ax.text(0.91, y, valor, transform=ax.transAxes, fontsize=20, color=INK, ha="right",
                va="center", fontweight="semibold")
        ax.text(0.91, y - 0.11, f"mediana · {len(valores)} soluções", transform=ax.transAxes,
                fontsize=7.5, color=MUTED, ha="right", va="center")


def desenhar_rq3(fig, esq, topo, larg, alt, estaticas):
    """Pequenos multiplos: um eixo por metrica (nunca dois eixos y no mesmo grafico)."""
    n = len(PAINEIS_RQ3) + 1
    folga = 0.55
    larg_painel = (larg - folga * (n - 1)) / n
    for i, (coluna, titulo, sub, casas) in enumerate(PAINEIS_RQ3):
        x = esq + i * (larg_painel + folga)
        texto(fig, x, topo, titulo, fontsize=10.5, fontweight="semibold", color=INK)
        texto(fig, x, topo + 0.22, sub, fontsize=8.5, color=MUTED)
        ax = eixos(fig, x + 0.35, topo + 0.62, larg_painel - 0.35, alt - 0.62)
        desenhar_painel_rq3(ax, estaticas, coluna, casas)
    x = esq + len(PAINEIS_RQ3) * (larg_painel + folga)
    desenhar_tile_duplicacao(fig, x, topo, larg_painel, alt - 0.25, estaticas)


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------


def descricao_amostra(df):
    participantes = ", ".join(sorted(df["participante"].unique()))
    return f"{len(df)} trials · participantes: {participantes}"


def figura(larg, alt):
    return plt.figure(figsize=(larg, alt), dpi=DPI)


def salvar(fig, nome):
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    caminho = CHARTS_DIR / nome
    fig.savefig(caminho, dpi=DPI)
    plt.close(fig)
    print(f"gerado: {caminho.relative_to(CODE_DIR)}")


def grafico_tempo_por_tratamento(trials):
    fig = figura(11, 4.75)
    ia = trials.loc[trials["tratamento"] == "IA", "tempo_min"].median()
    manual = trials.loc[trials["tratamento"] == "Manual", "tempo_min"].median()
    cabecalho(fig, 0.45, 0.35, "RQ1 · Tempo até passar nos testes",
              f"Mediana de {fmt_min(ia)} com IA contra {fmt_min(manual)} sem IA "
              f"({fmt(manual / ia, 1)}× mais rápido com IA).")
    ax = eixos(fig, 2.2, 1.4, 8.3, 2.35)
    desenhar_tempo_por_tratamento(ax, trials)
    rodape(fig, f"Fonte: data/raw/trials.csv · {descricao_amostra(trials)} · time-box de 35 min por trial")
    salvar(fig, "rq1_tempo_por_tratamento.png")


def grafico_tempo_por_kata(trials):
    n = trials["kata"].nunique()
    fig = figura(11, 2.45 + 0.62 * n)
    medianas = trials.groupby(["kata", "tratamento"])["tempo_min"].median().unstack().dropna()
    ia_mais_rapida = int((medianas["IA"] < medianas["Manual"]).sum())
    if ia_mais_rapida == len(medianas):
        sub = "Em todos os katas, a mediana com IA ficou abaixo da mediana manual."
    else:
        sub = (f"A mediana com IA ficou abaixo da mediana manual em {ia_mais_rapida} "
               f"de {len(medianas)} katas.")
    cabecalho(fig, 0.45, 0.35, "RQ1 · Tempo por kata e tratamento", sub)
    ax = eixos(fig, 3.35, 1.5, 6.45, 0.62 * n)
    desenhar_tempo_por_kata(ax, trials)
    rodape(fig, f"Fonte: data/raw/trials.csv · {descricao_amostra(trials)} · "
                "mediana por kata e tratamento")
    salvar(fig, "rq1_tempo_por_kata.png")


def grafico_taxa_sucesso(trials):
    fig = figura(11, 3.85)
    falhando = int(trials["testes_falhando"].sum())
    censurados = int(trials["censurado"].sum())
    if falhando == 0 and censurados == 0:
        sub = "Todos os trials terminaram com 100% dos testes passando e nenhum atingiu o time-box."
    else:
        sub = f"{falhando} testes falhando e {censurados} trials censurados no total."
    cabecalho(fig, 0.45, 0.35, "RQ2 · Taxa de sucesso dos testes de aceitação", sub)
    ax = eixos(fig, 2.2, 1.35, 7.4, 1.65)
    desenhar_taxa_sucesso(ax, trials)
    rodape(fig, f"Fonte: data/raw/trials.csv · {descricao_amostra(trials)}")
    salvar(fig, "rq2_taxa_sucesso.png")


def grafico_rq3(estaticas):
    fig = figura(12, 5.1)
    cabecalho(fig, 0.45, 0.35, "RQ3 · Estrutura do código produzido",
              "Cada ponto é a solução final de um trial; a linha preta marca a mediana do tratamento.")
    desenhar_rq3(fig, 0.45, 1.35, 11.1, 3.05, estaticas)
    rodape(fig, f"Fonte: data/processed/ck e data/processed/cpd/cpd-*.xml · {descricao_amostra(estaticas)} · "
                "katas diferentes em cada tratamento")
    salvar(fig, "rq3_metricas_estaticas.png")


def tile_kpi(fig, esq, topo, larg, alt, rotulo, valor, detalhe):
    ax = eixos(fig, esq, topo, larg, alt)
    ax.set_axis_off()
    ax.add_patch(FancyBboxPatch((0.01, 0.02), 0.98, 0.96, boxstyle="round,pad=0,rounding_size=0.05",
                                transform=ax.transAxes, facecolor=SURFACE, edgecolor=TILE_BORDER,
                                linewidth=pt(1)))
    ax.text(0.08, 0.82, rotulo, transform=ax.transAxes, fontsize=9, color=INK_2, va="top")
    ax.text(0.08, 0.5, valor, transform=ax.transAxes, fontsize=22, color=INK, va="center",
            fontweight="semibold")
    ax.text(0.08, 0.17, detalhe, transform=ax.transAxes, fontsize=8, color=MUTED, va="center")


def secao(fig, y, titulo, subtitulo):
    fig.add_artist(Line2D([0.45 / 14, 1 - 0.45 / 14], [1 - (y - 0.2) / fig.get_size_inches()[1]] * 2,
                          color=GRID, linewidth=pt(1)))
    texto(fig, 0.45, y, titulo, fontsize=12.5, fontweight="semibold", color=INK)
    texto(fig, 0.45, y + 0.3, subtitulo, fontsize=9, color=INK_2)


def dashboard(trials, estaticas):
    n_katas = trials["kata"].nunique()
    alt_kata = 0.55 * n_katas
    # posicoes verticais (polegadas a partir do topo) de cada secao
    y_rq1 = 3.2
    y_rq2 = y_rq1 + 4.35 + alt_kata + 1.0
    y_rq3 = y_rq2 + 2.95
    fig = figura(14, y_rq3 + 0.95 + 3.0 + 0.75)

    cabecalho(fig, 0.45, 0.4, "Assistentes de IA vs. codificação manual",
              "Laboratório de Experimentação de Software · Lab02 · experimento controlado "
              "crossover com katas Java e time-box de 35 min", tamanho=19)

    ia = trials.loc[trials["tratamento"] == "IA", "tempo_min"].median()
    manual = trials.loc[trials["tratamento"] == "Manual", "tempo_min"].median()
    sucesso = {t: 100 * g["testes_passando"].sum() / g["testes_total"].sum()
               for t, g in trials.groupby("tratamento")}
    tiles = [
        ("Trials analisados", f"{len(trials)}", ", ".join(sorted(trials["participante"].unique()))),
        ("Tempo mediano · com IA", fmt_min(ia), "até passar em todos os testes"),
        ("Tempo mediano · manual", fmt_min(manual), "até passar em todos os testes"),
        ("Redução do tempo mediano", f"{fmt(manual / ia, 1)}×", "manual ÷ IA"),
        ("Taxa de sucesso", f"{fmt(sucesso.get('IA', 0), 0)}% · {fmt(sucesso.get('Manual', 0), 0)}%",
         "com IA · manual"),
    ]
    larg_tile = (14 - 0.9 - 0.25 * 4) / 5
    for i, (rotulo, valor, detalhe) in enumerate(tiles):
        tile_kpi(fig, 0.45 + i * (larg_tile + 0.25), 1.35, larg_tile, 1.25, rotulo, valor, detalhe)

    y = y_rq1
    secao(fig, y, "RQ1 · Tempo", "Distribuição por tratamento e comparação kata a kata "
                                  "(escala logarítmica: cada divisão multiplica o tempo).")
    ax = eixos(fig, 2.3, y + 1.15, 11.2, 2.1)
    desenhar_tempo_por_tratamento(ax, trials)
    ax = eixos(fig, 3.45, y + 4.35, 9.35, alt_kata)
    desenhar_tempo_por_kata(ax, trials)

    y = y_rq2
    secao(fig, y, "RQ2 · Defeitos", "Testes de aceitação passando ao final de cada trial.")
    ax = eixos(fig, 2.3, y + 0.8, 10.2, 1.45)
    desenhar_taxa_sucesso(ax, trials)

    y = y_rq3
    secao(fig, y, "RQ3 · Estrutura do código",
          "Métricas estáticas das soluções finais"
          + (f" · {descricao_amostra(estaticas)}" if not estaticas.empty else "") + ".")
    if estaticas.empty:
        texto(fig, 0.45, y + 0.95, "Nenhuma métrica do CK encontrada em data/processed/ck.",
              fontsize=9.5, color=MUTED)
    else:
        desenhar_rq3(fig, 0.45, y + 0.95, 13.1, 3.0, estaticas)

    rodape(fig, "Fontes: data/raw/trials.csv, data/processed/ck, data/processed/cpd/cpd-*.xml · "
                "gerado por scripts/dashboard.py (issue #45)")
    salvar(fig, "dashboard.png")


def main():
    trials = carregar_trials()
    estaticas = carregar_metricas_estaticas()
    grafico_tempo_por_tratamento(trials)
    grafico_tempo_por_kata(trials)
    grafico_taxa_sucesso(trials)
    if estaticas.empty:
        print("aviso: nenhuma metrica do CK encontrada em data/processed/ck; RQ3 ignorada")
    else:
        grafico_rq3(estaticas)
    dashboard(trials, estaticas)


if __name__ == "__main__":
    main()

"""Etapa 02: normaliza os dados brutos no formato comum e valida o resultado.

Lê **só os arquivos locais** de ``dados/brutos/`` (nunca acessa a internet):

* GitHub: todos os ``incidentes/<código>.json``;
* GitLab: o ``all.ics``.

Cada incidente é convertido pelas mesmas funções dos coletores, recebe as
categorias do ``mapa_componentes.csv`` (ou, sem componente publicado, das
``regras_titulo.csv``) e passa pelas validações. Saídas:

* ``dados/processados/incidentes.csv`` — formato comum do grupo (11 colunas, na
  ordem combinada) e três colunas extras no fim: ``origem_componente``
  (``publicado``, ``titulo`` ou ``nenhuma``), ``retroativo`` e
  ``termina_apos_janela``, usadas nas análises de sensibilidade;
* ``resultados/tabelas/validacao.md`` — o que foi encontrado e corrigido.

Regras de tratamento (documentadas também no ``validacao.md``):

1. **Janela:** entra o incidente com ``inicio_utc`` dentro de
   ``[2025-11-01T00:00:00Z, 2026-10-31T23:59:59Z]``. Quem começou antes e terminou
   dentro fica fora (só contado no relatório). Quem começou dentro e terminou
   depois **entra com a duração inteira**, sem cortar na borda, e é marcado em
   ``termina_apos_janela``.
2. **Sem horário de fim** (retroativos do GitHub, incidentes não resolvidos ou
   ``fim_utc <= inicio_utc``): o incidente entra na frequência com ``fim_utc`` e
   ``duracao_min`` vazios. Nenhuma duração é imputada.
3. **Ids repetidos** na mesma plataforma: fica o primeiro (ordem do arquivo).
4. **Componente sem linha no mapa:** é listado no relatório e não gera categoria;
   o mapa precisa ganhar a linha nova.
5. **Sem componente publicado:** aplica as regras pelo título; se nenhuma casar,
   ``componente_equivalente = sem_componente``.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

PASTA_CODIGO = Path(__file__).resolve().parents[1]
if str(PASTA_CODIGO) not in sys.path:
    sys.path.insert(0, str(PASTA_CODIGO))

from coleta import github, gitlab  # noqa: E402

JANELA_INICIO = "2025-11-01T00:00:00Z"
JANELA_FIM = "2026-10-31T23:59:59Z"
PASTA_DADOS = PASTA_CODIGO / "dados"
PASTA_BRUTOS = PASTA_DADOS / "brutos"
ARQUIVO_MAPA = PASTA_DADOS / "mapa_componentes.csv"
ARQUIVO_REGRAS = PASTA_DADOS / "regras_titulo.csv"
ARQUIVO_SAIDA = PASTA_DADOS / "processados" / "incidentes.csv"
ARQUIVO_VALIDACAO = PASTA_CODIGO / "resultados" / "tabelas" / "validacao.md"

COLUNAS = (
    "plataforma",
    "id",
    "titulo",
    "componentes_originais",
    "componente_equivalente",
    "impacto",
    "inicio_utc",
    "fim_utc",
    "duracao_min",
    "fonte",
    "url",
)
COLUNAS_EXTRAS = ("origem_componente", "retroativo", "termina_apos_janela")
CATEGORIAS = ("git", "api", "web", "issues_prs", "ci_cd", "pacotes", "pages", "fora_do_escopo")
SEM_COMPONENTE = "sem_componente"
PLATAFORMAS = ("github", "gitlab")


# --------------------------------------------------------------------------- #
# Leitura dos dados brutos e das tabelas de apoio
# --------------------------------------------------------------------------- #


def ler_brutos_github(pasta: Path = PASTA_BRUTOS / "github") -> list[dict]:
    registros = []
    for arquivo in sorted((pasta / "incidentes").glob("*.json")):
        registro = github.normalizar_incidente(json.loads(arquivo.read_text(encoding="utf-8")))
        if not registro["manutencao"]:
            registros.append(registro)
    return registros


def ler_brutos_gitlab(pasta: Path = PASTA_BRUTOS / "gitlab") -> list[dict]:
    arquivo = pasta / gitlab.ARQUIVO_ICAL
    if not arquivo.exists():
        return []
    registros = []
    for evento in gitlab.ler_eventos(arquivo.read_bytes().decode("utf-8")):
        registro = gitlab.normalizar_evento(evento)
        if not registro["manutencao"]:
            registros.append(registro)
    return registros


def ler_mapa(arquivo: Path = ARQUIVO_MAPA) -> dict[tuple[str, str], str]:
    with arquivo.open(encoding="utf-8", newline="") as entrada:
        return {
            (linha["plataforma"], linha["componente_original"]): linha["componente_equivalente"]
            for linha in csv.DictReader(entrada)
        }


class RegraTitulo(NamedTuple):
    plataforma: str  # github, gitlab ou ambas
    tipo: str  # exclusiva, especifica ou generica
    padrao: re.Pattern
    categoria: str

    def vale_para(self, plataforma: str) -> bool:
        return self.plataforma in ("ambas", plataforma)


def ler_regras(arquivo: Path = ARQUIVO_REGRAS) -> list[RegraTitulo]:
    with arquivo.open(encoding="utf-8", newline="") as entrada:
        return [
            RegraTitulo(
                linha["plataforma"],
                linha["tipo"],
                re.compile(linha["padrao"], re.IGNORECASE),
                linha["componente_equivalente"],
            )
            for linha in csv.DictReader(entrada)
        ]


# --------------------------------------------------------------------------- #
# Categorias
# --------------------------------------------------------------------------- #


def juntar(categorias) -> str:
    return ";".join(sorted(set(categorias)))


def categorias_publicadas(
    plataforma: str, componentes: str, mapa: dict[tuple[str, str], str]
) -> tuple[str, list[str]]:
    """Traduz os componentes publicados. Devolve ``(categorias, sem_mapeamento)``."""
    nomes = [c for c in componentes.split(";") if c]
    sem_mapa = [c for c in nomes if (plataforma, c) not in mapa]
    return juntar(mapa[(plataforma, c)] for c in nomes if (plataforma, c) in mapa), sem_mapa


def categorias_pelo_titulo(plataforma: str, titulo: str, regras: list[RegraTitulo]) -> str:
    """Classifica pelo título, para incidentes publicados sem componente.

    1. Se uma regra ``exclusiva`` casar, o incidente é ``fora_do_escopo`` e pronto
       (ex.: "Issues with GitLab Duo in merge requests" é um problema do Duo).
    2. Senão, junta as categorias de todas as regras ``especifica`` que casarem
       (ex.: "Intermittent Git and CI/CD pipeline failures" vira ``ci_cd;git``).
    3. Se nenhuma específica deu categoria comparável, aplica as ``generica``
       (ex.: "Elevated 5xx Errors on GitLab.com" vira ``web``).
    4. Sem nenhuma regra, devolve vazio.
    """
    validas = [r for r in regras if r.vale_para(plataforma) and r.padrao.search(titulo)]
    if any(r.tipo == "exclusiva" for r in validas):
        return "fora_do_escopo"
    categorias = {r.categoria for r in validas if r.tipo == "especifica"}
    if not categorias - {"fora_do_escopo"}:
        categorias |= {r.categoria for r in validas if r.tipo == "generica"}
    return juntar(categorias)


# --------------------------------------------------------------------------- #
# Normalização e validação
# --------------------------------------------------------------------------- #


class Relatorio:
    """O que a normalização encontrou, para o ``validacao.md``."""

    def __init__(self) -> None:
        self.lidos: Counter = Counter()
        self.antes_da_janela: list[dict] = []
        self.depois_da_janela: Counter = Counter()
        self.termina_apos_janela: list[dict] = []
        self.repetidos: list[dict] = []
        self.sem_fim: list[dict] = []
        self.fim_invalido: list[dict] = []
        self.sem_mapeamento: Counter = Counter()
        self.pelo_titulo: list[dict] = []
        self.sem_componente: list[dict] = []
        self.categoria_invalida: list[str] = []


def utc(texto: str) -> datetime:
    return github.como_utc(texto)


def normalizar(
    brutos: list[dict],
    mapa: dict[tuple[str, str], str],
    regras: list[RegraTitulo],
    inicio: str = JANELA_INICIO,
    fim: str = JANELA_FIM,
) -> tuple[list[dict], Relatorio]:
    """Aplica as regras do cabeçalho do módulo e devolve ``(linhas, relatório)``."""
    inicio_janela, fim_janela = utc(inicio), utc(fim)
    relatorio = Relatorio()
    vistos: set[tuple[str, str]] = set()
    linhas: list[dict] = []

    for bruto in brutos:
        plataforma = bruto["plataforma"]
        relatorio.lidos[plataforma] += 1
        chave = (plataforma, bruto["id"])
        if chave in vistos:
            relatorio.repetidos.append(bruto)
            continue
        vistos.add(chave)

        comeco = utc(bruto["inicio_utc"])
        termino = utc(bruto["fim_utc"]) if bruto["fim_utc"] else None
        if comeco < inicio_janela:
            if termino is not None and termino >= inicio_janela:
                relatorio.antes_da_janela.append(bruto)
            continue
        if comeco > fim_janela:
            relatorio.depois_da_janela[plataforma] += 1
            continue

        fim_invalido = termino is not None and termino <= comeco
        if fim_invalido:
            termino = None

        categorias, sem_mapa = categorias_publicadas(plataforma, bruto["componentes_originais"], mapa)
        for componente in sem_mapa:
            relatorio.sem_mapeamento[(plataforma, componente)] += 1
        if bruto["componentes_originais"]:
            origem = "publicado"
        else:
            categorias = categorias_pelo_titulo(plataforma, bruto["titulo"], regras)
            origem = "titulo" if categorias else "nenhuma"
        if not categorias:
            categorias = SEM_COMPONENTE
        invalidas = set(categorias.split(";")) - set(CATEGORIAS) - {SEM_COMPONENTE}
        if invalidas:
            relatorio.categoria_invalida.extend(sorted(invalidas))

        linha = {
            "plataforma": plataforma,
            "id": bruto["id"],
            "titulo": bruto["titulo"],
            "componentes_originais": bruto["componentes_originais"],
            "componente_equivalente": categorias,
            "impacto": bruto["impacto"],
            "inicio_utc": github.formatar_utc(comeco),
            "fim_utc": github.formatar_utc(termino),
            "duracao_min": ""
            if termino is None
            else f"{round((termino - comeco).total_seconds() / 60, 2):g}",
            "fonte": bruto["fonte"],
            "url": bruto["url"],
            "origem_componente": origem,
            "retroativo": str(bool(bruto.get("retroativo", False))).lower(),
            "termina_apos_janela": str(termino is not None and termino > fim_janela).lower(),
        }
        if fim_invalido:
            relatorio.fim_invalido.append(linha)
        elif termino is None:
            relatorio.sem_fim.append(linha)
        if origem == "titulo":
            relatorio.pelo_titulo.append(linha)
        elif origem == "nenhuma":
            relatorio.sem_componente.append(linha)
        if linha["termina_apos_janela"] == "true":
            relatorio.termina_apos_janela.append(linha)
        linhas.append(linha)

    linhas.sort(key=lambda r: (r["plataforma"], r["inicio_utc"], r["id"]))
    return linhas, relatorio


def verificar(linhas: list[dict], inicio: str = JANELA_INICIO, fim: str = JANELA_FIM) -> list[str]:
    """Confere o resultado final. Devolve a lista de problemas (vazia = tudo certo)."""
    problemas = []
    chaves = Counter((r["plataforma"], r["id"]) for r in linhas)
    problemas += [f"id repetido: {p}/{i}" for (p, i), n in chaves.items() if n > 1]
    for r in linhas:
        nome = f"{r['plataforma']}/{r['id']}"
        if r["plataforma"] not in PLATAFORMAS:
            problemas.append(f"plataforma inválida: {nome}")
        if not utc(inicio) <= utc(r["inicio_utc"]) <= utc(fim):
            problemas.append(f"início fora da janela: {nome}")
        if r["fim_utc"] and utc(r["fim_utc"]) <= utc(r["inicio_utc"]):
            problemas.append(f"fim_utc <= inicio_utc: {nome}")
        if bool(r["fim_utc"]) != bool(r["duracao_min"]):
            problemas.append(f"fim_utc e duracao_min inconsistentes: {nome}")
        if r["duracao_min"] and float(r["duracao_min"]) <= 0:
            problemas.append(f"duração não positiva: {nome}")
    return problemas


# --------------------------------------------------------------------------- #
# Saídas
# --------------------------------------------------------------------------- #


def escrever_csv(linhas: list[dict], arquivo: Path = ARQUIVO_SAIDA) -> None:
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    with arquivo.open("w", encoding="utf-8", newline="") as saida:
        escritor = csv.DictWriter(saida, fieldnames=COLUNAS + COLUNAS_EXTRAS, lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(linhas)


def _tabela(cabecalho: list[str], linhas: list[list], numerica: bool = True) -> list[str]:
    """Tabela Markdown; com ``numerica``, as colunas depois da primeira ficam à direita."""

    def celula(valor) -> str:
        return str(valor).replace("|", "\\|")

    return [
        "| " + " | ".join(cabecalho) + " |",
        "|" + "|".join("---:" if i and numerica else "---" for i in range(len(cabecalho))) + "|",
        *("| " + " | ".join(celula(v) for v in linha) + " |" for linha in linhas),
    ]


def _lista_incidentes(registros: list[dict], limite: int | None = None) -> list[str]:
    if not registros:
        return ["Nenhum."]
    mostrados = registros if limite is None else registros[:limite]
    linhas = _tabela(
        ["Plataforma", "Id", "Início (UTC)", "Fim (UTC)", "Título", "Categoria"],
        [
            [
                r["plataforma"],
                r["id"],
                r["inicio_utc"],
                r["fim_utc"] or "—",
                r["titulo"],
                r.get("componente_equivalente", "—"),
            ]
            for r in mostrados
        ],
        numerica=False,
    )
    if limite is not None and len(registros) > limite:
        linhas.append(f"\n… e mais {len(registros) - limite} (lista completa no `incidentes.csv`).")
    return linhas


def montar_validacao(linhas: list[dict], relatorio: Relatorio, problemas: list[str]) -> str:
    por_plataforma = defaultdict(list)
    for r in linhas:
        por_plataforma[r["plataforma"]].append(r)

    def contar(plataforma: str, condicao) -> int:
        return sum(1 for r in por_plataforma[plataforma] if condicao(r))

    resumo = _tabela(
        ["Item", "GitHub", "GitLab"],
        [
            [rotulo, *(contar(p, condicao) if condicao else valor(p) for p in PLATAFORMAS)]
            for rotulo, condicao, valor in [
                ("Registros nos dados brutos (arquivo inteiro, sem manutenções)", None, lambda p: relatorio.lidos[p]),
                ("Incidentes no `incidentes.csv` (início na janela)", lambda r: True, None),
                ("Com duração", lambda r: bool(r["duracao_min"]), None),
                ("Sem horário de fim (sem duração)", lambda r: not r["duracao_min"], None),
                ("… dos quais retroativos", lambda r: r["retroativo"] == "true", None),
                ("Terminam depois da janela (duração inteira mantida)", lambda r: r["termina_apos_janela"] == "true", None),
                ("Componente publicado", lambda r: r["origem_componente"] == "publicado", None),
                ("Componente pelo título", lambda r: r["origem_componente"] == "titulo", None),
                ("`sem_componente`", lambda r: r["componente_equivalente"] == SEM_COMPONENTE, None),
                ("Sem impacto publicado", lambda r: not r["impacto"], None),
            ]
        ],
    )

    categorias = sorted(
        {c for r in linhas for c in r["componente_equivalente"].split(";")},
        key=lambda c: (CATEGORIAS + (SEM_COMPONENTE,)).index(c) if c in CATEGORIAS + (SEM_COMPONENTE,) else 99,
    )
    tabela_categorias = _tabela(
        [
            "Categoria",
            "GitHub (componente publicado)",
            "GitHub (sem componente publicado)",
            "GitLab (componente publicado)",
            "GitLab (sem componente publicado)",
        ],
        [
            [
                f"`{c}`",
                *(
                    contar(p, lambda r, c=c, o=o: c in r["componente_equivalente"].split(";") and r["origem_componente"] in o)
                    for p in PLATAFORMAS
                    for o in (("publicado",), ("titulo", "nenhuma"))
                ),
            ]
            for c in categorias
        ],
    )

    sem_mapa = (
        _tabela(
            ["Plataforma", "Componente", "Incidentes"],
            [[p, c, n] for (p, c), n in sorted(relatorio.sem_mapeamento.items())],
        )
        if relatorio.sem_mapeamento
        else ["Nenhum: todos os componentes publicados estão no `mapa_componentes.csv`."]
    )

    partes = [
        "# Validação dos incidentes",
        "",
        "> Gerado por `etapas/02_normalizar.py` (issue #105). Não edite à mão: rode o comando único.",
        "",
        f"Janela: `{JANELA_INICIO}` a `{JANELA_FIM}` (UTC). Entrada: `dados/brutos/` (sem internet).",
        "",
        "## Resumo",
        "",
        *resumo,
        "",
        "## Verificações finais do `incidentes.csv`",
        "",
        "Ids únicos por plataforma, `inicio_utc` dentro da janela, `fim_utc > inicio_utc`, "
        "`duracao_min` positiva e presente só quando há `fim_utc`, plataforma válida.",
        "",
        "**Resultado:** " + ("nenhum problema." if not problemas else f"{len(problemas)} problema(s):"),
        *(f"- {p}" for p in problemas),
        "",
        "## O que foi encontrado e como foi tratado",
        "",
        f"### Ids repetidos: {len(relatorio.repetidos)}",
        "",
        "Regra: fica o primeiro registro; os outros são descartados.",
        "",
        *_lista_incidentes(relatorio.repetidos),
        "",
        f"### `fim_utc <= inicio_utc`: {len(relatorio.fim_invalido)}",
        "",
        "Regra: o horário de fim é descartado (fica sem duração), o incidente continua na frequência.",
        "",
        *_lista_incidentes(relatorio.fim_invalido),
        "",
        f"### Sem horário de fim: {len(relatorio.sem_fim)}",
        "",
        "Regra: entram na frequência, ficam fora da duração; nenhuma duração é imputada. "
        "No GitHub são os incidentes **retroativos** (publicados depois do fato, só com a "
        "atualização `resolved`): o Statuspage grava um horário aproximado e a duração real "
        "só aparece no texto. Sensibilidade 1 do plano de análise: frequência sem eles.",
        "",
        *_lista_incidentes(relatorio.sem_fim),
        "",
        f"### Começaram antes da janela e terminaram dentro: {len(relatorio.antes_da_janela)}",
        "",
        "Regra: **ficam fora** da amostra principal (o critério é o início). Só contam aqui, "
        "para a sensibilidade 4 do plano de análise.",
        "",
        *_lista_incidentes(relatorio.antes_da_janela),
        "",
        f"### Começaram na janela e terminaram depois: {len(relatorio.termina_apos_janela)}",
        "",
        "Regra: **entram com a duração inteira**, sem cortar em `2026-10-31T23:59:59Z` "
        "(cortar encurtaria artificialmente o tempo de recuperação). Marcados em "
        "`termina_apos_janela`.",
        "",
        *_lista_incidentes(relatorio.termina_apos_janela),
        "",
        f"Registros com início depois da janela (descartados): "
        f"GitHub {relatorio.depois_da_janela['github']}, GitLab {relatorio.depois_da_janela['gitlab']}.",
        "",
        "### Componentes sem linha no `mapa_componentes.csv`",
        "",
        *sem_mapa,
        "",
        f"### Incidentes classificados pelo título: {len(relatorio.pelo_titulo)}",
        "",
        "Incidentes publicados **sem componente** (o iCal do GitLab nunca traz componente; no "
        "GitHub, parte dos incidentes vem sem) recebem a categoria pelas regras escritas em "
        "`dados/regras_titulo.csv` (opção (b) do plano de coleta, seção 6.2). Ficam com "
        "`origem_componente = titulo`, para a sensibilidade 2 do plano de análise "
        "(com e sem esses incidentes). A lista completa está no `incidentes.csv`; "
        "a conferência por outra pessoa do grupo é feita sobre ela.",
        "",
        f"### `sem_componente`: {len(relatorio.sem_componente)}",
        "",
        "Nem componente publicado nem regra de título. Ficam no `incidentes.csv` e fora da "
        "comparação por categoria.",
        "",
        *_lista_incidentes(relatorio.sem_componente),
        "",
        "## Incidentes por categoria",
        "",
        "Um incidente com várias categorias conta uma vez em cada (regra de `componentes.md`).",
        "",
        *tabela_categorias,
        "",
        "## Limitações que continuam",
        "",
        "- O GitLab não tem impacto no iCal: `impacto` fica vazio em todos os incidentes do GitLab.",
        "- A categoria pelo título é uma inferência; a escrita do título varia entre as empresas.",
        "",
    ]
    return "\n".join(partes)


def main() -> None:
    brutos = ler_brutos_github() + ler_brutos_gitlab()
    linhas, relatorio = normalizar(brutos, ler_mapa(), ler_regras())
    problemas = verificar(linhas)
    if relatorio.categoria_invalida:
        problemas.append(
            "categoria fora da lista combinada: " + ", ".join(sorted(set(relatorio.categoria_invalida)))
        )
    escrever_csv(linhas, ARQUIVO_SAIDA)
    ARQUIVO_VALIDACAO.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO_VALIDACAO.write_text(
        montar_validacao(linhas, relatorio, problemas), encoding="utf-8", newline="\n"
    )
    print(
        f"incidentes.csv: {len(linhas)} incidentes "
        f"({sum(r['plataforma'] == 'github' for r in linhas)} GitHub, "
        f"{sum(r['plataforma'] == 'gitlab' for r in linhas)} GitLab)"
    )
    if problemas:
        raise ValueError("Validação falhou:\n" + "\n".join(problemas))


if __name__ == "__main__":
    main()

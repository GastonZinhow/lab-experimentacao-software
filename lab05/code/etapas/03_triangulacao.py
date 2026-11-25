"""Etapa 03: triangula a página de status com fontes oficiais secundárias."""

from __future__ import annotations

import csv
import html
import re
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path


PASTA_CODIGO = Path(__file__).resolve().parents[1]
PASTA_RELATORIOS = PASTA_CODIGO / "dados" / "brutos" / "github" / "relatorios"
ARQUIVO_RELATORIOS = PASTA_RELATORIOS.parent / "relatorios_mensais.csv"
ARQUIVO_GITLAB = PASTA_CODIGO / "dados" / "brutos" / "gitlab" / "amostra_issues.csv"
ARQUIVO_INCIDENTES = PASTA_CODIGO / "dados" / "processados" / "incidentes.csv"
ARQUIVO_SAIDA = PASTA_CODIGO / "resultados" / "tabelas" / "triangulacao.csv"

URL_RELATORIO = (
    "https://github.blog/news-insights/company-news/"
    "github-availability-report-{mes}/"
)
MESES_EN = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}


class _Textos(HTMLParser):
    """Extrai parágrafos e títulos, conservando somente o texto visível."""

    def __init__(self) -> None:
        super().__init__()
        self.pilha: list[str] = []
        self.atual: list[str] = []
        self.textos: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"p", "h2"}:
            self.pilha.append(tag)
            if len(self.pilha) == 1:
                self.atual = []

    def handle_endtag(self, tag: str) -> None:
        if self.pilha and self.pilha[-1] == tag:
            self.pilha.pop()
            if not self.pilha:
                texto = " ".join("".join(self.atual).split())
                if texto:
                    self.textos.append(html.unescape(texto))

    def handle_data(self, data: str) -> None:
        if self.pilha:
            self.atual.append(data)


def _duracoes(texto: str) -> list[int]:
    trecho = texto.lower().split("lasting", 1)[-1]
    return [
        int(horas or 0) * 60 + int(minutos)
        for horas, minutos in re.findall(
            r"(?:(\d+)\s+hours?\s+and\s+)?(\d+)\s+minutes?", trecho
        )
    ]


def _causa(textos: list[str]) -> str:
    padrao = re.compile(
        r"\b(root cause|caused|because|due to|triggered|went wrong|failure|misconfiguration)\b",
        re.IGNORECASE,
    )
    candidatos = [t for t in textos if len(t) > 35 and "lasting" not in t]
    encontrados = [t for t in candidatos if padrao.search(t)]
    return (encontrados[0] if encontrados else (candidatos[1] if len(candidatos) > 1 else candidatos[0]))[:1500]


def _extrair_relatorio(arquivo: Path) -> list[dict[str, str]]:
    parser = _Textos()
    parser.feed(arquivo.read_text(encoding="utf-8"))
    textos = parser.textos
    marcadores = [i for i, texto in enumerate(textos) if "lasting" in texto.lower()]
    # O sumário lateral repete os títulos nos relatórios mais novos.
    marcadores = [i for pos, i in enumerate(marcadores) if textos[i] not in textos[:i]]
    ano, mes_num = map(int, arquivo.stem.split("-"))
    mes_slug = next(nome for nome, numero in MESES_EN.items() if numero == mes_num)
    link = URL_RELATORIO.format(mes=f"{mes_slug}-{ano}")
    linhas: list[dict[str, str]] = []

    for posicao, indice in enumerate(marcadores):
        marcador = textos[indice]
        fim_secao = marcadores[posicao + 1] if posicao + 1 < len(marcadores) else len(textos)
        secao = textos[indice + 1:fim_secao]
        if not secao:
            continue
        mes_nome = next((m for m in MESES_EN if marcador.lower().startswith(m)), mes_slug)
        dia_match = re.search(r"\b(\d{1,2})\b", marcador)
        if not dia_match:
            continue
        dia = int(dia_match.group(1))
        antes_duracao = marcador.lower().split("lasting", 1)[0]
        horarios = re.findall(r"\b(\d{1,2}:\d{2})\b", antes_duracao)
        if not horarios:
            busca = " ".join(secao[:4])
            horarios = re.findall(r"\b(\d{1,2}:\d{2})\b", busca)
        duracoes = _duracoes(marcador)
        if not horarios or not duracoes:
            continue
        if len(horarios) > len(duracoes):
            horarios = horarios[:len(duracoes)]
        incidente = next((t for t in secao if len(t) > 35 and "Duration:" not in t), marcador)
        causa = _causa(secao)
        for numero, (horario, duracao) in enumerate(zip(horarios, duracoes), start=1):
            inicio = datetime(
                ano, MESES_EN[mes_nome], dia,
                *map(int, horario.split(":")), tzinfo=timezone.utc,
            )
            fim = inicio + timedelta(minutes=duracao)
            sufixo = f" (ocorrência {numero})" if len(duracoes) > 1 else ""
            linhas.append({
                "mes": arquivo.stem,
                "incidente": incidente[:500] + sufixo,
                "inicio": inicio.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "fim": fim.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "causa": causa,
                "link": link,
            })
    return linhas


def gerar_relatorios_mensais() -> list[dict[str, str]]:
    linhas = []
    for arquivo in sorted(PASTA_RELATORIOS.glob("*.html")):
        linhas.extend(_extrair_relatorio(arquivo))
    ARQUIVO_RELATORIOS.parent.mkdir(parents=True, exist_ok=True)
    with ARQUIVO_RELATORIOS.open("w", newline="", encoding="utf-8") as saida:
        escritor = csv.DictWriter(
            saida, fieldnames=("mes", "incidente", "inicio", "fim", "causa", "link"),
            lineterminator="\n",
        )
        escritor.writeheader()
        escritor.writerows(linhas)
    return linhas


def _dt(valor: str) -> datetime:
    return datetime.fromisoformat(valor.replace("Z", "+00:00"))


def _duracao(inicio: str, fim: str) -> float:
    return (_dt(fim) - _dt(inicio)).total_seconds() / 60


def _penalidade_assunto(status: dict[str, str], oficial: dict[str, str]) -> int:
    """Evita trocar dois incidentes próximos apenas por duração semelhante."""
    titulo = status["titulo"].lower()
    primeira_frase = oficial["incidente"].split(".", 1)[0].lower()
    assuntos = ("actions", "copilot", "pull request", "ssh", "api", "packages", "pages")
    # Relatos amplos citam muitos produtos na mesma frase; nesses casos o
    # assunto não discrimina melhor que os horários.
    if sum(termo in primeira_frase for termo in assuntos) > 2:
        return 0
    return 240 * sum((termo in titulo) != (termo in primeira_frase) for termo in assuntos)


def _linha_resultado(status: dict[str, str] | None, oficial: dict[str, str], plataforma: str) -> dict[str, str]:
    inicio_status = status["inicio_utc"] if status else ""
    fim_status = status["fim_utc"] if status else ""
    duracao_status = status["duracao_min"] if status else ""
    diferenca_inicio = (
        (_dt(inicio_status) - _dt(oficial["inicio"])).total_seconds() / 60
        if inicio_status else None
    )
    duracao_oficial = _duracao(oficial["inicio"], oficial["fim"])
    diferenca_duracao = float(duracao_status) - duracao_oficial if duracao_status else None
    bate = (
        diferenca_inicio is not None and diferenca_duracao is not None
        and abs(diferenca_inicio) <= 15 and abs(diferenca_duracao) <= 15
    )
    return {
        "plataforma": plataforma,
        "id_status": status["id"] if status else "",
        "incidente_status": status["titulo"] if status else "",
        "inicio_status": inicio_status,
        "fim_status": fim_status,
        "duracao_status_min": duracao_status,
        "incidente_oficial": oficial["incidente"],
        "inicio_oficial": oficial["inicio"],
        "fim_oficial": oficial["fim"],
        "duracao_oficial_min": f"{duracao_oficial:.2f}",
        "causa_oficial": oficial["causa"],
        "link_oficial": oficial["link"],
        "situacao": "ambas" if status else "somente_fonte_oficial",
        "diferenca_inicio_min": "" if diferenca_inicio is None else f"{diferenca_inicio:.2f}",
        "diferenca_duracao_min": "" if diferenca_duracao is None else f"{diferenca_duracao:.2f}",
        "horarios_batem_15min": str(bate).lower(),
    }


def triangular(relatorios: list[dict[str, str]]) -> list[dict[str, str]]:
    with ARQUIVO_INCIDENTES.open(encoding="utf-8", newline="") as entrada:
        incidentes = list(csv.DictReader(entrada))
    github = [r for r in incidentes if r["plataforma"] == "github"]
    usados: set[str] = set()
    resultado: list[dict[str, str]] = []

    for oficial in relatorios:
        inicio_oficial = _dt(oficial["inicio"])
        duracao_oficial = _duracao(oficial["inicio"], oficial["fim"])
        candidatos = []
        for status in github:
            if status["id"] in usados or not status["duracao_min"]:
                continue
            delta_inicio = abs((_dt(status["inicio_utc"]) - inicio_oficial).total_seconds() / 60)
            # Uma diferença maior que 12 h não é um pareamento defensável sem
            # identificador comum; evita, por exemplo, ligar eventos de dias
            # consecutivos apenas porque têm duração parecida.
            if delta_inicio > 12 * 60:
                continue
            delta_duracao = abs(float(status["duracao_min"]) - duracao_oficial)
            candidatos.append((
                delta_inicio + delta_duracao * 0.25 + _penalidade_assunto(status, oficial),
                status,
            ))
        status = min(candidatos, key=lambda item: item[0])[1] if candidatos else None
        if status:
            usados.add(status["id"])
        resultado.append(_linha_resultado(status, oficial, "github"))

    for status in github:
        if status["id"] not in usados:
            vazio = {"incidente": "", "inicio": status["inicio_utc"], "fim": status["fim_utc"] or status["inicio_utc"], "causa": "", "link": ""}
            linha = _linha_resultado(status, vazio, "github")
            linha["situacao"] = "somente_status"
            linha["inicio_oficial"] = linha["fim_oficial"] = linha["duracao_oficial_min"] = ""
            linha["diferenca_inicio_min"] = linha["diferenca_duracao_min"] = ""
            linha["horarios_batem_15min"] = "false"
            resultado.append(linha)

    por_id = {r["id"]: r for r in incidentes if r["plataforma"] == "gitlab"}
    with ARQUIVO_GITLAB.open(encoding="utf-8", newline="") as entrada:
        for amostra in csv.DictReader(entrada):
            oficial = {
                "incidente": amostra["incidente"], "inicio": amostra["inicio_utc"],
                "fim": amostra["fim_utc"], "causa": amostra["causa"], "link": amostra["link"],
            }
            resultado.append(_linha_resultado(por_id.get(amostra["id_status"]), oficial, "gitlab"))
    return resultado


def main() -> None:
    relatorios = gerar_relatorios_mensais()
    resultado = triangular(relatorios)
    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with ARQUIVO_SAIDA.open("w", newline="", encoding="utf-8") as saida:
        escritor = csv.DictWriter(saida, fieldnames=resultado[0].keys(), lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(resultado)
    print(f"Triangulação: {len(relatorios)} relatos do GitHub e 1 issue do GitLab.")


if __name__ == "__main__":
    main()

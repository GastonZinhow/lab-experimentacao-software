"""Coletor do histórico de incidentes do GitLab Status (status.gitlab.com).

Fonte escolhida: o feed iCalendar ``all.ics`` da página no status.io. É a única
fonte que cobre os 12 meses em um único arquivo (o RSS traz só os últimos 10
incidentes e o histórico HTML exige dezenas de páginas).

**robots.txt:** ``status.gitlab.com`` bloqueia ``/pages/*``, onde ficam o iCal,
o RSS e o histórico. Por decisão do grupo (``plano_coleta.md``, opção C), uma
pessoa salva o ``all.ics`` pelo navegador em ``dados/brutos/gitlab/all.ics``.
Este coletor **só lê o arquivo local**: se ele não existir, o cliente consulta o
robots.txt, vê o bloqueio e para com uma mensagem explicando o que fazer.

Uso (a partir de ``lab05/code``)::

    python -m coleta.gitlab --inicio 2026-10-01T00:00:00Z --fim 2026-10-31T23:59:59Z
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

from coleta._http import ClienteEducado

ID_PAGINA = "5b36dc6502d06804c08349f7"
URL_ICAL = f"https://status.gitlab.com/pages/{ID_PAGINA}/calendar/all.ics"
ARQUIVO_ICAL = "all.ics"
PASTA_BRUTOS = Path(__file__).resolve().parents[1] / "dados" / "brutos" / "gitlab"
FONTE = "statusgitlab_ical"
PADRAO_ISSUE_PRODUCAO = re.compile(
    r"https://gitlab\.com/gitlab-com/gl-infra/production/-/(?:issues|work_items|incidents)/\d+"
)


# --------------------------------------------------------------------------- #
# iCalendar (RFC 5545), só o necessário
# --------------------------------------------------------------------------- #


def desdobrar_linhas(texto: str) -> list[str]:
    """Junta as linhas continuadas (que começam com espaço ou tab)."""
    linhas: list[str] = []
    for linha in texto.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if linha[:1] in (" ", "\t") and linhas:
            linhas[-1] += linha[1:]
        else:
            linhas.append(linha)
    return linhas


def desescapar(valor: str) -> str:
    return (
        valor.replace("\\n", "\n")
        .replace("\\N", "\n")
        .replace("\\,", ",")
        .replace("\\;", ";")
        .replace("\\\\", "\\")
    )


def ler_data(valor: str, parametros: dict[str, str]) -> datetime:
    """Lê DTSTART/DTEND. Aceita UTC (``...Z``); horário sem fuso é tratado como UTC."""
    if parametros.get("VALUE") == "DATE" or len(valor) == 8:
        return datetime.strptime(valor[:8], "%Y%m%d").replace(tzinfo=timezone.utc)
    if "TZID" in parametros and parametros["TZID"].upper() not in ("UTC", "GMT", "ETC/UTC"):
        raise ValueError(f"Fuso horário não tratado no iCal: {parametros['TZID']}")
    return datetime.strptime(valor.rstrip("Z")[:15], "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)


def ler_eventos(texto: str) -> list[dict]:
    """Devolve os VEVENT como dicionários ``{PROPRIEDADE: (valor, parametros)}``."""
    eventos, atual = [], None
    for linha in desdobrar_linhas(texto):
        if linha == "BEGIN:VEVENT":
            atual = {}
        elif linha == "END:VEVENT":
            if atual is not None:
                eventos.append(atual)
            atual = None
        elif atual is not None and ":" in linha:
            cabeca, valor = linha.split(":", 1)
            nome, *resto = cabeca.split(";")
            parametros = dict(p.split("=", 1) for p in resto if "=" in p)
            atual.setdefault(nome.upper(), (valor, parametros))
    return eventos


# --------------------------------------------------------------------------- #
# Incidentes
# --------------------------------------------------------------------------- #


def eh_manutencao(evento: dict) -> bool:
    """Manutenções planejadas também vêm no iCal e não são incidentes.

    O arquivo não tem campo que as diferencie (só UID, DTSTAMP, DTSTART, DTEND,
    SUMMARY, DESCRIPTION). O sinal confiável é o horário: manutenção é agendada
    e começa em hora cheia ou quarto de hora (``HH:00/15/30/45:00``) e termina com
    segundos ``00``; incidente começa quando é aberto (ex.: ``16:51:44``).
    Palavras como "maintenance" ou "scheduled" **não** servem: aparecem em
    incidentes reais ("Customers Portal in maintenance mode", "Scheduled jobs not
    triggering"). Regra conferida nos 797 eventos do arquivo de 2026-11-19.
    """
    inicio, fim = evento["DTSTART"][0], evento.get("DTEND", ("", {}))[0]
    hora = re.fullmatch(r"\d{8}T\d{2}(\d{2})(\d{2})Z?", inicio)
    fim_hora = re.fullmatch(r"\d{8}T\d{4}(\d{2})Z?", fim)
    if not hora or not fim_hora:
        return False
    minuto, segundo = int(hora.group(1)), int(hora.group(2))
    return segundo == 0 and minuto % 15 == 0 and fim_hora.group(1) == "00"


def formatar_utc(valor: datetime | None) -> str:
    return "" if valor is None else valor.strftime("%Y-%m-%dT%H:%M:%SZ")


def normalizar_evento(evento: dict) -> dict:
    """Converte um VEVENT para o dicionário devolvido pelo coletor.

    O iCal **não traz componentes nem impacto**: só título, início, fim e um
    texto do incidente (``descricao``; às vezes é a primeira atualização, às
    vezes a de resolução). Esses dois campos ficam vazios aqui; ver o relato do
    piloto em ``plano_coleta.md``.
    """
    uid = evento["UID"][0].strip().split("@")[0]
    inicio = ler_data(*evento["DTSTART"])
    fim = ler_data(*evento["DTEND"]) if "DTEND" in evento else None
    descricao = desescapar(evento.get("DESCRIPTION", ("", {}))[0])
    issues = sorted(set(PADRAO_ISSUE_PRODUCAO.findall(descricao)))
    return {
        "plataforma": "gitlab",
        "id": uid,
        "titulo": desescapar(evento.get("SUMMARY", ("", {}))[0]).strip(),
        "componentes_originais": "",
        "impacto": "",
        "inicio_utc": formatar_utc(inicio),
        "fim_utc": formatar_utc(fim),
        "duracao_min": None if fim is None else round((fim - inicio).total_seconds() / 60, 2),
        "fonte": FONTE,
        # O UID do iCal não é o id do status.io usado em /pages/incident/..., então
        # o endereço aponta para o evento dentro do arquivo de origem.
        "url": f"{URL_ICAL}#{uid}",
        "issue_producao": ";".join(issues),
        "manutencao": eh_manutencao(evento),
        "descricao": descricao,
    }


def coletar(
    inicio: str | datetime,
    fim: str | datetime,
    cliente: ClienteEducado | None = None,
) -> list[dict]:
    """Devolve um dicionário por incidente do GitLab iniciado em ``[inicio, fim]``."""
    from coleta.github import como_utc  # mesma conversão de datas nos dois coletores

    inicio, fim = como_utc(inicio), como_utc(fim)
    cliente = cliente or ClienteEducado(PASTA_BRUTOS)
    texto = cliente.obter(URL_ICAL, ARQUIVO_ICAL).decode("utf-8")
    if (cliente.pasta / ARQUIVO_ICAL).exists():
        cliente.registrar_arquivo_manual(URL_ICAL, ARQUIVO_ICAL)

    incidentes = []
    for evento in ler_eventos(texto):
        registro = normalizar_evento(evento)
        if registro["manutencao"]:
            continue
        if inicio <= como_utc(registro["inicio_utc"]) <= fim:
            incidentes.append(registro)
    return sorted(incidentes, key=lambda r: (r["inicio_utc"], r["id"]))


def resumir(incidentes: list[dict]) -> str:
    if not incidentes:
        return "Nenhum incidente na janela."
    duracoes = sorted(r["duracao_min"] for r in incidentes if r["duracao_min"] is not None)
    return "\n".join(
        [
            f"Incidentes: {len(incidentes)}",
            f"Primeiro início: {incidentes[0]['inicio_utc']} · último: {incidentes[-1]['inicio_utc']}",
            f"Com issue de produção: {sum(1 for r in incidentes if r['issue_producao'])}",
            f"Duração (min): mínima {duracoes[0]}, mediana {median(duracoes):.2f}, máxima {duracoes[-1]}"
            if duracoes
            else "Duração: sem dados",
            f"Títulos mais comuns: {Counter(r['titulo'] for r in incidentes).most_common(3)}",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--inicio", required=True)
    parser.add_argument("--fim", required=True)
    argumentos = parser.parse_args()
    print(resumir(coletar(argumentos.inicio, argumentos.fim)))


if __name__ == "__main__":
    main()

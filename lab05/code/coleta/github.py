"""Coletor do histórico de incidentes do GitHub Status (www.githubstatus.com).

Fontes usadas (ambas permitidas pelo robots.txt, que só bloqueia ``/api/`` e
``/embed/``):

* ``/history.json?page=N`` — a mesma lista que a página ``/history`` carrega
  por JavaScript. Cada página traz três meses, com código, título, impacto e
  horário de exibição de cada incidente. A página 1 começa no mês corrente.
* ``/incidents/<código>.json`` — detalhes de um incidente: ``started_at``,
  ``resolved_at``, ``impact``, ``components`` e as atualizações publicadas.

As respostas são salvas sem alteração em ``dados/brutos/github/``:
``historico/pagina_NN.json`` e ``incidentes/<código>.json``. Como a numeração
das páginas do histórico muda a cada mês, as páginas precisam ser baixadas no
mesmo dia; o coletor confere se elas são contíguas.

Uso pela linha de comando (a partir de ``lab05/code``)::

    python -m coleta.github --inicio 2026-10-01 --fim 2026-10-31T23:59:59Z
    python -m coleta.github --inicio 2025-11-01 --fim 2026-10-31T23:59:59Z --so-listar
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import median

from coleta._http import ClienteEducado, ErroColeta

BASE = "https://www.githubstatus.com"
URL_HISTORICO = BASE + "/history.json?page={pagina}"
URL_INCIDENTE_JSON = BASE + "/incidents/{codigo}.json"
URL_INCIDENTE = BASE + "/incidents/{codigo}"
PASTA_BRUTOS = Path(__file__).resolve().parents[1] / "dados" / "brutos" / "github"
FONTE = "githubstatus"
MAXIMO_PAGINAS = 60
MESES = {
    nome: numero
    for numero, nome in enumerate(
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        start=1,
    )
}


# --------------------------------------------------------------------------- #
# Datas
# --------------------------------------------------------------------------- #


def como_utc(valor: str | datetime) -> datetime:
    """Converte texto ISO 8601 (ou datetime) para datetime em UTC."""
    if isinstance(valor, str):
        valor = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc)


def formatar_utc(valor: datetime | None) -> str:
    return "" if valor is None else valor.strftime("%Y-%m-%dT%H:%M:%SZ")


def data_inicial_exibida(timestamp: str, ano_do_bloco: int, mes_do_bloco: int) -> date | None:
    """Lê a data de início do texto do histórico (ex.: ``Aug <var>26</var>, ...``)."""
    texto = re.sub(r"<[^>]+>", "", timestamp)
    achado = re.match(r"\s*([A-Z][a-z]{2})\s+(\d{1,2})", texto)
    if not achado or achado.group(1) not in MESES:
        return None
    mes, dia = MESES[achado.group(1)], int(achado.group(2))
    ano = ano_do_bloco - 1 if mes > mes_do_bloco else ano_do_bloco
    return date(ano, mes, dia)


# --------------------------------------------------------------------------- #
# Histórico
# --------------------------------------------------------------------------- #


def ler_pagina_historico(cliente: ClienteEducado, pagina: int) -> dict:
    conteudo = cliente.obter(
        URL_HISTORICO.format(pagina=pagina), f"historico/pagina_{pagina:02d}.json"
    )
    return json.loads(conteudo)


def listar_incidentes(
    inicio: datetime, fim: datetime, cliente: ClienteEducado
) -> tuple[list[dict], dict]:
    """Percorre o histórico até cobrir ``inicio`` e devolve os itens da janela.

    A data exibida no histórico é usada só como pré-filtro, com margem de um
    dia; o filtro exato usa ``started_at`` do JSON do incidente.
    """
    margem = timedelta(days=1)
    menor, maior = (inicio - margem).date(), (fim + margem).date()
    itens: list[dict] = []
    cobertura = {"paginas": 0, "inicio_mais_antigo": None, "cobre_inicio": False}
    inicio_pagina_anterior: datetime | None = None

    for pagina in range(1, MAXIMO_PAGINAS + 1):
        dados = ler_pagina_historico(cliente, pagina)
        meses = dados.get("months") or []
        if not meses:
            break
        cobertura["paginas"] = pagina
        inicio_pagina, fim_pagina = como_utc(dados["start_time"]), como_utc(dados["end_time"])
        if inicio_pagina_anterior is not None and fim_pagina >= inicio_pagina_anterior:
            raise ErroColeta(
                "As páginas do histórico não são contíguas: provavelmente foram baixadas "
                "em meses diferentes. Apague dados/brutos/github/historico/ e colete de novo."
            )
        inicio_pagina_anterior = inicio_pagina
        cobertura["inicio_mais_antigo"] = formatar_utc(inicio_pagina)

        for mes in meses:
            numero_mes = MESES[mes["name"][:3]]
            for item in mes.get("incidents", []):
                exibida = data_inicial_exibida(item.get("timestamp", ""), mes["year"], numero_mes)
                if exibida is None or menor <= exibida <= maior:
                    itens.append({**item, "data_exibida": exibida, "mes": f"{mes['year']}-{numero_mes:02d}"})

        if inicio_pagina <= inicio:
            cobertura["cobre_inicio"] = True
            break

    vistos: set[str] = set()
    unicos = [i for i in itens if not (i["code"] in vistos or vistos.add(i["code"]))]
    return unicos, cobertura


# --------------------------------------------------------------------------- #
# Incidentes
# --------------------------------------------------------------------------- #


def eh_retroativo(bruto: dict) -> bool:
    """Incidente publicado depois do fato: só tem atualização ``resolved``.

    Nesses casos o Statuspage grava ``created_at`` = ``resolved_at`` com um
    horário aproximado (às vezes o início, às vezes o fim do evento) e
    ``started_at`` com a hora da postagem. A duração real só aparece no texto.
    """
    estados = {u.get("status") for u in bruto.get("incident_updates") or []}
    return bool(estados) and estados <= {"resolved", "postmortem"}


def normalizar_incidente(bruto: dict) -> dict:
    """Converte o JSON de um incidente para o dicionário devolvido pelo coletor.

    * ``inicio_utc``: primeiro registro público, ``min(created_at, started_at)``.
      Há incidentes com ``started_at`` editado para depois de ``created_at``.
    * ``fim_utc``: ``resolved_at``.
    * Incidentes retroativos ficam sem ``fim_utc`` e sem ``duracao_min`` (não
      imputamos a duração sem evidência estruturada) e com ``retroativo=True``.
    """
    criado = como_utc(bruto["created_at"])
    inicio = min(criado, como_utc(bruto["started_at"])) if bruto.get("started_at") else criado
    retroativo = eh_retroativo(bruto)
    fim = (
        como_utc(bruto["resolved_at"])
        if bruto.get("resolved_at") and not retroativo
        else None
    )
    componentes = sorted({c["name"] for c in bruto.get("components") or []})
    return {
        "plataforma": "github",
        "id": bruto["id"],
        "titulo": bruto["name"].strip(),
        "componentes_originais": ";".join(componentes),
        "impacto": bruto.get("impact") or "",
        "inicio_utc": formatar_utc(inicio),
        "fim_utc": formatar_utc(fim),
        "duracao_min": None if fim is None else round((fim - inicio).total_seconds() / 60, 2),
        "fonte": FONTE,
        "url": URL_INCIDENTE.format(codigo=bruto["id"]),
        "status": bruto.get("status", ""),
        "retroativo": retroativo,
        "manutencao": bool(bruto.get("scheduled_for")),
    }


def ler_incidente(cliente: ClienteEducado, codigo: str) -> dict:
    conteudo = cliente.obter(
        URL_INCIDENTE_JSON.format(codigo=codigo), f"incidentes/{codigo}.json"
    )
    return json.loads(conteudo)


def coletar(
    inicio: str | datetime,
    fim: str | datetime,
    cliente: ClienteEducado | None = None,
) -> list[dict]:
    """Devolve um dicionário por incidente do GitHub iniciado em ``[inicio, fim]``."""
    inicio, fim = como_utc(inicio), como_utc(fim)
    cliente = cliente or ClienteEducado(PASTA_BRUTOS)
    itens, _ = listar_incidentes(inicio, fim, cliente)

    incidentes = []
    for item in itens:
        registro = normalizar_incidente(ler_incidente(cliente, item["code"]))
        if registro["manutencao"]:
            continue
        if inicio <= como_utc(registro["inicio_utc"]) <= fim:
            incidentes.append(registro)
    return sorted(incidentes, key=lambda r: (r["inicio_utc"], r["id"]))


# --------------------------------------------------------------------------- #
# Linha de comando
# --------------------------------------------------------------------------- #


def resumir(incidentes: list[dict]) -> str:
    if not incidentes:
        return "Nenhum incidente na janela."
    duracoes = sorted(r["duracao_min"] for r in incidentes if r["duracao_min"] is not None)
    componentes = Counter(
        c for r in incidentes for c in r["componentes_originais"].split(";") if c
    )
    linhas = [
        f"Incidentes: {len(incidentes)}",
        f"Primeiro início: {incidentes[0]['inicio_utc']} · último: {incidentes[-1]['inicio_utc']}",
        f"Impacto: {dict(Counter(r['impacto'] for r in incidentes))}",
        f"Sem componente: {sum(1 for r in incidentes if not r['componentes_originais'])}",
        f"Retroativos (sem duração): {sum(1 for r in incidentes if r['retroativo'])}",
        f"Sem resolução: {sum(1 for r in incidentes if not r['fim_utc'] and not r['retroativo'])}",
        f"Duração (min): mínima {duracoes[0]}, mediana {median(duracoes):.2f}, máxima {duracoes[-1]}"
        if duracoes
        else "Duração: sem dados",
        f"Componentes: {dict(componentes.most_common())}",
    ]
    return "\n".join(linhas)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--inicio", required=True)
    parser.add_argument("--fim", required=True)
    parser.add_argument(
        "--so-listar",
        action="store_true",
        help="só percorre o histórico (contagem por mês), sem baixar cada incidente",
    )
    argumentos = parser.parse_args()
    cliente = ClienteEducado(PASTA_BRUTOS)

    if argumentos.so_listar:
        itens, cobertura = listar_incidentes(
            como_utc(argumentos.inicio), como_utc(argumentos.fim), cliente
        )
        print(f"Cobertura: {cobertura}")
        for mes, total in sorted(Counter(i["mes"] for i in itens).items()):
            print(f"{mes}: {total} incidente(s) no histórico")
    else:
        print(resumir(coletar(argumentos.inicio, argumentos.fim, cliente)))
    print(f"Requisições feitas nesta execução: {cliente.requisicoes}")


if __name__ == "__main__":
    main()

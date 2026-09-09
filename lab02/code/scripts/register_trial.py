"""
Script de cronometragem e coleta de trials (LAB02, issue #20).

Cobre o Passo 3 do experimento: cada trial (integrante x kata x tratamento)
precisa registrar o tempo ate passar em todos os testes de aceitacao (ou o
fim do time-box) e o numero de testes passando ao final.

Uso tipico:

    python register_trial.py start --integrante Mirelly --kata k01 --tratamento IA
    ... (participante resolve o kata dentro do projeto katas-java) ...
    python register_trial.py stop

O "stop" roda `mvn test` filtrado no pacote do kata, le o resultado no
surefire e grava uma linha em lab02/code/data/raw/trials.csv. Se o tempo
decorrido ultrapassar o time-box (default 2100 segundos = 35 min), o trial
e marcado como censurado e o tempo e truncado no valor do time-box
(conforme especificado no enunciado: trial censurado deve ser registrado no
time-box, nao descartado).
"""

import argparse
import csv
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent.parent
MAVEN_PROJECT_DIR = CODE_DIR / "katas-java"
MAVEN_CMD = shutil.which("mvn") or "mvn"
DATA_DIR = CODE_DIR / "data" / "raw"
TRIALS_CSV = DATA_DIR / "trials.csv"
STATE_FILE = Path(__file__).resolve().parent / ".trial_state.json"

CSV_FIELDS = [
    "trial_id",
    "integrante",
    "kata",
    "tratamento",
    "timebox_segundos",
    "inicio",
    "fim",
    "tempo_segundos",
    "tempo_min",
    "censurado",
    "testes_passando",
    "testes_total",
    "taxa_sucesso",
    "observacoes",
]

DEFAULT_TIMEBOX_SEGUNDOS = 2100  # 35 min - so pode ser reduzido, nunca aumentado
TREATMENTS = {"IA", "Manual"}


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def cmd_start(args):
    if args.tratamento not in TREATMENTS:
        sys.exit(f"--tratamento deve ser um de {sorted(TREATMENTS)}, recebido '{args.tratamento}'")

    if args.timebox > DEFAULT_TIMEBOX_SEGUNDOS:
        sys.exit(
            f"--timebox de {args.timebox}s excede o limite de {DEFAULT_TIMEBOX_SEGUNDOS}s (35 min). "
            "O enunciado permite reduzir o time-box, nunca aumenta-lo."
        )

    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        sys.exit(
            "Ja existe um trial em andamento "
            f"({state['integrante']}/{state['kata']}/{state['tratamento']}, "
            f"iniciado em {state['inicio']}). Rode 'stop' ou 'abort' antes de iniciar outro."
        )

    state = {
        "integrante": args.integrante,
        "kata": args.kata,
        "tratamento": args.tratamento,
        "timebox_segundos": args.timebox,
        "inicio": now_iso(),
    }
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Trial iniciado: {state['integrante']} / {state['kata']} / {state['tratamento']}")
    print(f"Time-box: {state['timebox_segundos']}s. Inicio: {state['inicio']}")


def cmd_status(_args):
    if not STATE_FILE.exists():
        print("Nenhum trial em andamento.")
        return
    state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    inicio = datetime.fromisoformat(state["inicio"])
    elapsed = (datetime.now(timezone.utc).astimezone() - inicio).total_seconds()
    print(json.dumps(state, indent=2, ensure_ascii=False))
    print(f"Decorrido: {elapsed:.0f}s (time-box: {state['timebox_segundos']}s)")


def cmd_abort(_args):
    if not STATE_FILE.exists():
        sys.exit("Nenhum trial em andamento para abortar.")
    state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    STATE_FILE.unlink()
    print(f"Trial de {state['integrante']}/{state['kata']}/{state['tratamento']} abortado sem registrar dados.")


def run_maven_tests(kata: str):
    """Roda os testes de aceitacao do kata e devolve (passando, total, erro)."""
    package = f"katas.{kata}"
    reports_dir = MAVEN_PROJECT_DIR / "target" / "surefire-reports"
    for old in reports_dir.glob(f"TEST-{package}.*.xml"):
        old.unlink()

    result = subprocess.run(
        [MAVEN_CMD, "-q", "test", f"-Dtest={package}.*Test", "-DfailIfNoTests=false"],
        cwd=MAVEN_PROJECT_DIR,
        capture_output=True,
        text=True,
    )

    reports = sorted(reports_dir.glob(f"TEST-{package}.*.xml"))
    if not reports:
        return 0, None, "nenhum relatorio de teste gerado (erro de compilacao ou kata sem testes)"

    total = 0
    failing = 0
    for report in reports:
        root = ET.parse(report).getroot()
        total += int(root.attrib.get("tests", 0))
        failing += int(root.attrib.get("failures", 0)) + int(root.attrib.get("errors", 0))

    passing = total - failing
    erro = None if result.returncode == 0 else "mvn retornou erro (esperado se houver testes falhando)"
    return passing, total, erro


def cmd_stop(args):
    if not STATE_FILE.exists():
        sys.exit("Nenhum trial em andamento. Rode 'start' primeiro.")

    state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    fim_dt = datetime.now(timezone.utc).astimezone()
    inicio_dt = datetime.fromisoformat(state["inicio"])
    tempo_segundos = (fim_dt - inicio_dt).total_seconds()

    timebox_segundos = state["timebox_segundos"]
    censurado = tempo_segundos >= timebox_segundos
    tempo_efetivo = min(tempo_segundos, timebox_segundos)

    testes_passando, testes_total, erro = (None, None, None)
    if not args.sem_testes:
        testes_passando, testes_total, erro = run_maven_tests(state["kata"])

    taxa_sucesso = ""
    if testes_total:
        taxa_sucesso = f"{testes_passando / testes_total:.4f}"

    observacoes = args.observacao or ""
    if erro:
        observacoes = f"{observacoes} | {erro}".strip(" |")

    row = {
        "trial_id": f"{state['integrante']}-{state['kata']}-{state['tratamento']}",
        "integrante": state["integrante"],
        "kata": state["kata"],
        "tratamento": state["tratamento"],
        "timebox_segundos": timebox_segundos,
        "inicio": state["inicio"],
        "fim": fim_dt.isoformat(timespec="seconds"),
        "tempo_segundos": round(tempo_efetivo, 1),
        "tempo_min": round(tempo_efetivo / 60, 2),
        "censurado": censurado,
        "testes_passando": testes_passando if testes_passando is not None else "",
        "testes_total": testes_total if testes_total is not None else "",
        "taxa_sucesso": taxa_sucesso,
        "observacoes": observacoes,
    }
    append_row(row)
    STATE_FILE.unlink()

    print(f"Trial encerrado: {row['trial_id']}")
    print(f"Tempo: {row['tempo_segundos']}s (censurado={censurado})")
    if testes_total:
        print(f"Testes: {testes_passando}/{testes_total} passando ({row['taxa_sucesso']})")


def append_row(row: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    write_header = not TRIALS_CSV.exists()
    with TRIALS_CSV.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def build_parser():
    parser = argparse.ArgumentParser(description="Cronometragem e coleta de trials do LAB02.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_start = sub.add_parser("start", help="Inicia a cronometragem de um trial.")
    p_start.add_argument("--integrante", required=True, help="Nome do integrante que esta resolvendo o kata.")
    p_start.add_argument("--kata", required=True, help="Identificador do kata, ex.: k01 (pacote katas.k01).")
    p_start.add_argument("--tratamento", required=True, choices=sorted(TREATMENTS))
    p_start.add_argument(
        "--timebox",
        type=int,
        default=DEFAULT_TIMEBOX_SEGUNDOS,
        help="Time-box em segundos (default 2100 = 35 min; so pode ser reduzido).",
    )
    p_start.set_defaults(func=cmd_start)

    p_stop = sub.add_parser("stop", help="Encerra o trial em andamento e registra os dados.")
    p_stop.add_argument("--observacao", default="", help="Observacao livre para a linha do CSV.")
    p_stop.add_argument("--sem-testes", action="store_true", help="Nao roda mvn test (registra so o tempo).")
    p_stop.set_defaults(func=cmd_stop)

    p_status = sub.add_parser("status", help="Mostra o trial em andamento, se houver.")
    p_status.set_defaults(func=cmd_status)

    p_abort = sub.add_parser("abort", help="Cancela o trial em andamento sem gravar dados.")
    p_abort.set_defaults(func=cmd_abort)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

"""Executa, em ordem, todas as etapas reproduzíveis do Lab04."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

PASTA_CODIGO = Path(__file__).resolve().parent
PASTA_ETAPAS = PASTA_CODIGO / "etapas"
PASTAS_SAIDA = (PASTA_CODIGO / "dados", PASTA_CODIGO / "resultados")

if str(PASTA_CODIGO) not in sys.path:
    sys.path.insert(0, str(PASTA_CODIGO))


def descobrir_etapas(pasta: Path = PASTA_ETAPAS) -> list[Path]:
    """Lista as etapas ``NN_nome.py`` em ordem numérica."""
    return sorted(pasta.glob("[0-9][0-9]_*.py"), key=lambda caminho: caminho.name)


def carregar_etapa(caminho: Path) -> ModuleType:
    """Importa uma etapa diretamente de seu arquivo."""
    nome_modulo = f"lab04_etapas.{caminho.stem}"
    especificacao = importlib.util.spec_from_file_location(nome_modulo, caminho)
    if especificacao is None or especificacao.loader is None:
        raise ImportError(f"Não foi possível importar {caminho.name}")

    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


def executar(pasta: Path = PASTA_ETAPAS) -> None:
    """Executa a função ``main()`` de cada etapa encontrada."""
    etapas = descobrir_etapas(pasta)
    if not etapas:
        print("Nenhuma etapa disponível ainda.")
        return

    for numero, caminho in enumerate(etapas, start=1):
        print(f"[{numero}/{len(etapas)}] {caminho.name}")
        modulo = carregar_etapa(caminho)
        main = getattr(modulo, "main", None)
        if not callable(main):
            raise AttributeError(f"{caminho.name} precisa expor uma função main()")
        main()
    print("Todas as etapas foram concluídas.")


def resumir_saidas(pastas: tuple[Path, ...] = PASTAS_SAIDA) -> dict[str, str]:
    """Calcula hashes das saídas para comparar duas execuções."""
    hashes = {}
    for pasta in pastas:
        if not pasta.exists():
            continue
        for arquivo in sorted(caminho for caminho in pasta.rglob("*") if caminho.is_file()):
            if "__pycache__" in arquivo.parts:
                continue
            relativo = f"{pasta.name}/{arquivo.relative_to(pasta).as_posix()}"
            hashes[relativo] = hashlib.sha256(arquivo.read_bytes()).hexdigest()
    return hashes


def verificar_reprodutibilidade(
    pasta_etapas: Path = PASTA_ETAPAS,
    pastas_saida: tuple[Path, ...] = PASTAS_SAIDA,
) -> None:
    """Executa o pipeline duas vezes e falha se alguma saída mudar."""
    print("Execução 1 de 2")
    executar(pasta_etapas)
    primeira = resumir_saidas(pastas_saida)

    print("Execução 2 de 2")
    executar(pasta_etapas)
    segunda = resumir_saidas(pastas_saida)

    if primeira != segunda:
        alterados = sorted(
            caminho
            for caminho in primeira.keys() | segunda.keys()
            if primeira.get(caminho) != segunda.get(caminho)
        )
        raise RuntimeError(
            "As execuções produziram saídas diferentes: " + ", ".join(alterados)
        )
    print(f"Reprodutibilidade confirmada em {len(segunda)} arquivo(s) de saída.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verificar-reprodutibilidade",
        action="store_true",
        help="executa todas as etapas duas vezes e compara suas saídas",
    )
    argumentos = parser.parse_args()

    if argumentos.verificar_reprodutibilidade:
        verificar_reprodutibilidade()
    else:
        executar()


if __name__ == "__main__":
    main()

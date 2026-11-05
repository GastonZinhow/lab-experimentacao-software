from pathlib import Path

import pytest

from run_all import descobrir_etapas, executar, verificar_reprodutibilidade


def criar_etapa(pasta: Path, nome: str, corpo: str) -> Path:
    caminho = pasta / nome
    caminho.write_text(corpo, encoding="utf-8")
    return caminho


def test_descobre_somente_etapas_e_ordena_pelo_numero(tmp_path):
    criar_etapa(tmp_path, "10_decima.py", "def main(): pass\n")
    criar_etapa(tmp_path, "02_segunda.py", "def main(): pass\n")
    criar_etapa(tmp_path, "rascunho.py", "def main(): pass\n")

    assert [caminho.name for caminho in descobrir_etapas(tmp_path)] == [
        "02_segunda.py",
        "10_decima.py",
    ]


def test_executa_todas_as_etapas_na_ordem(tmp_path):
    saida = tmp_path / "ordem.txt"
    criar_etapa(
        tmp_path,
        "02_segunda.py",
        f"def main():\n    open({str(saida)!r}, 'a').write('2')\n",
    )
    criar_etapa(
        tmp_path,
        "01_primeira.py",
        f"def main():\n    open({str(saida)!r}, 'a').write('1')\n",
    )

    executar(tmp_path)

    assert saida.read_text(encoding="utf-8") == "12"


def test_falha_quando_etapa_nao_expoe_main(tmp_path):
    criar_etapa(tmp_path, "01_invalida.py", "VALOR = 1\n")

    with pytest.raises(AttributeError, match=r"função main\(\)"):
        executar(tmp_path)


def test_duas_execucoes_deterministicas_sao_aceitas(tmp_path):
    etapas = tmp_path / "etapas"
    resultados = tmp_path / "resultados"
    etapas.mkdir()
    resultados.mkdir()
    saida = resultados / "saida.txt"
    criar_etapa(
        etapas,
        "01_deterministica.py",
        f"def main():\n    open({str(saida)!r}, 'w').write('semente 42')\n",
    )

    verificar_reprodutibilidade(etapas, (resultados,))

    assert saida.read_text(encoding="utf-8") == "semente 42"

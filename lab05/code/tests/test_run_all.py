from pathlib import Path

import pytest

import run_all


def escrever_etapa(pasta: Path, nome: str, conteudo: str) -> None:
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / nome).write_text(conteudo, encoding="utf-8")


def test_descobrir_etapas_filtra_e_ordena(tmp_path: Path) -> None:
    escrever_etapa(tmp_path, "20_segunda.py", "def main(): pass\n")
    escrever_etapa(tmp_path, "01_primeira.py", "def main(): pass\n")
    escrever_etapa(tmp_path, "auxiliar.py", "def main(): pass\n")

    assert [etapa.name for etapa in run_all.descobrir_etapas(tmp_path)] == [
        "01_primeira.py",
        "20_segunda.py",
    ]


def test_executar_sem_etapas(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run_all.executar(tmp_path)

    assert capsys.readouterr().out == "Nenhuma etapa disponível ainda.\n"


def test_executar_chama_main_em_ordem(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    escrever_etapa(tmp_path, "02_segunda.py", "def main(): print('segunda')\n")
    escrever_etapa(tmp_path, "01_primeira.py", "def main(): print('primeira')\n")

    run_all.executar(tmp_path)

    saida = capsys.readouterr().out
    assert saida.index("primeira") < saida.index("segunda")
    assert "Todas as etapas foram concluídas." in saida


def test_executar_rejeita_etapa_sem_main(tmp_path: Path) -> None:
    escrever_etapa(tmp_path, "01_invalida.py", "VALOR = 1\n")

    with pytest.raises(AttributeError, match=r"precisa expor uma função main\(\)"):
        run_all.executar(tmp_path)


def test_verificar_reprodutibilidade_detecta_saida_variavel(tmp_path: Path) -> None:
    etapas = tmp_path / "etapas"
    saidas = tmp_path / "resultados"
    arquivo_saida = saidas / "valor.txt"
    escrever_etapa(
        etapas,
        "01_variavel.py",
        "from pathlib import Path\n"
        f"SAIDA = Path({str(arquivo_saida)!r})\n"
        "def main():\n"
        "    SAIDA.parent.mkdir(parents=True, exist_ok=True)\n"
        "    anterior = int(SAIDA.read_text()) if SAIDA.exists() else 0\n"
        "    SAIDA.write_text(str(anterior + 1))\n",
    )

    with pytest.raises(RuntimeError, match="resultados/valor.txt"):
        run_all.verificar_reprodutibilidade(etapas, (saidas,))

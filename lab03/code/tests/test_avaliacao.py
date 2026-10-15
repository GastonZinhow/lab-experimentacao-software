import pandas as pd
import pytest

from rotulagem.avaliacao import avaliar, formatar, metricas


def test_metricas_exemplo_enunciado():
    """40 marcadas, 30 confirmadas, 50 corretivas no consenso: P = 0,75, R = 0,60, F1 ≈ 0,67."""
    y_true = [True] * 30 + [False] * 10 + [True] * 20 + [False] * 40
    y_pred = [True] * 30 + [True] * 10 + [False] * 20 + [False] * 40
    res = metricas(y_true, y_pred)
    assert res["precisao"] == pytest.approx(0.75)
    assert res["recall"] == pytest.approx(0.60)
    assert res["f1"] == pytest.approx(2 * 0.75 * 0.6 / 1.35)
    assert (res["vp"], res["fp"], res["fn"], res["vn"], res["n"]) == (30, 10, 20, 40, 100)


def test_metricas_sem_positivos_previstos():
    res = metricas([True, False], [False, False])
    assert res["precisao"] == 0.0 and res["recall"] == 0.0 and res["f1"] == 0.0


def _planilha():
    return pd.DataFrame([
        {"item": "1", "full_name": "o/a", "tag_name": "v1.0.1", "tag_anterior": "v1.0.0"},
        {"item": "2", "full_name": "o/a", "tag_name": "v1.1.0", "tag_anterior": "v1.0.1"},
        {"item": "3", "full_name": "o/a", "tag_name": "v1.1.1", "tag_anterior": "v1.1.0"},
        {"item": "4", "full_name": "o/b", "tag_name": "v0.1.0", "tag_anterior": ""},
    ])


def _referencia(rotulos):
    df = _planilha()[["item", "full_name", "tag_name"]].copy()
    df["corretiva"] = rotulos
    return df


def _commits():
    return pd.DataFrame([
        {"repo": "o/a", "tag_name": "v1.0.1", "mensagem": "fix: crash"},
        {"repo": "o/a", "tag_name": "v1.1.0", "mensagem": "feat: export"},
        {"repo": "o/a", "tag_name": "v1.1.0", "mensagem": "fix: typo"},
        {"repo": "o/a", "tag_name": "v1.1.1", "mensagem": "docs: readme"},
    ])


def test_avaliar_v1_e_erros():
    res, tabela = avaliar(_referencia(["sim", "Não", "nao", "nao"]), _planilha(), _commits(), "v1")
    # v1 marca 1 (patch + fix), 2 (fix) e 3 (patch)
    assert (res["vp"], res["fp"], res["fn"], res["vn"]) == (1, 2, 0, 1)
    assert tabela.set_index("item")["erro"].to_dict() == {"1": "", "2": "FP", "3": "FP", "4": ""}
    assert pd.isna(tabela.set_index("item").loc["4", "tag_anterior"])


def test_avaliar_v3_com_notas():
    notas = pd.DataFrame([
        {"full_name": "o/a", "tag_name": "v1.1.1", "notas": "Bug fixes\n- Fixed broken export"},
    ])
    res, tabela = avaliar(_referencia(["sim", "nao", "sim", "nao"]), _planilha(), _commits(), "v3", notas)
    assert (res["vp"], res["fp"], res["fn"]) == (2, 0, 0)
    assert res["f1"] == pytest.approx(1.0)


def test_avaliar_ignora_itens_sem_rotulo():
    res, _ = avaliar(_referencia(["sim", "", "talvez", "nao"]), _planilha(), _commits(), "v1")
    assert res["n"] == 2


def test_avaliar_sem_rotulos_falha():
    with pytest.raises(ValueError):
        avaliar(_referencia(["", "", "", ""]), _planilha(), _commits(), "v1")


def test_formatar():
    texto = formatar("v1", metricas([True, False], [True, True]))
    assert texto.startswith("v1: P = 0.500 | R = 1.000 | F1 = 0.667")

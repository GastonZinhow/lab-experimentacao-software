import numpy as np
import pandas as pd
import pytest

from rotulagem.concordancia import (
    carregar_rotulos,
    conferir,
    consenso,
    divergencias,
    interpretar,
    kappa_fleiss,
    matriz,
    normalizar,
    resumo_kappa,
)
from rotulagem.sorteio import (
    base_do_sorteio,
    montar_planilha,
    releases_da_amostra,
    sortear_releases,
    sortear_repositorios,
)


# ==========================================
# Sorteio
# ==========================================

@pytest.fixture
def candidatos():
    n = 150
    status = ["incluido" if i % 3 else "descartado" for i in range(n)]
    return pd.DataFrame({
        "full_name": [f"org/repo{i:03d}" for i in range(n)],
        "ordem_avaliacao": list(range(n, 0, -1)),
        "status": status,
    })


@pytest.fixture
def releases():
    linhas = []
    for r in range(3):
        for v in range(8):
            linhas.append({
                "repo": f"org/r{r}",
                "tag_name": f"v1.{v}.0",
                "tag_anterior": f"v1.{v - 1}.0" if v else None,
                "published_at": f"2026-0{v + 1}-01T00:00:00Z",
                "na_janela": v != 0,
                "tipo": "prerelease" if v == 7 else "publicada",
                "html_url": f"https://github.com/org/r{r}/releases/tag/v1.{v}.0",
            })
    return pd.DataFrame(linhas)


def test_base_do_sorteio_pega_primeiros_incluidos_na_ordem(candidatos):
    base = base_do_sorteio(candidatos, 50)
    incluidos = candidatos[candidatos["status"] == "incluido"]
    esperado = set(incluidos.nsmallest(50, "ordem_avaliacao")["full_name"])
    assert set(base["full_name"]) == esperado


def test_base_do_sorteio_nao_muda_quando_a_amostra_cresce(candidatos):
    """Mais incluídos no fim da ordem não alteram a base nem o sorteio."""
    maior = pd.concat([
        candidatos,
        pd.DataFrame({"full_name": ["org/novo"], "ordem_avaliacao": [999], "status": ["incluido"]}),
    ])
    a = sortear_repositorios(base_do_sorteio(candidatos, 50), 20, 42)
    b = sortear_repositorios(base_do_sorteio(maior.sample(frac=1, random_state=1), 50), 20, 42)
    assert a["full_name"].tolist() == b["full_name"].tolist()


def test_base_do_sorteio_falha_se_amostra_pequena(candidatos):
    with pytest.raises(ValueError):
        base_do_sorteio(candidatos, 500)


def test_sorteio_e_reproduzivel(candidatos):
    base = base_do_sorteio(candidatos, 50)
    assert sortear_repositorios(base, 20, 42).equals(sortear_repositorios(base, 20, 42))
    assert not sortear_repositorios(base, 20, 42).equals(sortear_repositorios(base, 20, 7))


def test_sortear_releases_so_publicadas_na_janela(releases):
    s = sortear_releases(releases, pd.Series(["org/r0", "org/r1"]), 5, 42)
    assert s.groupby("repo").size().tolist() == [5, 5]
    assert set(s["tag_name"]).isdisjoint({"v1.0.0", "v1.7.0"})  # fora da janela / pré-release


def test_sortear_releases_repo_com_poucas_entra_com_todas(releases):
    s = sortear_releases(releases, pd.Series(["org/r2"]), 10, 42)
    assert len(s) == 6


def test_planilha_tem_links_e_rotulos_vazios_sem_heuristica(releases):
    s = sortear_releases(releases, pd.Series(["org/r0"]), 2, 42)
    p = montar_planilha(s)
    assert p["item"].tolist() == [1, 2]
    assert p["commits_url"].str.contains("/compare/").all()
    assert (p[["tipo_projeto", "entregas_reais", "corretiva"]] == "").all().all()
    assert not any("heur" in c for c in p.columns)


class FakeReleasesClient:
    def __init__(self, releases):
        self.releases = releases

    def paginate(self, url, params=None, transform_item=None):
        return self.releases


def test_releases_da_amostra_liga_anterior_na_serie_publicada():
    def rel(i, tag, data, pre=False, draft=False):
        return {"id": i, "tag_name": tag, "published_at": data, "prerelease": pre,
                "draft": draft, "html_url": f"u/{tag}"}
    client = FakeReleasesClient([
        rel(1, "v1.0", "2025-08-01T00:00:00Z"),
        rel(2, "v1.1-rc", "2025-10-01T00:00:00Z", pre=True),
        rel(3, "v1.1", "2025-11-01T00:00:00Z"),
        rel(4, "v2.0", "2026-09-30T12:00:00Z"),
        rel(5, "rascunho", None, draft=True),
    ])
    df = releases_da_amostra(client, pd.Series(["o/r"]), {"start": "2025-09-30", "end": "2026-09-30"})
    por_tag = df.set_index("tag_name")
    assert "rascunho" not in por_tag.index
    assert por_tag.loc["v1.1", "tag_anterior"] == "v1.0"          # pula a pré-release
    assert por_tag.loc["v1.1-rc", "tipo"] == "prerelease"
    assert por_tag["na_janela"].to_dict() == {"v1.0": False, "v1.1-rc": True, "v1.1": True, "v2.0": False}


# ==========================================
# Concordância
# ==========================================

def _planilha():
    return pd.DataFrame({
        "item": ["1", "2", "3", "4"],
        "full_name": ["a/x", "a/x", "b/y", "b/y"],
        "tag_name": ["v1", "v2", "v1", "v2"],
        "release_url": ["u1", "u2", "u3", "u4"],
    })


def _rotulos(tipo, entregas, corretiva):
    p = _planilha()
    p["tipo_projeto"] = [tipo[0], tipo[0], tipo[1], tipo[1]]
    p["entregas_reais"] = [entregas[0], entregas[0], entregas[1], entregas[1]]
    p["corretiva"] = corretiva
    p["observacoes"] = ""
    return p


def test_normalizar_tira_acento_e_caixa():
    assert normalizar(" Não ") == "nao"
    assert normalizar("Aplicação") == "aplicacao"
    assert normalizar(np.nan) == ""


@pytest.mark.parametrize("k,esperado", [
    (-0.1, "pobre"), (0.0, "leve"), (0.2, "leve"), (0.35, "razoável"),
    (0.5, "moderada"), (0.7, "substancial"), (0.9, "quase perfeita"),
    (float("nan"), "indefinido"),
])
def test_interpretar_landis_koch(k, esperado):
    assert interpretar(k) == esperado


def test_conferir_aponta_vazio_invalido_e_inconsistencia():
    df = _rotulos(["biblioteca", "cli"], ["sim", "nao"], ["sim", "", "talvez", "nao"])
    df.loc[1, "tipo_projeto"] = "outro"
    problemas = conferir(df, _planilha())
    assert any("corretiva vazio" in p for p in problemas)
    assert any("'talvez' inválido" in p for p in problemas)
    assert any("tipo_projeto diferente entre as releases de a/x" in p for p in problemas)


def test_conferir_aponta_item_faltando():
    df = _rotulos(["cli", "cli"], ["sim", "sim"], ["sim", "nao", "sim", "nao"]).iloc[:3]
    assert conferir(df, _planilha()) == ["faltando b/y v2"]


def test_matriz_repositorio_tem_um_item_por_repo():
    r = {n: _rotulos(["cli", "outro"], ["sim", "nao"], ["sim"] * 4) for n in "abc"}
    m = matriz(r, "tipo_projeto")
    assert m.shape == (2, 3)


def test_kappa_fleiss_concordancia_perfeita_e_exemplo_conhecido():
    m = pd.DataFrame({"a": ["sim", "nao", "sim"], "b": ["sim", "nao", "sim"], "c": ["sim", "nao", "sim"]})
    assert kappa_fleiss(m, ["sim", "nao"]) == pytest.approx(1.0)

    # 4 itens, 3 avaliadores: tabela [[3,0],[0,3],[2,1],[1,2]]
    # P_barra = (1 + 1 + 1/3 + 1/3)/4 = 2/3; p = (0.5, 0.5) -> Pe = 0.5; kappa = 1/3
    m = pd.DataFrame({
        "a": ["sim", "nao", "sim", "sim"],
        "b": ["sim", "nao", "sim", "nao"],
        "c": ["sim", "nao", "nao", "nao"],
    })
    assert kappa_fleiss(m, ["sim", "nao"]) == pytest.approx(1 / 3)


def test_resumo_kappa_tem_tres_dimensoes():
    r = {
        "a": _rotulos(["cli", "outro"], ["sim", "nao"], ["sim", "nao", "sim", "nao"]),
        "b": _rotulos(["cli", "outro"], ["sim", "nao"], ["sim", "nao", "nao", "nao"]),
        "c": _rotulos(["cli", "biblioteca"], ["sim", "nao"], ["sim", "nao", "sim", "nao"]),
    }
    k = resumo_kappa(r).set_index("dimensao")
    assert k.loc["entregas_reais", "kappa_fleiss"] == pytest.approx(1.0)
    assert k.loc["corretiva", "itens"] == 4
    assert k.loc["tipo_projeto", "itens"] == 2


def test_divergencias_e_consenso_por_maioria_com_empate_decidido_em_reuniao():
    r = {
        "a": _rotulos(["cli", "outro"], ["sim", "nao"], ["sim", "nao", "sim", "nao"]),
        "b": _rotulos(["cli", "biblioteca"], ["sim", "nao"], ["sim", "nao", "nao", "nao"]),
        "c": _rotulos(["cli", "aplicacao"], ["sim", "nao"], ["sim", "nao", "sim", "nao"]),
    }
    div = divergencias(r)
    assert set(div["dimensao"]) == {"tipo_projeto", "corretiva"}
    assert div.loc[div["dimensao"] == "tipo_projeto", "empate"].tolist() == [True]

    sem_decisao = pd.DataFrame(columns=["dimensao", "full_name", "tag_name", "rotulo", "justificativa"])
    _, pendentes = consenso(r, _planilha(), sem_decisao)
    assert pendentes == ["tipo_projeto b/y"]

    decisoes = pd.DataFrame([{
        "dimensao": "tipo_projeto", "full_name": "b/y", "tag_name": "",
        "rotulo": "Biblioteca", "justificativa": "README descreve um pacote",
    }])
    out, pendentes = consenso(r, _planilha(), decisoes)
    assert pendentes == []
    assert out["tipo_projeto"].tolist() == ["cli", "cli", "biblioteca", "biblioteca"]
    assert out["origem_tipo_projeto"].tolist() == ["unanime", "unanime", "reuniao", "reuniao"]
    assert out["corretiva"].tolist() == ["sim", "nao", "sim", "nao"]
    assert out.loc[2, "origem_corretiva"] == "maioria"


def test_carregar_rotulos_ignora_consenso(tmp_path):
    df = _rotulos(["cli", "outro"], ["Sim", "Não"], ["sim"] * 4)
    df.to_csv(tmp_path / "rotulos_luisa.csv", index=False)
    df.to_csv(tmp_path / "rotulos_consenso.csv", index=False)
    r = carregar_rotulos(str(tmp_path))
    assert list(r) == ["luisa"]
    assert r["luisa"]["entregas_reais"].tolist() == ["sim", "sim", "nao", "nao"]

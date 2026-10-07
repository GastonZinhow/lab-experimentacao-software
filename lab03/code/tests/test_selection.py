from datetime import date

import pandas as pd
import pytest
import requests_mock

from pipeline.cache import ResponseCache
from pipeline.client import GitHubClient, parse_last_page
from pipeline.selection import (
    DESCARTADO,
    INCLUIDO,
    NAO_AVALIADO,
    SearchSlice,
    age_in_days,
    build_funnel,
    count_releases_in_window,
    count_valid_runs,
    initial_slices,
    plan_slices,
)

API = "https://api.github.com"


@pytest.fixture
def client(tmp_path):
    cache = ResponseCache(str(tmp_path / "test_cache.db"))
    return GitHubClient(token="fake_token_test", cache=cache, max_retries=3)


# ==========================================
# Parser do cabeçalho Link
# ==========================================

def test_parse_last_page_le_rel_last():
    link = (
        f'<{API}/repositories/1/contributors?per_page=1&anon=true&page=2>; rel="next", '
        f'<{API}/repositories/1/contributors?per_page=1&anon=true&page=523>; rel="last"'
    )
    assert parse_last_page(link) == 523


def test_parse_last_page_rel_last_antes_do_next():
    link = (
        f'<{API}/x?page=40&per_page=1>; rel="last", '
        f'<{API}/x?page=2&per_page=1>; rel="next"'
    )
    assert parse_last_page(link) == 40


def test_parse_last_page_na_ultima_pagina_nao_tem_last():
    link = f'<{API}/x?page=1>; rel="first", <{API}/x?page=9>; rel="prev"'
    assert parse_last_page(link) is None


@pytest.mark.parametrize("link", [None, ""])
def test_parse_last_page_sem_cabecalho(link):
    assert parse_last_page(link) is None


# ==========================================
# Contagem de contribuidores (count_items)
# ==========================================

def test_count_items_usa_ultima_pagina_e_cache(client):
    url = f"{API}/repos/org/repo/contributors"
    link = f'<{url}?anon=true&per_page=1&page=2>; rel="next", <{url}?anon=true&per_page=1&page=87>; rel="last"'

    with requests_mock.Mocker() as m:
        m.get(url, json=[{"login": "a"}], headers={"Link": link})

        assert client.count_items(url, params={"anon": "true"}) == 87
        assert client.count_items(url, params={"anon": "true"}) == 87
        assert m.call_count == 1
        assert m.request_history[0].qs["per_page"] == ["1"]


def test_count_items_pagina_unica_sem_link(client):
    url = f"{API}/repos/org/solo/contributors"
    with requests_mock.Mocker() as m:
        m.get(url, json=[{"login": "unico"}])
        assert client.count_items(url) == 1


def test_count_items_repositorio_vazio_204(client):
    url = f"{API}/repos/org/vazio/contributors"
    with requests_mock.Mocker() as m:
        m.get(url, status_code=204)
        assert client.count_items(url) == 0
        assert m.call_count == 1


def test_count_items_404_retorna_none(client):
    url = f"{API}/repos/org/sumiu/contributors"
    with requests_mock.Mocker() as m:
        m.get(url, status_code=404, json={"message": "Not Found"})
        assert client.count_items(url) is None


def test_403_que_nao_e_rate_limit_falha_sem_repetir(client):
    url = f"{API}/repos/org/gigante/contributors"
    with requests_mock.Mocker() as m:
        m.get(url, status_code=403, json={"message": "contributor list is too large"},
              headers={"X-RateLimit-Remaining": "4000"})
        with pytest.raises(Exception):
            client.count_items(url)
        assert m.call_count == 1


# ==========================================
# Fatiamento da busca
# ==========================================

def test_initial_slices_sem_sobreposicao():
    queries = [s.query() for s in initial_slices(1001, [2000, 5000])]
    assert queries == ["stars:1001..1999", "stars:2000..4999", "stars:>=5000"]


def test_split_faixa_fechada_ao_meio():
    parts = SearchSlice(1000, 1999).split(date(2026, 10, 7))
    assert [p.query() for p in parts] == ["stars:1000..1499", "stars:1500..1999"]


def test_split_faixa_aberta_dobra_limite():
    parts = SearchSlice(50000).split(date(2026, 10, 7))
    assert [p.query() for p in parts] == ["stars:50000..99999", "stars:>=100000"]


def test_split_estrela_unica_passa_a_fatiar_por_data():
    parts = SearchSlice(1500, 1500).split(date(2026, 10, 7))
    assert parts[0].query().startswith("stars:1500..1500 created:2007-10-01..")
    assert parts[1].query().endswith("..2026-10-07")
    assert parts[0].created_to < parts[1].created_from


class FakeSearchClient:
    """Simula a busca: o total de cada faixa vem da função `total_for`."""

    def __init__(self, total_for):
        self.total_for = total_for
        self.queries = []

    def get_json(self, url, params=None):
        self.queries.append(params["q"])
        return {"total_count": self.total_for(params["q"]), "items": []}, False


def test_plan_slices_subdivide_ate_nenhuma_faixa_passar_do_teto():
    # 1 repositório por estrela entre 1001 e 4000 => [1001..4000] tem 3.000
    def total_for(q):
        lo, hi = q.replace("stars:", "").split("..")
        return int(hi) - int(lo) + 1

    leaves = plan_slices(FakeSearchClient(total_for), [SearchSlice(1001, 4000)], date(2026, 10, 7))
    totals = [first["total_count"] for _, first in leaves]

    assert all(t <= 1000 for t in totals)
    assert sum(totals) == 3000
    # faixas finais contíguas e sem sobreposição
    bounds = [(s.stars_lo, s.stars_hi) for s, _ in leaves]
    assert bounds[0][0] == 1001 and bounds[-1][1] == 4000
    assert all(a[1] + 1 == b[0] for a, b in zip(bounds, bounds[1:]))


def test_plan_slices_mantem_faixa_dentro_do_teto():
    client = FakeSearchClient(lambda q: 800)
    leaves = plan_slices(client, [SearchSlice(1001, 1999)], date(2026, 10, 7))
    assert len(leaves) == 1
    assert client.queries == ["stars:1001..1999"]


# ==========================================
# Critério de inclusão e metadados
# ==========================================

@pytest.fixture
def releases():
    return [
        {"tag_name": "v1.0", "draft": False, "prerelease": False, "published_at": "2025-09-30T10:00:00Z"},
        {"tag_name": "v1.1", "draft": False, "prerelease": False, "published_at": "2026-03-15T10:00:00Z"},
        {"tag_name": "v1.2", "draft": False, "prerelease": False, "published_at": "2026-09-30T23:00:00Z"},
        {"tag_name": "v2.0-rc1", "draft": False, "prerelease": True, "published_at": "2026-05-01T10:00:00Z"},
        {"tag_name": "v2.0", "draft": True, "prerelease": False, "published_at": None},
        {"tag_name": "v0.9", "draft": False, "prerelease": False, "published_at": "2025-09-29T23:59:59Z"},
        {"tag_name": "v3.0", "draft": False, "prerelease": False, "published_at": "2026-10-01T00:00:00Z"},
    ]


def test_count_releases_na_janela(releases):
    # v1.0, v1.1 e v1.2 (limites inclusivos); rc é pré-release; draft,
    # v0.9 (antes) e v3.0 (depois) ficam de fora
    assert count_releases_in_window(releases, "2025-09-30", "2026-09-30") == (3, 1)


def test_count_releases_lista_vazia():
    assert count_releases_in_window([], "2025-09-30", "2026-09-30") == (0, 0)


def test_count_valid_runs_ignora_cancelados():
    df = pd.DataFrame({"status_classificacao": ["sucesso", "falha", "ignorar", "sucesso"]})
    assert count_valid_runs(df) == 3
    assert count_valid_runs(pd.DataFrame()) == 0


def test_idade_em_dias_relativa_ao_fim_da_janela():
    assert age_in_days("2025-09-29T12:00:00Z", "2026-09-30") == 366


# ==========================================
# Funil
# ==========================================

def test_build_funnel_conta_cada_etapa():
    sel = {"min_releases": 5, "min_runs": 50}
    motivos = (
        [("arquivado", DESCARTADO)]
        + [("sem GitHub Actions (total_count = 0)", DESCARTADO)] * 3
        + [("indisponivel na API (HTTP 451)", DESCARTADO)]
        + [("menos de 5 releases na janela", DESCARTADO)] * 4
        + [("menos de 50 workflow runs validos na janela", DESCARTADO)] * 2
        + [("", INCLUIDO)] * 5
        + [("", NAO_AVALIADO)] * 10
    )
    selected = pd.DataFrame(motivos, columns=["motivo_descarte", "status"])

    funnel = build_funnel(selected, sel).set_index("etapa")

    assert funnel.loc["Candidatos da busca (sem duplicatas)", "quantidade"] == 26
    assert funnel.loc["Avaliados em ordem aleatoria (seed)", "quantidade"] == 16
    assert funnel.loc["Nao arquivados", "descartados"] == 1
    assert funnel.loc["Nao fork", "descartados"] == 0
    assert funnel.loc["Disponiveis na API", "descartados"] == 1
    assert funnel.loc["Com GitHub Actions", "quantidade"] == 11
    assert funnel.loc[">= 5 releases na janela", "quantidade"] == 7
    assert funnel.loc[">= 50 workflow runs validos na janela", "quantidade"] == 5
    assert funnel.loc["Amostra final", "quantidade"] == 5

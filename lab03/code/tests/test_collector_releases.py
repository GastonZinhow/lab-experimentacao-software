import pandas as pd
import pytest
import requests_mock

from pipeline.cache import ResponseCache
from pipeline.client import GitHubClient, NotFoundError
from pipeline.collector_releases import (
    CompareUnavailableError,
    collect_repo_releases,
    collect_repo_tags,
    fetch_compare_commits,
    ligar_anteriores,
    separar_releases,
)

REPO = "https://api.github.com/repos/org/proj"
JANELA = ("2025-09-30", "2026-09-30")


def _release(id_, tag, published_at, prerelease=False, draft=False):
    return {
        "id": id_, "tag_name": tag, "name": tag, "draft": draft, "prerelease": prerelease,
        "created_at": published_at, "published_at": published_at,
        "html_url": f"https://github.com/org/proj/releases/tag/{tag}",
    }


def _commit(i, data="2025-11-01T00:00:00Z"):
    return {"sha": f"sha{i:04d}", "commit": {
        "author": {"date": data}, "committer": {"date": data}, "message": f"fix: commit {i}\n\ncorpo",
    }}


@pytest.fixture
def client(tmp_path):
    return GitHubClient(token="fake_token_test", cache=ResponseCache(str(tmp_path / "c.db")), max_retries=2)


@pytest.fixture
def releases_api():
    """Releases como a API devolve (ordem por criação, mais nova primeiro)."""
    return [
        _release(7, "v1.4-draft", None, draft=True),
        _release(6, "v1.3", "2026-01-01T00:00:00Z"),
        _release(5, "v1.2", "2025-12-01T00:00:00Z"),
        _release(4, "v1.1", "2025-11-10T00:00:00Z"),
        _release(3, "v1.1-rc1", "2025-11-01T00:00:00Z", prerelease=True),
        _release(2, "v1.0", "2025-10-10T00:00:00Z"),
        _release(1, "v0.9", "2025-06-01T00:00:00Z"),  # fora da janela, primeira da história
    ]


def _registrar_compare_paginado(m, base, head, total):
    """Simula o compare paginado (100 por página) seguindo o cabeçalho Link."""
    url = f"{REPO}/compare/{base}...{head}"
    paginas = [list(range(i, min(i + 100, total))) for i in range(0, total, 100)] or [[]]
    for n, idx in enumerate(paginas, start=1):
        qs = "per_page=100" if n == 1 else f"per_page=100&page={n}"
        headers = {}
        if n < len(paginas):
            headers["Link"] = f'<{url}?per_page=100&page={n + 1}>; rel="next"'
        m.get(f"{url}?{qs}", complete_qs=True, headers=headers,
              json={"total_commits": total, "commits": [_commit(i) for i in idx]})


@pytest.fixture
def api_mock(releases_api):
    with requests_mock.Mocker() as m:
        m.get(f"{REPO}/releases?per_page=100", complete_qs=True, json=releases_api)
        _registrar_compare_paginado(m, "v0.9", "v1.0", 2)
        _registrar_compare_paginado(m, "v1.0", "v1.1", 260)  # > 250: exige paginação
        m.get(f"{REPO}/compare/v1.1...v1.2?per_page=100", complete_qs=True,
              status_code=404, json={"message": "Not Found"})
        _registrar_compare_paginado(m, "v1.2", "v1.3", 0)
        yield m


# ==========================================
# Funções puras de separação e encadeamento
# ==========================================

def test_separar_releases(releases_api):
    grupos = separar_releases(releases_api)
    assert [r["tag_name"] for r in grupos["draft"]] == ["v1.4-draft"]
    assert [r["tag_name"] for r in grupos["prerelease"]] == ["v1.1-rc1"]
    assert len(grupos["publicada"]) == 5


def test_ligar_anteriores_ordena_por_data_e_marca_primeira(releases_api):
    ligadas = ligar_anteriores(separar_releases(releases_api)["publicada"])
    assert [(r["tag_name"], r["tag_anterior"]) for r in ligadas] == [
        ("v0.9", None), ("v1.0", "v0.9"), ("v1.1", "v1.0"), ("v1.2", "v1.1"), ("v1.3", "v1.2"),
    ]
    assert ligadas[0]["sem_anterior"] is True
    assert not any(r["sem_anterior"] for r in ligadas[1:])


def test_ligar_anteriores_com_prerelease_na_serie(releases_api):
    grupos = separar_releases(releases_api)
    ligadas = {r["tag_name"]: r["tag_anterior"] for r in ligar_anteriores(grupos["publicada"] + grupos["prerelease"])}
    assert ligadas["v1.1-rc1"] == "v1.0"
    assert ligadas["v1.1"] == "v1.1-rc1"


# ==========================================
# Coleta (API simulada)
# ==========================================

def test_compare_com_mais_de_250_commits_traz_todos(client, api_mock):
    commits = fetch_compare_commits(client, "org", "proj", "v1.0", "v1.1")
    assert len(commits) == 260
    assert len({c["sha"] for c in commits}) == 260


def test_compare_404_lanca_not_found(client, api_mock):
    with pytest.raises(NotFoundError):
        fetch_compare_commits(client, "org", "proj", "v1.1", "v1.2")


def test_compare_422_lanca_indisponivel(client):
    with requests_mock.Mocker() as m:
        m.get(
            f"{REPO}/compare/v1.1...v1.2?per_page=100",
            complete_qs=True,
            status_code=422,
            json={
                "message": "Server Error: Sorry, this diff is taking too long to generate.",
                "errors": [{"resource": "Comparison", "field": "diff", "code": "not_available"}],
            },
        )
        with pytest.raises(CompareUnavailableError) as exc_info:
            fetch_compare_commits(client, "org", "proj", "v1.1", "v1.2")

    assert "v1.1...v1.2" in str(exc_info.value)


def test_collect_repo_releases_continua_com_compare_indisponivel(client):
    releases = [
        _release(2, "v1.1", "2025-11-10T00:00:00Z"),
        _release(1, "v1.0", "2025-10-10T00:00:00Z"),
    ]
    with requests_mock.Mocker() as m:
        m.get(f"{REPO}/releases?per_page=100", complete_qs=True, json=releases)
        m.get(
            f"{REPO}/compare/v1.0...v1.1?per_page=100",
            complete_qs=True,
            status_code=422,
            json={"errors": [{"code": "not_available"}]},
        )
        df_rel, df_com, cont = collect_repo_releases(client, "org", "proj", *JANELA)

    release = df_rel.set_index("tag_name").loc["v1.1"]
    assert release["status_compare"] == "indisponivel"
    assert pd.isna(release["n_commits"])
    assert df_com.empty
    assert cont["ignoradas_indisponivel"] == 1
    assert cont["commits_coletados"] == 0


def test_collect_repo_releases(client, api_mock):
    df_rel, df_com, cont = collect_repo_releases(client, "org", "proj", *JANELA)

    por_tag = df_rel.set_index("tag_name")
    assert "v1.4-draft" not in por_tag.index  # drafts não entram em nada
    assert por_tag.loc["v0.9", "status_compare"] == "fora_da_janela"
    assert por_tag.loc["v1.1-rc1", "status_compare"] == "fora_da_serie"
    assert por_tag.loc["v1.0", "status_compare"] == "ok"
    assert por_tag.loc["v1.1", "n_commits"] == 260
    assert por_tag.loc["v1.2", "status_compare"] == "404"
    assert por_tag.loc["v1.3", "n_commits"] == 0

    assert len(df_com) == 2 + 260
    assert set(df_com.columns) >= {"sha", "commit_author_date", "tag_name", "tag_anterior", "mensagem"}
    assert df_com["mensagem"].iloc[0] == "fix: commit 0"

    assert cont["drafts_descartados"] == 1
    assert cont["releases_na_janela"] == 5  # v1.0, rc1, v1.1, v1.2, v1.3
    assert cont["ignoradas_404"] == 1
    assert cont["ignoradas_sem_anterior"] == 0  # v0.9 está fora da janela
    assert cont["sem_commits_novos"] == 1
    assert cont["commits_coletados"] == 262


def test_collect_repo_releases_primeira_da_historia_na_janela(client, releases_api):
    so_na_janela = [r for r in releases_api if r["tag_name"] in ("v1.0", "v1.1")]
    with requests_mock.Mocker() as m:
        m.get(f"{REPO}/releases?per_page=100", complete_qs=True, json=so_na_janela)
        _registrar_compare_paginado(m, "v1.0", "v1.1", 3)
        df_rel, _, cont = collect_repo_releases(client, "org", "proj", *JANELA)

    assert df_rel.set_index("tag_name").loc["v1.0", "status_compare"] == "sem_anterior"
    assert cont["ignoradas_sem_anterior"] == 1


def test_collect_repo_releases_retoma_do_cache(client, api_mock):
    collect_repo_releases(client, "org", "proj", *JANELA)
    chamadas_rede = client.network_requests
    _, df_com, _ = collect_repo_releases(client, "org", "proj", *JANELA)
    # Só o 404 (que não é cacheado) volta para a rede
    assert client.network_requests == chamadas_rede + 1
    assert len(df_com) == 262


def test_collect_repo_tags_busca_data_uma_vez_por_sha(client):
    tags = [
        {"name": "v2.0", "commit": {"sha": "aaa"}},
        {"name": "latest", "commit": {"sha": "aaa"}},
        {"name": "v1.0", "commit": {"sha": "bbb"}},
    ]
    with requests_mock.Mocker() as m:
        m.get(f"{REPO}/tags?per_page=100", complete_qs=True, json=tags)
        m.get(f"{REPO}/commits/aaa", json={"commit": {
            "author": {"date": "2026-01-02T00:00:00Z"}, "committer": {"date": "2026-01-03T00:00:00Z"}}})
        m.get(f"{REPO}/commits/bbb", status_code=404, json={"message": "Not Found"})
        df = collect_repo_tags(client, "org", "proj")
        chamadas_commit = [h for h in m.request_history if "/commits/" in h.url]

    assert len(chamadas_commit) == 2
    por_tag = df.set_index("tag_name")
    assert por_tag.loc["latest", "commit_author_date"] == "2026-01-02T00:00:00Z"
    assert por_tag.loc["v2.0", "commit_committer_date"] == "2026-01-03T00:00:00Z"
    assert pd.isna(por_tag.loc["v1.0", "commit_author_date"])


def test_collect_repo_tags_max_tags(client):
    tags = [{"name": f"v{i}", "commit": {"sha": f"s{i}"}} for i in range(5)]
    with requests_mock.Mocker() as m:
        m.get(requests_mock.ANY, json={"commit": {"author": {"date": "2026-01-01T00:00:00Z"}}})
        m.get(f"{REPO}/tags?per_page=100", complete_qs=True, json=tags)
        df = collect_repo_tags(client, "org", "proj", max_tags=2)
    assert list(df["tag_name"]) == ["v0", "v1"]

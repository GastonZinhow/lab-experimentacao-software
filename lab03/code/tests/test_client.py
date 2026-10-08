import time
import pytest
import requests
import requests_mock
from unittest.mock import patch

from pipeline.client import GitHubClient
from pipeline.cache import ResponseCache


@pytest.fixture
def mock_cache(tmp_path):
    db_file = tmp_path / "test_cache.db"
    return ResponseCache(str(db_file))


@pytest.fixture
def client(mock_cache):
    return GitHubClient(token="fake_token_test", cache=mock_cache, max_retries=3)

def test_client_retry_sucesso_apos_500(client):
    url = "https://api.github.com/test-retry"

    with requests_mock.Mocker() as m:
        m.get(url, [
            {"text": "Internal Server Error", "status_code": 500},
            {"json": {"status": "ok"}, "status_code": 200}
        ])

        with patch("time.sleep") as mock_sleep:
            data, from_cache = client.get_json(url)
            assert data == {"status": "ok"}
            assert from_cache is False
            assert mock_sleep.called


def test_client_retry_apos_queda_de_conexao(client):
    url = "https://api.github.com/test-conexao"

    with requests_mock.Mocker() as m:
        m.get(url, [
            {"exc": requests.exceptions.ConnectionError("Remote end closed connection")},
            {"json": {"status": "ok"}, "status_code": 200},
        ])

        with patch("time.sleep") as mock_sleep:
            data, _ = client.get_json(url)
            assert data == {"status": "ok"}
            assert mock_sleep.called


def test_client_queda_de_conexao_persistente_lanca_erro(client):
    url = "https://api.github.com/test-conexao-fora"

    with requests_mock.Mocker() as m:
        m.get(url, exc=requests.exceptions.ConnectionError("fora do ar"))

        with patch("time.sleep"):
            with pytest.raises(requests.exceptions.ConnectionError):
                client.get_json(url)
        assert m.call_count == 3


def test_client_retry_exaustao_lanca_erro(client):
    url = "https://api.github.com/test-fail"

    with requests_mock.Mocker() as m:
        m.get(url, status_code=503)

        with patch("time.sleep"):
            with pytest.raises(requests.exceptions.HTTPError):
                client.get_json(url)

def test_client_aguarda_quando_rate_limit_esgota(client):
    url = "https://api.github.com/test-ratelimit"
    future_reset_epoch = int(time.time()) + 10

    headers_rate_limited = {
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": str(future_reset_epoch)
    }

    with requests_mock.Mocker() as m:
        m.get(url, json={"data": 123}, headers=headers_rate_limited, status_code=200)

        with patch("time.sleep") as mock_sleep:
            data, _ = client.get_json(url)
            assert data == {"data": 123}
            assert mock_sleep.called
            sleep_time = mock_sleep.call_args[0][0]
            assert sleep_time >= 10


def test_client_paginacao_link_header(client):
    url_p1 = "https://api.github.com/repos/org/repo/actions/runs?page=1"
    url_p2 = "https://api.github.com/repos/org/repo/actions/runs?page=2"

    payload_p1 = {"workflow_runs": [{"id": 101, "name": "CI 1"}]}
    payload_p2 = {"workflow_runs": [{"id": 102, "name": "CI 2"}]}

    with requests_mock.Mocker() as m:
        m.get(url_p1, json=payload_p1, headers={"Link": f'<{url_p2}>; rel="next"'})
        m.get(url_p2, json=payload_p2)

        runs = client.paginate(url_p1)
        assert len(runs) == 2
        assert runs[0]["id"] == 101
        assert runs[1]["id"] == 102

def test_client_persistencia_cache(client):
    url = "https://api.github.com/cached-endpoint"

    with requests_mock.Mocker() as m:
        m.get(url, json={"resultado": "primeira_chamada"}, status_code=200)

        dado1, do_cache1 = client.get_json(url)
        assert dado1 == {"resultado": "primeira_chamada"}
        assert do_cache1 is False
        assert m.call_count == 1

        dado2, do_cache2 = client.get_json(url)
        assert dado2 == {"resultado": "primeira_chamada"}
        assert do_cache2 is True
        assert m.call_count == 1

def test_client_paginate_guarda_itens_enxutos_no_cache(client, mock_cache):
    from pipeline.collector_runs import slim_run

    url = "https://api.github.com/repos/org/repo/actions/runs?page=1"
    run = {"id": 1, "workflow_id": 7, "conclusion": "success", "repository": {"x": "y" * 1000}}

    with requests_mock.Mocker() as m:
        m.get(url, json={"workflow_runs": [run]})
        runs = client.paginate(url, transform_item=slim_run)

    assert runs[0]["id"] == 1 and runs[0]["conclusion"] == "success"
    assert "repository" not in runs[0]
    assert "repository" not in mock_cache.get(url)["items"][0]

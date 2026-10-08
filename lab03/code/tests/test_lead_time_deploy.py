import pytest
from datetime import datetime, timezone

from metrics.datas import parse_data
from metrics.deploy import calcular_deploy_frequency, releases_na_janela, semanas_da_janela
from metrics.lead_time import (
    calcular_lead_time_a,
    calcular_lead_time_b,
    lead_time_release_horas,
    lead_times_commits_horas,
)

DIA = 24.0  # horas


# ==========================================
# Fixtures
# ==========================================

@pytest.fixture
def release_v1_1():
    """Exemplo do enunciado: v1.1 em 15/03 com commits de 02/03, 10/03 e 14/03."""
    return {
        "tag_name": "v1.1",
        "published_at": "2024-03-15T00:00:00Z",
        "commit_dates": ["2024-03-02T00:00:00Z", "2024-03-10T00:00:00Z", "2024-03-14T00:00:00Z"],
        "sem_anterior": False,
    }


@pytest.fixture
def primeira_release():
    """Primeira release da história: não tem anterior e deve ser ignorada."""
    return {
        "tag_name": "v1.0",
        "published_at": "2024-03-01T00:00:00Z",
        "commit_dates": ["2023-01-01T00:00:00Z"],
        "sem_anterior": True,
    }


@pytest.fixture
def release_v1_2():
    """Release com um único commit, 2 dias antes da publicação."""
    return {
        "tag_name": "v1.2",
        "published_at": "2024-04-03T00:00:00Z",
        "commit_dates": ["2024-04-01T00:00:00Z"],
        "sem_anterior": False,
    }


@pytest.fixture
def releases_janela():
    return [
        {"published_at": "2025-09-30T00:00:00Z", "draft": False, "prerelease": False},  # início: entra
        {"published_at": "2026-01-10T12:00:00Z", "draft": False, "prerelease": False},
        {"published_at": "2026-02-01T12:00:00Z", "draft": False, "prerelease": True},   # pré-release
        {"published_at": None, "draft": True, "prerelease": False},                     # draft
        {"published_at": "2025-09-29T23:59:59Z", "draft": False, "prerelease": False},  # antes da janela
        {"published_at": "2026-09-30T00:00:00Z", "draft": False, "prerelease": False},  # fim é exclusivo
    ]


# ==========================================
# Lead time (RQ 02)
# ==========================================

def test_lead_time_exemplo_enunciado_variante_a(release_v1_1):
    lt = lead_time_release_horas(release_v1_1["published_at"], release_v1_1["commit_dates"])
    assert lt == pytest.approx(13 * DIA)
    assert calcular_lead_time_a([release_v1_1]) == pytest.approx(13 * DIA)


def test_lead_time_exemplo_enunciado_variante_b(release_v1_1):
    valores = lead_times_commits_horas(release_v1_1["published_at"], release_v1_1["commit_dates"])
    assert valores == pytest.approx([13 * DIA, 5 * DIA, 1 * DIA])
    assert calcular_lead_time_b([release_v1_1]) == pytest.approx(5 * DIA)


def test_lead_time_varias_releases_mediana(release_v1_1, release_v1_2, primeira_release):
    releases = [primeira_release, release_v1_1, release_v1_2]
    # (a): mediana de [13 d, 2 d] = 7,5 d (primeira release ignorada)
    assert calcular_lead_time_a(releases) == pytest.approx(7.5 * DIA)
    # (b): mediana de [13, 5, 1, 2] d = 3,5 d
    assert calcular_lead_time_b(releases) == pytest.approx(3.5 * DIA)


def test_lead_time_commit_antigo_esquecido_explode_a_mas_nao_b(release_v1_1):
    """Pista do enunciado: um commit antigo infla (a) e quase não afeta (b)."""
    release = {**release_v1_1, "commit_dates": release_v1_1["commit_dates"] + ["2023-03-15T00:00:00Z"]}
    assert calcular_lead_time_a([release]) == pytest.approx(366 * DIA)
    assert calcular_lead_time_b([release]) == pytest.approx(9 * DIA)


def test_lead_time_release_sem_commits_novos(release_v1_1):
    vazia = {"published_at": "2024-03-20T00:00:00Z", "commit_dates": [], "sem_anterior": False}
    assert lead_time_release_horas(vazia["published_at"], []) is None
    assert calcular_lead_time_a([vazia]) is None
    assert calcular_lead_time_b([vazia]) is None
    # Junto de outra release, a vazia não altera o resultado
    assert calcular_lead_time_a([vazia, release_v1_1]) == pytest.approx(13 * DIA)
    assert calcular_lead_time_b([vazia, release_v1_1]) == pytest.approx(5 * DIA)


def test_lead_time_repositorio_com_uma_unica_release(primeira_release):
    assert calcular_lead_time_a([primeira_release]) is None
    assert calcular_lead_time_b([primeira_release]) is None


def test_lead_time_release_com_compare_404_e_ignorada(release_v1_1):
    erro_404 = {"published_at": "2024-03-20T00:00:00Z", "commit_dates": None, "sem_anterior": False}
    assert calcular_lead_time_a([erro_404, release_v1_1]) == pytest.approx(13 * DIA)


def test_lead_time_lista_vazia():
    assert calcular_lead_time_a([]) is None
    assert calcular_lead_time_b([]) is None


# ==========================================
# Deployment frequency (RQ 01)
# ==========================================

def test_semanas_da_janela_de_12_meses():
    assert semanas_da_janela("2025-09-30", "2026-09-30") == pytest.approx(365 / 7)
    assert round(semanas_da_janela("2025-09-30", "2026-09-30"), 1) == 52.1


def test_releases_na_janela_filtra_draft_prerelease_e_limites(releases_janela):
    assert len(releases_na_janela(releases_janela, "2025-09-30", "2026-09-30")) == 2
    assert len(releases_na_janela(releases_janela, "2025-09-30", "2026-09-30", incluir_prerelease=True)) == 3


def test_deploy_frequency(releases_janela):
    df = calcular_deploy_frequency(releases_janela, "2025-09-30", "2026-09-30")
    assert df == pytest.approx(2 / (365 / 7))


def test_deploy_frequency_semana_exata():
    releases = [{"published_at": f"2024-01-0{d}T10:00:00Z", "draft": False, "prerelease": False} for d in range(1, 8)]
    assert calcular_deploy_frequency(releases, "2024-01-01", "2024-01-08") == pytest.approx(7.0)


def test_deploy_frequency_sem_releases():
    assert calcular_deploy_frequency([], "2025-09-30", "2026-09-30") == 0.0


def test_deploy_frequency_janela_invalida():
    with pytest.raises(ValueError):
        calcular_deploy_frequency([], "2026-09-30", "2025-09-30")


def test_parse_data_aceita_datetime_ingenuo_e_ciente():
    ingenuo = datetime(2024, 1, 1)
    ciente = datetime(2024, 1, 1, tzinfo=timezone.utc)
    assert parse_data(ingenuo) == ciente
    assert parse_data(ciente) == ciente
    assert parse_data("2024-01-01") == ciente

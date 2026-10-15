import pandas as pd
import pytest

from validacao.gerar_amostra_ouro import PLACEHOLDER, generate_gold_sample


def _inputs(n_repos=65, releases_per_repo=6):
    metadata = pd.DataFrame(
        {"full_name": [f"org/repo-{i:03d}" for i in range(n_repos)]}
    )
    releases = []
    for repo in metadata["full_name"]:
        for index in range(releases_per_repo):
            releases.append(
                {
                    "repo": repo,
                    "release_id": f"{repo}-{index}",
                    "tag_name": f"v1.0.{index}",
                    "tag_anterior": f"v1.0.{index - 1}" if index else pd.NA,
                    "published_at": f"2026-0{index + 1}-01T00:00:00Z",
                    "tipo": "publicada",
                    "draft": False,
                    "prerelease": False,
                    "na_janela": True,
                    "html_url": f"https://github.com/{repo}/releases/tag/v1.0.{index}",
                }
            )
    return metadata, pd.DataFrame(releases)


def test_amostra_padrao_tem_60_repos_e_300_releases():
    metadata, releases = _inputs()
    sample = generate_gold_sample(metadata, releases)

    assert len(sample) == 300
    assert sample["repo"].nunique() == 60
    assert sample.groupby("repo").size().eq(5).all()
    assert sample[[
        "tipo_projeto",
        "releases_representam_entregas",
        "release_corretiva",
        "observacoes",
    ]].eq(PLACEHOLDER).all().all()
    assert not any("heuristica" in column for column in sample.columns)


def test_sorteio_nao_depende_da_ordem_das_entradas():
    metadata, releases = _inputs()
    expected = generate_gold_sample(metadata, releases, seed=123)
    shuffled = generate_gold_sample(
        metadata.sample(frac=1, random_state=9),
        releases.sample(frac=1, random_state=17),
        seed=123,
    )

    pd.testing.assert_frame_equal(expected, shuffled)


def test_falha_se_repo_sorteado_nao_tem_cinco_releases():
    metadata, releases = _inputs(n_repos=1, releases_per_repo=4)

    with pytest.raises(ValueError, match="menos de 5 releases elegíveis"):
        generate_gold_sample(metadata, releases, n_repos=1, releases_per_repo=5)

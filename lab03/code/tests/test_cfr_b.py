import pandas as pd
import pytest

from metrics.cfr import avaliar_cfr_b, calcular_cfr_b, cfr_b_por_repositorio, marcar_corretivas
from metrics.corretiva import (
    VERSAO_ATUAL,
    VERSOES,
    contar_sinais,
    e_corretiva,
    e_corretiva_v1,
    e_corretiva_v2,
    e_corretiva_v3,
    linhas_significativas,
    pacote_da_tag,
    parse_versao,
    tem_commit_corretivo,
    tipo_incremento,
)

FIM = "2026-09-30"


# ==========================================
# Heurística de release corretiva
# ==========================================

@pytest.mark.parametrize("tag, esperado", [
    ("v2.3.1", (2, 3, 1)),
    ("2.3.1", (2, 3, 1)),
    ("v3.0", (3, 0, 0)),
    ("rig-surrealdb-v0.1.19", (0, 1, 19)),
    ("@tanstack/vue-virtual@3.13.14", (3, 13, 14)),
    ("dulwich-0.24.10", (0, 24, 10)),
    ("v4.20.0-hotfix1", (4, 20, 0)),
    ("7.3.0.CR1", (7, 3, 0)),
    ("v1.07.4", (1, 7, 4)),
])
def test_parse_versao_semver(tag, esperado):
    assert parse_versao(tag) == esperado


@pytest.mark.parametrize("tag", ["unlshd-083", "october-2025", "nightly", "gh-attach-assets", "", None])
def test_parse_versao_fora_do_semver(tag):
    assert parse_versao(tag) is None


@pytest.mark.parametrize("anterior, atual, esperado", [
    ("v2.3.0", "v2.3.1", "patch"),
    ("v2.4.0", "v2.5.0", "minor"),
    ("v2.5.3", "v3.0.0", "major"),
    ("v2.3.1", "v2.3.0", None),       # versão menor que a anterior (série paralela)
    ("v2.3.1", "v2.3.1", None),       # mesma versão (outro pacote do monorepo)
    ("unlshd-082", "unlshd-083", None),
    (None, "v1.0.0", None),           # primeira release
])
def test_tipo_incremento(anterior, atual, esperado):
    assert tipo_incremento(anterior, atual) == esperado


@pytest.mark.parametrize("mensagem", [
    "fix: crash on startup",
    "Fixes #123",
    "Revert \"feat: new parser\"",
    "hotfix for 2.3.0",
    "fix(api): null check",
])
def test_commit_corretivo(mensagem):
    assert tem_commit_corretivo([mensagem])


@pytest.mark.parametrize("mensagem", ["feat: add prefix option", "docs: update README", "", None])
def test_commit_nao_corretivo(mensagem):
    assert not tem_commit_corretivo([mensagem])


def test_v1_so_patch_e_corretiva():
    assert e_corretiva_v1("v2.3.1", "v2.3.0", ["feat: nova opção"])


def test_v1_minor_sem_fix_nao_e_corretiva():
    assert not e_corretiva_v1("v2.5.0", "v2.4.0", ["feat: nova opção"])


def test_v1_minor_com_fix_e_corretiva():
    assert e_corretiva_v1("v2.5.0", "v2.4.0", ["feat: nova opção", "fix: typo"])


def test_v1_fora_do_semver_nao_quebra():
    assert not e_corretiva_v1("october-2025", "september-2025", ["build(deps): bump rack"])
    assert e_corretiva_v1("unlshd-088", "unlshd-087", ["hotfix: crash"])


def test_e_corretiva_usa_versao_atual():
    assert VERSAO_ATUAL in VERSOES
    args = ("v2.3.1", "v2.3.0", ["fix: crash"], "Bug fixes")
    assert e_corretiva(*args) == VERSOES[VERSAO_ATUAL](*args)


@pytest.mark.parametrize("tag, pacote", [
    ("v1.2.3", ""),
    ("1.2.3", ""),
    ("rig-core-v0.1.2", "rig-core"),
    ("@tanstack/vue-virtual@3.13.14", "@tanstack/vue-virtual"),
    ("dulwich-0.24.2", "dulwich"),
    ("unlshd-083", None),
])
def test_pacote_da_tag(tag, pacote):
    assert pacote_da_tag(tag) == pacote


def test_tipo_incremento_mesmo_pacote():
    # sem a checagem, tags de pacotes diferentes viram "major"/"patch" por acaso
    assert tipo_incremento("rig-sqlite-v0.1.24", "rig-surrealdb-v0.1.19") is None
    assert tipo_incremento("fumadocs-openapi@9.7.1", "create-fumadocs-app@16.0.7") == "major"
    assert tipo_incremento("fumadocs-openapi@9.7.1", "create-fumadocs-app@16.0.7", mesmo_pacote=True) is None
    assert tipo_incremento("pkg@1.2.3", "pkg@1.2.4", mesmo_pacote=True) == "patch"


def test_linhas_significativas_descarta_ruido_e_marcadores():
    textos = [
        "## What's Changed\n- fix: crash on load by @x in #1\n* Bump lodash from 1 to 2\n\n"
        "Full Changelog: v1...v2",
        "chore(deps): update go",
        "Merge pull request #3 from a/b",
        None,
    ]
    assert linhas_significativas(textos) == ["fix: crash on load by @x in #1"]


def test_contar_sinais():
    assert contar_sinais(["fix: crash", "feat: new option", "add support for X", "docs tweak"]) == (1, 2)


# ------------------------------------------
# v2 (só commits) e v3 (commits + notas)
# ------------------------------------------

def test_v2_patch_com_correcao_e_corretiva():
    assert e_corretiva_v2("v2.3.1", "v2.3.0", ["fix: crash", "chore: release 2.3.1"])


def test_v2_patch_sem_correcao_nao_e_corretiva():
    assert not e_corretiva_v2("v2.3.1", "v2.3.0", ["chore(deps): bump x"])


def test_v2_minor_nao_e_corretiva():
    assert not e_corretiva_v2("v2.5.0", "v2.4.0", ["fix: crash"])


def test_v2_muitos_commits_nao_e_corretiva():
    mensagens = [f"fix: bug {i}" for i in range(6)]
    assert not e_corretiva_v2("v2.3.1", "v2.3.0", mensagens)


def test_v2_funcionalidades_demais_nao_e_corretiva():
    assert not e_corretiva_v2("v2.3.1", "v2.3.0", ["fix: crash", "feat: a", "feat: b"])


def test_v2_fora_do_semver_usa_commits():
    assert e_corretiva_v2("unlshd-088", "unlshd-087", ["hotfix: crash"])
    assert not e_corretiva_v2("october-2025", "september-2025", ["build(deps): bump rack"])


def test_v2_ignora_notas():
    assert not e_corretiva_v2("v2.3.1", "v2.3.0", [], "Fixed a crash")


def test_v3_usa_notas():
    notas = "## Bug Fixes\n- Fixed a crash when opening files\n- Fix memory leak"
    assert e_corretiva_v3("v2.3.1", "v2.3.0", [], notas)
    assert not e_corretiva_v2("v2.3.1", "v2.3.0", [], notas)


def test_v3_aceita_minor_mas_nao_major():
    assert e_corretiva_v3("v2.41.0", "v2.40.0", ["Protect startup."], "Fixed: protect task from interrupts.")
    assert not e_corretiva_v3("v3.0.0", "v2.40.0", ["fix: crash"], "Fixed crash")


def test_v3_notas_com_muitas_funcionalidades_nao_e_corretiva():
    notas = "Fixed a crash\nNew dashboard\nAdded export\nSupport for X"
    assert not e_corretiva_v3("v2.3.1", "v2.3.0", ["fix: crash"], notas)


# ==========================================
# CFR (b)
# ==========================================

def _rel(tag, anterior, data, mensagens=()):
    return {
        "tag_name": tag,
        "published_at": data,
        "corretiva": e_corretiva(tag, anterior, list(mensagens)),
    }


def test_cfr_b_patch_seguinte_marca_falha():
    """v2.3.0 → v2.3.1 dois dias depois: a v2.3.0 falhou."""
    releases = [
        _rel("v2.3.0", "v2.2.0", "2026-03-01T10:00:00Z", ["feat: x"]),
        _rel("v2.3.1", "v2.3.0", "2026-03-03T10:00:00Z", ["fix: crash"]),
    ]
    res = avaliar_cfr_b(releases, FIM)
    assert res == {"cfr": 0.5, "falhas": 1, "avaliadas": 2, "censuradas": 0}


def test_cfr_b_minor_seguinte_nao_marca_falha():
    """v2.4.0 → v2.5.0 só com features: a v2.4.0 não falhou."""
    releases = [
        _rel("v2.4.0", "v2.3.0", "2026-03-01T10:00:00Z", ["feat: x"]),
        _rel("v2.5.0", "v2.4.0", "2026-03-03T10:00:00Z", ["feat: y"]),
    ]
    assert calcular_cfr_b(releases, FIM) == 0.0


def test_cfr_b_corretiva_depois_do_prazo_nao_marca_falha():
    releases = [
        _rel("v2.3.0", "v2.2.0", "2026-03-01T10:00:00Z"),
        _rel("v2.3.1", "v2.3.0", "2026-03-08T10:00:01Z", ["fix: crash"]),
    ]
    assert avaliar_cfr_b(releases, FIM)["falhas"] == 0


def test_cfr_b_corretiva_exatamente_em_7_dias_marca_falha():
    releases = [
        _rel("v2.3.0", "v2.2.0", "2026-03-01T10:00:00Z"),
        _rel("v2.3.1", "v2.3.0", "2026-03-08T10:00:00Z", ["fix: crash"]),
    ]
    assert avaliar_cfr_b(releases, FIM)["falhas"] == 1


def test_cfr_b_corretiva_nao_imediatamente_seguinte():
    """Uma release no meio não impede que a corretiva marque a primeira."""
    releases = [
        _rel("v2.3.0", "v2.2.0", "2026-03-01T10:00:00Z"),
        _rel("v2.4.0", "v2.3.0", "2026-03-02T10:00:00Z"),
        _rel("v2.4.1", "v2.4.0", "2026-03-04T10:00:00Z", ["fix: crash"]),
    ]
    res = avaliar_cfr_b(releases, FIM)
    assert res["falhas"] == 2 and res["avaliadas"] == 3


def test_cfr_b_release_censurada():
    """Releases nos últimos 7 dias da janela saem do denominador."""
    releases = [
        _rel("v2.3.0", "v2.2.0", "2026-09-01T10:00:00Z"),
        _rel("v2.4.0", "v2.3.0", "2026-09-25T10:00:00Z"),   # censurada
        _rel("v2.4.1", "v2.4.0", "2026-09-27T10:00:00Z", ["fix: crash"]),  # censurada
    ]
    res = avaliar_cfr_b(releases, FIM)
    assert res == {"cfr": 0.0, "falhas": 0, "avaliadas": 1, "censuradas": 2}


def test_cfr_b_censurada_ainda_marca_anterior():
    releases = [
        _rel("v2.4.0", "v2.3.0", "2026-09-20T10:00:00Z"),
        _rel("v2.4.1", "v2.4.0", "2026-09-25T10:00:00Z", ["fix: crash"]),  # censurada
    ]
    res = avaliar_cfr_b(releases, FIM)
    assert res == {"cfr": 1.0, "falhas": 1, "avaliadas": 1, "censuradas": 1}


def test_cfr_b_versao_fora_do_semver():
    releases = [
        _rel("october-2025", "september-2025", "2025-10-01T00:00:00Z", ["build(deps): bump"]),
        _rel("november-2025", "october-2025", "2025-10-05T00:00:00Z", ["build(deps): bump"]),
    ]
    assert calcular_cfr_b(releases, FIM) == 0.0


def test_cfr_b_todas_censuradas_ou_vazia():
    assert calcular_cfr_b([], FIM) is None
    assert calcular_cfr_b([_rel("v1.0.1", "v1.0.0", "2026-09-29T00:00:00Z")], FIM) is None


def test_cfr_b_ordena_por_data():
    releases = [
        _rel("v2.3.1", "v2.3.0", "2026-03-03T10:00:00Z", ["fix: crash"]),
        _rel("v2.3.0", "v2.2.0", "2026-03-01T10:00:00Z"),
    ]
    assert avaliar_cfr_b(releases, FIM)["falhas"] == 1


# ==========================================
# CFR (b) a partir das saídas do pipeline
# ==========================================

def _df_releases():
    return pd.DataFrame([
        {"repo": "o/a", "tag_name": "v1.0.0", "tag_anterior": None, "published_at": "2026-03-01T00:00:00Z",
         "na_janela": True, "prerelease": False},
        {"repo": "o/a", "tag_name": "v1.0.1", "tag_anterior": "v1.0.0", "published_at": "2026-03-02T00:00:00Z",
         "na_janela": True, "prerelease": False, "body": "### Bug Fixes\n- fix crash on startup"},
        {"repo": "o/a", "tag_name": "v1.1.0-rc.1", "tag_anterior": "v1.0.1", "published_at": "2026-03-03T00:00:00Z",
         "na_janela": True, "prerelease": True},
        {"repo": "o/a", "tag_name": "v0.9.0", "tag_anterior": None, "published_at": "2025-01-01T00:00:00Z",
         "na_janela": False, "prerelease": False},
        {"repo": "o/b", "tag_name": "v2.0.0", "tag_anterior": "v1.9.0", "published_at": "2026-04-01T00:00:00Z",
         "na_janela": True, "prerelease": False},
        {"repo": "o/b", "tag_name": "v2.1.0", "tag_anterior": "v2.0.0", "published_at": "2026-04-03T00:00:00Z",
         "na_janela": True, "prerelease": False},
    ])


def _df_commits():
    return pd.DataFrame([
        {"repo": "o/b", "tag_name": "v2.1.0", "mensagem": "feat: x"},
        {"repo": "o/b", "tag_name": "v2.1.0", "mensagem": "Revert \"feat: y\""},
    ])


def test_marcar_corretivas_v1():
    marcadas = marcar_corretivas(_df_releases(), _df_commits(), e_corretiva_v1)
    por_tag = dict(zip(marcadas["tag_name"], marcadas["corretiva"]))
    assert por_tag["v1.0.1"] is True        # só patch
    assert por_tag["v1.0.0"] is False       # sem anterior
    assert por_tag["v2.1.0"] is True        # commit com revert
    assert por_tag["v2.0.0"] is False


def test_marcar_corretivas_versao_atual_usa_notas():
    marcadas = marcar_corretivas(_df_releases(), _df_commits())
    por_tag = dict(zip(marcadas["tag_name"], marcadas["corretiva"]))
    assert por_tag["v1.0.1"] is True        # patch com "Bug fixes" nas notas
    assert por_tag["v2.1.0"] is False       # minor com mais funcionalidade que correção


def test_marcar_corretivas_sem_commits():
    marcadas = marcar_corretivas(_df_releases(), pd.DataFrame())
    assert not marcadas.loc[marcadas["tag_name"] == "v2.1.0", "corretiva"].iloc[0]


def test_cfr_b_por_repositorio():
    df = cfr_b_por_repositorio(_df_releases(), _df_commits(), FIM, e_corretiva_v1)
    linhas = df.set_index("repo").to_dict("index")
    # o/a: pré-release e release fora da janela não entram; v1.0.0 falhou (v1.0.1 é patch)
    assert linhas["o/a"]["releases"] == 2
    assert linhas["o/a"]["cfr_b"] == 0.5
    assert linhas["o/b"]["falhas"] == 1 and linhas["o/b"]["corretivas"] == 1


def test_cfr_b_por_repositorio_csv_como_texto():
    """releases.csv lido sem conversão traz booleanos como texto."""
    df = _df_releases().astype({"na_janela": str, "prerelease": str})
    assert len(cfr_b_por_repositorio(df, _df_commits(), FIM)) == 2

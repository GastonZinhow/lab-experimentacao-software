"""Gera a planilha cega usada na rotulagem independente da amostra-ouro.

Cada linha representa uma release. Com os parâmetros padrão, o arquivo tem
60 repositórios x 5 releases = 300 linhas. Os campos de rótulo começam com
``PREENCHER`` e nenhuma saída da heurística automática é incluída.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Iterable, Sequence
from urllib.parse import quote

import pandas as pd


VALIDACAO_DIR = Path(__file__).resolve().parent
CODE_DIR = VALIDACAO_DIR.parent
DEFAULT_METADATA = CODE_DIR / "data" / "metadados.csv"
DEFAULT_RELEASES = CODE_DIR / "data" / "releases.csv"
DEFAULT_OUTPUT = VALIDACAO_DIR / "amostra_sorteada.csv"

PLACEHOLDER = "PREENCHER"
METADATA_COLUMNS = {"full_name"}
RELEASE_COLUMNS = {
    "repo",
    "release_id",
    "tag_name",
    "tag_anterior",
    "published_at",
    "tipo",
    "draft",
    "prerelease",
    "na_janela",
    "html_url",
}


def _require_columns(df: pd.DataFrame, required: Iterable[str], source: Path) -> None:
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f"{source} não possui as colunas obrigatórias: {', '.join(missing)}")


def _boolean_series(series: pd.Series, column: str) -> pd.Series:
    """Converte booleanos lidos do CSV sem aceitar valores ambíguos."""
    normalized = series.astype("string").str.strip().str.lower()
    mapping = {
        "true": True,
        "false": False,
        "1": True,
        "0": False,
        "sim": True,
        "nao": False,
        "não": False,
    }
    invalid = sorted(normalized.dropna()[~normalized.dropna().isin(mapping)].unique())
    if invalid:
        raise ValueError(f"Valores booleanos inválidos em {column}: {invalid}")
    return normalized.map(mapping).fillna(False).astype(bool)


def _seeded_digest(seed: int, namespace: str, key: str) -> str:
    payload = f"{seed}\0{namespace}\0{key}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def stable_sample(
    df: pd.DataFrame,
    n: int,
    key_columns: Sequence[str],
    seed: int,
    namespace: str,
) -> pd.DataFrame:
    """Amostra determinística, independente da ordem das linhas de entrada."""
    if n <= 0:
        raise ValueError("O tamanho da amostra deve ser positivo.")
    if len(df) < n:
        raise ValueError(f"A população possui {len(df)} linhas, mas foram solicitadas {n}.")

    keys = df.loc[:, key_columns].astype("string").agg("\x1f".join, axis=1)
    if keys.duplicated().any():
        duplicates = sorted(keys[keys.duplicated(keep=False)].unique())[:5]
        raise ValueError(f"Chaves duplicadas impedem o sorteio estável: {duplicates}")

    ranked = df.copy()
    ranked["_sample_key"] = keys
    ranked["_sample_score"] = keys.map(
        lambda key: _seeded_digest(seed, namespace, key)
    )
    return (
        ranked.sort_values(["_sample_score", "_sample_key"], kind="stable")
        .head(n)
        .drop(columns=["_sample_key", "_sample_score"])
        .reset_index(drop=True)
    )


def _release_url(repo: str, tag: str, html_url: object) -> str:
    if pd.notna(html_url) and str(html_url).strip():
        return str(html_url).strip()
    return f"https://github.com/{repo}/releases/tag/{quote(tag, safe='')}"


def _commits_url(repo: str, previous_tag: object, tag: str) -> str:
    head = quote(tag, safe="")
    if pd.notna(previous_tag) and str(previous_tag).strip():
        base = quote(str(previous_tag).strip(), safe="")
        return f"https://github.com/{repo}/compare/{base}...{head}"
    return f"https://github.com/{repo}/commits/{head}"


def generate_gold_sample(
    metadata: pd.DataFrame,
    releases: pd.DataFrame,
    *,
    seed: int = 42,
    n_repos: int = 60,
    releases_per_repo: int = 5,
) -> pd.DataFrame:
    """Seleciona repositórios e releases e devolve a planilha cega."""
    _require_columns(metadata, METADATA_COLUMNS, Path("metadados.csv"))
    _require_columns(releases, RELEASE_COLUMNS, Path("releases.csv"))

    metadata = metadata.copy()
    metadata["full_name"] = metadata["full_name"].astype("string").str.strip()
    if metadata["full_name"].isna().any() or (metadata["full_name"] == "").any():
        raise ValueError("metadados.csv contém full_name vazio.")
    if metadata["full_name"].duplicated().any():
        duplicated = metadata.loc[metadata["full_name"].duplicated(), "full_name"].tolist()
        raise ValueError(f"Repositórios duplicados em metadados.csv: {duplicated[:5]}")

    selected_repos = stable_sample(
        metadata,
        n_repos,
        ["full_name"],
        seed,
        "repositorios",
    )
    selected_repos = selected_repos.assign(ordem_repo=range(1, n_repos + 1))

    releases = releases.copy()
    releases["repo"] = releases["repo"].astype("string").str.strip()
    releases["tag_name"] = releases["tag_name"].astype("string").str.strip()
    releases["release_id"] = releases["release_id"].astype("string").str.strip()
    releases["_draft"] = _boolean_series(releases["draft"], "draft")
    releases["_prerelease"] = _boolean_series(releases["prerelease"], "prerelease")
    releases["_na_janela"] = _boolean_series(releases["na_janela"], "na_janela")

    eligible = releases[
        releases["repo"].isin(selected_repos["full_name"])
        & releases["tipo"].astype("string").str.strip().eq("publicada")
        & ~releases["_draft"]
        & ~releases["_prerelease"]
        & releases["_na_janela"]
        & releases["published_at"].notna()
        & releases["release_id"].notna()
        & releases["tag_name"].notna()
        & releases["tag_name"].ne("")
    ].copy()

    duplicated = eligible.duplicated(["repo", "release_id"], keep=False)
    if duplicated.any():
        examples = eligible.loc[duplicated, ["repo", "release_id"]].head(5).to_dict("records")
        raise ValueError(f"Releases duplicadas por repo/release_id: {examples}")

    rows = []
    insufficient = []
    for repo_row in selected_repos.itertuples(index=False):
        repo = repo_row.full_name
        pool = eligible[eligible["repo"] == repo].copy()
        if len(pool) < releases_per_repo:
            insufficient.append((repo, len(pool)))
            continue

        chosen = stable_sample(
            pool,
            releases_per_repo,
            ["repo", "release_id"],
            seed,
            f"releases:{repo}",
        )
        chosen["_published"] = pd.to_datetime(chosen["published_at"], utc=True, errors="coerce")
        if chosen["_published"].isna().any():
            raise ValueError(f"{repo} possui published_at inválido entre as releases sorteadas.")
        chosen = chosen.sort_values(["_published", "release_id"], ascending=[False, True])

        for release_order, release in enumerate(chosen.itertuples(index=False), start=1):
            tag = str(release.tag_name)
            rows.append(
                {
                    "seed_sorteio": seed,
                    "ordem_repo": repo_row.ordem_repo,
                    "ordem_release": release_order,
                    "repo": repo,
                    "repo_url": f"https://github.com/{repo}",
                    "release_id": release.release_id,
                    "release_tag": tag,
                    "release_published_at": release.published_at,
                    "release_url": _release_url(repo, tag, release.html_url),
                    "commits_url": _commits_url(repo, release.tag_anterior, tag),
                    "tipo_projeto": PLACEHOLDER,
                    "releases_representam_entregas": PLACEHOLDER,
                    "release_corretiva": PLACEHOLDER,
                    "observacoes": PLACEHOLDER,
                }
            )

    if insufficient:
        details = ", ".join(f"{repo} ({count})" for repo, count in insufficient)
        raise ValueError(
            "Repositórios sorteados com menos de "
            f"{releases_per_repo} releases elegíveis: {details}. "
            "Corrija a coleta/janela antes de gerar a amostra; não substitua "
            "esses repositórios silenciosamente."
        )

    result = pd.DataFrame(rows)
    expected_rows = n_repos * releases_per_repo
    counts = result.groupby("repo", sort=False).size()
    if len(result) != expected_rows or result["repo"].nunique() != n_repos:
        raise AssertionError("A amostra gerada não possui as dimensões esperadas.")
    if not counts.eq(releases_per_repo).all():
        raise AssertionError("Nem todos os repositórios possuem a quantidade esperada de releases.")
    if result.isna().any().any() or result.astype("string").apply(lambda c: c.str.strip().eq("")).any().any():
        raise AssertionError("A amostra gerada contém células vazias.")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera a amostra-ouro cega (60 repositórios x 5 releases)."
    )
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--releases", type=Path, default=DEFAULT_RELEASES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n-repos", type=int, default=60)
    parser.add_argument("--releases-por-repo", type=int, default=5)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Permite sobrescrever o arquivo de saída existente.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.output.exists() and not args.force:
        raise FileExistsError(
            f"{args.output} já existe. Use --force somente se o grupo decidiu refazer o sorteio."
        )

    metadata = pd.read_csv(args.metadata, dtype={"full_name": "string"})
    releases = pd.read_csv(
        args.releases,
        dtype={"repo": "string", "release_id": "string", "tag_name": "string"},
    )
    sample = generate_gold_sample(
        metadata,
        releases,
        seed=args.seed,
        n_repos=args.n_repos,
        releases_per_repo=args.releases_por_repo,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    sample.to_csv(temporary, index=False, encoding="utf-8")
    temporary.replace(args.output)

    print(f"Amostra salva em: {args.output}")
    print(f"Repositórios: {sample['repo'].nunique()}")
    print(f"Releases: {len(sample)}")
    print(f"Seed: {args.seed}")
    print("O arquivo não contém saídas da heurística; substitua PREENCHER durante a rotulagem.")


if __name__ == "__main__":
    main()

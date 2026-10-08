# Pipeline DORA Metrics Mining (Lab03S01)

### Pré-requisitos
```bash
pip install -r requirements.txt
export GITHUB_TOKEN="seu_token_aqui"
```

### Execução
```bash
python -m pipeline --config config.yaml
```

### Saídas de releases, commits e tags (issue #54)

| Arquivo | Conteúdo |
|---|---|
| `data/releases.csv` | Releases publicadas e pré-releases (drafts são descartados). `status_compare`: `ok`, `404` (tag apagada/reescrita, ignorada no lead time), `sem_anterior` (primeira release da história), `fora_da_janela`, `fora_da_serie` (pré-release fora da série principal). `n_commits` = commits incluídos na release. |
| `data/commits_por_release.csv` | Um commit por linha para cada release da janela: `sha`, `commit_author_date`, `commit_committer_date`, primeira linha da `mensagem`, `tag_name` e `tag_anterior`. O `compare` é paginado (100 por página), então releases com mais de 250 commits vêm completas. |
| `data/tags.csv` | Tags com o SHA e a data do commit apontado (`commit_author_date`). `max_tags_por_repo` no `config.yaml` limita quantas tags recebem data. |

A janela é o intervalo semiaberto `[window.start, window.end)`. Ao final da execução, o log mostra os contadores de releases ignoradas (`ignoradas_404`, `ignoradas_sem_anterior`) e de releases sem commits novos.

### Testes
```bash
pytest --cov=metrics --cov-report=term-missing
```

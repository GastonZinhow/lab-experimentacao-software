# Pipeline DORA Metrics Mining (Lab03S01)

### Pré-requisitos
```bash
pip install -r requirements.txt
export GITHUB_TOKEN="seu_token_aqui"     # PowerShell: $env:GITHUB_TOKEN = "seu_token_aqui"
```
Sem `GITHUB_TOKEN`, os scripts usam o token do GitHub CLI (`gh auth login`).
Os caminhos de `config.yaml` (`cache_dir`, `output_dir`) são relativos à pasta
do próprio `config.yaml`, então os comandos abaixo podem ser rodados de
`lab03/code` ou, trocando o caminho do config, de qualquer pasta.

### Execução
```bash
python -m pipeline --config config.yaml                  # amostra completa (selection.sample_size)
python -m pipeline --config config.yaml --sample-size 5  # teste rápido
python -m pipeline --config config.yaml --reusar-amostra # mesma amostra de data/metadados.csv
```

A busca devolve candidatos diferentes a cada dia (as estrelas mudam), e o
embaralhamento com a mesma semente sobre outra lista de candidatos gera outra
amostra. Para coletar de novo **a amostra já fechada** (a de `metadados.csv`
versionado), use `--reusar-amostra`: a busca e a seleção são puladas e só são
coletados runs, releases, commits e tags; `candidatos.csv`, `metadados.csv`,
`funil.csv` e `faixas_busca.csv` não são reescritos. Repositórios cujo número
de runs válidos mudou desde a seleção (runs apagados pela retenção do GitHub)
aparecem no log com `[Aviso]`.

No Windows, `coletar.cmd` roda a coleta e a conferência em sequência e grava
o log em `.cache/pipeline.log`; enquanto o pipeline roda, o Windows não entra
em suspensão automática (a tela pode apagar).

Todas as respostas da API ficam em `.cache/api_cache.db`. Se a coleta for
interrompida (rate limit, rede, `Ctrl+C`), basta rodar o mesmo comando de novo:
o que já foi baixado é lido do cache.

### Etapas
1. **Busca de candidatos** (`GET /search/repositories?q=stars:>1000`): a busca é
   fatiada pelas faixas de `selection.star_breaks`; toda faixa com mais de 1.000
   resultados (teto da API) é subdividida ao meio até caber no teto. Duplicatas
   são removidas pelo `id` do repositório.
2. **Critério de inclusão**: os candidatos são avaliados em ordem aleatória
   (`seed`) até reunir `selection.sample_size` repositórios. Os filtros são
   aplicados do mais barato ao mais caro, parando no primeiro que reprova:
   arquivado/fork → sem workflows (`total_count = 0`) → menos de `min_releases`
   releases na janela → menos de `min_runs` workflow runs válidos na janela.
3. **Metadados** dos incluídos: estrelas, linguagem, idade, `default_branch`
   e nº de contribuidores (`GET /contributors?per_page=1&anon=true`, lendo a
   última página do cabeçalho `Link`).
4. **Releases, commits entre releases e tags** da amostra final (issue #54,
   seção abaixo).

### Conferência da coleta
```bash
python conferencia.py --config config.yaml
```
Recalcula, sem cache e por um caminho independente do pipeline, o nº de
releases e de runs válidos do repositório com menos e do com mais runs da
amostra, e grava `data/conferencia.md` com a comparação e os links para
conferir na interface do GitHub. Sai com código 1 se algum valor divergir.

### Saídas (`data/`)
| Arquivo | Conteúdo |
|---|---|
| `faixas_busca.csv` | Faixas consultadas na busca: `total_count` e quantos itens foram coletados (nenhuma acima de 1.000). |
| `candidatos.csv` | Todos os candidatos, com `ordem_avaliacao`, `status` (`incluido`, `descartado`, `nao_avaliado`) e `motivo_descarte`. |
| `metadados.csv` | Amostra final com os fatores da RQ 06. |
| `funil.csv` | Quantos repositórios restam após cada etapa e por que os demais saíram. |
| `runs.csv` | Workflow runs (`event=push`, default branch, janela) da amostra final (não versionado: é regerado pelo cache). |
| `conferencia.md` | Resultado de `conferencia.py`. |

#### `metadados.csv`
| Coluna | Tipo | Unidade | Origem |
|---|---|---|---|
| `full_name`, `owner`, `repo` | texto | – | busca (`full_name`, `owner.login`, `name`) |
| `stars` | inteiro | estrelas | busca (`stargazers_count`), no momento da coleta |
| `language` | texto | – | busca (`language`), linguagem principal |
| `created_at` | data ISO | – | busca (`created_at`) |
| `idade_dias` | inteiro | dias | fim da janela − `created_at` |
| `default_branch` | texto | – | busca (`default_branch`) |
| `fork`, `archived` | booleano | – | busca |
| `contributors` | inteiro | pessoas | última página de `GET /contributors?per_page=1&anon=true` (vazio se a API recusar a listagem) |
| `n_workflows` | inteiro | workflows | `total_count` de `GET /actions/workflows` |
| `n_releases_janela` | inteiro | releases | releases com `draft = false`, `prerelease = false` e `published_at` na janela |
| `n_prereleases_janela` | inteiro | releases | idem, com `prerelease = true` |
| `n_runs_validos_janela` | inteiro | runs | runs com `conclusion` em sucesso ou falha (tabela da seção 3 do enunciado) |

### Saídas de releases, commits e tags (issue #54)

| Arquivo | Conteúdo |
|---|---|
| `data/releases.csv` | Releases publicadas e pré-releases (drafts são descartados). `status_compare`: `ok`, `404` (tag apagada/reescrita, ignorada no lead time), `indisponivel` (a API não conseguiu gerar um compare muito grande), `sem_anterior` (primeira release da história), `fora_da_janela`, `fora_da_serie` (pré-release fora da série principal). `n_commits` = commits incluídos na release. `body` = texto das release notes (usado pela heurística corretiva v3). |
| `data/commits_por_release.csv` | Um commit por linha para cada release da janela: `sha`, `commit_author_date`, `commit_committer_date`, primeira linha da `mensagem`, `tag_name` e `tag_anterior`. O `compare` é paginado (100 por página), então releases com mais de 250 commits vêm completas. |
| `data/tags.csv` | Tags com o SHA e a data do commit apontado (`commit_author_date`). `max_tags_por_repo` no `config.yaml` limita quantas tags recebem data. |

A janela é o intervalo semiaberto `[window.start, window.end)`. O compare é feito entre releases consecutivas da série coletada, aproveitando releases intermediárias quando elas existem. Se o GitHub retornar `422/not_available` para uma comparação grande demais, a release recebe `status_compare=indisponivel`, fica sem `n_commits` e a coleta continua; esses commits não entram nos contadores. Ao final da execução, o log mostra os contadores de releases ignoradas (`ignoradas_404`, `ignoradas_indisponivel`, `ignoradas_sem_anterior`) e de releases sem commits novos.

### Validação manual (amostra-ouro, issue #59)

```bash
python -m rotulagem.sorteio --config config.yaml       # sorteio + planilha de rotulagem
python -m rotulagem.concordancia --config config.yaml  # kappa de Fleiss, divergências e consenso
```

O sorteio usa a seção `validation` do `config.yaml`: 60 repositórios entre os
100 primeiros incluídos na ordem de avaliação e 5 releases publicadas na janela
de cada um, sempre com `seed = 42`. Rodá-lo de novo gera exatamente os mesmos
arquivos. As saídas ficam em `lab03/validacao/`:

| Arquivo | Conteúdo |
|---|---|
| `amostra_ouro_repos.csv` | Os 60 repositórios sorteados. |
| `planilha_rotulagem.csv` | Uma linha por release, com links para a release e para os commits desde a anterior; colunas de rótulo vazias e nenhuma coluna da heurística. |
| `rotulos_<avaliador>.csv` | Planilha preenchida por cada avaliador ([guia](../validacao/guia_rotulagem.md)). |
| `kappa_fleiss.csv` | Kappa de Fleiss e interpretação de Landis & Koch por dimensão. |
| `divergencias.csv` | Itens sem unanimidade (pauta da reunião). |
| `decisoes_reuniao.csv` | Decisões da reunião de consenso (empates e revisões). |
| `rotulos_consenso.csv` | Rótulo de consenso por release e a origem de cada um (`unanime`, `maioria`, `reuniao`). |
| `commits_amostra_ouro.csv` | Commits `tag_anterior..tag_name` das 300 releases da amostra-ouro (formato de `commits_por_release.csv`). |
| `notas_amostra_ouro.csv` | Release notes das 300 releases da amostra-ouro. |
| `erros_heuristica_<versao>.csv` | Falsos positivos e negativos de cada versão da heurística (gerado por `rotulagem.avaliacao`). |

O protocolo de desempate está em [`docs/protocolo_consenso.md`](../docs/protocolo_consenso.md).

### Heurística corretiva e CFR (b) (issue #61)

```bash
python -m rotulagem.avaliacao --config config.yaml --todas   # P/R/F1 de cada versão contra o consenso
python calcular_cfr_b.py --config config.yaml                # data/cfr_b.csv e data/releases_corretivas.csv
```

A heurística está em `metrics/corretiva.py` (versão atual em `VERSAO_ATUAL`);
o histórico das versões e o P/R/F1 de cada uma, em
[`docs/versoes_heuristica.md`](../docs/versoes_heuristica.md). Uma release R
falhou se alguma release publicada até 7 dias depois dela for corretiva;
releases dos últimos 7 dias da janela são censuradas. `cfr_b.csv` traz, por
repositório, `cfr_b`, `falhas`, `avaliadas`, `censuradas`, `corretivas` e
`releases`.

### Dataset final e análises (issues #63, #64 e #65)

```bash
python gerar_dataset.py --config config.yaml   # data/dataset_dora.csv
```

`dataset_dora.csv` tem uma linha por repositório com os metadados, todas as
métricas DORA em todas as variantes (frequência por release, release +
pré-release e tag; lead time (a)/(b); CFR (a)/(b) com as releases censuradas;
tempo de recuperação com os episódios censurados) e a classificação de
referência C1. Cada coluna está no
[dicionário de dados](../docs/dicionario_de_dados.md).

As análises ficam em `lab03/analise/` e leem só o `dataset_dora.csv`:

```bash
cd ../analise
python -m nbconvert --to notebook --execute --inplace rq01_04_descritiva.ipynb  # RQ01 a RQ04 (#64)
python -m nbconvert --to notebook --execute --inplace classificacao_c1.ipynb    # C1 e data/classificacao_c1.csv (#65)
python -m nbconvert --to notebook --execute --inplace rq07_sensibilidade.ipynb  # C1/C2/C3, kappa e transições (#68)
python -m nbconvert --to notebook --execute --inplace rq08_rework_rate.ipynb     # rework rate × CFR (b) (#69)
```

As figuras vão para `analise/figuras/` e as tabelas para `analise/tabelas/`.
Os notebooks precisam de `matplotlib`, `scipy` e, para rodar pela linha de
comando, `nbconvert` e `ipykernel` (todos no `requirements.txt`).

O notebook da RQ07 também grava `data/classificacao_rq07.csv`, com as
categorias por métrica e geral de cada repositório nas três combinações. As
tabelas `rq07_pares.csv` e `rq07_transicao_*.csv` trazem, respectivamente, a
porcentagem de mudança com kappa ponderado linear e as matrizes de transição.
O kappa usa explicitamente a ordem ordinal Elite → High → Medium → Low; a
ordem alfabética padrão atribuiria distâncias incorretas às categorias.

O notebook da RQ08 confere a coluna `rework_rate` do dataset, exporta
`rq08_resumo.csv` e `rq08_comparacao_cfr_b.csv` para `analise/tabelas/` e
gera o gráfico de violino com a comparação pareada em
`analise/figuras/rq08_rework_vs_cfr.png`.

### Testes
```bash
pytest --cov=metrics --cov-report=term-missing
```

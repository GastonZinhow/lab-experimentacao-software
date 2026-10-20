# Dicionário de dados

Arquivos finais do Lab03, uma linha por repositório da amostra. A janela é o
intervalo semiaberto `[2025-09-30, 2026-09-30)` (365 dias ≈ 52,14 semanas).
Convenções: tempos em **horas**, frequências em **deploys por semana**, taxas
como **fração de 0 a 1** (0,25 = 25%). Célula vazia = métrica indefinida para
o repositório (ex.: CFR (b) sem nenhuma release avaliável).

## `code/data/dataset_dora.csv`

Gerado por `python gerar_dataset.py --config config.yaml` a partir das saídas
do pipeline (`metadados.csv`, `runs.csv`, `releases.csv`,
`commits_por_release.csv` e `tags.csv`). As funções de cálculo estão em
`code/metrics/`.

### Metadados (de `metadados.csv`)

| Coluna | Tipo | Unidade | Origem / fórmula |
|---|---|---|---|
| `full_name` | texto | – | `owner/repo`; chave do repositório em todos os CSVs |
| `owner`, `repo` | texto | – | busca (`owner.login`, `name`) |
| `stars` | inteiro | estrelas | busca (`stargazers_count`), no dia da coleta |
| `language` | texto | – | busca (`language`), linguagem principal |
| `created_at` | data ISO | – | busca (`created_at`) |
| `idade_dias` | inteiro | dias | fim da janela − `created_at` |
| `default_branch` | texto | – | busca (`default_branch`) |
| `contributors` | inteiro | pessoas | última página de `GET /contributors?per_page=1&anon=true` |
| `n_workflows` | inteiro | workflows | `total_count` de `GET /actions/workflows` |

### RQ01: deployment frequency

| Coluna | Tipo | Unidade | Fórmula |
|---|---|---|---|
| `n_releases` | inteiro | releases | releases com `draft = false`, `prerelease = false` e `published_at` na janela |
| `n_prereleases` | inteiro | releases | idem, com `prerelease = true` |
| `n_tags` | inteiro | tags | tags cujo commit apontado tem `commit.author.date` na janela |
| `deploy_freq_release` | real | deploys/semana | `n_releases ÷ 52,14` (definição principal, C1) |
| `deploy_freq_release_pre` | real | deploys/semana | `(n_releases + n_prereleases) ÷ 52,14` (variante C2 da RQ07) |
| `deploy_freq_tag` | real | deploys/semana | `n_tags ÷ 52,14` (variante C3 da RQ07) |

### RQ02: lead time for changes

Para cada release R da janela, os commits de R são os de
`compare/{release anterior}...{R}` (a anterior pode estar fora da janela). A
data do commit é `commit.author.date`.

| Coluna | Tipo | Unidade | Fórmula |
|---|---|---|---|
| `lead_time_a_horas` | real | horas | (a) mediana, entre as releases avaliadas, de `published_at(R) − commit mais antigo de R` |
| `lead_time_b_horas` | real | horas | (b) mediana de `published_at(R) − data do commit` sobre todos os commits de todas as releases avaliadas |
| `lt_releases_avaliadas` | inteiro | releases | releases da janela com compare `ok` e pelo menos 1 commit |
| `lt_commits_avaliados` | inteiro | commits | commits dessas releases (base da variante b) |
| `lt_releases_sem_commits` | inteiro | releases | compare `ok`, mas sem commits novos (fora do lead time) |
| `lt_releases_sem_anterior` | inteiro | releases | primeira release da história do repositório (fora do lead time) |
| `lt_releases_404` | inteiro | releases | compare com 404, tag apagada ou reescrita (fora do lead time) |
| `lt_releases_indisponivel` | inteiro | releases | compare grande demais para a API (`422`) (fora do lead time) |

### RQ03: change failure rate

| Coluna | Tipo | Unidade | Fórmula |
|---|---|---|---|
| `runs_sucesso` | inteiro | runs | runs (`event = push`, default branch, janela) com `conclusion = success` |
| `runs_falha` | inteiro | runs | runs com `conclusion` em `failure`, `timed_out`, `startup_failure` |
| `cfr_a` | real | fração | (a) proxy de CI: `runs_falha ÷ (runs_falha + runs_sucesso)` |
| `cfr_b` | real | fração | (b) proxy de entrega: `cfr_b_falhas ÷ cfr_b_avaliadas`; vazio se nenhuma release for avaliável |
| `cfr_b_falhas` | inteiro | releases | releases seguidas, em até 7 dias, por uma release corretiva (heurística v3, `metrics/corretiva.py`) |
| `cfr_b_avaliadas` | inteiro | releases | releases da janela publicadas antes de `2026-09-23` (fim da janela − 7 dias) |
| `cfr_b_censuradas` | inteiro | releases | releases dos últimos 7 dias da janela: fora do numerador e do denominador |
| `releases_corretivas` | inteiro | releases | releases da janela que a heurística v3 marca como corretivas (base do rework rate, RQ08) |
| `rework_rate` | real | fração | RQ08: `releases_corretivas ÷ n_releases`; não usa a censura de 7 dias do CFR (b) |

### RQ04: tempo de recuperação

As runs de cada workflow são ordenadas por `run_started_at`. Um episódio de
falha começa numa falha e termina no próximo sucesso do mesmo workflow; runs
ignoradas (`cancelled`, `skipped`…) não abrem nem fecham episódios.

| Coluna | Tipo | Unidade | Fórmula |
|---|---|---|---|
| `tempo_recuperacao_horas` | real | horas | mediana, entre os episódios recuperados de todos os workflows, de `updated_at do sucesso − run_started_at da primeira falha`; vazio sem episódio recuperado |
| `episodios_falha` | inteiro | episódios | total de episódios |
| `episodios_recuperados` | inteiro | episódios | episódios encerrados por um sucesso dentro da janela |
| `episodios_censurados` | inteiro | episódios | episódios sem sucesso até o fim da janela |
| `prop_episodios_censurados` | real | fração | `episodios_censurados ÷ episodios_falha`; vazio sem episódios |

### Classificação de referência C1

Combinação C1 da RQ07: release, lead time (a), CFR (a), mais o tempo de
recuperação. Cortes da tabela da disciplina (`metrics/classificacao.py`).

| Coluna | Tipo | Valores | Fórmula |
|---|---|---|---|
| `c1_deploy_frequency` | categoria | Elite, High, Medium, Low | `deploy_freq_release`: ≥ 7/sem; ≥ 1/sem; ≥ 1/mês; < 1/mês |
| `c1_lead_time` | categoria | idem | `lead_time_a_horas`: < 1 dia; < 1 semana; < 30 dias; ≥ 30 dias |
| `c1_cfr` | categoria | idem | `cfr_a`: ≤ 15%; ≤ 30%; ≤ 45%; > 45% |
| `c1_tempo_recuperacao` | categoria | idem | `tempo_recuperacao_horas`: < 1 h; < 1 dia; < 1 semana; ≥ 1 semana |
| `c1_geral` | categoria | idem | mediana das notas (Elite 4, High 3, Medium 2, Low 1) arredondada para baixo; métricas vazias ficam fora |

## `code/data/classificacao_c1.csv`

Exportado pelo notebook `analise/classificacao_c1.ipynb` (Issue #65), base da
análise de sensibilidade (RQ07).

| Coluna | Tipo | Unidade | Descrição |
|---|---|---|---|
| `full_name` | texto | – | repositório |
| `deploy_freq_release`, `lead_time_a_horas`, `cfr_a`, `tempo_recuperacao_horas` | real | como acima | valores usados na C1 |
| `cat_deploy_frequency`, `cat_lead_time`, `cat_cfr`, `cat_tempo_recuperacao` | categoria | Elite…Low | categoria de cada métrica |
| `nota_deploy_frequency`, `nota_lead_time`, `nota_cfr`, `nota_tempo_recuperacao` | inteiro | 1 a 4 | nota de cada categoria |
| `n_metricas_classificadas` | inteiro | 0 a 4 | métricas com valor |
| `mediana_notas` | real | 1 a 4 | mediana das notas, antes do arredondamento |
| `categoria_geral` | categoria | Elite…Low | `floor(mediana_notas)` convertido em categoria (= `c1_geral`) |

## `code/data/classificacao_rq07.csv`

Exportado pelo notebook `analise/rq07_sensibilidade.ipynb` (Issue #68), com
uma linha para cada um dos 300 repositórios. Para cada combinação `c1`, `c2`
e `c3`, contém as colunas `*_deploy_frequency`, `*_lead_time`, `*_cfr`,
`*_tempo_recuperacao` e `*_geral`, todas categóricas (Elite, High, Medium ou
Low). As combinações são:

| Combinação | Frequência | Lead time | CFR | Recuperação |
|---|---|---|---|---|
| C1 | `deploy_freq_release` | `lead_time_a_horas` | `cfr_a` | `tempo_recuperacao_horas` |
| C2 | `deploy_freq_release_pre` | `lead_time_b_horas` | `cfr_b` | `tempo_recuperacao_horas` |
| C3 | `deploy_freq_tag` | `lead_time_b_horas` | `cfr_a` | `tempo_recuperacao_horas` |

As tabelas derivadas ficam em `analise/tabelas/`: `rq07_pares.csv` registra
o número e a porcentagem de mudanças, o kappa de Cohen ponderado linearmente
e a distância ordinal das mudanças; `rq07_transicao_c1_c2.csv`,
`rq07_transicao_c1_c3.csv` e `rq07_transicao_c2_c3.csv` são as matrizes de
transição em contagens de repositórios.

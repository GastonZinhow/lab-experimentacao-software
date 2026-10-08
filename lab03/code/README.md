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
```

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

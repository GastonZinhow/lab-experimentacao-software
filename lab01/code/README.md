# Lab01 - Repositorios populares

Coleta dados dos repositorios mais populares do GitHub via GraphQL, exporta em
CSV/JSON e calcula as metricas das 7 questoes de pesquisa (RQ01 a RQ07) do
laboratorio.

## Estrutura do projeto

```
code/
├── main.py                          # coleta os 1000 repositorios e exporta em CSV
├── check_releases_updates.py        # validacao amostral de releases/atualizacoes
├── export_project_snapshot.py       # exporta snapshot do GitHub Projects em CSV
├── requirements.txt
├── data/
│   ├── raw/                         # dados brutos coletados (JSON/CSV)
│   ├── processed/                   # relatorios de validacao
│   └── snapshots/                   # snapshots do Project por sprint
└── src/
    ├── config.py                    # le o GITHUB_TOKEN do .env
    ├── github_client.py             # executa requisicoes GraphQL na API do GitHub
    ├── queries.py                   # query de busca de repositorios
    ├── project_queries.py           # query dos itens do GitHub Projects v2
    ├── collectors/
    │   ├── repository_collector.py  # pagina e coleta repositorios
    │   └── project_collector.py     # pagina e coleta itens do Project
    ├── exporters/
    │   ├── repository_exporter.py   # exporta repositorios em CSV/JSON
    │   └── project_snapshot_exporter.py  # exporta snapshot do Project em CSV
    └── metrics/
        ├── analyze_rq01_rq02.py     # RQ01 (idade) e RQ02 (% PRs merged)
        ├── analyze_rq05_rq06.py     # RQ05 (linguagem popular) e RQ06 (% issues fechadas)
        ├── analyze_rq07.py          # bonus: RQ02/03/04 comparadas por linguagem popular
        └── validate_data_consistency.py  # valores ausentes, duplicatas e outliers
```

## Como configurar (do zero)

1. **Python 3.11+** instalado.
2. Instale as dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Gere um Personal Access Token no GitHub em
   [github.com/settings/tokens](https://github.com/settings/tokens) com os escopos:
   - `public_repo` (ou `repo`) — para consultar repositorios.
   - `read:project` — para consultar o GitHub Projects v2 (necessario so pro
     `export_project_snapshot.py`).
4. Crie um arquivo `.env` dentro de `lab01/code/` com:
   ```
   GITHUB_TOKEN=ghp_seu_token_aqui
   ```
   Esse arquivo esta no `.gitignore` e nunca deve ser commitado.

## Como rodar cada script

Todos os comandos abaixo devem ser executados a partir da pasta `lab01/code/`.

**Coletar os 1000 repositorios (RQ01-RQ06, base de dados principal):**
```
python main.py
```
Gera `data/raw/top_1000_repositories.csv` (separador `;`) e imprime a contagem
de valores ausentes por campo.

**Validar consistencia dos dados coletados:**
```
python src/metrics/validate_data_consistency.py
```
Le `data/raw/top_1000_repositories.csv` e reporta valores ausentes, duplicatas,
inconsistencias logicas (ex.: issues fechadas > total de issues) e outliers por
metrica (IQR).

**Rodar as analises das RQs:**
```
python src/metrics/analyze_rq01_rq02.py
python src/metrics/analyze_rq05_rq06.py
python src/metrics/analyze_rq07.py
```
> Atencao: esses tres scripts ainda leem `data/raw/top_100_repositories.json`
> (a amostra de validacao de 100 repositorios da Sprint 01), nao o CSV de 1000.
> Se o grupo decidir rodar as RQs sobre os 1000 repositorios, e preciso migrar
> essas analises para ler do `top_1000_repositories.csv`.

**Exportar snapshot do GitHub Projects (ao final de cada sprint):**
```
python export_project_snapshot.py <NOME_DA_SPRINT>
```
Exemplo: `python export_project_snapshot.py Lab01S02`. Detalhes de como
funciona e como repetir em sprints futuras estao em
[`../docs/project_snapshot.md`](../docs/project_snapshot.md).

## Fonte de referencia usada na RQ05

TIOBE Index (https://www.tiobe.com/tiobe-index/), ranking de agosto/2026, top 10
linguagens. A lista esta definida em `POPULAR_LANGUAGES` em
`src/metrics/analyze_rq05_rq06.py` e reutilizada em `analyze_rq07.py`.

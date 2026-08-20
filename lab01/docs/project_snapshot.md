# Snapshot do GitHub Projects por sprint

## Toda sprint, ao final dela, faça isto:

1. De dentro de `lab01/code/`, rode:
   ```
   python export_project_snapshot.py <NOME_DA_SPRINT>
   ```
   Exemplo, ao fechar a Sprint 02:
   ```
   python export_project_snapshot.py Lab01S02
   ```
2. Confira o CSV gerado em `data/snapshots/<nome_da_sprint_minusculo>_project_snapshot.csv`.
3. Comite o CSV referenciando a issue do snapshot no commit.

Só isso — não precisa editar nenhum arquivo `.py`, o nome da sprint é passado
direto no comando.

## Pré-requisito (só precisa checar uma vez, não toda sprint)

O `.env` em `lab01/code/.env` precisa de um `GITHUB_TOKEN` com o escopo
**`read:project`** habilitado (em
[github.com/settings/tokens](https://github.com/settings/tokens), editar o
token existente). Sem esse escopo a consulta falha com `INSUFFICIENT_SCOPES`.

## Por que isso existe

O GitHub Projects não guarda histórico consultável de mudanças de coluna
(Status) via API. Rodando esse export ao final de cada sprint, acumulamos uma
série de snapshots que serve de base de dados pros Labs 04 e 05.

## O que o script coleta

Para cada item do Project que aponta pra uma Issue (draft issues soltas são
ignoradas): número da issue, título, URL, assignees e o valor atual do campo
**Status**. A coluna `sprint` recebe o nome passado no comando — o Project não
tem um campo nativo de sprint/iteração, por isso o rótulo é carimbado na hora
da exportação.

## Onde está o código

- `src/project_queries.py` — query GraphQL que busca os itens do Project (com paginação).
- `src/collectors/project_collector.py` — consome a query e monta os registros.
- `src/exporters/project_snapshot_exporter.py` — escreve o CSV.
- `export_project_snapshot.py` — script de entrada (recebe o nome da sprint como argumento).

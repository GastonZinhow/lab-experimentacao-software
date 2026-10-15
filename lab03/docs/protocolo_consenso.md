# Protocolo de consenso da amostra-ouro

Issue #59 · seção 6 do enunciado.

## 1. Sorteio

- `python -m rotulagem.sorteio --config config.yaml` (em `lab03/code`).
- **Base:** os 100 primeiros repositórios incluídos na ordem de avaliação do pipeline (`ordem_avaliacao` em `candidatos.csv`, embaralhada com `seed = 42`). Essa ordem é a mesma na coleta completa (#63): os 100 primeiros incluídos continuam sendo os mesmos quando a amostra cresce, então o sorteio é estável e todos os sorteados pertencem à amostra final.
- **Repositórios:** `base.sample(n=60, random_state=42)`, com a base ordenada por `full_name`.
- **Releases:** 5 por repositório, `sample(n=5, random_state=42)` entre as releases publicadas (sem pré-releases e drafts) dentro da janela.
- **Saídas:** `validacao/amostra_ouro_repos.csv` e `validacao/planilha_rotulagem.csv` (links para a release e para os commits desde a release anterior; nenhuma coluna da heurística).
- Rodar o script de novo gera exatamente os mesmos arquivos.

## 2. Rotulagem independente

Cada integrante preenche `validacao/rotulos_<nome>.csv` seguindo o [guia de rotulagem](../validacao/guia_rotulagem.md), sem consultar os demais nem a heurística, e commita o arquivo **antes** da reunião:

| Avaliador | Issue | Arquivo |
|---|---|---|
| Luisa | #58 | `rotulos_luisa.csv` |
| Mirelly | #60 | `rotulos_mirelly.csv` |
| Matheus | #62 | `rotulos_matheus.csv` |

## 3. Concordância

`python -m rotulagem.concordancia --config config.yaml` calcula o kappa de Fleiss (`statsmodels`: `aggregate_raters` + `fleiss_kappa`) em cada dimensão:

| Dimensão | Itens | Categorias |
|---|---|---|
| `tipo_projeto` | 60 repositórios | biblioteca, aplicacao, cli, outro |
| `entregas_reais` | 60 repositórios | sim, nao, incerto |
| `corretiva` | 300 releases | sim, nao |

Interpretação de Landis & Koch (1977): < 0 pobre; 0–0,20 leve; 0,21–0,40 razoável; 0,41–0,60 moderada; 0,61–0,80 substancial; 0,81–1 quase perfeita. Os valores ficam em `validacao/kappa_fleiss.csv`, e os itens sem unanimidade, em `validacao/divergencias.csv`.

Os kappas são calculados **sobre as planilhas independentes**, antes de qualquer discussão, e não são recalculados depois da reunião.

## 4. Desempate

1. **Unanimidade (3-0):** o rótulo é aceito sem discussão.
2. **Maioria simples (2-1):** o rótulo da maioria é aceito. Na reunião, o avaliador vencido pode pedir revisão do item; a revisão só muda o rótulo se os três concordarem, e a mudança é registrada em `decisoes_reuniao.csv`.
3. **Empate (1-1-1),** possível em `tipo_projeto` e `entregas_reais`: decidido na reunião. Cada um apresenta o seu argumento, o grupo relê o README e as release notes, e decide por acordo; se o acordo não sair, vale a categoria mais conservadora (`outro` para `tipo_projeto`, `incerto` para `entregas_reais`).

Cada decisão de reunião vira uma linha de `validacao/decisoes_reuniao.csv`:

| Coluna | Conteúdo |
|---|---|
| `dimensao` | `tipo_projeto`, `entregas_reais` ou `corretiva` |
| `full_name` | repositório |
| `tag_name` | tag da release (vazio nas dimensões de repositório) |
| `rotulo` | rótulo decidido |
| `justificativa` | uma frase com o motivo |

Com todos os empates decididos, o script grava `validacao/rotulos_consenso.csv` (uma linha por release, com o rótulo e a origem de cada dimensão: `unanime`, `maioria` ou `reuniao`). Esse arquivo é a referência para avaliar a heurística de release corretiva (#61, RQ 03 b) e fornece o tipo do projeto da RQ 06.

## 5. Registro da reunião

| Data | Participantes | Itens discutidos | Observações |
|---|---|---|---|
| *a preencher* | | | |

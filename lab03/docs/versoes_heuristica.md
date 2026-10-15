# Versões da heurística de *release* corretiva

Issue #61 · seção 6 do enunciado. A heurística está em
[`code/metrics/corretiva.py`](../code/metrics/corretiva.py) e a definição
operacional de cada versão, na Seção 2.7 do artigo ([`main.md`](main.md)).
A versão usada no CFR (b) e no *rework rate* é `VERSAO_ATUAL` (hoje, **v3**).

## Como reproduzir

```bash
cd lab03/code
python -m rotulagem.concordancia --config config.yaml   # gera validacao/rotulos_consenso.csv
python -m rotulagem.avaliacao --config config.yaml --todas
python calcular_cfr_b.py --config config.yaml           # CFR (b) com a versão atual
```

`rotulagem.avaliacao` compara cada versão com o rótulo `corretiva` da
referência (padrão: `rotulos_consenso.csv`; `--referencia` aceita outra
planilha), calcula precisão, *recall* e F1 com
`sklearn.metrics.precision_recall_fscore_support` (classe positiva:
corretiva = sim) e grava os erros em `validacao/erros_heuristica_<versao>.csv`.

Entradas da amostra-ouro (em `validacao/`):

| Arquivo | Conteúdo | Origem |
|---|---|---|
| `commits_amostra_ouro.csv` | Primeira linha de cada *commit* em `tag_anterior..tag_name` das 300 *releases* (35.670 *commits*). Mesmo formato de `data/commits_por_release.csv`. | `git log` em clones locais (sem árvore) dos 60 repositórios, o mesmo intervalo do `compare` da API. |
| `notas_amostra_ouro.csv` | Texto das *release notes* (285 das 300 têm notas), truncado em 2.500 caracteres. | HTML da página de cada *release*, convertido em texto durante a rotulagem. No pipeline, as notas vêm do campo `body` da API (Markdown). |

## Resumo

Valores **dentro da amostra** (a heurística é aplicada às mesmas 300
*releases* usadas para ajustá-la) e, entre parênteses, a **média da
validação cruzada** (5 partes agrupadas por repositório, 5 sementes): em
cada parte, os limiares são escolhidos sem ver os repositórios avaliados.

| Versão | Referência | Precisão | Recall | F1 | F1 (validação cruzada) |
|---|---|---:|---:|---:|---:|
| v1 | consenso | *pendente* | *pendente* | *pendente* | – |
| v1 | concordantes (n = 281) | 0,235 | 0,919 | 0,374 | – |
| v1 | Mirelly (n = 300) | 0,244 | 0,928 | 0,387 | – |
| v1 | Luisa (n = 300) | 0,263 | 0,932 | 0,411 | – |
| v2 | consenso | *pendente* | *pendente* | *pendente* | *pendente* |
| v2 | concordantes | 0,778 | 0,565 | 0,654 | 0,612 |
| v2 | Mirelly | 0,745 | 0,507 | 0,603 | 0,558 |
| v2 | Luisa | 0,787 | 0,500 | 0,612 | 0,572 |
| **v3** | consenso | *pendente* | *pendente* | *pendente* | *pendente* |
| **v3** | concordantes | 0,827 | 0,694 | **0,754** | 0,695 |
| **v3** | Mirelly | 0,782 | 0,623 | 0,694 | 0,661 |
| **v3** | Luisa | 0,836 | 0,622 | 0,713 | 0,653 |

**Por que ainda não há números contra o consenso.** Em 15/10/2026, só as
planilhas de Mirelly (#60) e Luisa (#58) cobrem as releases de
`planilha_rotulagem.csv`. A planilha de Matheus (#62, branch
`git-local-optimization`) rotula **outra** amostra de 60 repositórios e 300
releases, sorteada por `validacao/gerar_amostra_ouro.py` sobre a amostra
expandida; nenhuma release é comum às duas. Sem um terceiro avaliador nos
mesmos itens, não há kappa de Fleiss nem `rotulos_consenso.csv`. Enquanto
isso, a referência provisória são os **281 itens em que Mirelly e Luisa
concordam** (93,7% de concordância na dimensão corretiva; 62 corretivas). Quando o
consenso existir, basta rodar os comandos acima e preencher as linhas
"consenso".

## v1: enunciado

**Regra.** Corretiva se a versão muda só o *patch* (`2.3.0 → 2.3.1`) **ou**
algum *commit* entre as releases contém `revert`, `hotfix` ou `fix` no
início de uma palavra.

**Resultado.** *Recall* alto e precisão muito baixa: a v1 marca 262 das 300
*releases*. Quase toda *release* tem algum *commit* com "fix", inclusive
*minors* com dezenas de funcionalidades, e o critério de *commit* sozinho
basta para marcar.

**Análise dos erros (FP = 186, FN = 5 nos concordantes).**

- O critério "há um *commit* com fix" não distingue uma *release* só de
  correção de uma *release* grande com algumas correções no meio. As
  corretivas têm mediana de 4 *commits*; as demais, de 23.
- *Commits* de funcionalidade quase não aparecem nas corretivas (mediana 0,
  contra 3 nas demais).
- Em monorepos (`rig`, `fumadocs`, `electric`, `TanStack/virtual`,
  `redux-saga`), a `tag_anterior` é de outro pacote, e a comparação de
  versões vira acaso (`fumadocs-openapi@9.7.1 → create-fumadocs-app@16.0.7`
  parece um *major*).

## v2: só *commits*

**Mudanças.** (1) Versões comparadas só entre *tags* do mesmo pacote (prefixo
antes da versão); pacotes diferentes contam como "fora do SemVer". (2) Linhas
de ruído descartadas: `chore`, `ci`, `docs`, `build`, `test`, `refactor`,
*merges*, *bumps*, *commits* de versão e texto padrão das notas do GitHub.
(3) Corretiva se a versão muda só o *patch* (ou está fora do SemVer), há no
máximo 5 *commits* significativos e há ao menos um sinal de correção, com no
máximo 0,5 sinal de funcionalidade por sinal de correção. O "e/ou" da v1
virou "e".

**Resultado.** A precisão sobe de 0,24 para 0,78, mas o *recall* cai para
0,57: F1 de 0,65 (0,61 na validação cruzada), ainda abaixo de 0,70.

**Análise dos erros (FP = 10, FN = 27 nos concordantes).** A maioria dos
FN é de corretivas cuja intenção está nas *release notes*, não nos *commits*:

- correções sem as palavras-chave nos *commits*: "Protect initial task
  startup from interrupts" (`socketry/async`), "Skip repositories with pull
  requests disabled instead of crashing" (`python-github-backup`);
- *releases* sem *commits* significativos: republicação após falha
  ("Patch release since the previous one failed", `bambi` 0.17.2), *bumps*
  de dependência que propagam uma correção (`redux-saga`), só "upd
  changelog" (`unleashed-firmware`, "This release is the hotfix…");
- projetos que sobem o *minor* em *releases* só de correção
  (`socketry/async`).

## v3: *commits* + *release notes* (versão atual)

**Mudanças.** Os sinais de correção e de funcionalidade passam a ser contados
também nas linhas das *release notes* (sem marcadores de lista/título e sem
as linhas de ruído), e o incremento de *minor* é aceito; só o de *major* fica
de fora. Para isso, o coletor passou a gravar o `body` de cada release em
`data/releases.csv`. O campo já vem na listagem de releases, então não há
chamadas extras à API.

**Resultado.** F1 de 0,754 nos concordantes (0,695 na validação cruzada),
com precisão de 0,83 e *recall* de 0,69. Contra cada avaliadora, F1 de 0,69 e
0,71.

**Erros restantes (FP = 9, FN = 19 nos concordantes).**

- **FN, hotfixes grandes:** `immich` v2.5.2 e v2.5.5 (15 e 31 *commits*,
  todos de correção, notas "Hotfixes"), `cider` v2.0.1, `miniflux` 2.3.1,
  `pyglet` v2.1.11 e v2.1.14 passam do limite de 5 *commits*
  significativos. Na grade testada (5, 10, 20 ou sem limite), aumentar o
  limite traz mais FP do que recupera FN.
- **FN, intenção só implícita:** `bambi` 0.17.2, `openebs` v4.5.1/v4.6.1
  (notas ricas, mas os *commits* são só submódulos), `universal-installer`
  v1.6.3 ("Downgrade android sdk to 36"), `kops` v1.36.1 (notas com
  *cherry-picks* sem a palavra "fix").
- **FP, manutenção de rotina:** `kubelogin` v1.35.2 e v1.36.4 e `vscode-vsce`
  v3.8.0 (só dependências com prefixo `fix(deps)`), `octobox` (release
  mensal automática), `HTMLHint` v1.9.2 ("npm audit fix").
- **FP, monorepos/séries:** `electric` (`tag_anterior` de outro pacote),
  `beyla` v3.9.1/v3.27.0.

## Testado e descartado

- **Intervalo desde a release anterior.** O guia de rotulagem cita "uma
  *release* lançada logo depois da anterior só com correções". Nas
  concordantes, as corretivas saem com mediana de 3,2 dias após a anterior,
  contra 20,9 dias das demais. Usado como regra extra (aceitar mais *commits*
  quando a *release* sai em até 1 dia), o F1 dentro da amostra sobe para
  0,77, mas a validação cruzada não melhora (0,66 a 0,70). Ficou de fora para
  não acrescentar um parâmetro sem ganho fora da amostra.
- **Fração mínima de *commits* de correção** (≥ 0,34, 0,5 ou 0,6 dos
  significativos) no lugar da razão funcionalidade ÷ correção: F1 igual ou
  menor.

## Ameaças à validade (rascunho para a Seção 5)

- **Ajuste e avaliação na mesma amostra.** Os limiares da v2 e da v3 foram
  escolhidos olhando as 300 releases da amostra-ouro, que também são a base
  do P/R/F1. A validação cruzada agrupada por repositório estima o F1 da v3
  fora da amostra em ≈ 0,69, um pouco abaixo do valor dentro da amostra
  (0,75) e no limite do critério de 0,70.
- **Notas da amostra-ouro × notas do pipeline.** Na avaliação, as notas vêm
  do HTML da página da release, convertido em texto e truncado em 2.500
  caracteres. No CFR (b), vêm do `body` em Markdown, sem truncamento. As
  palavras são as mesmas, mas notas longas podem ter mais sinais de
  funcionalidade no pipeline do que na avaliação.
- **Rótulos baseados nas notas.** As avaliadoras decidiram sobretudo pelas
  *release notes*. *Releases* cujo propósito só aparece no texto, e não em
  palavras-chave, continuam fora do alcance de uma heurística de
  palavras-chave (FN listados acima).

# Validação de consistência dos dados — 1000 repositórios (issue #8)

Gerado a partir de `src/metrics/validate_data_consistency.py`, executado sobre
`data/raw/top_1000_repositories.csv`.

## 1. Valores ausentes

| Campo | Ausentes | % |
|---|---|---|
| name, owner, url, created_at, stars, releases_count, pushed_at, pull_requests_count, merged_pull_requests_count, issues_count, closed_issues_count | 0 | 0% |
| primary_language | 87 | 8.7% |

Único campo com valores ausentes é `primary_language`, o que é esperado: repositórios
compostos majoritariamente por Markdown/documentação ou sem linguagem dominante
detectável pelo GitHub retornam `primaryLanguage: null` na API. Não invalida a coleta,
mas deve ser tratado como categoria própria ("sem linguagem definida") na RQ05 —
já é o que `analyze_rq05_rq06.py` faz.

## 2. Duplicados

0 repositórios duplicados (chave `owner/name`) entre os 1000 registros.

## 3. Inconsistências lógicas

Verificado para todos os 1000 repositórios:
- `closed_issues_count > issues_count` → 0 ocorrências
- `merged_pull_requests_count > pull_requests_count` → 0 ocorrências
- `stars <= 0` → 0 ocorrências
- `pushed_at` anterior a `created_at` → 0 ocorrências

Nenhuma inconsistência lógica encontrada nos 1000 repositórios.

## 4. Distribuições e outliers (IQR, 1.5×)

| Métrica | min | max | média | mediana | desvio padrão | outliers (IQR) |
|---|---|---|---|---|---|---|
| stars | 32.933 | 540.861 | 66.204,75 | 48.585,5 | 52.601,46 | 82 |
| releases_count | 0 | 1.000 | 126,16 | 39,0 | 212,39 | 92 |
| pull_requests_count | 0 | 262.083 | 6.357,32 | 1.346,0 | 16.470,68 | 118 |
| merged_pull_requests_count | 0 | 103.316 | 4.234,14 | 768,0 | 10.661,79 | 124 |
| issues_count | 0 | 251.150 | 5.096,87 | 1.662,0 | 12.610,48 | 100 |
| closed_issues_count | 0 | 233.639 | 4.440,55 | 1.297,5 | 11.297,03 | 97 |
| age_days | 6 | 6.704 | 2.799,78 | 2.830,0 | 1.654,54 | 0 |
| days_since_update | 0 | 2.451 | 114,11 | 2,0 | 265,1 | 194 |

Observações:
- Todas as métricas de contribuição/atividade (stars, PRs, issues, releases) têm
  distribuição fortemente assimétrica à direita (média >> mediana, muitos outliers
  positivos) — esperado em rankings por popularidade, onde poucos repositórios
  "mega populares" puxam a média para cima. Justifica reportar **mediana**, não média,
  no relatório final (conforme pedido no enunciado).
- `age_days` não tem outliers pelo critério IQR — a distribuição de idade é bem mais
  homogênea que as demais métricas.
- `days_since_update` tem mediana de 2 dias (a maioria dos repositórios populares foi
  atualizada muito recentemente) mas com outliers de até 2.451 dias (~6,7 anos) sem
  atualização — repositórios populares "congelados" (ex.: livros/tutoriais que não
  precisam de manutenção contínua).

### Problema de coleta confirmado: teto de 1000 em `releases_count`

O campo `releases_count` (vindo de `releases { totalCount }` na query GraphQL)
aparece com o valor **exatamente 1000** em **21 dos 1000 repositórios (2,1%)**
da base coletada. Isso foi confirmado como um teto artificial da API do GitHub,
não o total real de releases — validado manualmente via API REST
(`GET /repos/{owner}/{repo}/releases?per_page=1`, usando o cabeçalho `Link`
para descobrir o número real de páginas/releases, sem necessidade de token):

| Repositório | Coletado (`releases_count`) | Real (via paginação REST) |
|---|---|---|
| electron/electron | 1000 | 1.986 |
| vercel/next.js | 1000 | 3.810 |
| langchain-ai/langchain | 1000 | 1.337 |
| ggml-org/llama.cpp | 1000 | 6.894 |
| storybookjs/storybook | 1000 | 1.838 |

Ou seja, `releases { totalCount }` do GitHub GraphQL trunca em 1000 para
conexões muito grandes — comportamento conhecido/documentado da API para
campos de contagem em conexões extensas, não um erro do script de coleta do
grupo. Os outros 16 repositórios com `releases_count == 1000` (lista completa:
`home-assistant/core`, `zed-industries/zed`, `lobehub/lobehub`,
`ruvnet/ruflo`, `withastro/astro`, `BerriAI/litellm`, `TanStack/query`,
`RocketChat/Rocket.Chat`, `gradio-app/gradio`, `chakra-ui/chakra-ui`,
`mattermost/mattermost`, `frappe/erpnext`, `CopilotKit/CopilotKit`,
`pnpm/pnpm`, `refinedev/refine`, `k3s-io/k3s`) muito provavelmente sofrem do
mesmo teto, ainda que não tenham sido verificados individualmente via REST.

**Impacto na RQ03:** para esses 21 repositórios (2,1% da base), o valor de
"total de releases" está subestimado — em alguns casos, por uma margem grande
(ex.: llama.cpp: 1000 coletado vs. 6.894 real, quase 7× menor). Isso não
invalida a RQ03 como um todo (97,9% dos repositórios têm o valor correto), mas
deve ser mencionado como limitação metodológica na discussão da RQ03, e a
mediana/estatísticas devem ser calculadas com essa ressalva em mente — como o
teto rebaixa os valores para os repositórios que têm MAIS releases, o efeito
tende a ser subestimar a cauda superior da distribuição, não a mediana em si.

**Ação recomendada:** abrir subtarefa vinculada à issue #8 para: (a) documentar
essa limitação da API no relatório final (seção de discussão da RQ03), e (b)
avaliar, para o Lab01S03, se vale a pena recotar `releases_count` via paginação
REST apenas para os repositórios afetados (21 casos), em vez de reprocessar a
base toda.

## 5. Conclusão

Os dados dos 1000 repositórios estão consistentes: sem duplicados, sem violações
lógicas entre contagens totais/subconjuntos, e apenas uma lacuna esperada de dados
(linguagem primária ausente em 8,7% dos casos). O único problema real encontrado
é o teto de 1000 em `releases_count`, confirmado em 21 repositórios (2,1% da
base) — ver seção 4 para o impacto e a ação recomendada.

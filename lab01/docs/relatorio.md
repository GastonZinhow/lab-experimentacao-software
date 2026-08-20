# Relatório — Laboratório 01: Características de repositórios populares

*Versão: primeira versão (Lab01S02) — introdução, hipóteses informais e
metodologia de coleta. Resultados por RQ e discussão hipótese vs. resultado
serão preenchidos no Lab01S03, após a análise e visualização dos dados.*

## 1. Introdução e hipóteses informais

Este estudo investiga características de repositórios open-source populares no
GitHub, a partir dos 1.000 repositórios com maior número de estrelas. Para cada
questão de pesquisa (RQ), formulamos abaixo uma hipótese informal, uma
expectativa inicial, baseada em conhecimento prévio sobre o ecossistema
open-source, que será confrontada com os dados coletados no Lab01S03.

**RQ01 — Sistemas populares são maduros/antigos?**
Hipótese: a maioria dos repositórios populares é madura, com vários anos de
existência. Acumular um grande número de estrelas normalmente exige tempo de
exposição e maturação da comunidade em torno do projeto; poucos repositórios
muito recentes conseguem entrar no top de popularidade, mesmo em casos de
"hype" pontual.

**RQ02 — Sistemas populares recebem muita contribuição externa?**
Hipótese: repositórios populares recebem um volume alto de pull requests
aceitas, dado o efeito de rede típico de projetos open-source visíveis (mais
olhos, mais contribuidores). Esperamos, porém, grande variação no percentual
de PRs aceitas em relação ao total, dependendo do quão rigoroso é o processo
de revisão de cada mantenedor.

**RQ03 — Sistemas populares lançam releases com frequência?**
Hipótese: a maioria dos repositórios populares lança releases, mas com forte
variação por tipo de projeto. Bibliotecas e frameworks tendem a ter um
histórico de releases mais consistente, enquanto listas "awesome", tutoriais e materiais de estudo podem nunca ter uma release formal.

**RQ04 — Sistemas populares são atualizados com frequência?**
Hipótese: a maioria dos repositórios populares tem atualizações recentes
(dias/semanas), já que deixar de atualizar tende a reduzir engajamento e
visibilidade ao longo do tempo. Esperamos, no entanto, uma cauda de
repositórios "completos" ou de conteúdo estático (livros, listas de recursos)
que podem ficar longos períodos sem push, mesmo mantendo popularidade.

**RQ05 — Sistemas populares são escritos nas linguagens mais populares?**
Métrica de referência de "linguagens mais populares": **TIOBE Index**
(ranking de agosto/2026, top 10 — https://www.tiobe.com/tiobe-index/), mesma
fonte já usada em `analyze_rq05_rq06.py`.
Hipótese: a maioria dos repositórios populares usa linguagens do topo do
TIOBE (Python, C, C++, Java, C#, JavaScript, entre outras), pois popularidade
de linguagem e de projeto tendem a se reforçar mutuamente — mais
desenvolvedores familiarizados com a linguagem ampliam tanto o público quanto
o pool de contribuidores em potencial.

**RQ06 — Sistemas populares possuem um alto percentual de issues fechadas?**
Hipótese: repositórios populares mantêm um percentual alto de issues
fechadas, pois costumam ter equipes de manutenção mais estruturadas e
processos de triagem mais maduros. Ainda assim, esperamos que projetos muito
grandes (milhares de issues abertas) apresentem percentuais menores, pois o
volume de issues recebido pode superar a capacidade de resposta dos
mantenedores.

**RQ07 (bônus) — Sistemas escritos em linguagens mais populares recebem mais
contribuição externa, lançam mais releases e são atualizados com mais
frequência?**
Hipótese: repositórios em linguagens do topo do TIOBE devem apresentar mais
PRs aceitas e atualizações mais frequentes, pois uma base maior de
desenvolvedores familiarizados com a linguagem amplia o pool de contribuidores
ativos. Já para releases, esperamos uma diferença menor entre grupos de
linguagem, já que a frequência de releases parece depender mais do domínio/tipo
do projeto (biblioteca vs. conteúdo estático) do que da linguagem em si.

## 2. Metodologia de coleta

- Os dados foram coletados via **GraphQL API do GitHub** (`https://api.github.com/graphql`),
  usando um script próprio do grupo (sem bibliotecas de terceiros para acesso à API),
  implementado em `code/src/github_client.py`, `code/src/queries.py` e
  `code/src/collectors/repository_collector.py`.
- A busca utiliza `search(query: "stars:>0 sort:stars-desc", type: REPOSITORY, ...)`,
  paginada com `first`/`after` (cursor), coletando os 1.000 repositórios com maior
  número de estrelas (`code/main.py`).
- Para cada repositório, foram extraídos: nome, dono, URL, data de criação
  (`createdAt`), estrelas (`stargazerCount`), total de releases
  (`releases.totalCount`), data do último push (`pushedAt`), total de pull
  requests (`pullRequests.totalCount`) e PRs mescladas
  (`pullRequests(states: MERGED).totalCount`), linguagem primária
  (`primaryLanguage.name`), total de issues (`issues.totalCount`) e issues
  fechadas (`issues(states: CLOSED).totalCount`).
- Os dados foram exportados para `code/data/raw/top_1000_repositories.csv`
  (UTF-8, separador `;`) via `code/src/exporters/repository_exporter.py`.
- Antes da análise final, os dados foram validados quanto a consistência
  (distribuições, outliers, valores ausentes, contagens) — ver
  `code/data/processed/validation_report_1000_repos.md` para o relatório
  completo dessa validação (issue #8). Resumo: nenhum repositório duplicado,
  nenhuma inconsistência lógica entre contagens totais/subconjuntos, e apenas
  uma lacuna de dados esperada (`primary_language` ausente em 8,7% dos casos).
  Um problema real foi confirmado: o campo `releases.totalCount` da API do
  GitHub tem um teto de 1000, afetando 21 dos 1000 repositórios (2,1%) — para
  esses casos, o total de releases coletado é menor que o real (ex.:
  ggml-org/llama.cpp: 1000 coletado vs. 6.894 real). Isso é uma limitação da
  API, não um erro do script de coleta, e deve ser considerado como ressalva
  metodológica na discussão da RQ03. 

## 3. Resultados por RQ

*A ser preenchido no Lab01S03, com valores medianos e contagens por categoria
para cada RQ, após a análise e visualização dos dados coletados.*

## 4. Discussão hipótese vs. resultado

*A ser preenchido no Lab01S03 / Relatório Final, confrontando cada hipótese
informal da seção 1 com os resultados obtidos.*

## 5. Configuração do processo

O grupo utiliza o **GitHub Projects (v2)** vinculado ao repositório, com
cartões representando Issues reais do repositório (não *draft issues*),
atribuídas a um responsável (campo *Assignee*).

**Colunas do board (campo Status):**
`Backlog → To Do → In Progress → Review → Done`

**Limite de WIP:** 4 issues na coluna **In Progress**.

**Justificativa do WIP:** com o trio atual, o limite de 4 issues em andamento
permite que cada integrante mantenha até 1–2 tarefas em progresso
simultaneamente, equilibrando a carga de trabalho sem perder o controle do
fluxo no quadro, considerando o prazo de cada sprint e o volume de demandas do
laboratório.

**Política de acompanhamento:**
- **Backlog:** tarefas previstas, ainda não priorizadas.
- **To Do:** tarefas selecionadas para execução na sprint.
- **In Progress:** tarefas em desenvolvimento, respeitando o limite de 4 issues.
- **Review:** tarefas concluídas aguardando revisão.
- **Done:** tarefas finalizadas e validadas.

Ao final de cada sprint, um snapshot dos itens do Project (via script GraphQL
próprio) é exportado para CSV, servindo de base para os Labs 04 e 05.

**Link do repositório/GitHub Projects:** `<preencher>`

*(Anexar print do board ao final do laboratório, mostrando o fluxo completo
do Lab01 e a política de WIP em uso — a ser incluído no Relatório Final.)*

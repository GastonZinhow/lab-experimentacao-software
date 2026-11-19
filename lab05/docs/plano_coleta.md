# Plano de coleta e regras de ética

> Issue #100. Este documento diz de onde vem cada dado, o que cada fonte devolve, como coletar e quais cuidados o grupo segue. Os relatos das coletas piloto (issues de piloto do GitHub e do GitLab) entram no fim.

**Janela do estudo:** `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z` (UTC).
**Data da verificação das fontes, do robots.txt e dos termos:** 2026-11-19.

## 1. Fontes

### GitHub (githubstatus.com, hospedada no Atlassian Statuspage)

| Fonte | Endereço | O que devolve | Profundidade | robots.txt |
|---|---|---|---|---|
| Feed Atom / RSS | `https://www.githubstatus.com/history.atom` e `/history.rss` | Últimos 25 incidentes: título, link para `/incidents/<código>`, data, texto das atualizações | ~17 dias (25 itens, de 2026-11-02 a 2026-11-19) — **insuficiente sozinho** | Permitido |
| Histórico | `https://www.githubstatus.com/history?page=N` | Lista de incidentes por período | A lista é carregada por JavaScript a partir do `history.json` (linha abaixo) | Permitido |
| **Histórico em JSON** (piloto #101) | `https://www.githubstatus.com/history.json?page=N` | O que a página `/history` carrega: 3 meses por página, com `code`, `name`, `impact` e horário exibido de cada incidente | **Cobre a janela inteira**: página 5 começa em 2025-09-01 | Permitido (não está em `/api/`) |
| Página do incidente | `https://www.githubstatus.com/incidents/<código>` | Título e atualizações com rótulo (Investigating, Update, Monitoring, Resolved) e horário "Posted … UTC" | Qualquer incidente cujo código seja conhecido | Permitido |
| **Incidente em JSON** (piloto #101) | `https://www.githubstatus.com/incidents/<código>.json` | Mesmos campos da API: `created_at, started_at, resolved_at, impact, components, incident_updates` | Qualquer incidente cujo código seja conhecido | Permitido (não está em `/api/`) |
| API pública do Statuspage | `https://www.githubstatus.com/api/v2/incidents.json`, `/api/v2/components.json` | JSON com `id, name, status, created_at, started_at, resolved_at, impact` (`none`/`minor`/`major`/`critical`), `components` e `incident_updates[].affected_components` | Incidentes mais recentes (o tamanho exato da lista não foi confirmado) | **Bloqueado** (`Disallow: /api/`) |
| Relatórios mensais de disponibilidade | `https://github.blog/tag/github-availability-report/` | Um post por mês com os incidentes relevantes: início, fim, causa e correção | Todos os meses da janela (nov/2025 a out/2026), publicados no mês seguinte | Não verificado ainda |

Links dos 12 relatórios da janela (todos em `https://github.blog/news-insights/company-news/`):
`github-availability-report-november-2025/`, `...-december-2025/`, `...-january-2026/`, `...-february-2026/`, `...-march-2026/`, `...-april-2026/`, `...-may-2026/`, `...-june-2026/`, `...-july-2026/`, `...-august-2026/`, `...-september-2026/`, `...-october-2026/`.

Observações:
- A página HTML do incidente **não mostra o impacto nem os componentes afetados**. Esses campos só aparecem no JSON da API.
- Os relatórios mensais trazem só os incidentes que o GitHub considera relevantes; servem para **triangular**, não para substituir a página de status.

### GitLab (status.gitlab.com, hospedada no status.io)

ID da página no status.io: `5b36dc6502d06804c08349f7`.

| Fonte | Endereço | O que devolve | Profundidade | robots.txt |
|---|---|---|---|---|
| Histórico | `https://status.gitlab.com/pages/history/5b36dc6502d06804c08349f7` (páginas `/2`, `/3`, …) | Por incidente: título, rótulo de impacto, componentes, locations, atualizações com horário e estágio (INVESTIGATING, IDENTIFIED, MONITORING, RESOLVED) e link de postmortem | ~20 incidentes por página; página 2 já chega a 2026-08-05 | **Bloqueado** (`Disallow: /pages/*`) |
| Feed RSS | `https://status.gitlab.com/pages/5b36dc6502d06804c08349f7/rss` | Últimos 10 incidentes: título, descrição com atualizações, link, data | ~3 semanas — **insuficiente** | **Bloqueado** (`/pages/*`) |
| Feed iCalendar | `https://status.gitlab.com/pages/5b36dc6502d06804c08349f7/calendar/all.ics` | Um `VEVENT` por incidente ou manutenção: `UID, DTSTART, DTEND, SUMMARY, DESCRIPTION` | Desde 2018 — **cobre a janela inteira em um único arquivo** | **Bloqueado** (`/pages/*`) |
| API pública do status.io | `https://api.status.io/1.0/status/5b36dc6502d06804c08349f7` | Só o **estado atual** dos 23 componentes e incidentes abertos; não tem histórico | Agora | Não foi possível ler (403) |
| Issues de produção | `https://gitlab.com/gitlab-com/gl-infra/production/-/work_items/<n>` | Detalhes técnicos, linha do tempo e causa do incidente (link vem no histórico, campo "Postmortem") | Qualquer incidente com link | Permitido (o robots.txt do gitlab.com bloqueia `/api/v*` e `/*/-/incidents`, mas não `work_items`) |

Observações:
- O histórico não tem campo de duração: o **início** é o horário da primeira atualização e o **fim** é o horário de RESOLVED. No iCal, `DTSTART` e `DTEND` já trazem os dois.
- O iCal mistura incidentes e **manutenções planejadas**; manutenções devem ser filtradas (não são incidentes).
- A escala de impacto do GitLab (Degraded Performance, Partial Service Disruption, Service Disruption) é diferente da do GitHub; a correspondência proposta está em [componentes.md](componentes.md#escala-de-impacto-relacionado).

## 2. robots.txt e termos de uso (verificados em 2026-11-19)

| Site | robots.txt (resumo) |
|---|---|
| www.githubstatus.com | `Disallow: /api/`, `Disallow: /embed/` |
| status.gitlab.com | `Disallow: /pages/*`, `/user/*`, `/dashboard/*`, `/subscriber/*` |
| status.io | Igual ao status.gitlab.com |
| api.status.io | Não foi possível ler (HTTP 403) |
| gitlab.com | Bloqueia `/api/v*`, `/search`, `/*/-/incidents`, entre outros; não bloqueia `work_items` |

Termos de uso:
- **GitHub** (Acceptable Use Policies, seção 7): define *scraping* como extração automatizada por bot ou webcrawler e diz que *scraping* não inclui a coleta pela API. O uso permitido inclui pesquisa; é proibido colocar "carga indevida" nos servidores (seção 4). Os Terms of Service (seção H) proíbem requisições excessivas à API.
- **GitLab** (about.gitlab.com/terms) e **status.io** (status.io/tos): não encontramos regra específica sobre acesso automatizado. O status.io proíbe ações que imponham carga não razoável.

### ⚠️ Decisão pendente: conflito com o robots.txt

As fontes que cobrem os 12 meses com componentes e impacto (**API do githubstatus.com** e **histórico/iCal do status.gitlab.com**) estão em caminhos bloqueados no robots.txt, e o enunciado pede para respeitá-lo. Opções:

| Opção | Como funciona | Prós | Contras |
|---|---|---|---|
| **A. Feeds como assinante** (proposta do grupo) | Baixar uma única vez os feeds e endpoints que as empresas oferecem para consumo por programas (iCal do GitLab; API do Statuspage do GitHub), sem navegar por links | Poucas requisições (dezenas), dados completos, reprodutível | Os caminhos estão no `Disallow`; precisa de aval do professor |
| **B. Só o que o robots.txt permite** | GitHub: `/incidents/<código>` + relatórios mensais; GitLab: issues de produção no gitlab.com | Cumpre o robots.txt à risca | Sem lista completa de incidentes; perde impacto e componentes do GitHub; GitLab só quando há issue de produção |
| **C. Coleta manual** | Integrantes abrem as páginas no navegador e salvam (robots.txt vale para robôs, não para pessoas) | Sem conflito com o robots.txt | Lenta, sujeita a erro de digitação, menos reprodutível |

**Atualização do piloto do GitHub (#101):** para o GitHub **não há mais conflito**. `history.json` e `/incidents/<código>.json` estão fora de `/api/` e trazem impacto e componentes; a coleta do GitHub não precisa da API. O conflito continua só para o GitLab.

**Encaminhamento:** levar ao professor na S01. Até a resposta, os pilotos usam só fontes permitidas (feeds Atom/RSS do GitHub, página `/incidents/<código>` e uma página de issue de produção do GitLab) e **não** acessam os caminhos bloqueados.

## 3. Regras de coleta

1. **No máximo 1 requisição por segundo** no total: um coletor de cada vez, com pausa de pelo menos 1 s entre requisições. Leituras do cache não contam, porque não acessam a internet.
2. **User-Agent genérico**, sem nome nem e-mail: `lab05-coleta/1.0 (pesquisa academica)`.
3. **Cache local:** antes de qualquer requisição, o coletor procura a resposta em `dados/brutos/<plataforma>/`. Se já existe, não acessa a internet. Para baixar de novo, é preciso apagar o arquivo de propósito.
4. **Sem teste de carga** e sem paralelismo.
5. **Sem dados pessoais:** os textos das páginas de status são institucionais. Nomes de pessoas que aparecerem (ex.: autor de issue de produção) não são guardados no `incidentes.csv`.
6. **Erros:** respostas 4xx/5xx são registradas no manifesto e **não** são repetidas em loop; no máximo 1 nova tentativa depois de 60 s.
7. **Datas sempre em UTC**, no formato ISO 8601 (`2026-06-03T14:05:00Z`).

## 4. O que é versionado e o que é gerado

| Caminho | Conteúdo | Versionado? |
|---|---|---|
| `code/dados/brutos/github/` e `code/dados/brutos/gitlab/` | Respostas originais, **sem nenhuma alteração** (JSON, XML, ICS, HTML) | **Sim** — são a evidência; o CI e qualquer pessoa reproduzem a análise sem internet |
| `code/dados/brutos/<plataforma>/manifesto.csv` | Uma linha por requisição: `url,data_hora_utc,status_http,arquivo,sha256` | **Sim** |
| `code/dados/brutos/github/relatorios_mensais.csv` | Incidentes transcritos dos relatórios mensais (triangulação) | **Sim** (é dado de entrada feito à mão) |
| `code/dados/mapa_componentes.csv` | Mapa de componentes (issue #99) | **Sim** |
| `code/dados/processados/` | `incidentes.csv` e intermediários | **Sim**, mas sempre **gerado** pelo comando único (ninguém edita à mão) |
| `code/resultados/` | Tabelas e figuras | **Sim**, gerado pelo comando único |

Regra: o processamento (normalização, análise, dashboard) **nunca acessa a internet**; só a etapa de coleta acessa, e só quando o cache não tem o arquivo.

## 5. Como refazer a coleta

1. Ativar o ambiente e instalar as dependências: `python -m pip install -r lab05/code/requirements.txt`.
2. Conferir se o robots.txt das fontes mudou desde 2026-11-19 (seção 2). Se mudou, parar e avisar o grupo.
3. Rodar a etapa de coleta (`lab05/code/etapas/01_coletar.py`, criada na issue de coleta completa). Sem apagar nada, ela só reaproveita o cache.
4. Conferir o `manifesto.csv`: nenhuma linha com erro sem explicação.
5. Rodar o comando único para gerar `incidentes.csv` e os resultados.

## 6. Relato das coletas piloto

### 6.1 GitHub (issue #101), coletado em 2026-11-19

**Como:** `python -m coleta.github --inicio 2026-10-01T00:00:00Z --fim 2026-10-31T23:59:59Z` (a partir de `lab05/code`). Foram 32 requisições ao githubstatus.com (robots.txt 2×, 5 páginas do histórico, 25 incidentes) e 2 ao github.blog (robots.txt e o relatório de outubro), sempre com ≥ 1,1 s de intervalo. O manifesto tem as 31 respostas salvas; as leituras de robots.txt dessas primeiras execuções não foram anotadas, porque o registro do robots.txt no manifesto foi incluído depois. Tudo está em `code/dados/brutos/github/` (`historico/`, `incidentes/`, `manifesto.csv`).

**Até onde a fonte vai:** o `history.json` cobre os 12 meses. Bastam 5 páginas (a 5ª começa em 2025-09-01). Contagem bruta do histórico, todos os componentes, por mês de início:

| 2025-11 | 2025-12 | 2026-01 | 2026-02 | 2026-03 | 2026-04 | 2026-05 | 2026-06 | 2026-07 | 2026-08 | 2026-09 | 2026-10 | Total |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 17 | 15 | 25 | 37 | 32 | 26 | 23 | 23 | 26 | 27 | 14 | 25 | **290** |

A coleta completa (#104) vai precisar de cerca de 290 requisições de incidente, ou ~6 min a 1 req/s.

**Mês piloto (outubro/2026): 25 incidentes**

| Campo | O que veio |
|---|---|
| Impacto | `minor` 14, `critical` 8, `major` 2, `none` 1 (o `none` é um incidente real, não manutenção; mantido como publicado) |
| Componentes | Actions 12, Pull Requests 7, Issues 6, Webhooks 5, Pages 4, Git Operations 2, API Requests 2, Packages 1, Copilot 1, Copilot AI Model Providers 1 |
| Sem componente | **9 de 25 (36%)**, ex.: "Disruption with some GitHub services", "Elevated 404s for GitHub App s2s tokens in git/API" |
| Duração (22 com duração) | mediana 84,1 min, IQR 43,2–210,6, mínima 9,0, máxima 662,4, média 147,8 |
| Manutenções | nenhuma (o histórico do GitHub não as mistura com incidentes) |

**Conferência com o relatório mensal** ([GitHub Availability Report: October 2026](https://github.blog/news-insights/company-news/github-availability-report-october-2026/), salvo em `brutos/github/relatorios/2026-10.html`): o relatório diz "eight incidents" e lista 8 inícios e durações. **Os 8 estão no piloto**, todos com impacto `critical`, com o início igual até o minuto e a duração com diferença de no máximo 1 min (ex.: 05/10 19:11, 218 min no relatório × 217,7 min no status). Os outros 17 incidentes da página de status (`minor`, `major`, `none`) não aparecem no relatório. Ou seja, **o relatório cobre só os `critical`**, e isso entra na triangulação (#106) e na Q4.

**Problemas encontrados e como o coletor trata:**

1. **`started_at` não é confiável sozinho.** Em 1 incidente (07/10, `djlmxz2zd0j7`), `started_at` foi gravado igual a `resolved_at`, o que daria duração 0. O coletor usa como início o **primeiro registro público**, `min(created_at, started_at)`. Com isso a duração fica 70,5 min, e o relatório oficial diz "1 hour and 11 minutes".
2. **Incidentes retroativos** (3 de 25): publicados depois do fato, só com a atualização `resolved`. Neles, `created_at = resolved_at` é um horário aproximado (às vezes o início, às vezes o fim do evento), e a duração real só está no texto (ex.: "Between 0655 and 0801 UTC"). O coletor marca `retroativo=True` e deixa `fim_utc` e `duracao_min` vazios, sem imputar. Eles contam na frequência e ficam fora da duração. Para a normalização (#105), decidir se a duração será transcrita do texto à mão (com `fonte` indicando isso).
3. **36% sem componente:** os componentes vêm só do campo `components` do JSON. Conferimos `incident_updates[].affected_components` e não há nada a mais. Vários são claramente classificáveis pelo título (Actions, git/API). Para a normalização (#105) e para o mapa (#99): classificar pelo título à mão, com regra escrita, ou deixar fora, e fazer a sensibilidade do [plano de análise](plano_analise.md#4-análises-de-sensibilidade-pré-definidas).
4. A numeração das páginas do histórico muda todo mês (a página 1 é sempre o mês corrente). Por isso as 5 páginas precisam ser baixadas no mesmo dia; o coletor confere se elas são contíguas e para com erro se não forem.
5. Copilot e Copilot AI Model Providers aparecem com impacto `critical`. Pelo mapa (#99) ficam `fora_do_escopo`, mas pesam no total bruto da plataforma.

### 6.2 GitLab (issue #102), coletado em 2026-11-19

**Fonte escolhida: feed iCalendar (`all.ics`).** Os três candidatos (histórico, RSS e iCal) estão em `/pages/*`, bloqueado no robots.txt, e por isso **nenhum robô acessou** esses endereços. Comparação, com base no levantamento da seção 1:

| Fonte | Cobertura | Componentes e impacto | Esforço |
|---|---|---|---|
| RSS | Últimos 10 incidentes (~3 semanas) | Não | 1 arquivo, mas **não cobre a janela** |
| Histórico HTML | Tudo, ~20 incidentes por página | **Sim** | ~7–8 páginas para a janela |
| **iCal** | **Desde 2018, em um arquivo só** | **Não** | 1 arquivo |

O iCal foi escolhido por ser a fonte mais completa no tempo. Seguindo a **opção C** (coleta manual), uma pessoa do grupo abriu o link no navegador e salvou o arquivo sem alterações em `code/dados/brutos/gitlab/all.ics`. O manifesto registra isso com `status_http = manual`, a hora em que foi salvo (2026-11-19T19:58:06Z) e o sha256. O coletor (`python -m coleta.gitlab ...`) **só lê o arquivo local**: sem o arquivo, ele consulta o robots.txt, vê o bloqueio e para com uma mensagem.

**Até onde a fonte vai:** 797 eventos, de 2018-07-02 a 2026-11-03, ou seja, **cobre a janela inteira**. Na janela há 134 eventos: 133 incidentes e 1 manutenção. Contagem por mês de início (todos os componentes):

| 2025-11 | 2025-12 | 2026-01 | 2026-02 | 2026-03 | 2026-04 | 2026-05 | 2026-06 | 2026-07 | 2026-08 | 2026-09 | 2026-10 | Total |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 7 | 7 | 7 | 11 | 20 | 10 | 13 | 11 | 7 | 13 | 11 | 16 | **133** |

**Campos que vêm:** só `UID`, `DTSTAMP` (sempre igual a `DTSTART`), `DTSTART`, `DTEND`, `SUMMARY` e `DESCRIPTION`. Não há `URL`, categoria, componente, impacto nem a lista de atualizações.

**Mês piloto (outubro/2026): 16 incidentes**

| Item | Valor |
|---|---|
| Duração | mediana 208,3 min, IQR 142,4–467,8, mínima 31,9, máxima 3 206 (≈ 53 h), média 669,3 |
| Com link para issue de produção | 11 de 16 (na janela: 78 de 133, 59%) |
| Manutenção excluída | 1 (31/10, Customers Portal) |

**Problemas encontrados e como o coletor trata:**

1. **⚠️ O iCal não tem componentes nem impacto.** Isso afeta o centro do estudo: a comparação é só entre componentes equivalentes (#99), e a Q3 depende do impacto. O coletor deixa `componentes_originais` e `impacto` vazios, sem inventar nada. **Decisão para o grupo (#104/#105):**
   - **(a) recomendado:** salvar à mão (opção C) as ~7–8 páginas do histórico que cobrem a janela, que trazem componente e impacto, e casar com o iCal por título + início;
   - **(b)** classificar o componente pelo título/descrição com regra escrita e conferida por duas pessoas, e deixar o impacto do GitLab ausente;
   - **(c)** aguardar o aval do professor para a opção A.
2. **Manutenções misturadas aos incidentes, sem campo que as diferencie.** Palavras-chave não servem: "Customers Portal in maintenance mode" e "Scheduled jobs not triggering" são incidentes reais. A regra adotada usa o **horário agendado**: começa em hora cheia ou quarto de hora com segundos `00` e termina com segundos `00`. Incidentes começam na hora em que são abertos (ex.: 16:51:44). Nos 797 eventos, a regra marca 63 manutenções. Em 53 delas o texto também fala em manutenção, upgrade ou "will be ..."; as outras 10 foram conferidas uma a uma e são avisos planejados ("Gitaly Storage Node Upgrade", "Change in OAuth grant support", ...). Nenhum evento com palavra de manutenção e horário quebrado era manutenção de verdade.
3. **Durações muito longas:** 14 dos 133 incidentes da janela passam de 24 h (máximo no piloto: 53 h). Provavelmente o incidente fica aberto em "monitoring" depois da recuperação. É ameaça de validade de construto (duração publicada ≠ tempo de recuperação) e reforça o uso de mediana e testes de postos ([plano de análise](plano_analise.md)).
4. **`DESCRIPTION` é um texto só**, às vezes a primeira atualização ("We're investigating..."), às vezes a de resolução ("has been resolved"). Não dá para reconstruir as etapas (investigating → resolved) pelo iCal.
5. **Não há link direto para o incidente:** o `UID` do iCal (ex.: `000-mrwygx`) não é o id usado em `/pages/incident/...`. O campo `url` aponta para o evento dentro do arquivo (`all.ics#<uid>`), e o link da **issue de produção**, quando existe, vai em `issue_producao`.
6. **Quebras de linha:** o arquivo usa CRLF. O `lab05/code/.gitattributes` impede o git de convertê-las, para o sha256 do manifesto continuar valendo.

### 6.3 Comparação inicial dos dois pilotos (outubro/2026, sem filtro de componente)

| | GitHub | GitLab |
|---|---:|---:|
| Incidentes no mês | 25 | 16 |
| Incidentes na janela (12 meses) | 290 | 133 |
| Mediana da duração (min) | 84,1 | 208,3 |
| Componentes e impacto na fonte | Sim (36% sem componente) | **Não** |

*Números brutos, só para planejar a coleta: ainda não há filtro de componentes equivalentes nem validação, então não servem como resultado.*

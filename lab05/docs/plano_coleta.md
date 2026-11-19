# Plano de coleta e regras de ética

> Issue #100. Este documento diz de onde vem cada dado, o que cada fonte devolve, como coletar e quais cuidados o grupo segue. Os relatos das coletas piloto (issues de piloto do GitHub e do GitLab) entram no fim.

**Janela do estudo:** `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z` (UTC).
**Data da verificação das fontes, do robots.txt e dos termos:** 2026-11-19.

## 1. Fontes

### GitHub (githubstatus.com, hospedada no Atlassian Statuspage)

| Fonte | Endereço | O que devolve | Profundidade | robots.txt |
|---|---|---|---|---|
| Feed Atom / RSS | `https://www.githubstatus.com/history.atom` e `/history.rss` | Últimos 25 incidentes: título, link para `/incidents/<código>`, data, texto das atualizações | ~17 dias (25 itens, de 2026-11-02 a 2026-11-19) — **insuficiente sozinho** | Permitido |
| Histórico | `https://www.githubstatus.com/history?page=N` | Lista de incidentes por período | **Desconhecida**: a lista é carregada por JavaScript e não vem no HTML estático | Permitido |
| Página do incidente | `https://www.githubstatus.com/incidents/<código>` | Título e atualizações com rótulo (Investigating, Update, Monitoring, Resolved) e horário "Posted … UTC" | Qualquer incidente cujo código seja conhecido | Permitido |
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

*A preencher nas issues de coleta piloto do GitHub e do GitLab:* quantos incidentes vieram, quais campos, até que data a fonte vai, e problemas encontrados.

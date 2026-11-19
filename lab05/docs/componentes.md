# Componentes equivalentes entre GitHub e GitLab

> Issue #99. O mapa fica em [`lab05/code/dados/mapa_componentes.csv`](../code/dados/mapa_componentes.csv).

A pergunta de pesquisa compara as duas plataformas "considerando apenas componentes equivalentes". Este documento lista todos os componentes das duas páginas de status, explica o critério de equivalência e registra os casos duvidosos.

## Fontes e data

Listas copiadas em **2026-11-19**, com os nomes exatamente como publicados:

| Plataforma | Fonte | Componentes |
|---|---|---|
| GitHub | Página inicial de <https://www.githubstatus.com> (mesma lista do endpoint `/api/v2/components.json`) | 12 |
| GitLab | Página inicial de <https://status.gitlab.com> (mesma lista do endpoint público `https://api.status.io/1.0/status/5b36dc6502d06804c08349f7`) | 23 |

No GitHub nenhum componente é grupo (`group: false`). No GitLab não há grupos visíveis; cada componente tem "locations" (Google Compute Engine, AWS, Digital Ocean, Zendesk, Self-Managed Runner Connectivity), que **não** entram no mapa porque indicam onde roda, e não o que é o serviço.

## Critério de equivalência

Dois componentes são equivalentes quando atendem às três condições:

1. **Mesma função para o usuário:** o usuário percebe a falha da mesma forma (ex.: não consegue dar `git push`, a API responde erro, o pipeline não roda).
2. **Existe nas duas plataformas:** a categoria precisa ter pelo menos um componente de cada lado. Categoria sem par não entra na comparação.
3. **Faz parte do produto principal** (GitHub.com / GitLab.com): sites auxiliares, suporte, portal de cobrança e recursos de IA ficam fora.

## Mapa final

| Categoria | GitHub | GitLab | Entra na comparação? |
|---|---|---|---|
| `git` | Git Operations | Git Operations | Sim |
| `api` | API Requests | API | Sim |
| `web` | Issues; Pull Requests | Website | Sim (ver caso 1) |
| `ci_cd` | Actions | CI/CD; CI/CD - Hosted runners on Linux; CI/CD - Hosted runners on Windows; CI/CD - Hosted runners on macOS; CI/CD - Self-managed runners | Sim (ver casos 2 e 3) |
| `pacotes` | Packages | Package Registry; Container Registry | Sim (ver caso 4) |
| `pages` | Pages | GitLab Pages | Sim |
| `issues_prs` | — | — | **Não usada** (ver caso 1) |
| `fora_do_escopo` | Webhooks; Codespaces; Copilot; Copilot AI Model Providers; Visit www.githubstatus.com for more information | CI/CD - Hosted runners for GitLab community contributions; Background Processing; SAML SSO - GitLab SaaS; GitLab Duo; GitLab agent server for Kubernetes; Canary; GitLab Customers Portal; Support Services; packages.gitlab.com; version.gitlab.com; forum.gitlab.com; docs.gitlab.com | Não |

Conferência: 12 componentes do GitHub + 23 do GitLab = **35 linhas** no CSV, todas mapeadas.

## Casos duvidosos e decisões

### 1. `web` × `issues_prs` (mudança em relação ao combinado)

O GitHub publica **Issues** e **Pull Requests** como componentes separados e **não tem** um componente "Website". O GitLab faz o contrário: tem **Website** e não separa issues nem merge requests (que são parte da interface web).

Se o grupo usasse as duas categorias do combinado, `issues_prs` só existiria no GitHub e `web` só no GitLab, e as duas sairiam da comparação pela regra 2 — perdendo uma parte grande dos incidentes. **Decisão:** Issues e Pull Requests do GitHub e Website do GitLab entram juntos em `web` ("interface web e colaboração"). A categoria `issues_prs` continua na lista do combinado, mas fica sem uso.

Ameaça registrada (construto): `web` do GitLab cobre a interface inteira, enquanto no GitHub só issues e PRs aparecem; uma falha só na página inicial do GitHub pode não ter componente próprio.

### 2. GitHub Actions × GitLab CI/CD e runners

Actions é descrito como "Workflows, Compute and Orchestration for GitHub Actions", ou seja, orquestração **e** execução (runners hospedados). No GitLab isso aparece dividido em CI/CD (orquestração) e um componente por tipo de runner hospedado. **Decisão:** todos entram em `ci_cd`, e um incidente conta **uma vez** na categoria, mesmo que marque vários runners (ver regra abaixo).

### 3. Runners: self-managed e community contributions

- **CI/CD - Self-managed runners** (location "Self-Managed Runner Connectivity") mede a conexão de runners do próprio cliente com o GitLab.com. No GitHub, runners self-hosted dependem da orquestração do Actions, que está dentro do componente Actions. **Decisão:** entra em `ci_cd`. **Sensibilidade:** repetir a análise de `ci_cd` sem esse componente.
- **CI/CD - Hosted runners for GitLab community contributions** atende a quem contribui com o próprio projeto do GitLab, um uso interno sem paralelo no GitHub. **Decisão:** `fora_do_escopo`.

### 4. Pacotes e registro de contêineres

GitHub Packages inclui o Container registry (ghcr.io), por isso Package Registry e Container Registry do GitLab entram juntos em `pacotes`. Atenção: **packages.gitlab.com** é o repositório de instaladores do próprio GitLab (Omnibus), não o registro de pacotes dos usuários, por isso fica fora.

### 5. Webhooks × Background Processing

O componente Webhooks do GitHub não tem par direto. No GitLab, webhooks são entregues por processamento assíncrono (Background Processing), mas esse componente também cobre outras tarefas internas (e-mails, mirrors, etc.). A equivalência seria fraca. **Decisão:** os dois ficam `fora_do_escopo`.

### 6. IA, ambientes e serviços auxiliares

- **Copilot**, **Copilot AI Model Providers** e **GitLab Duo**: recursos de IA, com modelos de terceiros e dinâmica própria (os relatórios do GitHub de 2026 citam muitos incidentes de modelos). Ficam fora para não misturar a confiabilidade da plataforma com a dos provedores de IA.
- **Codespaces** e **GitLab agent server for Kubernetes**: produtos à parte, sem par.
- **SAML SSO**: o GitHub não publica autenticação como componente.
- **Canary**: ambiente de pré-produção do GitLab, sem par.
- **Customers Portal, Support Services, version, forum e docs**: serviços auxiliares, fora do produto principal.
- **"Visit www.githubstatus.com for more information"**: não é um serviço, é um item de texto publicado como componente.

## Regra para incidente com vários componentes

1. Cada componente afetado é traduzido para a sua categoria pelo mapa.
2. As categorias repetidas são removidas: **um incidente conta uma vez por categoria**. Ex.: um incidente do GitLab que marca "CI/CD" e "CI/CD - Hosted runners on Linux" conta uma vez em `ci_cd`.
3. Um incidente que afeta categorias diferentes conta uma vez em cada uma na análise **por categoria**. Ex.: Git Operations + API conta em `git` e em `api`.
4. Na análise **geral** (total da plataforma), o incidente conta **uma vez**, desde que afete pelo menos uma categoria comparável.
5. Incidente que só afeta componentes `fora_do_escopo` não entra na comparação (mas continua no `incidentes.csv`, para a validação e a descrição).
6. Incidente sem nenhum componente informado recebe `sem_componente` e é contado à parte na validação. Não entra na comparação por categoria.

**Consequência para o formato comum:** a coluna `componente_equivalente` do `incidentes.csv` pode ter mais de uma categoria, separadas por `;` e sem repetição (ex.: `api;git`), do mesmo jeito que `componentes_originais`.

## Cuidados para a coleta (avisar o papel B)

- **Nomes que mudaram durante a janela:** a lista é de 2026-11-19. Componentes antigos ou renomeados entre 2025-11 e 2026-10 (ex.: o filtro do histórico do GitLab ainda mostra a location "Azure") podem aparecer nos incidentes. A normalização deve **listar todo nome que não está no mapa**, e o mapa é atualizado com uma nova linha.
- **Componentes nos incidentes do GitHub:** a página HTML de um incidente (`/incidents/<código>`) não mostra os componentes afetados; eles vêm no campo `components`/`affected_components` do JSON. A coleta piloto precisa confirmar de onde virá essa informação.

## Escala de impacto (relacionado)

As duas páginas usam escalas diferentes, ambas **ordinais**:

| GitHub (`impact`) | GitLab (rótulo do histórico) |
|---|---|
| none | Operational |
| minor | Degraded Performance |
| major | Partial Service Disruption |
| critical | Service Disruption |

Esta correspondência é uma **proposta** para a análise de sensibilidade ("só incidentes graves" = `major`/`critical` × Partial/Service Disruption). Ela ainda precisa ser validada com os dados da coleta piloto.

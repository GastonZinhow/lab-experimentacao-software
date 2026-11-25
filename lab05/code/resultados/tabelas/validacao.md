# Validação dos incidentes

> Gerado por `etapas/02_normalizar.py` (issue #105). Não edite à mão: rode o comando único.

Janela: `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z` (UTC). Entrada: `dados/brutos/` (sem internet).

## Resumo

| Item | GitHub | GitLab |
|---|---:|---:|
| Registros nos dados brutos (arquivo inteiro, sem manutenções) | 290 | 734 |
| Incidentes no `incidentes.csv` (início na janela) | 290 | 133 |
| Com duração | 273 | 133 |
| Sem horário de fim (sem duração) | 17 | 0 |
| … dos quais retroativos | 17 | 0 |
| Terminam depois da janela (duração inteira mantida) | 0 | 0 |
| Componente publicado | 176 | 0 |
| Componente pelo título | 54 | 127 |
| `sem_componente` | 60 | 6 |
| Sem impacto publicado | 0 | 133 |

## Verificações finais do `incidentes.csv`

Ids únicos por plataforma, `inicio_utc` dentro da janela, `fim_utc > inicio_utc`, `duracao_min` positiva e presente só quando há `fim_utc`, plataforma válida.

**Resultado:** nenhum problema.

## O que foi encontrado e como foi tratado

### Ids repetidos: 0

Regra: fica o primeiro registro; os outros são descartados.

Nenhum.

### `fim_utc <= inicio_utc`: 0

Regra: o horário de fim é descartado (fica sem duração), o incidente continua na frequência.

Nenhum.

### Sem horário de fim: 17

Regra: entram na frequência, ficam fora da duração; nenhuma duração é imputada. No GitHub são os incidentes **retroativos** (publicados depois do fato, só com a atualização `resolved`): o Statuspage grava um horário aproximado e a duração real só aparece no texto. Sensibilidade 1 do plano de análise: frequência sem eles.

| Plataforma | Id | Início (UTC) | Fim (UTC) | Título | Categoria |
|---|---|---|---|---|---|
| github | 0xpyl7hs9hm6 | 2025-11-04T22:00:00Z | — | Incident With GitHub Enterprise Importer | sem_componente |
| github | 11n51rf8tf27 | 2026-05-28T19:07:00Z | — | Elevated error rates across multiple services | sem_componente |
| github | 594m87r8sw13 | 2026-07-24T11:00:00Z | — | Incident With Blocked GitHub.com Traffic | web |
| github | 6yk962mhlr3h | 2026-10-13T20:30:00Z | — | [Retroactive] Actions workflow run logs delayed | ci_cd |
| github | 8jx0t5c136x2 | 2026-03-10T15:00:00Z | — | Incident With Webhooks | fora_do_escopo |
| github | 9vyj2jwsk8by | 2026-03-27T05:00:00Z | — | Incident with Copilot | fora_do_escopo |
| github | dnslv7xdl4fj | 2026-10-27T08:00:00Z | — | Elevated 404s for GitHub App s2s tokens in git/API | api;git |
| github | dqn46wtvbdzv | 2026-10-01T02:00:00Z | — | [Retroactive] Actions workflow run failures after deployment gate approvals | ci_cd |
| github | jpd6l1jq0r54 | 2026-06-08T15:00:00Z | — | Degraded availability for GitHub.com, GraphQL API, and Webhooks UI/API | api;fora_do_escopo |
| github | k95d6yq4tmly | 2025-12-03T22:30:00Z | — | Webhooks delivery degradation | fora_do_escopo |
| github | kn7gv3tlfc54 | 2026-06-17T19:00:00Z | — | Incident With Webhooks | fora_do_escopo |
| github | lctp4bzd37h2 | 2025-12-16T12:00:00Z | — | Incident With Copilot | fora_do_escopo |
| github | sq20c7lrwjrp | 2026-01-14T18:00:00Z | — | [Retroactive] Incident with GitHub Copilot (GPT-5 model) | fora_do_escopo |
| github | t5mch8tlq6vl | 2026-05-15T01:30:00Z | — | [Retroactive] Incident with GitHub.com | web |
| github | tm84vy58jq0h | 2026-05-25T09:02:00Z | — | Elevated rate of Git push errors | git |
| github | wms44hv62t3p | 2026-08-21T14:00:00Z | — | Degraded Git Operations over SSH | git |
| github | ykb44v068g8v | 2026-05-19T05:30:00Z | — | Incident with Copilot | fora_do_escopo |

### Começaram antes da janela e terminaram dentro: 0

Regra: **ficam fora** da amostra principal (o critério é o início). Só contam aqui, para a sensibilidade 4 do plano de análise.

Nenhum.

### Começaram na janela e terminaram depois: 0

Regra: **entram com a duração inteira**, sem cortar em `2026-10-31T23:59:59Z` (cortar encurtaria artificialmente o tempo de recuperação). Marcados em `termina_apos_janela`.

Nenhum.

Registros com início depois da janela (descartados): GitHub 0, GitLab 2.

### Componentes sem linha no `mapa_componentes.csv`

Nenhum: todos os componentes publicados estão no `mapa_componentes.csv`.

### Incidentes classificados pelo título: 181

Incidentes publicados **sem componente** (o iCal do GitLab nunca traz componente; no GitHub, parte dos incidentes vem sem) recebem a categoria pelas regras escritas em `dados/regras_titulo.csv` (opção (b) do plano de coleta, seção 6.2). Ficam com `origem_componente = titulo`, para a sensibilidade 2 do plano de análise (com e sem esses incidentes). A lista completa está no `incidentes.csv`; a conferência por outra pessoa do grupo é feita sobre ela.

### `sem_componente`: 66

Nem componente publicado nem regra de título. Ficam no `incidentes.csv` e fora da comparação por categoria.

| Plataforma | Id | Início (UTC) | Fim (UTC) | Título | Categoria |
|---|---|---|---|---|---|
| github | 00h92ct3ggvv | 2026-04-01T16:06:11Z | 2026-04-01T16:10:17Z | GitHub audit logs are unavailable | sem_componente |
| github | 0rkjjs2ssp7z | 2026-06-28T17:50:30Z | 2026-06-28T20:55:58Z | Disruption with some GitHub services | sem_componente |
| github | 0xpyl7hs9hm6 | 2025-11-04T22:00:00Z | — | Incident With GitHub Enterprise Importer | sem_componente |
| github | 11n51rf8tf27 | 2026-05-28T19:07:00Z | — | Elevated error rates across multiple services | sem_componente |
| github | 1dk955gg3bvz | 2026-09-24T16:51:32Z | 2026-09-24T20:41:12Z | Disruption with billing information updates | sem_componente |
| github | 1ghdqdbyyjmt | 2026-04-13T16:41:27Z | 2026-04-13T17:40:09Z | Disruption with some GitHub services | sem_componente |
| github | 2kxnqcxcrr7f | 2026-10-05T23:47:45Z | 2026-10-06T01:32:43Z | Disruption with some GitHub services | sem_componente |
| github | 2rqwxl8y7m0j | 2026-04-09T16:20:03Z | 2026-04-09T20:36:52Z | Disruption with some GitHub services | sem_componente |
| github | 2yb2tvwny50l | 2026-03-31T13:47:46Z | 2026-03-31T15:10:22Z | Issues with metered billing report generation | sem_componente |
| github | 3bmqzkljz8s3 | 2025-11-17T16:52:18Z | 2025-11-17T19:08:41Z | Disruption with some GitHub services | sem_componente |
| github | 3hdjjpkvz895 | 2025-12-05T18:38:55Z | 2025-12-05T22:20:19Z | Team synchronization is experiencing delays for non enterprise managed users | sem_componente |
| github | 4843jm0lsls6 | 2026-06-06T15:31:32Z | 2026-06-06T18:49:15Z | EU Network Maintenance | sem_componente |
| github | 54hndjxft5bx | 2026-02-09T15:54:52Z | 2026-02-09T19:29:45Z | Notifications are delayed | sem_componente |
| github | 5bn0vk444m1w | 2026-08-26T23:37:20Z | 2026-08-27T19:44:08Z | Disruption with GitHub Billing | sem_componente |
| github | 5txsjlt9299p | 2026-02-12T10:38:35Z | 2026-02-12T11:12:16Z | Disruption with some GitHub services | sem_componente |
| github | 5wdgxw2rvbt3 | 2026-06-01T15:17:09Z | 2026-06-02T00:17:58Z | Delays with Code Scanning and Billing | sem_componente |
| github | 71y513kjvbzh | 2026-10-23T14:58:48Z | 2026-10-23T18:51:24Z | Disruption with Dependabot Alerts | sem_componente |
| github | 7vwbds3snh28 | 2026-03-22T09:08:38Z | 2026-03-22T10:02:05Z | Disruption with some GitHub services | sem_componente |
| github | 7ylfn6fnwgrq | 2026-02-11T18:58:10Z | 2026-02-12T00:59:23Z | Disruption with some GitHub services | sem_componente |
| github | 8bcsk6c4prjl | 2026-01-09T17:53:59Z | 2026-01-10T02:33:18Z | Disruption with some GitHub services | sem_componente |
| github | 8wxkrmhm6744 | 2026-05-13T14:41:28Z | 2026-05-13T16:03:53Z | Incident with CodeQL | sem_componente |
| github | b4235qyfzx2z | 2026-04-21T15:03:21Z | 2026-04-22T01:24:13Z | Disruption with projects service | sem_componente |
| github | bk7zgdcq7s9t | 2026-09-15T19:11:31Z | 2026-09-15T20:00:50Z | Disruption with some GitHub services | sem_componente |
| github | bnvg7qml7krl | 2026-04-09T04:42:06Z | 2026-04-09T04:57:17Z | Disruption with GitHub notifications | sem_componente |
| github | br7kz68t38cl | 2025-11-12T22:26:29Z | 2025-11-12T23:04:23Z | Disruption with some GitHub services | sem_componente |
| github | c8466lzvnmsv | 2026-10-01T13:37:33Z | 2026-10-01T13:57:59Z | Elevated request latency | sem_componente |
| github | cg3wwz9dw5dg | 2025-11-20T18:04:25Z | 2025-11-20T19:24:33Z | Disruption with some GitHub services | sem_componente |
| github | d35pngcy6sb9 | 2026-07-16T09:13:51Z | 2026-07-16T12:20:56Z | Disruption with some GitHub services | sem_componente |
| github | d5t56pdnjxhd | 2026-01-01T21:24:39Z | 2026-01-01T22:31:49Z | Disruption with some GitHub services | sem_componente |
| github | d96l71t3h63k | 2026-04-02T17:49:36Z | 2026-04-02T21:48:43Z | Disruption with some GitHub services | sem_componente |
| github | d9b4dsg8d0r6 | 2026-06-15T18:32:02Z | 2026-06-15T19:10:15Z | Multiple services have elevated errors and endpoint failures when checking feature flags | sem_componente |
| github | g9mdtzd4rt72 | 2026-02-02T17:41:19Z | 2026-02-02T18:46:39Z | Disruption with some GitHub services | sem_componente |
| github | gldshbt8tvdg | 2026-04-14T01:57:55Z | 2026-04-14T06:08:16Z | Disruption with some GitHub services | sem_componente |
| github | hcbtzksccj2f | 2026-08-26T15:09:03Z | 2026-08-26T16:07:52Z | Disruption with some GitHub services | sem_componente |
| github | j240y90h4g0r | 2026-06-03T03:13:28Z | 2026-06-03T06:46:59Z | Disruption with some GitHub services | sem_componente |
| github | jn8kcmg5ydch | 2026-02-23T19:59:55Z | 2026-02-24T00:46:29Z | Code search experiencing degraded performance | sem_componente |
| github | k5z4d1v1tqmt | 2026-05-23T16:00:55Z | 2026-05-23T19:32:26Z | Intermittent errors with app installation token authentication | sem_componente |
| github | kv1lzpgzr9yp | 2026-02-27T03:08:23Z | 2026-02-27T06:04:02Z | Code view fails to load when content contains some non-ASCII characters | sem_componente |
| github | l0brgg302bf5 | 2025-11-12T14:23:54Z | 2025-11-12T17:39:40Z | Delay in notification deliveries | sem_componente |
| github | lvf95rlzkxrr | 2026-02-13T22:30:40Z | 2026-02-13T22:58:42Z | Disruption with some GitHub services regarding file upload | sem_componente |
| github | lw6j95nyw3py | 2026-03-12T01:54:18Z | 2026-03-12T02:45:55Z | Disruption with some GitHub services | sem_componente |
| github | lyyfm7j4pkgl | 2026-10-30T20:59:14Z | 2026-10-30T23:29:06Z | Incident with Dependabot | sem_componente |
| github | m7pgzw1wlfq7 | 2026-04-20T13:28:48Z | 2026-04-21T05:04:56Z | Partial degradation for code scanning default setup and for code quality | sem_componente |
| github | n4fpndtvbmwb | 2025-12-08T21:28:27Z | 2025-12-08T22:33:23Z | Disruption with some GitHub services | sem_componente |
| github | n8htfgj6wv3t | 2026-05-06T11:21:28Z | 2026-05-06T11:59:51Z | Disruption with some GitHub services | sem_componente |
| github | nlmpksjb2ll7 | 2026-03-05T01:13:44Z | 2026-03-05T01:30:37Z | Disruption with some GitHub services | sem_componente |
| github | pf25whpq58hh | 2026-08-13T16:21:33Z | 2026-08-13T18:27:54Z | Disruption with GHEC Team Sync | sem_componente |
| github | ph5nns5y4gxj | 2026-07-20T00:25:09Z | 2026-07-20T01:46:02Z | Disruption with some GitHub services | sem_componente |
| github | ql19qqqmdf99 | 2025-11-17T23:01:06Z | 2025-11-18T00:10:50Z | Disruption with some GitHub services | sem_componente |
| github | s19bth7wzkf7 | 2026-08-10T18:02:04Z | 2026-08-10T18:46:22Z | Disruption with creation of fine grained personal access tokens | sem_componente |
| github | tf25qs8wdw5h | 2026-06-03T19:42:55Z | 2026-06-04T04:11:59Z | Disruption with some GitHub services | sem_componente |
| github | v0b3bpsyvqtk | 2026-06-27T14:02:52Z | 2026-06-27T20:33:11Z | Disruption with some GitHub services | sem_componente |
| github | vq183jvj6vrw | 2026-04-27T16:48:18Z | 2026-04-27T19:02:59Z | Disruption with some GitHub services | sem_componente |
| github | xs2p9z3b73r3 | 2026-04-01T15:02:54Z | 2026-04-01T23:45:45Z | Disruption with GitHub's code search | sem_componente |
| github | y7kzv1ps2qrm | 2026-02-12T18:36:09Z | 2026-02-12T20:34:55Z | Disruption with some GitHub services | sem_componente |
| github | z7gsp4wd05c5 | 2026-03-24T16:59:27Z | 2026-03-24T19:51:16Z | Teams Github Notifications App is down | sem_componente |
| github | zltcsbhqmvqq | 2026-01-16T23:53:43Z | 2026-01-17T02:54:51Z | Disruption with some GitHub services | sem_componente |
| github | zn1t56bfxdzg | 2026-04-09T09:50:21Z | 2026-04-09T10:15:37Z | Disruption with some GitHub services | sem_componente |
| github | zwlfnp5z0r4s | 2026-01-13T22:21:12Z | 2026-01-14T00:18:22Z | Disruption with some GitHub services | sem_componente |
| github | zzl9nl31lb35 | 2025-11-19T16:13:21Z | 2025-11-21T00:22:14Z | Disruption with some GitHub services | sem_componente |
| gitlab | 000-8j2kvx | 2025-11-08T01:14:45Z | 2025-11-10T07:14:55Z | Unable to confirm secondary email address | sem_componente |
| gitlab | 000-z6wdn6 | 2025-11-11T14:08:56Z | 2025-11-12T16:05:46Z | Docker API version mismatch resulting in blocked deployments | sem_componente |
| gitlab | 0000jjph5s | 2026-03-11T15:56:19Z | 2026-03-11T20:05:19Z | We are experiencing 5XX errors | sem_componente |
| gitlab | 0000ncgk5e | 2026-08-17T07:24:40Z | 2026-08-17T13:56:42Z | Project and Group Deletions Delayed | sem_componente |
| gitlab | 000-caegkn | 2026-09-21T12:10:07Z | 2026-09-21T20:18:05Z | Performance degradation in APAC/Singapore | sem_componente |
| gitlab | 000-ebzcdw | 2026-09-24T13:48:00Z | 2026-09-24T20:50:34Z | 500 errors while accessing projects | sem_componente |

## Incidentes por categoria

Um incidente com várias categorias conta uma vez em cada (regra de `componentes.md`).

| Categoria | GitHub (componente publicado) | GitHub (sem componente publicado) | GitLab (componente publicado) | GitLab (sem componente publicado) |
|---|---:|---:|---:|---:|
| `git` | 19 | 6 | 0 | 14 |
| `api` | 17 | 4 | 0 | 2 |
| `web` | 49 | 5 | 0 | 36 |
| `ci_cd` | 70 | 9 | 0 | 37 |
| `pacotes` | 10 | 0 | 0 | 2 |
| `pages` | 22 | 0 | 0 | 0 |
| `fora_do_escopo` | 88 | 33 | 0 | 42 |
| `sem_componente` | 0 | 60 | 0 | 6 |

## Limitações que continuam

- O GitLab não tem impacto no iCal: `impacto` fica vazio em todos os incidentes do GitLab.
- A categoria pelo título é uma inferência; a escrita do título varia entre as empresas.

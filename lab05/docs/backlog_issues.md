# Backlog de issues do Lab05

Cada issue abaixo está pronta para copiar no GitHub: o título é o `###` e o corpo é tudo até o próximo `---`.
O bloco **Combinado do grupo** é igual em todas.

Papéis (seção 6 do enunciado), preencher com os nomes:

- **A — Planejamento e Método:** `<nome>`
- **B — Instrumentação e Operação:** `<nome>`
- **C — Análise e Impacto:** `<nome>`

| # | Sprint | Título | Papel |
|---|---|---|---|
| 1 | S01 | Criar comando único, CI e Kanban do Lab05 | B |
| 2 | S01 | Comprovar os três critérios do GitHub e do GitLab | A |
| 3 | S01 | Pergunta de pesquisa, GQM e hipóteses | A |
| 4 | S01 | Primeira versão das 7 categorias de pesquisa | A |
| 5 | S01 | Mapear componentes equivalentes entre GitHub e GitLab | A |
| 6 | S01 | Plano de coleta e regras de ética | B |
| 7 | S01 | Coleta piloto do GitHub Status | B |
| 8 | S01 | Coleta piloto do GitLab Status | B |
| 9 | S01 | Plano de análise e estrutura do dashboard | C |
| 10 | S02 | Coleta completa dos 12 meses | B |
| 11 | S02 | Normalizar e validar os incidentes | B |
| 12 | S02 | Triangulação com os relatórios oficiais de incidentes | A |
| 13 | S02 | Estatística descritiva de frequência e tempo de recuperação | C |
| 14 | S02 | Testes de hipótese e tamanho do efeito | C |
| 15 | S02 | Ameaças à validade | A |
| 16 | S02 | Seções de dados e resultados no dashboard | C |
| 17 | S03 | Disponibilidade calculada × disponibilidade oficial | C |
| 18 | S03 | Estimativa de impacto para usuários e empresas | C |
| 19 | S03 | Revisar e justificar as 7 categorias | A |
| 20 | S03 | Conclusões e limitações | A |
| 21 | S03 | Reaproveitamento dos labs anteriores | B |
| 22 | S03 | Rascunho do documento e da apresentação | B |
| 23 | Final | Documento final | Todos |
| 24 | Final | Apresentação e respostas das perguntas orais | Todos |

---

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.

---

### [Lab05S01] Criar comando único, CI e Kanban do Lab05

## Objetivo
Deixar o Lab05 pronto para o grupo trabalhar em paralelo: comando único, testes no CI e quadro do GitHub Projects.

## Passos
- [ ] Criar `lab05/code/run_all.py` no mesmo formato do Lab04 (descobre `etapas/NN_nome.py` e chama `main()`), com `--verificar-reprodutibilidade`
- [ ] Adicionar o job `test-lab05` em `.github/workflows/tests.yml` (pytest + comando único)
- [ ] Criar o `exemplo_incidentes.csv` com poucas linhas inventadas no formato comum
- [ ] Criar os milestones Lab05S01, Lab05S02, Lab05S03 e Lab05 Final e colocar todas as issues no Projects
- [ ] Preencher o link do repositório/GitHub Projects no enunciado (`lab05/docs/05 - Experimento em software real.md`)
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- `python lab05/code/run_all.py` roda sem erro mesmo sem nenhuma etapa pronta
- CI verde no push

## Dependências
Nenhuma com outra pessoa.

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S01)

---

### [Lab05S01] Comprovar os três critérios do GitHub e do GitLab

## Objetivo
Mostrar, com números e fontes, que GitHub.com e GitLab.com são reais, estão em operação e têm alto impacto (seção 2a do enunciado).

## Passos
- [ ] Criar `lab05/docs/criterios.md` com uma tabela por plataforma: critério, evidência, número, fonte (link) e data de acesso
- [ ] **Real:** site oficial, documentação e página de status
- [ ] **Em operação:** atividade recente da página de status, data da última versão do GitLab, empresas e órgãos que usam cada um
- [ ] **Alto impacto:** nº de desenvolvedores/usuários, organizações, repositórios ou projetos, preferencialmente de fonte oficial (ex.: Octoverse, relatórios anuais do GitLab) e do Stack Overflow Developer Survey
- [ ] Registrar o contexto de 2026 do GitHub (problemas de disponibilidade, migração para o Azure) com o link do The Register e do blog do GitHub
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Todo número tem link e data de acesso; nada sem fonte

## Dependências
Nenhuma com outra pessoa.

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S01)

---

### [Lab05S01] Pergunta de pesquisa, GQM e hipóteses

## Objetivo
Transformar a pergunta "o GitHub e o GitLab diferem na frequência de incidentes e no tempo de recuperação?" em objetivo, perguntas, métricas e hipóteses testáveis.

## Passos
- [ ] Criar `lab05/docs/gqm.md` com o objetivo no template de Basili (analisar / com o propósito de / com respeito a / do ponto de vista de / no contexto de)
- [ ] Definir as perguntas (ex.: Q1 frequência, Q2 tempo de recuperação, Q3 gravidade, Q4 diferença entre medição oficial e independente)
- [ ] Definir cada métrica com entidade (produto, processo ou recurso), atributo interno/externo, medida direta ou derivada e **escala**: nº de incidentes por mês, duração (min) como proxy de MTTR, tempo entre incidentes (MTBF), proporção por impacto
- [ ] Escrever H₀ e H₁ para frequência e para tempo de recuperação
- [ ] Discutir se as métricas podem ser "jogadas" (Goodhart, Campbell, McNamara): quem decide abrir e fechar um incidente na página de status?
- [ ] Atualizar `lab05/docs/proposta.md`
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Cada métrica do GQM aparece no formato comum ou é derivada dele

## Dependências
Nenhuma com outra pessoa.

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S01)

---

### [Lab05S01] Primeira versão das 7 categorias de pesquisa

## Objetivo
Classificar o estudo nas 7 categorias da Aula 8, com uma justificativa curta para cada.

## Passos
- [ ] Criar `lab05/docs/categorias.md` com: natureza, objetivos, abordagem, procedimentos, tempo, controle e nível de evidência
- [ ] Justificar cada uma pensando no que foi feito de fato (análise de dados de operação, observacional, retrospectivo, sem controle sobre os tratamentos)
- [ ] Explicar o que isso significa para a força da evidência (associação, não causa)
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Primeira versão pronta para a S01; a versão revisada fica para a S03

## Dependências
Nenhuma com outra pessoa.

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S01)

---

### [Lab05S01] Mapear componentes equivalentes entre GitHub e GitLab

## Objetivo
Definir quais componentes das duas páginas de status são comparáveis, para que a comparação seja justa ("considerando apenas componentes equivalentes").

## Passos
- [ ] Listar todos os componentes das duas páginas de status
- [ ] Criar `lab05/code/dados/mapa_componentes.csv` com as categorias do combinado (`git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`)
- [ ] Documentar o critério de equivalência e os casos duvidosos em `lab05/docs/componentes.md` (ex.: GitHub Actions × GitLab CI/CD runners; Copilot fica fora do escopo)
- [ ] Definir a regra para incidente que afeta vários componentes (conta uma vez por categoria)
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Todo componente das duas páginas aparece no mapa, inclusive os que ficam fora do escopo

## Dependências
Nenhuma com outra pessoa (os nomes dos componentes podem ser copiados das páginas; a coleta piloto confirma depois).

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S01)

---

### [Lab05S01] Plano de coleta e regras de ética

## Objetivo
Documentar de onde vem cada dado, como ele é coletado e quais cuidados de ética o grupo segue.

## Passos
- [ ] Criar `lab05/docs/plano_coleta.md` com as fontes (API, histórico, RSS/iCal, relatórios mensais do blog do GitHub, issues de produção do GitLab) e o que cada uma devolve
- [ ] Conferir o robots.txt e os termos de uso das duas páginas e registrar a data
- [ ] Definir limite de 1 req/s, User-Agent genérico e cache local para não repetir requisições
- [ ] Definir o que é versionado (dados brutos) e o que é gerado (processados)
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Qualquer pessoa do grupo consegue refazer a coleta lendo só esse documento

## Dependências
Nenhuma com outra pessoa.

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S01)

---

### [Lab05S01] Coleta piloto do GitHub Status

## Objetivo
Coletar uma amostra do histórico do githubstatus.com e descobrir até onde é possível voltar no tempo.

## Passos
- [ ] Criar `lab05/code/coleta/github.py` com `coletar(inicio, fim)` respeitando o combinado (1 req/s, cache, dados brutos)
- [ ] Coletar um mês de piloto e salvar em `dados/brutos/github/`
- [ ] Verificar se a fonte cobre os 12 meses da janela (a API pública pode devolver só os incidentes mais recentes; nesse caso usar o histórico paginado)
- [ ] Conferir o mês do piloto contra o relatório mensal de disponibilidade do blog
- [ ] Teste em `tests/` com uma resposta salva (sem internet)
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Relato curto no `plano_coleta.md`: quantos incidentes, quais campos vêm, até que data a fonte vai, problemas encontrados

## Dependências
Nenhuma com outra pessoa.

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S01)

---

### [Lab05S01] Coleta piloto do GitLab Status

## Objetivo
Coletar uma amostra do histórico do status.gitlab.com e descobrir até onde é possível voltar no tempo.

## Passos
- [ ] Criar `lab05/code/coleta/gitlab.py` com `coletar(inicio, fim)` respeitando o combinado
- [ ] Testar o histórico e os feeds RSS e iCalendar e escolher a fonte mais completa
- [ ] Coletar um mês de piloto e salvar em `dados/brutos/gitlab/`
- [ ] Verificar se a fonte cobre os 12 meses da janela
- [ ] Guardar o link da issue de produção de cada incidente, quando existir
- [ ] Teste em `tests/` com uma resposta salva (sem internet)
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Relato curto no `plano_coleta.md`, no mesmo formato do piloto do GitHub

## Dependências
Nenhuma com outra pessoa.

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S01)

---

### [Lab05S01] Plano de análise e estrutura do dashboard

## Objetivo
Definir como os dados serão analisados e criar o dashboard que recebe as seções de todo o grupo sem que ninguém precise mexer no arquivo principal.

## Passos
- [ ] Criar `lab05/docs/plano_analise.md`: descritiva (mediana, IQR, por escala), testes previstos (ex.: Mann-Whitney para duração, comparação de taxas de Poisson ou teste pareado por mês para frequência), tamanho do efeito (Cliff's delta, razão de taxas com IC 95% por bootstrap) e α
- [ ] Justificar a escolha dos testes pela escala e pela distribuição esperada (reaproveitar o raciocínio do Lab04)
- [ ] Criar `lab05/code/dashboard.py` no formato do Lab04, carregando `secoes/` na ordem: 1 Software, 2 Pergunta e método, 3 Dados e coleta, 4 Frequência, 5 Tempo de recuperação, 6 Triangulação, 7 Impacto, 8 Ameaças e conclusão
- [ ] Mostrar aviso de "em construção" nas seções que ainda não existem, sem quebrar a página
- [ ] Criar a seção 1 como exemplo do formato, em `secoes/secao_1_software.py`
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Dashboard abre mesmo sem nenhuma outra seção pronta

## Dependências
Nenhuma com outra pessoa.

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S01)

---

### [Lab05S02] Coleta completa dos 12 meses

## Objetivo
Coletar todos os incidentes das duas plataformas na janela combinada e versionar os dados brutos.

## Passos
- [ ] Criar `etapas/01_coletar.py` que chama os dois coletores (com opção de usar só o cache, para o CI não acessar a internet)
- [ ] Coletar `2025-11-01` a `2026-10-31` nas duas plataformas
- [ ] Versionar `dados/brutos/` e registrar a data da coleta
- [ ] Atualizar `plano_coleta.md` com o total de incidentes por plataforma e mês
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Rodar o comando único sem internet reproduz os mesmos arquivos

## Dependências
Coletas piloto do GitHub e do GitLab.

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S02)

---

### [Lab05S02] Normalizar e validar os incidentes

## Objetivo
Transformar os dados brutos no formato comum (`incidentes.csv`) e garantir que estão corretos.

## Passos
- [ ] Criar `etapas/02_normalizar.py` que gera `dados/processados/incidentes.csv` aplicando o `mapa_componentes.csv`
- [ ] Validar: ids únicos, `fim_utc > inicio_utc`, datas dentro da janela, incidentes sem fim, componentes sem mapeamento
- [ ] Definir e documentar o tratamento de incidentes que cruzam a borda da janela e de incidentes sem horário de fim
- [ ] Gerar `resultados/tabelas/validacao.md` com o que foi encontrado e corrigido
- [ ] Testes com casos de borda em `tests/`
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- `incidentes.csv` pronto para a análise, com relatório de validação

## Dependências
Coleta completa e mapa de componentes. Até lá, usar o `exemplo_incidentes.csv`.

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S02)

---

### [Lab05S02] Triangulação com os relatórios oficiais de incidentes

## Objetivo
Conferir se a página de status conta a mesma história que os relatórios oficiais.

## Passos
- [ ] Coletar os relatórios mensais de disponibilidade do blog do GitHub da janela e montar `dados/brutos/github/relatorios_mensais.csv` (mês, incidente, início, fim, causa, link)
- [ ] Para uma amostra de incidentes do GitLab, conferir a issue de produção correspondente (início, fim, causa)
- [ ] Comparar com o `incidentes.csv`: incidentes que aparecem em uma fonte e não na outra, diferença de duração
- [ ] Gerar `resultados/tabelas/triangulacao.csv` e escrever a interpretação em `lab05/docs/triangulacao.md`
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Concordância entre as fontes em números (ex.: % de incidentes que batem), usada depois nas ameaças à validade

## Dependências
Normalização (usar o exemplo enquanto não existir).

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S02)

---

### [Lab05S02] Estatística descritiva de frequência e tempo de recuperação

## Objetivo
Descrever os incidentes das duas plataformas com estatísticas adequadas à escala de cada métrica.

## Passos
- [ ] Criar `etapas/03_descritiva.py`
- [ ] Frequência: nº de incidentes por mês, por plataforma e por componente equivalente
- [ ] Tempo de recuperação: mediana, IQR, mínimo, máximo e média (só como apoio) da duração
- [ ] Tempo entre incidentes (MTBF) e distribuição por impacto
- [ ] Gráficos: série mensal, boxplot/violino da duração, barras por componente; salvar em `resultados/figuras/`
- [ ] Tabela em `resultados/tabelas/descritiva.csv`
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Tabelas e gráficos gerados pelo comando único

## Dependências
Normalização (usar o exemplo enquanto não existir).

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S02)

---

### [Lab05S02] Testes de hipótese e tamanho do efeito

## Objetivo
Responder se as diferenças entre GitHub e GitLab são estatisticamente significativas e qual o tamanho delas.

## Passos
- [ ] Criar `etapas/04_testes.py`
- [ ] Tempo de recuperação: teste escolhido no plano de análise (ex.: Mann-Whitney) + Cliff's delta com IC 95%
- [ ] Frequência: comparação de taxas (ex.: teste de razão de taxas de Poisson ou Wilcoxon pareado por mês) + razão de taxas com IC 95%
- [ ] Repetir por componente equivalente, com correção de Holm para múltiplas comparações
- [ ] Análise de sensibilidade: só incidentes `major`/`critical`, e sem o maior incidente de cada plataforma
- [ ] Salvar em `resultados/tabelas/testes.csv` e interpretar H₀/H₁
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Para cada hipótese: estatística, p-valor, tamanho do efeito com IC e conclusão em uma frase

## Dependências
Normalização e hipóteses do GQM (usar o exemplo enquanto não existirem).

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S02)

---

### [Lab05S02] Ameaças à validade

## Objetivo
Discutir as ameaças dos quatro tipos e como o grupo mitigou cada uma.

## Passos
- [ ] Criar `lab05/docs/ameacas.md` com conclusão, interna, construto e externa
- [ ] Construto: a página de status mede a confiabilidade real? quem decide abrir/fechar incidente e com que critério (cada empresa tem o seu)
- [ ] Interna: mudança de política de comunicação durante a janela, migração de infraestrutura do GitHub, granularidade diferente dos componentes
- [ ] Conclusão: poucos meses (n = 12), múltiplas comparações, dependência entre incidentes
- [ ] Externa: GitHub.com e GitLab.com não representam GitHub Enterprise Server nem GitLab self-managed; 12 meses atípicos
- [ ] Para cada ameaça, a mitigação usada (mapa de componentes, triangulação, sensibilidade)
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Tabela ameaça × tipo × mitigação, ligada aos resultados da triangulação

## Dependências
Nenhuma com outra pessoa (completar com a triangulação quando sair).

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S02)

---

### [Lab05S02] Seções de dados e resultados no dashboard

## Objetivo
Mostrar no dashboard os dados coletados e os resultados da análise.

## Passos
- [ ] `secoes/secao_3_dados.py`: fontes, janela, total de incidentes, resultado da validação
- [ ] `secoes/secao_4_frequencia.py`: série mensal, teste e razão de taxas
- [ ] `secoes/secao_5_recuperacao.py`: distribuição da duração, teste e Cliff's delta
- [ ] `secoes/secao_6_triangulacao.py`: concordância entre status e relatórios oficiais
- [ ] Ler só arquivos de `resultados/` (o dashboard não recalcula nada)
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Seções 3 a 6 aparecem no dashboard e se atualizam ao rodar o comando único

## Dependências
Estrutura do dashboard, descritiva, testes e triangulação (usar o exemplo enquanto não existirem).

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S02)

---

### [Lab05S03] Disponibilidade calculada × disponibilidade oficial

## Objetivo
Mostrar que a métrica de disponibilidade depende de quem mede e de como mede (construto e Goodhart), usando o caso do GitHub em 2026.

## Passos
- [ ] Calcular a disponibilidade mensal a partir do `incidentes.csv` em pelo menos duas definições (ex.: qualquer incidente × só `major`/`critical`; um componente × todos os componentes)
- [ ] Comparar com o número oficial (~99,9%) e com o projeto independente citado pelo The Register (78,33% em abril, 93,86% em maio, 88,39% em junho de 2026), com links
- [ ] Explicar a diferença de definição entre as fontes
- [ ] Gráfico em `resultados/figuras/` e texto em `lab05/docs/disponibilidade.md`
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Um gráfico com as várias "disponibilidades" do mesmo mês e a explicação de cada uma

## Dependências
Normalização (usar o exemplo enquanto não existir).

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S03)

---

### [Lab05S03] Estimativa de impacto para usuários e empresas

## Objetivo
Traduzir o resultado em impacto real: o que a diferença de incidentes e de tempo de recuperação significa para quem usa cada plataforma.

## Passos
- [ ] Juntar números públicos com fonte e data de acesso (usuários, organizações, uso de CI) a partir de `criterios.md`
- [ ] Estimar, por exemplo, horas de indisponibilidade por mês × usuários afetados, ou nº de pipelines de CI potencialmente afetados
- [ ] Deixar explícitas as suposições e fazer cenários (otimista, central, pessimista)
- [ ] Escrever o que **não** é possível afirmar (validade externa)
- [ ] `secoes/secao_7_impacto.py` e `lab05/docs/impacto.md`
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Frase no formato do enunciado: "Com X usuários, isso equivale a Y horas…", com fonte de cada número

## Dependências
Critérios, descritiva e testes (usar o exemplo enquanto não existirem).

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S03)

---

### [Lab05S03] Revisar e justificar as 7 categorias

## Objetivo
Fechar a classificação do estudo com base no que foi de fato executado.

## Passos
- [ ] Revisar `lab05/docs/categorias.md` à luz da coleta e da análise
- [ ] Justificar o nível de evidência considerando a triangulação
- [ ] Levar a tabela final para o dashboard (`secoes/secao_2_metodo.py`)
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Cada categoria com justificativa que qualquer integrante consegue explicar oralmente

## Dependências
Primeira versão das categorias e triangulação.

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S03)

---

### [Lab05S03] Conclusões e limitações

## Objetivo
Responder às duas perguntas do enunciado: "o que o estudo mostrou?" e "o que isso significa para quem usa esse software?"

## Passos
- [ ] Resposta à pergunta de pesquisa em uma frase, com os números principais
- [ ] Resposta para cada hipótese
- [ ] Limitações ligadas às ameaças à validade
- [ ] Trabalhos futuros (ex.: medir de fora com 1 req/s, survey com usuários)
- [ ] `secoes/secao_8_conclusao.py` e `lab05/docs/conclusao.md`
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Conclusão coerente com os testes, sem afirmar causa

## Dependências
Testes, ameaças e impacto.

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S03)

---

### [Lab05S03] Reaproveitamento dos labs anteriores

## Objetivo
Mostrar o que veio dos Labs 01 a 04 e o que foi feito de novo (seção 4 do enunciado).

## Passos
- [ ] Criar `lab05/docs/reaproveitamento.md` com uma tabela: lab, o que foi reaproveitado, onde aparece no Lab05
- [ ] Lab01: coleta automatizada e Kanban; Lab03: MTTR e falhas (DORA) aplicados à operação; Lab04: escolha de testes, comando único e dashboard
- [ ] Listar o que é novo (páginas de status, triangulação, estimativa de impacto)
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Tabela pronta para virar um slide

## Dependências
Nenhuma com outra pessoa.

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S03)

---

### [Lab05S03] Rascunho do documento e da apresentação

## Objetivo
Escolher o formato do documento e da apresentação e montar a primeira versão.

## Passos
- [ ] Decidir em grupo o formato (ex.: dashboard + relatório; reunião simulada com o CTO)
- [ ] Rascunho do documento com todas as partes da seção 8 do enunciado
- [ ] Roteiro da apresentação de 10 minutos, com quem fala cada parte
- [ ] Salvar em `lab05/docs/` e `lab05/docs/apresentacao/`
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Rascunho revisado pelos três integrantes

## Dependências
Conclusões, impacto e reaproveitamento.

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Sprint S03)

---

### [Lab05Final] Documento final

## Objetivo
Entregar o documento final no formato escolhido, cobrindo todos os itens da seção 8 do enunciado.

## Passos
- [ ] Revisar o rascunho com os resultados finais (só dados reais)
- [ ] Conferir: software e critérios, pergunta e caminho, 7 categorias, conceitos da teórica, reaproveitamento, resultados, 4 tipos de ameaça, impacto e limites
- [ ] Preencher links do repositório, do Projects e do dashboard
- [ ] Rodar o comando único do zero e conferir que tudo é reproduzido
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Documento final publicado no repositório

## Dependências
Todas as issues da S03.

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Documento Final e Apresentação)

---

### [Lab05Final] Apresentação e respostas das perguntas orais

## Objetivo
Preparar a apresentação de 10 minutos e garantir que qualquer integrante consegue explicar qualquer parte.

## Passos
- [ ] Versão final da apresentação no formato escolhido
- [ ] Ensaio cronometrado (10 min)
- [ ] Lista de perguntas prováveis com respostas em `lab05/docs/apresentacao/perguntas.md` (ex.: por que esses testes? por que esses componentes? a página de status é confiável? o que não dá para afirmar?)
- [ ] Cada integrante explica uma parte que não é dele
- [ ] Referenciar esta issue em todos os commits

## O que se espera
- Apresentação dentro do tempo e grupo preparado para perguntas cruzadas

## Dependências
Documento final.

## Combinado do grupo (igual em todas as issues)

Serve para ninguém precisar esperar o código de outra pessoa.

- **Objeto de estudo:** o serviço em operação (GitHub.com e GitLab.com), medido pelas páginas de status públicas. Nada de minerar commits, issues ou PRs de repositórios.
- **Janela:** 12 meses fechados, de `2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`. Todas as datas em UTC.
- **Coletores** (`lab05/code/coleta/github.py` e `lab05/code/coleta/gitlab.py`, papel B): `coletar(inicio, fim) -> list[dict]` grava as respostas originais em `dados/brutos/<plataforma>/` e devolve um dicionário por incidente.
- **Formato comum** (`lab05/code/dados/processados/incidentes.csv`): `plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url`. `plataforma` é `github` ou `gitlab`; `componentes_originais` separados por `;`; `impacto` como a página publica (ex.: `minor`, `major`, `critical`).
- **Componentes equivalentes** (`lab05/code/dados/mapa_componentes.csv`, papel A): `plataforma,componente_original,componente_equivalente`. Categorias: `git`, `api`, `web`, `issues_prs`, `ci_cd`, `pacotes`, `pages`, `fora_do_escopo`. Só entram na comparação os incidentes de categorias que existem nas duas plataformas.
- **Enquanto a peça de outra pessoa não existir:** use um `incidentes.csv` de exemplo com poucas linhas inventadas (`dados/processados/exemplo_incidentes.csv`). Ao trocar pelo arquivo real, basta rodar o comando único de novo. **Números e textos finais só valem com os dados reais.**
- **Ética:** no máximo 1 requisição por segundo, respeitar robots.txt e termos de uso, User-Agent genérico (sem nome ou e-mail), sem dados pessoais. Nada de teste de carga.
- **Dashboard (Streamlit):** um arquivo por seção em `lab05/code/secoes/secao_<N>_<nome>.py`, com uma função `render()`. Quem é dono da seção só mexe no próprio arquivo.
- **Comando único:** cada etapa fica em `lab05/code/etapas/<NN>_<nome>.py`, com uma função `main()`.
- **Reprodutibilidade:** semente `numpy.random.default_rng(42)` (bootstrap e simulações). Os dados brutos ficam versionados; o processamento não acessa a internet.
- **Cores em todos os gráficos:** GitHub `#6e40c9`, GitLab `#fc6d26`. Sempre com título, eixos com nome e unidade, e legenda.


---
Milestone/entrega: Lab05 (Documento Final e Apresentação)

# Proposta — Confiabilidade operacional: GitHub × GitLab

## Pergunta de pesquisa

O GitHub e o GitLab diferem na frequência de incidentes e no tempo de recuperação, considerando apenas componentes equivalentes, nos últimos 12 meses?

Perguntas complementares examinam a gravidade dos incidentes, o tempo entre
incidentes e a diferença entre medições oficiais e independentes. O objetivo,
as perguntas, as métricas e as hipóteses completas estão em [gqm.md](gqm.md).

## Objetivo GQM

Analisar GitHub.com e GitLab.com para comparar e caracterizar sua confiabilidade
operacional quanto à frequência, duração, intervalo e gravidade dos incidentes
publicados, do ponto de vista de quem depende das plataformas para desenvolver
e entregar software, no contexto dos componentes equivalentes durante a janela
do estudo.

## Caminho

Análise de dados de operação (páginas de status), com triangulação usando os relatórios oficiais de incidentes.

> O objeto de estudo é o **serviço em operação** (GitHub.com e GitLab.com), não os repositórios hospedados neles. Não há mineração de commits, issues ou PRs.

O estudo é observacional e retrospectivo. A janela fechada vai de
`2025-11-01T00:00:00Z` a `2026-10-31T23:59:59Z`, com todas as datas em UTC.
Somente categorias de componentes presentes nas duas plataformas entram na
comparação principal.

## Por que o momento é bom

- O GitHub teve um 2026 turbulento: problemas de disponibilidade coincidiram
  com o aumento de tráfego associado a codificação assistida por IA e fluxos
  com agentes. A empresa também acelerou sua migração para o Azure e a redução
  de dependências compartilhadas.
- Uma reconstrução independente citada pelo *The Register* divergiu dos
  percentuais exibidos pela página oficial. Isso torna explícita a ameaça de
  validade de construto: disponibilidade depende de quem mede, do componente,
  da janela e da definição de indisponibilidade.

Os números, links e datas de acesso estão documentados em
[criterios.md](criterios.md).

## Métricas principais

- incidentes distintos por mês e plataforma;
- duração em minutos por incidente, usada como proxy de tempo de recuperação;
- MTTR observado e tempo operacional entre incidentes como proxy de MTBF;
- proporção de incidentes por classe de impacto;
- diferença de contagem e de disponibilidade entre fontes oficiais e
  independentes.

Todas são campos do formato comum ou derivações de `plataforma`, `id`,
`componente_equivalente`, `impacto`, `inicio_utc`, `fim_utc`, `duracao_min` e
`fonte`.

## Hipóteses

- **Frequência:** H₀ afirma que não há diferença na distribuição mensal de
  incidentes entre as plataformas; H₁ afirma que há diferença.
- **Recuperação:** H₀ afirma que a distribuição das durações dos incidentes
  é igual nas plataformas; H₁ afirma que ela difere.

As hipóteses são bilaterais. A definição operacional e os cuidados com
Goodhart, Campbell e McNamara estão em [gqm.md](gqm.md).

## Fontes de dados

### GitHub

- Página de status: <https://www.githubstatus.com>, com histórico por incidente.
- Relatórios mensais de disponibilidade no blog do GitHub, para validar os dados (ex.: junho de 2026 com seis incidentes de degradação, cada um com início, fim e causa).

### GitLab

- Página de status: <https://status.gitlab.com>, exclusiva para o GitLab.com e serviços associados, com histórico e feeds RSS e iCalendar.
- Incidentes resolvidos trazem link para a issue de produção correspondente (fonte extra de detalhes).

## Pendências

- [x] Evidências dos três critérios (real, em operação, alto impacto) com links e data de acesso
- [ ] Mapeamento de componentes equivalentes
- [x] Janela exata dos 12 meses
- [x] GQM e hipóteses
- [ ] 7 categorias de pesquisa

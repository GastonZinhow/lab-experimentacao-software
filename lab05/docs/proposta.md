# Proposta — Confiabilidade operacional: GitHub × GitLab

> Rascunho inicial do tema escolhido pelo grupo. Será completado na issue de proposta da S01.

## Pergunta de pesquisa

O GitHub e o GitLab diferem na frequência de incidentes e no tempo de recuperação, considerando apenas componentes equivalentes, nos últimos 12 meses?

## Caminho

Análise de dados de operação (páginas de status), com triangulação usando os relatórios oficiais de incidentes.

> O objeto de estudo é o **serviço em operação** (GitHub.com e GitLab.com), não os repositórios hospedados neles. Não há mineração de commits, issues ou PRs.

## Por que o momento é bom

- O GitHub teve um 2026 turbulento: problemas de disponibilidade com o aumento de tráfego (puxado por codificação assistida por IA e fluxos com agentes) e uma migração de infraestrutura em andamento. O relatório de julho de 2026 cita progresso na migração para o Azure e na redução de dependências compartilhadas. *(fonte: The Register — link e data de acesso a preencher)*
- Gancho de medição: segundo o The Register, um projeto independente calculou disponibilidade de 78,33% em abril, 93,86% em maio e 88,39% em junho, enquanto a página de status oficial mostra números em torno de 99,9%. A métrica depende de quem mede e de como mede (validade de construto, Lei de Goodhart). *(fonte a preencher)*

## Fontes de dados

### GitHub

- Página de status: <https://www.githubstatus.com>, com histórico por incidente.
- Relatórios mensais de disponibilidade no blog do GitHub, para validar os dados (ex.: junho de 2026 com seis incidentes de degradação, cada um com início, fim e causa).

### GitLab

- Página de status: <https://status.gitlab.com>, exclusiva para o GitLab.com e serviços associados, com histórico e feeds RSS e iCalendar.
- Incidentes resolvidos trazem link para a issue de produção correspondente (fonte extra de detalhes).

## Pendências

- [ ] Evidências dos três critérios (real, em operação, alto impacto) com links e data de acesso
- [ ] Mapeamento de componentes equivalentes
- [ ] Janela exata dos 12 meses
- [ ] 7 categorias de pesquisa, GQM e hipóteses

# Critérios do objeto de estudo: GitHub.com e GitLab.com

Este documento reúne evidências de que **GitHub.com** e **GitLab.com** são
serviços reais, em operação e de alto impacto. O objeto de estudo é o serviço
em produção observado por suas páginas públicas de status, e não a mineração
dos repositórios hospedados nas plataformas.

Todas as fontes foram acessadas em **19 de novembro de 2026**. Números
publicados pelos próprios fornecedores são identificados como tais e não foram
tratados como medições independentes.

## GitHub.com

| Critério | Evidência | Número | Fonte | Data de acesso |
|---|---|---:|---|---|
| Real | Presença oficial verificável: produto, documentação e página que monitora o serviço em produção. | 3 canais oficiais | [GitHub](https://github.com/), [GitHub Docs](https://docs.github.com/en/get-started/start-your-journey/what-is-github) e [GitHub Status](https://www.githubstatus.com/) | 19/11/2026 |
| Em operação | A página de status registrou degradação de Actions e Checks API em 09/11/2026, com início às 18:07 e recuperação às 18:59 UTC. | 52 min; 28% dos workflows afetados em média e pico de 65% | [GitHub Status — incidente de 09/11/2026](https://www.githubstatus.com/incidents/tp8cghg7tlc4) | 19/11/2026 |
| Em operação | O Octoverse mede atividade efetivamente processada entre 01/10/2025 e 30/09/2026. | 17,9 bi de pushes; 34,3 bi de commits; 45,4 bi de jobs do Actions; 1,3 bi de PRs mesclados | [Octoverse 2026](https://github.blog/news-insights/octoverse/octoverse-commits-pushes-reach-new-highs-in-2026-as-developers-build-with-agents/) | 19/11/2026 |
| Em operação | Histórias oficiais mostram uso empresarial e governamental: EY, Ford e Cathay; NASA JPL, U.S. Department of Veterans Affairs e California Department of Technology. | 6 exemplos documentados | [GitHub Customer Stories](https://github.com/customer-stories/enterprise?industry=Government) | 19/11/2026 |
| Alto impacto | A página institucional informa a escala atual da plataforma. | 225 mi+ de desenvolvedores; 4 mi+ de organizações; 800 mi+ de repositórios; 90% da Fortune 100 | [About GitHub](https://github.com/about) | 19/11/2026 |
| Alto impacto | O Stack Overflow Developer Survey 2026 perguntou quais plataformas comunitárias os respondentes usaram no ano anterior; o item mede projetos públicos do GitHub, não repositórios privados. | 7.460 respondentes; 69,5% | [Stack Overflow Developer Survey 2026 — Community](https://survey.stackoverflow.co/2026/community) | 19/11/2026 |
| Alto impacto | Um caso governamental ajuda a traduzir a escala para serviços públicos: o U.S. Department of Veterans Affairs adotou GitHub para modernizar o VA.gov. | 20 mil+ desenvolvedores; 5 mil usuários do GitHub; 10 mi de veteranos visitam o VA.gov por mês | [GitHub Customer Story — U.S. Department of Veterans Affairs](https://github.com/customer-stories/va) | 19/11/2026 |

## GitLab.com

| Critério | Evidência | Número | Fonte | Data de acesso |
|---|---|---:|---|---|
| Real | Presença oficial verificável: produto, documentação e página dedicada exclusivamente ao GitLab.com e aos serviços associados. | 3 canais oficiais | [GitLab](https://gitlab.com/), [GitLab Docs](https://docs.gitlab.com/) e [GitLab System Status](https://status.gitlab.com/) | 19/11/2026 |
| Em operação | A página de status registrou em 03/11/2026 uma investigação de erros do Gitaly que impediam clientes de executar pipelines no GitLab.com. | 1 incidente recente; CI/CD degradado | [GitLab System Status](https://status.gitlab.com/) | 19/11/2026 |
| Em operação | A lista oficial de versões identifica o GitLab 19.5 como a versão mensal mais recente publicada na data da consulta. | versão 19.5, lançada em 15/10/2026 | [What's new in GitLab](https://about.gitlab.com/whats-new/?tab=explore-release) | 19/11/2026 |
| Em operação | Histórias oficiais mostram uso empresarial, científico e governamental: Goldman Sachs, Siemens e Deutsche Bahn; CERN, European Space Agency e U.S. Army Cyber School. | 6 exemplos documentados | [GitLab Customer Stories](https://about.gitlab.com/customers/all/) | 19/11/2026 |
| Alto impacto | A página institucional informa a comunidade e a continuidade de entrega do produto, com números de junho de 2026. | 50 mi+ de usuários registrados; 5.500+ contribuidores; 177 lançamentos mensais consecutivos | [About GitLab](https://about.gitlab.com/company/) | 19/11/2026 |
| Alto impacto | O GitLab declara adoção ampla entre organizações que planejam, constroem, protegem e entregam software. | 100 mil+ organizações | [GitLab by the numbers](https://about.gitlab.com/jobs/) | 19/11/2026 |
| Alto impacto | O resultado financeiro oficial do segundo trimestre do ano fiscal de 2027 mostra uma base empresarial pagante relevante. | 11.114 clientes com ARR acima de US$ 5 mil; 1.571 com ARR acima de US$ 100 mil | [GitLab Investor Relations — Q2 FY2027](https://ir.gitlab.com/financials/quarterly-results/default.aspx) | 19/11/2026 |
| Alto impacto | Um caso de setor público mostra uso em projetos ligados à segurança nacional e à modernização governamental dos EUA. | 24 mil+ empregados; cerca de 190 projetos de software | [GitLab Customer Story — CACI](https://about.gitlab.com/customers/caci/) | 19/11/2026 |

## Contexto operacional do GitHub em 2026

O ano de 2026 exige cautela ao interpretar disponibilidade. Em junho, o
**The Register** relatou que os relatórios oficiais do GitHub reconheceram dez
incidentes com degradação em abril e nove em maio. A mesma reportagem citou o
projeto independente *The Missing GitHub Status Page*, que reconstruía a série
a partir do feed público e estimava **78,33%** de disponibilidade em abril,
**93,86%** em maio e **88,39%** em junho até a data da matéria, enquanto a
página oficial exibia valores próximos de **99,9%** para a maioria dos
componentes ([The Register, 12/06/2026](https://assets.theregister.com/2026/06/12/202615/),
acesso em 19/11/2026).

Esses percentuais **não são diretamente comparáveis**: variam o componente, a
janela, o que conta como indisponibilidade e a forma de agregar incidentes. Eles
serão usados como alerta de validade de construto, não como substitutos dos
dados brutos desta pesquisa.

O próprio GitHub documentou a resposta de infraestrutura. No relatório de julho,
publicado em agosto, informou **oito incidentes** com degradação; em 28/07,
**52,75%** do tráfego de leitura do monólito e **47%** do tráfego Git estavam no
Azure Central US, e **29%** dos repositórios já tinham uma segunda réplica nessa
região. O relatório também registra a aceleração da migração do GitHub Actions
para o Azure e a redução de dependências compartilhadas
([GitHub Availability Report — julho de 2026](https://github.blog/news-insights/company-news/github-availability-report-july-2026/),
acesso em 19/11/2026).

## Conclusão

As duas plataformas atendem aos três critérios da seção 2a do enunciado:
possuem produto, documentação e telemetria operacional públicos; apresentam
atividade recente, versões e clientes verificáveis; e operam em escala de
milhões de pessoas e milhares de organizações. O contexto de instabilidade do
GitHub em 2026 reforça a relevância do estudo comparativo, mas também exige que
as conclusões explicitem a definição de incidente e a janela de medição.

# Triangulação com relatórios oficiais

## Objetivo e fontes

Esta conferência verifica se a página de status e uma segunda fonte oficial
descrevem os mesmos incidentes na janela de 2025-11-01 a 2026-10-31. Para o
GitHub, foram preservados e lidos os 12 relatórios mensais do
[GitHub Availability Report](https://github.blog/tag/github-availability-report/).
Para o GitLab, foi usada uma amostra de uma issue de produção que informa no
próprio texto o início, o fim e a causa; outras issues consultadas registravam a
causa, mas não os dois horários, por isso não foram usadas para comparar duração.

Os relatórios do GitHub são seletivos: a própria fonte diz que apresenta os
incidentes relevantes do mês, enquanto a página de status registra eventos de
escopo muito mais amplo. Portanto, `somente_status` mede **cobertura editorial**
do relatório, não uma contradição. O CSV de entrada transcrito dos HTMLs está em
`code/dados/brutos/github/relatorios_mensais.csv`; o cruzamento linha a linha
está em `code/resultados/tabelas/triangulacao.csv`.

## Método

- Cada ocorrência dos relatórios foi separada, inclusive quando um título
  descrevia dois incidentes.
- O pareamento usa plataforma, proximidade temporal (no máximo 12 horas),
  duração e assunto. Nenhum incidente da página de status é reutilizado.
- Consideramos que os horários “batem” quando as diferenças absolutas de início
  **e** duração são de até 15 minutos. Esse limite absorve arredondamentos do
  texto mensal sem esconder janelas operacionalmente diferentes.
- Diferenças são `status - fonte oficial`: valor positivo significa que a
  página de status começou depois ou mediu duração maior.

## Resultados

### GitHub

Os 12 relatórios contêm **65 ocorrências**. Foi possível parear **64 (98,5%)**
com um dos 290 incidentes da página de status; uma ocorrência do relatório de
julho (8 de julho, ambientes com residência de dados) não teve par defensável.
Vistos pelo outro lado, os relatórios cobrem **64 de 290 incidentes (22,1%)** da
página de status, e 226 aparecem apenas no status.

Entre os 64 pares, **47 (73,4%)** atendem simultaneamente ao limite de 15
minutos para início e duração. Separadamente, 51 (79,7%) têm início dentro do
limite e 54 (84,4%) têm duração dentro do limite. A diferença absoluta mediana
é pequena: **0,74 minuto no início** e **0,48 minuto na duração**. O percentil
90 da diferença absoluta de duração é **23,97 minutos**, indicando que a maior
parte dos casos concorda de perto, mas existe uma cauda de incidentes em que o
relatório usa a janela de impacto ao usuário e o status usa a janela de
declaração/acompanhamento.

### GitLab (amostra)

A issue de produção [#20878](https://gitlab.com/gitlab-com/gl-infra/production/-/work_items/20878)
informa impacto entre 03:20 e 17:51 UTC e atribui a falha a faixas de IP
sobrepostas em clusters Kubernetes, que impediram a conectividade SSH dos
runners. O evento correspondente no iCalendar do status começa 516,77 minutos
depois e dura 378,93 minutos, contra 871 minutos na issue (diferença de -492,07
minutos). O fim é próximo, mas o início publicado no status representa uma
janela de comunicação bem menor que a janela de impacto descrita na issue.

Como `n = 1`, o caso do GitLab é evidência qualitativa e **não** deve ser
apresentado como percentual de concordância da plataforma.

## Interpretação e ameaça à validade

As fontes contam uma história coerente para os incidentes escolhidos pelo
GitHub: 98,5% dos relatos encontram um evento no status e, nos pares, 73,4%
concordam em início e duração dentro de 15 minutos. Ao mesmo tempo, os 22,1% de
cobertura mostram que o relatório mensal não é um catálogo completo e não pode
substituir o histórico da página de status.

A divergência do caso GitLab e a cauda de diferenças do GitHub mostram que
“duração” não tem sempre o mesmo marco semântico: pode significar impacto real,
detecção pública, declaração ou encerramento do acompanhamento. Essa diferença
de mensuração é uma ameaça de construto ao comparar tempos de recuperação. A
análise principal deve manter os horários da página de status, aplicar a mesma
regra às duas plataformas e usar esta triangulação para qualificar — não
reescrever — as durações.

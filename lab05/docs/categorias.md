# Categorias de pesquisa — primeira versão (S01)

> Issue #98. Versão inicial, feita antes da coleta completa. A versão revisada e final fica para a S03, depois que a coleta e a análise mostrarem o que foi de fato possível fazer.

**Estudo:** o GitHub e o GitLab diferem na frequência de incidentes e no tempo de recuperação, considerando apenas componentes equivalentes, nos últimos 12 meses (2025-11-01 a 2026-10-31)?

**O que o grupo faz de fato:** lê os incidentes que as próprias empresas publicaram nas páginas de status (githubstatus.com e status.gitlab.com), confere uma parte deles nos relatórios oficiais (relatórios mensais do blog do GitHub e issues de produção do GitLab) e compara as duas plataformas. O grupo não interfere em nada: os incidentes já aconteceram e foram registrados por terceiros.

## Resumo

| # | Categoria | Classificação | Justificativa curta |
|---|---|---|---|
| 1 | Natureza | **Aplicada** | Responde a uma pergunta prática de quem escolhe ou opera uma plataforma de desenvolvimento |
| 2 | Objetivos | **Descritiva**, com parte **exploratória** | Descreve e compara frequência e duração; explora como cada empresa registra incidentes |
| 3 | Abordagem | **Quantitativa**, com apoio **qualitativo** | Métricas numéricas e testes; leitura das causas nos relatórios serve para triangular |
| 4 | Procedimentos | **Pesquisa documental** com análise de dados de operação (*ex post facto*) | Os dados são registros públicos produzidos pelas empresas, não pelo grupo |
| 5 | Tempo | **Longitudinal retrospectivo** | 12 meses de histórico, analisados mês a mês, depois que os fatos aconteceram |
| 6 | Controle | **Observacional** (sem controle) | O grupo não escolhe nem manipula a "plataforma"; só observa |
| 7 | Nível de evidência | **Baixo a moderado**: associação, não causa | Estudo observacional com dados de fonte única por empresa, reforçado por triangulação |

## Justificativas

### 1. Natureza — aplicada

O objetivo não é criar teoria nova sobre confiabilidade, e sim gerar um resultado usado na prática: ajudar quem depende do GitHub ou do GitLab (equipes, empresas, órgãos) a entender o risco operacional de cada um. A pergunta nasce de um problema real e atual (a instabilidade do GitHub em 2026) e o resultado é traduzido em impacto para usuários (seção 5 do enunciado).

### 2. Objetivos — descritiva, com parte exploratória

- **Descritiva:** o núcleo do estudo é descrever e comparar duas populações de incidentes (quantos por mês, quanto tempo duram, com que gravidade) com estatística descritiva e testes de hipótese.
- **Exploratória:** antes de comparar, o grupo precisa entender como cada empresa define e registra um incidente (granularidade dos componentes, escala de impacto, quando abre e fecha). Isso não é conhecido de antemão e pode mudar a interpretação.
- **Não é explicativa:** o estudo não consegue dizer *por que* uma plataforma tem mais incidentes (arquitetura, tráfego, migração para o Azure, cultura de comunicação). As causas aparecem só como contexto, na triangulação.

### 3. Abordagem — quantitativa, com apoio qualitativo

- **Quantitativa:** as métricas principais são numéricas — contagem de incidentes por mês (escala de razão), duração em minutos (razão), tempo entre incidentes (razão) e impacto (ordinal). As perguntas são respondidas com testes de hipótese e tamanho do efeito.
- **Apoio qualitativo:** a leitura das causas nos relatórios mensais do GitHub e nas issues de produção do GitLab é usada para conferir os dados e interpretar casos extremos, não para gerar as conclusões principais. Por isso a abordagem não é chamada de mista "plena".

### 4. Procedimentos — pesquisa documental / análise de dados de operação (*ex post facto*)

- Os dados são **documentos públicos produzidos pelas próprias empresas** (páginas de status e relatórios), o que caracteriza pesquisa documental.
- É ***ex post facto***: os incidentes já ocorreram e a "variável independente" (ser GitHub ou GitLab) não foi atribuída pelo grupo.
- A **triangulação** (status × relatórios oficiais × medição independente citada pelo The Register) é o procedimento usado para reduzir o viés de depender de uma única fonte.
- Não é levantamento (survey), estudo de caso aprofundado nem experimento.

### 5. Tempo — longitudinal retrospectivo

- **Longitudinal:** a janela cobre 12 meses e a frequência é analisada como série mensal, o que permite ver tendência e meses atípicos (ex.: abril a junho de 2026 no GitHub).
- **Retrospectivo:** o grupo olha para trás, em dados já registrados; não acompanha os incidentes à medida que acontecem.
- Uma observação: a comparação entre plataformas também pode ser lida como um "corte" de 12 meses. Na S03 o grupo decide se a análise ficou mais longitudinal (série mensal) ou mais transversal (totais do período).

### 6. Controle — observacional

- O grupo **não manipula nenhuma variável**: não escolhe quando ocorrem incidentes, não altera configuração, não sorteia tratamento.
- Não há grupo de controle nem aleatorização, então não é experimento controlado nem quase-experimento.
- O único "controle" possível é de **comparabilidade**: comparar só componentes equivalentes (issue #99), a mesma janela e o mesmo critério de duração. Isso reduz, mas não elimina, as diferenças entre as duas plataformas.

### 7. Nível de evidência — baixo a moderado (associação, não causa)

- Por ser observacional e documental, o estudo mostra **se existe diferença** e **de que tamanho**, mas **não permite afirmar causa**. Exemplo: se o GitHub tiver mais incidentes, isso pode refletir mais falhas, mais tráfego, mais componentes, ou apenas uma política de comunicação mais transparente.
- Fatores que **enfraquecem** a evidência:
  - cada página de status é escrita pela própria empresa (quem mede é quem é medido — ligação com Goodhart e Campbell);
  - os critérios para abrir, classificar e encerrar incidentes são diferentes entre as empresas;
  - n pequeno na análise mensal (12 meses por plataforma).
- Fatores que **fortalecem** a evidência:
  - dados reais de produção, de um período completo e recente;
  - triangulação com relatórios oficiais e com medição independente;
  - análise de sensibilidade (só incidentes graves; sem o maior incidente).
- Na hierarquia de evidência, fica acima de opinião e relato isolado, e abaixo de experimento controlado.

## O que isso significa para as conclusões

1. As frases finais devem usar "o GitHub **registrou** mais incidentes…" em vez de "o GitHub **é** menos confiável…".
2. Toda diferença encontrada precisa vir acompanhada da discussão de construto (o que a página de status mede de verdade).
3. Generalização só para GitHub.com e GitLab.com no período estudado; não vale para GitHub Enterprise Server, GitLab self-managed nem para outros anos.

## Pendências para a S03

- [ ] Confirmar a fonte usada para cada plataforma depois da coleta piloto (issues #7 e #8 do backlog), porque isso muda o procedimento
- [ ] Revisar o nível de evidência com o resultado da triangulação (% de concordância entre as fontes)
- [ ] Decidir entre leitura longitudinal (série mensal) e transversal (totais)

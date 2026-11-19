# GQM — confiabilidade operacional do GitHub.com e do GitLab.com

## Objetivo no template de Basili

> **Analisar** os serviços GitHub.com e GitLab.com **com o propósito de**
> comparar e caracterizar sua confiabilidade operacional **com respeito a**
> frequência, duração, intervalo e gravidade dos incidentes publicados **do
> ponto de vista de** organizações e profissionais que dependem das plataformas
> para desenvolver e entregar software **no contexto de** incidentes das
> categorias de componentes comuns às duas plataformas, registrados nas páginas
> públicas de status entre `2025-11-01T00:00:00Z` e
> `2026-10-31T23:59:59Z`.

O objetivo é comparativo e descritivo. O desenho observacional não permite
atribuir causalidade a diferenças encontradas entre as plataformas.

## Perguntas

- **Q1 — Frequência:** GitHub.com e GitLab.com diferem no número de incidentes
  publicados por mês, considerando somente componentes equivalentes?
- **Q2 — Recuperação:** as plataformas diferem na duração dos incidentes e no
  tempo operacional entre incidentes consecutivos?
- **Q3 — Gravidade:** como os incidentes se distribuem por impacto e como a
  duração varia entre as classes de impacto em cada plataforma?
- **Q4 — Fonte da medição:** quanto as estimativas baseadas nas páginas
  oficiais diferem das estimativas obtidas por fontes independentes que
  reconstruam incidentes para a mesma janela e os mesmos componentes?

## Formato comum e unidade de observação

A unidade de observação é um incidente em
`lab05/code/dados/processados/incidentes.csv`. O formato comum é:

```text
plataforma,id,titulo,componentes_originais,componente_equivalente,impacto,inicio_utc,fim_utc,duracao_min,fonte,url
```

As comparações principais usam apenas:

1. incidentes dentro da janela fechada do estudo, em UTC;
2. categorias de `componente_equivalente` existentes nas duas plataformas;
3. registros oficiais identificados por `fonte`;
4. um registro por par `(plataforma, id)`, após a validação de duplicatas.

Registros independentes usados em Q4 devem ser normalizados para o mesmo
formato, preservando a origem em `fonte` e `url`. Assim, nenhuma métrica depende
de uma coluna ausente no conjunto comum.

## Métricas

Uma **medida direta** é lida do registro publicado. Uma **medida derivada** é
calculada a partir de uma ou mais colunas. A classificação interno/externo se
refere ao atributo observado: as métricas abaixo descrevem comportamento
percebido fora da implementação do serviço e, portanto, são externas.

| ID | Pergunta | Métrica e definição operacional | Campos do formato comum | Entidade | Atributo | Obtenção | Escala |
|---|---|---|---|---|---|---|---|
| M1 | Q1 | **Número de incidentes por mês:** contagem de `id` distintos por `plataforma` e mês de `inicio_utc`. Também será estratificada por `componente_equivalente`. | `plataforma`, `id`, `inicio_utc`, `componente_equivalente`, `fonte` | Produto (serviço em operação) | Confiabilidade externa | Derivada | Razão, contagem discreta; unidade: incidentes/mês; zero é ausência de incidente publicado. |
| M2 | Q2 | **Duração do incidente:** minutos entre o primeiro registro de impacto e a resolução. `duracao_min = (fim_utc - inicio_utc)`; o campo calculado deve ser validado contra os timestamps. É a proxy de tempo de recuperação por incidente. | `inicio_utc`, `fim_utc`, `duracao_min` | Processo de recuperação do serviço | Recuperabilidade externa | Derivada, embora armazenada no CSV | Razão, contínua; unidade: minutos; zero representa duração nula. |
| M3 | Q2 | **MTTR observado:** média das durações dos incidentes por plataforma no período. Como a distribuição tende a ser assimétrica, mediana e IQR serão apresentados junto da média. O termo é uma aproximação, pois o status informa detecção e resolução públicas, não necessariamente todo o ciclo interno de reparo. | `plataforma`, `duracao_min`, `componente_equivalente`, `fonte` | Processo de recuperação do serviço | Recuperabilidade externa | Derivada | Razão, contínua; unidade: minutos/incidente. |
| M4 | Q2 | **Tempo entre incidentes (proxy de MTBF):** após ordenar por plataforma e componente, diferença entre `inicio_utc` do incidente seguinte e `fim_utc` do anterior. Sobreposições produzem valor zero e são marcadas para análise de sensibilidade; não se usa valor negativo como tempo operacional. | `plataforma`, `componente_equivalente`, `inicio_utc`, `fim_utc` | Produto (serviço em operação) | Confiabilidade externa | Derivada | Razão, contínua; unidade: minutos entre incidentes; zero indica sobreposição ou ausência de intervalo operacional. |
| M5 | Q3 | **Impacto publicado:** classe de gravidade atribuída pela própria plataforma (`minor`, `major`, `critical` e demais valores encontrados, sem recodificação silenciosa). | `impacto` | Produto (serviço em operação) | Severidade externa publicada | Direta | Ordinal; a ordem representa gravidade, mas as distâncias entre classes não são iguais. |
| M6 | Q3 | **Proporção por impacto:** `nº de incidentes da classe / nº total de incidentes` por plataforma, com intervalo de confiança. | `plataforma`, `id`, `impacto`, `fonte` | Produto (serviço em operação) | Perfil de severidade externa | Derivada | Razão; proporção de 0 a 1 (ou percentual de 0% a 100%). |
| M7 | Q3 | **Duração por impacto:** mediana e IQR de `duracao_min` para cada combinação de plataforma e classe de impacto. | `plataforma`, `impacto`, `duracao_min` | Processo de recuperação do serviço | Recuperabilidade externa condicionada à severidade | Derivada | Razão, contínua; unidade: minutos. |
| M8 | Q4 | **Diferença no número de incidentes por fonte:** contagem independente menos contagem oficial para a mesma plataforma, janela e conjunto de componentes; também expressa como diferença percentual em relação à fonte oficial. | `plataforma`, `id`, `componente_equivalente`, `inicio_utc`, `fonte`, `url` | Processo de comunicação de incidentes | Cobertura externa da medição | Derivada | Diferença absoluta em escala intervalar (incidentes) e razão percentual; pode ser negativa. |
| M9 | Q4 | **Diferença de disponibilidade:** para cada fonte, unir intervalos sobrepostos e calcular `1 - minutos_com_impacto/minutos_da_janela`; comparar fonte independente e oficial em pontos percentuais. | `plataforma`, `inicio_utc`, `fim_utc`, `componente_equivalente`, `fonte`, `url` | Produto e processo de comunicação | Disponibilidade externa observada | Derivada | Disponibilidade em escala de razão (0 a 1); diferença em pontos percentuais em escala intervalar. |

### Regras de derivação

- A amostra principal inclui incidentes cujo `inicio_utc` está dentro da janela.
  Se a coleta também recuperar um incidente iniciado antes da borda inferior,
  ele entra apenas em uma análise de sensibilidade; para M9, seu intervalo é
  truncado na borda da janela.
- Intervalos simultâneos não são somados duas vezes no cálculo de
  indisponibilidade.
- Um incidente que afeta vários componentes conta uma vez no total da
  plataforma e uma vez em cada estrato de componente afetado; os dois totais
  não devem ser confundidos.
- Valores ausentes de `fim_utc`, `impacto` ou componente não são imputados sem
  evidência. Eles são contabilizados e excluídos somente da métrica que exige o
  campo.
- M4 é chamada de **proxy de MTBF**, pois as páginas de status observam
  incidentes publicados, não todas as falhas internas do serviço.

## Hipóteses

As hipóteses são bilaterais porque não há justificativa prévia para assumir
qual plataforma terá o maior valor. A unidade de comparação primária é a
plataforma dentro da mesma janela e do mesmo conjunto de componentes
equivalentes.

### Frequência de incidentes (Q1/M1)

- **H₀-F:** a distribuição mensal da frequência de incidentes é igual no
  GitHub.com e no GitLab.com; operacionalmente, a mediana das diferenças
  pareadas entre as contagens dos mesmos meses é zero.
- **H₁-F:** a distribuição mensal da frequência de incidentes difere entre
  GitHub.com e GitLab.com; operacionalmente, a mediana das diferenças pareadas
  entre os mesmos meses é diferente de zero.

### Tempo de recuperação (Q2/M2–M3)

- **H₀-R:** a distribuição das durações dos incidentes, incluindo sua
  mediana, é igual no GitHub.com e no GitLab.com.
- **H₁-R:** a distribuição das durações dos incidentes difere entre
  GitHub.com e GitLab.com.

A escolha do teste, o nível de significância e o tamanho de efeito serão
pré-definidos no plano de análise após verificar somente os pressupostos
necessários, sem escolher o método pelo resultado de significância.

## As métricas podem ser "jogadas"?

Sim. A página de status é uma fonte operacional valiosa, mas o fornecedor
controla o processo que transforma uma falha real em um incidente publicado:
equipes de SRE/operações e gestores de incidente decidem os limiares de
detecção, quando abrir o incidente, quais componentes e impactos marcar, quando
agrupar ocorrências e quando declarar a resolução. Os critérios internos podem
diferir entre GitHub e GitLab e mudar ao longo do tempo.

- **Lei de Goodhart:** se "menos incidentes" ou "maior disponibilidade" vira
  meta, há incentivo para elevar o limiar de publicação, agrupar eventos ou
  encerrar o registro antes da recuperação completa. A métrica deixa de ser uma
  boa representação quando passa a ser o alvo.
- **Lei de Campbell:** quanto maior a consequência gerencial ou comercial do
  indicador, maior a pressão para distorcer classificações, componentes,
  horários ou o que conta como incidente. Isso não implica fraude; regras
  operacionais legítimas também podem favorecer um número melhor.
- **Falácia de McNamara:** contar apenas o que a página quantifica ignora falhas
  não detectadas ou não publicadas, quantidade de usuários afetados, regiões,
  operações que falharam, perdas de produtividade e degradações parciais. Um
  incidente curto e global não é necessariamente menos danoso que um incidente
  longo e restrito.

### Mitigações

1. versionar as respostas brutas e manter `fonte` e `url` em cada registro;
2. calcular duração a partir dos timestamps, sem alterar retroativamente a
   narrativa publicada;
3. comparar somente componentes equivalentes e aplicar as mesmas regras às duas
   plataformas;
4. apresentar contagem, duração, intervalo e gravidade em conjunto, sem reduzir
   confiabilidade a um único ranking;
5. triangular incidentes com relatórios oficiais detalhados e, em Q4, com uma
   reconstrução independente normalizada para a mesma janela;
6. executar análises de sensibilidade para sobreposições, dados ausentes,
   incidentes multicomponente e diferenças de cobertura entre fontes;
7. interpretar os resultados como **incidentes publicados**, não como todas as
   falhas que ocorreram nas plataformas.

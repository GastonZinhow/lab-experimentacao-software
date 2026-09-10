# Katas do Experimento (K01-K06)

Issue #22 do Lab02: selecao e validacao de 6 katas Java de dificuldade
variada para o experimento "Assistentes de IA vs. codificacao manual".

## Origem e decisao do grupo

Os 6 katas usados no experimento sao os mesmos problemas do LeetCode ja
resolvidos por um integrante do grupo no trabalho pratico da disciplina de
FPAA (Fundamentos de Projeto e Analise de Algoritmos). A decisao de
reaproveita-los foi tomada conscientemente pelo grupo, mesmo sabendo que
isso diverge da recomendacao do enunciado do Lab02 de preferir "katas
autorais do grupo/professor ou exercicios pouco indexados" para reduzir o
risco de memorizacao pelo assistente de IA.

**Essa decisao e registrada aqui como uma ameaca a validade aceita e
documentada** (ver tambem `desenho_experimento.md`, secao "Ameacas a
validade"): como os 6 problemas sao exercicios classicos e amplamente
indexados do LeetCode, com solucoes publicas conhecidas (inclusive no
proprio GitHub do integrante que os resolveu no trabalho de FPAA), o
assistente de IA (GitHub Copilot com GPT-5) pode reproduzir uma solucao
memorizada durante seu treinamento em vez de efetivamente "ajudar" o
participante a raciocinar sobre o problema. Isso pode inflar
artificialmente o desempenho do tratamento `IA` nas RQ1 e RQ2 em relacao ao
que se observaria com katas ineditos. Essa limitacao deve ser retomada na
discussao do Relatorio Final.

## Criterios de selecao

- **Mescla de dificuldades**: ao contrario da recomendacao de dificuldade
  homogenea, o grupo optou por uma mescla deliberada de katas faceis,
  medios e dificeis (ver tabela abaixo), para observar se o efeito do
  assistente de IA varia conforme a complexidade do problema.
- **Diversidade de tecnicas algoritmicas**: os 6 katas cobrem tecnicas
  distintas (dois ponteiros, busca em largura, programacao dinamica,
  guloso/grafos, backtracking), evitando que o resultado do experimento
  reflita apenas uma unica categoria de algoritmo.
- **Testes de aceitacao prontos**: cada kata tem uma classe
  `SolutionTest` em JUnit 5 baseada nos casos de exemplo oficiais do
  LeetCode para o problema correspondente.
- **Numero par**: 6 katas, permitindo dividir exatamente 3 com IA / 3 sem
  IA por participante (ver `desenho_experimento.md`).
- Os katas mais custosos de implementar do zero dentro do time-box de 35
  minutos (ex.: os que exigem BFS sobre estado composto, deteccao de ciclo
  em grafo direcionado, ou DFS sobre grade com leitura customizada de
  entrada) foram deixados de fora desta selecao, mesmo constando no
  trabalho de FPAA original, para manter os 6 katas escolhidos viaveis
  dentro do tempo limite.

## Tabela de katas

| Kata | Problema | Dificuldade | Tecnica | Fonte |
|---|---|---|---|---|
| K01 | Is Subsequence | Facil | Dois ponteiros | leetcode.com/problems/is-subsequence |
| K02 | Find if Path Exists in Graph | Facil | BFS em grafo nao direcionado | leetcode.com/problems/find-if-path-exists-in-graph |
| K03 | House Robber | Media | Programacao dinamica | leetcode.com/problems/house-robber |
| K04 | Flower Planting With No Adjacent | Media | Guloso sobre grafo | leetcode.com/problems/flower-planting-with-no-adjacent |
| K05 | Longest Cycle in a Graph | Dificil | Deteccao de ciclo em grafo direcionado | leetcode.com/problems/longest-cycle-in-a-graph |
| K06 | N-Queens II | Dificil | Backtracking | leetcode.com/problems/n-queens-ii |

## K01 - Is Subsequence

**Pacote:** `katas.k01`

Dadas duas strings `s` e `t`, determinar se `s` e uma subsequencia de `t`
(isto e, se e possivel obter `s` removendo alguns caracteres de `t`, sem
reordenar os caracteres restantes).

Exemplos oficiais: `s="abc", t="ahbgdc"` -> `true`; `s="axc", t="ahbgdc"`
-> `false`.

## K02 - Find if Path Exists in Graph

**Pacote:** `katas.k02`

Dado um grafo nao direcionado com `n` vertices e uma lista de arestas,
determinar se existe um caminho entre um vertice de origem e um vertice de
destino.

Exemplos oficiais: `n=3, edges=[[0,1],[1,2],[2,0]], source=0,
destination=2` -> `true`; `n=6, edges=[[0,1],[0,2],[3,5],[5,4],[4,3]],
source=0, destination=5` -> `false`.

## K03 - House Robber

**Pacote:** `katas.k03`

Dado um vetor com o valor de dinheiro guardado em cada casa de uma rua,
determinar o valor maximo que pode ser roubado sem roubar duas casas
adjacentes.

Exemplos oficiais: `nums=[1,2,3,1]` -> `4`; `nums=[2,7,9,3,1]` -> `12`.

## K04 - Flower Planting With No Adjacent

**Pacote:** `katas.k04`

Dados `n` jardins e uma lista de caminhos (arestas) entre pares de
jardins, atribuir a cada jardim um entre 4 tipos de flores, de forma que
nenhum par de jardins conectados por um caminho tenha o mesmo tipo de
flor. Qualquer atribuicao valida e aceita (o problema garante que sempre
existe solucao, pois cada jardim tem no maximo 3 vizinhos).

## K05 - Longest Cycle in a Graph

**Pacote:** `katas.k05`

Dado um grafo direcionado com `n` vertices em que cada vertice tem no
maximo uma aresta de saida, representado por um vetor `edges`, encontrar
o tamanho do maior ciclo existente. `edges[i]` indica o proximo vertice
alcancado a partir de `i`; quando `edges[i] = -1`, o vertice nao possui
aresta de saida.

Exemplos oficiais: `edges=[3,3,4,2,3]` -> `3`;
`edges=[2,-1,3,1]` -> `-1`.

## K06 - N-Queens II

**Pacote:** `katas.k06`

Dado um inteiro `n`, retornar o numero de solucoes distintas do problema
das `n` rainhas (posicionar `n` rainhas em um tabuleiro `n x n` de forma
que nenhuma ataque outra).

Exemplos oficiais: `n=4` -> `2`; `n=1` -> `1`.

## Observacoes de validacao

- Todos os katas foram implementados com o esqueleto (`Solution.java`
  lancando `UnsupportedOperationException`) e os testes de aceitacao
  (`SolutionTest.java`) no projeto `lab02/code/katas-java`, seguindo as
  assinaturas de metodo originais do LeetCode para cada problema.
- Antes de qualquer implementacao, `mvn test -Dtest=katas.k0N.*Test` falha
  para todos os katas (0% de testes passando), confirmando que cada kata
  esta corretamente "vazio" no inicio do trial.
- Para K04 (Flower Planting), como existe mais de uma atribuicao valida de
  flores, os testes de aceitacao verificam a propriedade de validade da
  solucao (nenhum par adjacente com a mesma flor, valores entre 1 e 4),
  em vez de comparar com uma unica saida esperada.

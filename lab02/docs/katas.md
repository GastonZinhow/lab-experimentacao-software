# Katas do Experimento (K01-K06)

Issue #22 do Lab02: selecao e validacao de 6 katas Java de dificuldade
comparavel para o experimento "Assistentes de IA vs. codificacao manual".

## Criterios de selecao

- **Dificuldade comparavel**: todos os katas tem escopo de uma unica classe
  `Solution`, entre 3 e 5 metodos publicos, resolviveis dentro do time-box de
  35 minutos por um estudante de graduacao com conhecimento basico de Java.
- **Baixa indexacao / risco de memorizacao**: nenhum kata e uma copia de um
  exercicio classico de plataformas como LeetCode/HackerRank/Codewars. Todos
  sao autorais do grupo, ambientados em um cenario fictício de sistema
  universitario (cantina, matricula, grade horaria), o que reduz a chance de
  o assistente de IA ja ter visto a solucao exata durante o treinamento.
- **Testes de aceitacao prontos**: cada kata tem uma classe
  `SolutionTest` em JUnit 5 que define o "pronto" da tarefa. Os testes nao
  sao alterados pelo participante durante o trial.
- **Numero par**: 6 katas, permitindo dividir exatamente 3 com IA / 3 sem IA
  por participante (ver `desenho_experimento.md`).

## K01 - Fila de Atendimento com Prioridade

**Pacote:** `katas.k01`

Na fila da cantina, alguns estudantes tem prioridade de atendimento (ex.:
pessoas com deficiencia, gestantes). Implemente uma fila que:

- atende primeiro quem tem prioridade, na ordem em que chegaram entre os
  prioritarios;
- atende os demais em ordem de chegada (FIFO), somente apos esgotar todos os
  prioritarios presentes no momento do atendimento.

**Dificuldade estimada:** baixa-media (estrutura de dados simples, duas
filas).

**Fonte:** kata autoral do grupo.

## K02 - Calculo de Desconto por Combo

**Pacote:** `katas.k02`

O sistema de vendas da cantina aplica desconto quando o cliente compra um
combo (uma unidade de "principal" + uma unidade de "bebida" no mesmo
pedido). Implemente o calculo do valor total de um pedido, aplicando um
percentual de desconto sobre o item de menor valor do combo sempre que um
combo completo puder ser formado no pedido.

**Dificuldade estimada:** media (agrupamento por categoria + regra de
formacao de pares).

**Fonte:** kata autoral do grupo.

## K03 - Validador de Codigo de Matricula

**Pacote:** `katas.k03`

Códigos de matricula da universidade seguem o formato `AAYYNNNNN-D`, onde
`AA` é a sigla do curso (2 letras maiusculas), `YY` é o ano de ingresso (2
digitos), `NNNNN` é um numero sequencial (5 digitos) e `D` é um digito
verificador calculado como a soma de todos os digitos numericos do codigo
(YY + NNNNN) modulo 10. Implemente a validacao do formato e do digito
verificador.

**Dificuldade estimada:** media (parsing de string + regra aritmetica).

**Fonte:** kata autoral do grupo.

## K04 - Agrupador de Notas por Conceito

**Pacote:** `katas.k04`

Dada uma lista de notas numericas (0-10) de uma turma, implemente a
conversao de cada nota para um conceito (`A`: nota >= 9, `B`: >= 7, `C`: >=
5, `D`: < 5) e o calculo de estatisticas da turma: a mediana das notas e o
conceito mais frequente (em caso de empate, o conceito alfabeticamente
menor).

**Dificuldade estimada:** media (ordenacao, mediana, contagem de frequencia).

**Fonte:** kata autoral do grupo.

## K05 - Detector de Conflito de Horario

**Pacote:** `katas.k05`

Cada disciplina da grade horaria de um estudante tem um dia da semana e um
horario de inicio/fim (em minutos desde 00:00). Implemente a deteccao de
conflitos: duas disciplinas conflitam se estao no mesmo dia e os intervalos
de horario se sobrepoem (sobreposicao parcial conta como conflito; um
terminar exatamente quando o outro comeca nao conta). O metodo deve
retornar todos os pares de disciplinas em conflito.

**Dificuldade estimada:** media (comparacao de intervalos, combinacao de
pares).

**Fonte:** kata autoral do grupo.

## K06 - Compactador de Texto Simples

**Pacote:** `katas.k06`

Implemente uma compactacao Run-Length Encoding customizada para as
observacoes de texto do sistema da cantina: apenas sequencias de 3 ou mais
caracteres iguais consecutivos sao compactadas no formato `<caractere><contagem>`;
sequencias menores que 3 permanecem inalteradas, caractere a caractere.
Implemente tambem a descompactacao (operacao inversa).

**Dificuldade estimada:** media (parsing de string, dois metodos
complementares).

**Fonte:** kata autoral do grupo.

## Observacoes de validacao

- Todos os katas foram implementados com o esqueleto (`Solution.java`
  lancando `UnsupportedOperationException`) e os testes de aceitacao
  (`SolutionTest.java`) no projeto `lab02/code/katas-java`.
- Antes de qualquer implementacao, `mvn test -Dtest=katas.k0N.*Test` falha
  para todos os katas (0% de testes passando), confirmando que cada kata
  esta corretamente "vazio" no inicio do trial.
- Justificativa de dificuldade comparavel: todos os 6 katas exigem uso de
  estruturas de dados basicas (listas, mapas), manipulacao de string ou
  aritmetica simples, e nenhum exige bibliotecas externas alem do JDK
  padrao.

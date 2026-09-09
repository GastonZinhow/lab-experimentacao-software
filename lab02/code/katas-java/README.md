# katas-java

Projeto Maven + JUnit 5 usado para resolver os katas do experimento
"Assistentes de IA vs. codificação manual" (LAB02, issue #19).

## Requisitos

- Java 21+ (o projeto compila com `maven.compiler.release=21`; um JDK mais
  novo com suporte a `--release 21`, ex.: JDK 21 ou 25, funciona)
- Maven 3.6+

Conferir as versões instaladas:

```
java -version
mvn -version
```

## Estrutura

Cada kata vive em seu próprio pacote `katas.kNN`, com:

- `src/main/java/katas/kNN/Solution.java` — esqueleto da solução. Durante um
  trial, os métodos começam lançando `UnsupportedOperationException` e o
  participante os implementa dentro do time-box (35 min, ver
  `lab02/docs/02 - LABORATORIO 02.md`).
- `src/test/java/katas/kNN/SolutionTest.java` — testes de aceitação em
  JUnit 5, já prontos e **não alterados** pelo participante durante o trial.
  São eles que definem "passou" e alimentam o script de cronometragem
  (issue #20, `lab02/code/scripts/register_trial.py`).

`katas.k00example` é um kata de exemplo (não faz parte do experimento) que
serve apenas como template para a issue #22 (seleção dos 6 katas reais).

## Rodando os testes

Todos os katas:

```
mvn test
```

Um kata específico:

```
mvn test -Dtest=katas.k01.*Test
```

Saída esperada (exemplo, kata de exemplo K00): `target/surefire-reports/`
mostra `Tests run: 7, Failures: 0, Errors: 0`.

**Troubleshooting:** se `mvn test` falhar com `invalid target release: 21` (ou
similar), o `JAVA_HOME` usado pelo Maven está apontando para um JDK anterior
ao 21 — aponte-o para um JDK 21+ (`mvn -version` mostra qual Java o Maven
está usando) e rode novamente.

## Adicionando um kata real (K01–K06)

1. Criar `src/main/java/katas/k0N/Solution.java` com o esqueleto dos métodos
   (assinatura completa, corpo lançando `UnsupportedOperationException`).
2. Criar `src/test/java/katas/k0N/SolutionTest.java` com os testes de
   aceitação que definem o kata.
3. Confirmar que `mvn test -Dtest=katas.k0N.*Test` falha (0% passando) antes
   de qualquer implementação — isso valida que o kata está corretamente
   "vazio" no início de cada trial.
4. Documentar o kata (enunciado, dificuldade estimada, fonte) na issue #22.

O script `lab02/code/scripts/register_trial.py` assume esse layout: ele roda
`mvn test -Dtest=katas.<kata>.*Test` sobre este projeto e lê o resultado em
`target/surefire-reports/`.

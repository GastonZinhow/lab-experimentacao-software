# Apresentação oral: perguntas da Luisa (1, 3, 4, 11 e 14)

Respostas de cerca de 30 segundos cada. O professor pode pedir qualquer pergunta a qualquer integrante.

## Pergunta 1: qual é o cenário e o que H₀ e H₁ afirmam, em palavras simples?

**Onde mostrar:** seção 1 (Cenário).

Queremos saber se **módulos maiores têm mais defeitos**. O tamanho é medido em linhas de código (LOC), e os defeitos são os registrados para cada classe. **H₀** diz que não há associação: saber o tamanho de uma classe não diz nada sobre quantos defeitos ela tem. **H₁** diz que há associação, para mais ou para menos. Comparamos dois testes que respondem a essa mesma pergunta: Pearson, que olha a relação linear nos valores, e Spearman, que olha a tendência nos postos.

## Pergunta 3: como os dados reais foram coletados e o que mostraram sobre a forma da distribuição?

**Onde mostrar:** seção 1 (origem dos dados) e seção 2, no G1.

Usamos o dataset público **KC1, da NASA, disponibilizado pelo PROMISE**, no nível de classe, que traz o LOC e o número de defeitos de 145 classes. Sorteamos **30 classes** com semente fixa, sem escolher a dedo. Os dados são **muito assimétricos**: a mediana é de 214 LOC, mas a maior classe tem 2.883 LOC; e **63% das classes não têm nenhum defeito**, enquanto uma chega a 101. Ou seja, muitos módulos pequenos e sem defeito, e poucos módulos grandes concentrando os valores altos. Isso está longe de uma normal.

## Pergunta 4: como os dados reais ajudaram a escolher os parâmetros da simulação?

**Onde mostrar:** seção 2, no G1 e na tabela "parâmetros da simulação".

A forma dos dados escolheu as distribuições, e a amostra deu os números:

- **LOC:** positivo e assimétrico, então usamos uma **lognormal**, com μ = 5,24 e σ = 1,46 estimados na amostra (mediana de cerca de 188 LOC).
- **Defeitos:** uma contagem com muitos zeros e variância muito maior que a média, então usamos uma **binomial negativa**, com média 7,63 e k = 0,115.
- **Associação:** as duas variáveis são ligadas por uma cópula, e o efeito 0,61 reproduz o ρ = 0,51 observado.

O G1 mostra que a simulação reproduz a forma real, por exemplo 62% de módulos sem defeito contra 63% na amostra.

## Pergunta 11: que violação de pressuposto simulamos e por que ela afeta mais um teste do que o outro?

**Onde mostrar:** seção 2 (tabela de situações), G3 na seção 4 e G4 na seção 5.

Simulamos três situações:

- **`normal`:** onde os pressupostos do Pearson valem, como comparação.
- **`base`:** com a **assimetria e os empates em zero** dos dados reais.
- **`outliers`:** com **módulos atípicos** independentes.

A violação afeta mais o **Pearson** porque ele usa os **valores**: um módulo extremo pesa muito no r. O Spearman usa os **postos**, e um valor extremo vira só o maior posto. Com outliers, o Pearson ficou liberal no erro tipo I (6,00% contra 5,18%) e perdeu muito poder: no efeito 0,5, detectou a associação em 23% das vezes, contra 51% do Spearman. Já na situação normal, o Pearson teve mais poder (83% contra 78%).

## Pergunta 14: nos dados reais, os testes chegaram à mesma conclusão? O efeito tem importância prática?

**Onde mostrar:** seção 6 (Dados reais).

Sim, **os dois rejeitam H₀**: r = 0,84 (p < 0,001) e ρ = 0,51 (p = 0,004). Mas a força é diferente: o r é inflado por **uma única classe**, com 2.883 LOC e 101 defeitos. Sem ela, o r cai para 0,58, e o ρ quase não muda (0,45), e os dois continuam significativos.

Na prática, um ρ em torno de 0,5 é uma tendência clara, mas não determinística. Há uma classe de 1.108 LOC sem nenhum defeito. Então o tamanho serve para **priorizar** revisões e testes nas classes maiores, não para prever quantos defeitos cada uma terá. E, com 30 classes, o intervalo do ρ é largo, de 0,17 a 0,75.

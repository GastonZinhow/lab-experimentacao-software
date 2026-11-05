# Interpretação dos testes em um conjunto simulado

Issue #78. Os testes de Pearson e de Spearman aplicados a **um** conjunto simulado, para mostrar como cada um decide. Qual teste é melhor no cenário só será respondido pelas simulações de erro tipo I e de poder (Q1 a Q3).

## Como o conjunto foi gerado

| Item | Valor |
|---|---|
| Gerador | `gerar` real, de `lab04/code/gerador.py` (issue #77) |
| Situação | `base` (LOC lognormal e defeitos binomial negativa, calibrados no KC1) |
| `efeito` | 0,612, o valor calibrado para o ρ simulado se aproximar do ρ = 0,51 da amostra real |
| n | 30 módulos, o mesmo tamanho da amostra real |
| Semente | `numpy.random.default_rng(42)` |
| Testes | `aplicar_testes` de `lab04/code/testes.py` (`scipy.stats.pearsonr` e `scipy.stats.spearmanr`), bicaudais |
| α | 0,05 |

Para refazer: `python lab04/code/etapas/02_exemplo_testes.py`, que grava `lab04/code/resultados/exemplo_testes.json`.

Como `efeito` ≠ 0, **neste conjunto H₀ é falsa**: LOC e defeitos foram gerados com associação. Com dados simulados, sabemos de antemão a resposta certa, o que não acontece com dados reais.

## Como é o conjunto

- LOC vai de 11 a 1.122, com mediana de 217.
- 21 dos 30 módulos (70%) não têm defeito. Os outros 9 têm de 1 a 64 defeitos.
- Os 16 menores módulos (até 227 LOC) têm todos zero defeito. Os defeitos aparecem a partir de 294 LOC, mas sem crescer junto com o tamanho: o módulo com mais defeitos (64) tem 294 LOC, e os dois maiores (743 e 1.122 LOC) não têm nenhum.

## Resultado

| Teste | Coeficiente (tamanho do efeito) | Magnitude | Estatística | p-valor | Decisão (α = 0,05) |
|---|---|---|---|---|---|
| Pearson | r = 0,150 | fraca | t = 0,80 (28 g.l.) | 0,430 | Não rejeita H₀ |
| Spearman | ρ = 0,510 | forte | — | 0,004 | Rejeita H₀ |

A magnitude segue os limiares de Cohen (1988) para |r|, usados também para |ρ|: menos de 0,1 é desprezível, de 0,1 a 0,3 é fraca, de 0,3 a 0,5 é moderada e 0,5 ou mais é forte. O coeficiente já é o tamanho do efeito, então não há outra medida a calcular.

### Pearson

- **Coeficiente:** r = 0,15, uma associação linear fraca e positiva.
- **p-valor:** 0,43. Se LOC e defeitos fossem independentes, um |r| igual ou maior que 0,15 apareceria em cerca de 43% das amostras de 30 módulos.
- **Conclusão:** não rejeitamos H₀. Os dados não dão evidência de associação **linear** entre tamanho e defeitos.

### Spearman

- **Coeficiente:** ρ = 0,51, uma associação monotônica forte e positiva.
- **p-valor:** 0,004. Se LOC e defeitos fossem independentes, um |ρ| igual ou maior que 0,51 apareceria em cerca de 0,4% das amostras.
- **Conclusão:** rejeitamos H₀. Há evidência de que módulos maiores tendem a ter mais defeitos.

### Por que r e ρ discordam

Os dois coeficientes medem coisas diferentes:

- **O r usa os valores.** Cada módulo pesa conforme a distância à média nas duas variáveis. Os dois maiores módulos (1.122 e 743 LOC) estão muito acima da média de LOC (316) e não têm defeito, então puxam o r para baixo: sozinhos, respondem por cerca de 40% da soma dos produtos que forma o r, com sinal negativo. O módulo com 64 defeitos tem 294 LOC, um pouco abaixo da média, e também contribui com sinal negativo. Como a relação nos valores não é uma reta, o r fica perto de zero.
- **O ρ usa os postos.** Ele só pergunta se os módulos maiores tendem a ficar à frente na ordem de defeitos, sem importar por quanto. Os 16 menores módulos têm zero defeito e 9 dos 14 maiores têm algum, uma tendência clara de crescimento. O 1.122 LOC conta apenas como o último posto de LOC, e os 64 defeitos contam apenas como o último posto de defeitos.

Nenhum ponto isolado explica a diferença. Sem o maior módulo, o r sobe para 0,22 (p = 0,24); sem o módulo de 64 defeitos, sobe para 0,32 (p = 0,09). Em nenhum dos casos o Pearson rejeita H₀, enquanto o Spearman continua rejeitando. A causa é a forma dos dados: as duas variáveis são muito assimétricas, e a associação gerada pela cópula é monotônica, não linear.

### O que isso mostra (e o que não mostra)

- Neste conjunto, o **Pearson cometeu um erro tipo II**: havia associação e ele não a detectou. O Spearman acertou.
- Um conjunto só não basta para dizer qual teste é melhor. Outra semente poderia inverter o resultado. É por isso que a Q1 e a Q2 repetem o teste em 10.000 conjuntos.
- O p-valor **não** é a probabilidade de H₀ ser verdadeira, nem mede a força da associação. Quem mede a força é o próprio r ou ρ.

## Observação sobre o p-valor do Spearman

O `scipy.stats.spearmanr` calcula o p-valor por uma aproximação pela t com n − 2 graus de liberdade. Como 70% dos módulos empatam em zero defeito, conferimos esse valor com a distribuição de ρ simulada sob H₀ (10.000 conjuntos com `efeito = 0`, usada no G2). A proporção de |ρ| ≥ 0,51 na simulação é 0,0046, próxima do 0,004 da aproximação. A região de rejeição simulada (ρ ≤ −0,370 ou ρ ≥ 0,363) também fica perto da aproximada (|ρ| ≥ 0,361). Com n = 30, os empates não mudam a decisão.

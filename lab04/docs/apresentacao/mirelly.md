# Apresentação oral: perguntas da Mirelly (2, 5, 6, 7 e 9)

Respostas de cerca de 30 segundos cada. Lembrete: o professor pode pedir a qualquer integrante que responda a qualquer pergunta.

## Pergunta 2: o teste é unicaudal ou bicaudal? Por quê?

**Onde mostrar:** seção 1 (Cenário) e o G2, na seção 3.

É **bicaudal**. A expectativa mais comum é de que módulos maiores tenham mais defeitos, mas o sentido contrário também interessaria: significaria que dividir o código em módulos menores não reduz defeitos. Como nenhum dos dois sentidos podia ser descartado antes de ver os dados, testamos correlação diferente de zero. Por isso o α de 5% é dividido entre as duas caudas, 2,5% em cada, como aparece no G2.

## Pergunta 5: o que cada um dos dois testes compara de fato?

**Onde mostrar:** seção 3 (Como os testes funcionam), no texto do G2.

O **Pearson** compara os **valores**: mede se LOC e defeitos crescem juntos em linha reta, e cada módulo pesa conforme a distância à média. O **Spearman** compara os **postos**: troca cada valor pela sua posição na ordem e mede se os módulos maiores tendem a ter mais defeitos, sem importar quanto. No nosso exemplo simulado, deu r = 0,15 e ρ = 0,51, porque os maiores módulos não tinham defeito e puxaram o r para baixo, mas no ρ contam só como os últimos postos.

## Pergunta 6: no G2, o que é a distribuição sob H₀ e por que a região de rejeição fica onde fica?

**Onde mostrar:** seção 3, no G2.

A curva mostra os valores que a estatística assume quando **não existe associação**, repetindo a amostra de 30 módulos muitas vezes. Ela fica centrada em zero. No Pearson é a t com 28 graus de liberdade, que é teórica; no Spearman, simulamos 10.000 conjuntos, porque 70% dos módulos empatam em zero defeito. A região de rejeição fica nas **duas pontas**, porque o teste é bicaudal: são os 5% de valores mais extremos, |t| ≥ 2,05 e |ρ| ≥ cerca de 0,36. Valores ali são raros se H₀ for verdadeira.

## Pergunta 7: o que significa o p-valor do exemplo mostrado no G2? E o que ele não significa?

**Onde mostrar:** seção 3, nas áreas coloridas do G2.

O p-valor é a área colorida: a probabilidade de uma correlação tão forte quanto a observada, ou mais, **se não houvesse associação**. No Spearman, p = 0,004: só 0,4% das amostras dariam ρ ≥ 0,51 por acaso, então rejeitamos H₀. No Pearson, p = 0,43: um r de 0,15 é comum por acaso, então não rejeitamos.

O p-valor **não** é a probabilidade de H₀ ser verdadeira, **não** mede a força da associação (quem mede é r ou ρ) e "não rejeitar" **não** prova que não há associação. Aliás, nesse exemplo a associação existia, e o Pearson cometeu um erro tipo II.

## Pergunta 9: no G3, algum teste se afastou de 5%? Ficou liberal ou conservador, e por quê?

**Onde mostrar:** seção 4 (Erro tipo I), no G3.

Sim, o **Pearson**, e ele ficou **liberal**: encontra associação que não existe com mais frequência que os 5% prometidos. A faixa cinza do G3 é 5% ± 0,43 ponto percentual, a variação esperada com 10.000 conjuntos.

| Situação | Pearson | Spearman |
|---|---|---|
| `normal` | 5,35% (perto de 5%) | 5,41% (perto de 5%) |
| `base` | **5,92% (liberal)** | 5,58% (um pouco acima) |
| `outliers` | **6,00% (liberal)** | 5,18% (perto de 5%) |

Na situação **normal**, que é onde os pressupostos do Pearson valem, os dois ficam dentro da faixa. Quando os dados ficam **assimétricos** (base) ou ganham **módulos atípicos** (outliers), o Pearson passa do limite. O motivo é que o p-valor dele supõe dados aproximadamente normais, e um único módulo extremo pode produzir um r alto por acaso. O **Spearman** usa postos, então o valor extremo vira só o último posto, e ele fica perto de 5% nas três situações.

**Se perguntarem do Spearman na situação base (5,58%):** repetimos com 200.000 conjuntos fora do pipeline, só como conferência. O Pearson ficou em 5,83% e o Spearman em 5,13%, com margem de ± 0,10 ponto percentual. Ou seja, o desvio do Pearson é real, e o do Spearman, com 10.000 conjuntos, é em boa parte variação da simulação.

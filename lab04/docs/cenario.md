# Cenário do Lab04: tamanho do módulo × número de defeitos

**Par de testes:** P5, correlação de Pearson × correlação de Spearman.

## Pergunta

Módulos de software maiores (em LOC) têm mais defeitos registrados?

## Hipóteses

- **H₀:** não há associação entre o tamanho do módulo e o número de defeitos (correlação igual a zero).
- **H₁:** há associação entre o tamanho do módulo e o número de defeitos (correlação diferente de zero).

Cada teste mede a correlação à sua maneira: Pearson avalia a associação **linear** nos valores, e Spearman avalia a associação **monotônica** nos postos.

**O teste é bicaudal.** A expectativa mais comum é de que módulos maiores tenham mais defeitos, mas o sentido contrário também interessaria: significaria que dividir o código em módulos menores não reduz defeitos. Por isso nenhum dos dois sentidos foi descartado antes de ver os resultados. O nível de significância é α = 0,05.

## Dados reais

| Item | Valor |
|---|---|
| Dataset | KC1, nível de classe, com contagem de defeitos (NASA MDP, via PROMISE) |
| Endereço | <http://promise.site.uottawa.ca/SERepository/datasets/kc1-class-level-numericdefect.arff> |
| Arquivo no repositório | `lab04/code/dados/brutos/kc1-class-level-numericdefect.arff` |
| SHA-256 | `e83d22835bc98e4602acce372900c2d75bae0b52d073f6fa1f13984a64c0f9da` |
| Data do download | 05/11/2026 |
| Referência | Koru, A. G.; Liu, H. *An Investigation of the Effect of Module Size on Defect Prediction Using Static Measures*. PROMISE, ICSE 2005 |
| Módulo | Uma classe do sistema KC1 |
| LOC | Coluna `sumLOC_TOTAL`: soma das linhas de código dos métodos da classe |
| Defeitos | Coluna `NUMDEFECTS`: número de defeitos registrados para a classe |

**Seleção:** amostra aleatória simples, sem reposição, de 30 das 145 classes, com a semente `numpy.random.default_rng(42)`. O resultado está em `lab04/code/dados/amostra_kc1.csv`. Para refazê-la, rode `python lab04/code/etapas/01_preparar_dados.py`.

## Estatísticas descritivas

| Estatística | LOC, amostra (n = 30) | Defeitos, amostra (n = 30) | LOC, dataset (n = 145) | Defeitos, dataset (n = 145) |
|---|---|---|---|---|
| Média | 419,9 | 7,63 | 296,3 | 4,61 |
| Mediana | 213,5 | 0 | 162 | 0 |
| Desvio-padrão | 620,9 | 19,77 | 448,0 | 10,86 |
| Máximo | 2.883 | 101 | 2.883 | 101 |
| Assimetria | 2,66 | 3,85 | 3,40 | 5,53 |
| Outliers (regra do IQR) | 5 | 4 | 15 | 21 |
| Módulos com zero defeito | — | 63,3% | — | 58,6% |

Os dados são muito assimétricos: a maioria das classes é pequena e não tem defeito registrado, e poucas concentram os valores altos.

A correlação descritiva já mostra a diferença entre os testes. Na amostra, **r = 0,84 e ρ = 0,51**; no dataset completo, r = 0,69 e ρ = 0,57. A classe com 2.883 LOC e 101 defeitos pesa muito no r, mas no ρ conta apenas como o posto mais alto. O teste formal nos dados reais fica para a issue #83.

**Atenção:** a amostra sorteou justamente a maior classe do dataset e tem média de defeitos maior que a do dataset completo (7,63 contra 4,61). Os parâmetros abaixo herdam essa característica.

## Como os dados são simulados

Os parâmetros são estimados na amostra de 30 classes, por máxima verossimilhança, e ficam em `lab04/code/dados/parametros.json`.

| Variável | Distribuição | Parâmetros | Por que essa distribuição |
|---|---|---|---|
| LOC | Lognormal, arredondada, mínimo 1 | μ = 5,237; σ = 1,461 (mediana teórica de cerca de 188 LOC) | LOC é positivo e muito assimétrico à direita |
| Defeitos | Binomial negativa | média = 7,63; k = 0,115 | É uma contagem com variância muito maior que a média e muitos zeros (61,7% simulados contra 63,3% na amostra) |

**Associação:** as duas variáveis são ligadas por uma cópula gaussiana, que controla a associação sem mudar a forma de cada variável. O `efeito` do gerador é a correlação das normais latentes da cópula, e **não é igual a r nem a ρ observados**.

- `efeito = 0`: as variáveis são independentes, então H₀ é verdadeira.
- `efeito = 0,612`: valor calibrado para que o ρ simulado se aproxime do ρ = 0,51 observado na amostra. É uma referência útil para escolher os efeitos da Q2.

**Limitações do ajuste:**

- A binomial negativa simula a cauda de defeitos com valores mais altos que os observados (o máximo chega a centenas em 200.000 módulos simulados), consequência da média e da dispersão estimadas com poucas classes.
- A forma geral é reproduzida, mas há diferenças nas faixas intermediárias: 200–499 LOC têm 40% dos módulos reais e 23% dos simulados, e 1–5 defeitos têm 7% dos reais e 17% dos simulados. Com 30 módulos, cada faixa fica com poucas observações, e isso explica parte da diferença.

## O que o grupo espera antes de simular

Registrado antes de qualquer simulação de erro tipo I ou de poder.

**Esperamos que o Spearman se saia melhor neste cenário**, pelos seguintes motivos:

- **Erro tipo I:** o p-valor do teste de Pearson pressupõe dados aproximadamente normais, e aqui as duas variáveis são muito assimétricas. Esperamos que ele se afaste mais de 5%. O Spearman usa postos, então os valores extremos não pesam. O ponto de atenção é o grande número de empates em zero defeito, que pode afastá-lo um pouco de 5%.
- **Poder:** esperamos que o Spearman detecte a associação com mais frequência, porque a relação gerada é monotônica e não linear nos valores originais, e poucos pontos extremos aumentam a variabilidade do r.
- **O que mudaria nossa opinião:** o Pearson manter o erro tipo I perto de 5% e ter poder igual ou maior. Isso é possível, porque os valores extremos de LOC e de defeitos também podem aparecer juntos e reforçar o r quando há associação.

## Situações simuladas (Q3)

A situação `base` foi calibrada com dados reais e, por isso, **já viola** a normalidade que o p-valor do Pearson pressupõe. Para a Q3 mostrar o efeito da violação, o gerador tem três situações, em ordem crescente de problemas. Em todas, `efeito = 0` mantém LOC e defeitos independentes, ou seja, H₀ verdadeira.

| Situação | Como é gerada | O que viola | Por que foi escolhida |
|---|---|---|---|
| `normal` | Normal bivariada padrão; o `efeito` é a própria correlação | Nada: é o caso em que o Pearson é exato | É o ponto de comparação. Os valores estão em unidades padronizadas, sem significado de LOC ou de defeitos |
| `base` | Margens calibradas na amostra (lognormal e binomial negativa) ligadas pela cópula | Normalidade: forte assimetria, cauda longa e cerca de 60% de empates em zero defeito | É o cenário realista, com a forma dos dados do KC1 |
| `outliers` | A `base` com 5% dos valores de LOC e 5% dos valores de defeitos, sorteados de forma independente, empurrados 2 desvios para a cauda na escala latente | Normalidade e presença de módulos atípicos | Na amostra, a maior classe tem 2.883 LOC, cerca de 13 vezes a mediana. O deslocamento de 2 desvios multiplica o LOC por cerca de 18, e um módulo típico contaminado fica com cerca de 3.500 LOC, perto desse máximo real |

**Como os outliers afetam cada teste:** com `efeito = 0,6` e 200.000 módulos simulados, o r cai de 0,38 na `base` para 0,11 em `outliers`, e o ρ cai só de 0,50 para 0,44. Isso acontece porque os módulos atípicos não seguem a relação entre as variáveis: o Pearson usa os valores, e alguns pontos extremos dominam o r; o Spearman usa os postos, e um valor extremo conta apenas como o maior posto.

**Amostra pequena:** não virou uma situação do gerador porque o tamanho da amostra é um parâmetro da simulação (`n` em `simulacao.py`, hoje 30). Para estudar amostras pequenas, basta rodar as simulações com um `n` menor, como 10.

O erro tipo I de cada situação (Q1 e Q3) está em `lab04/code/resultados/erro_tipo1_<situacao>.csv`, e o poder (Q2 e Q3) fica com a issue #86.

# Resultado dos testes nos dados reais

Os testes de Pearson e de Spearman, bicaudais com α = 0,05, foram aplicados à amostra de 30 classes do KC1 descrita em [cenario.md](cenario.md). Os números são gerados pela etapa `lab04/code/etapas/05_dados_reais.py` e ficam em `lab04/code/resultados/dados_reais.csv`.

## Resultado

| Conjunto | Teste | n | Coeficiente (tamanho do efeito) | IC 95% | t | p-valor | Conclusão |
|---|---|---|---|---|---|---|---|
| Amostra | Pearson | 30 | r = 0,84 (forte) | 0,69 a 0,92 | 8,27 | 5 × 10⁻⁹ | Rejeita H₀ |
| Amostra | Spearman | 30 | ρ = 0,51 (forte) | 0,17 a 0,75 | 3,18 | 0,004 | Rejeita H₀ |
| Sem a maior classe | Pearson | 29 | r = 0,58 (forte) | 0,27 a 0,78 | 3,71 | 0,001 | Rejeita H₀ |
| Sem a maior classe | Spearman | 29 | ρ = 0,45 (moderada) | 0,09 a 0,71 | 2,65 | 0,013 | Rejeita H₀ |

As magnitudes seguem os limiares de Cohen (1988), os mesmos de `testes.py`. O intervalo de confiança usa a transformação z de Fisher; no Spearman, com a correção de Bonett e Wright (2000).

## Conclusão

- **Os dois testes concordam:** há associação positiva entre o tamanho da classe e o número de defeitos registrados. Classes maiores tendem a ter mais defeitos.
- **A força da associação depende do teste.** O r = 0,84 é inflado por uma única classe, com 2.883 LOC e 101 defeitos. Sem ela, o r cai para 0,58, enquanto o ρ quase não muda (de 0,51 para 0,45). O ρ descreve melhor a tendência da maioria das classes; o r descreve sobretudo o peso dos poucos módulos muito grandes.
- **A conclusão não depende da maior classe:** sem ela, os dois testes continuam rejeitando H₀.
- **O p-valor do Pearson é menos confiável aqui**, porque os dados são muito assimétricos. Na simulação da situação `base`, o erro tipo I do Pearson foi de 5,9%, acima de 5%. Mas o p-valor observado é tão pequeno (5 × 10⁻⁹) que esse desvio não muda a decisão.

## Importância prática

Um ρ em torno de 0,5 indica uma tendência clara, mas longe de determinística. Muitas classes grandes não têm nenhum defeito registrado (por exemplo, uma de 1.108 LOC), e 63% das classes da amostra têm zero defeito. Na prática, o tamanho serve para **priorizar** revisões e testes nas classes maiores, mas não para prever quantos defeitos cada classe terá.

O intervalo do ρ é largo (0,17 a 0,75), consequência das 30 observações: os dados são compatíveis tanto com uma associação fraca quanto com uma forte.

## Limitações

- **Correlação não é causalidade:** classes maiores também podem ser mais usadas ou mais testadas, o que aumenta a chance de um defeito ser encontrado e registrado.
- **Um só sistema:** os dados vêm de um único sistema da NASA (KC1), com 30 de 145 classes.
- **Análise de sensibilidade feita depois:** retirar a maior classe foi decidido depois de ver os dados, então serve só para mostrar a influência dela, e não como resultado principal.

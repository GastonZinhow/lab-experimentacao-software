# Apresentação oral: perguntas do Matheus (8, 10, 12, 13 e 15)

Respostas de cerca de 30 segundos. O professor pode pedir qualquer pergunta a qualquer integrante.

## Pergunta 8: o que seria um erro tipo I e um tipo II no cenário, e qual é mais grave?

**Onde mostrar:** seções 3, 4 e 5; no G3 aparece o erro tipo I e no G4 aparece a capacidade de evitar o tipo II.

Erro tipo I seria concluir que classes maiores têm associação com mais defeitos quando, na realidade, LOC e defeitos são independentes. Isso pode desperdiçar revisão e testes nas classes grandes. Erro tipo II seria não detectar uma associação que realmente existe, deixando de priorizar módulos com maior risco. Neste cenário eu considero o tipo II mais grave, porque pode deixar defeitos reais sem atenção, mas a escolha depende do custo: se uma revisão desnecessária for muito cara, o tipo I também pode ser crítico.

## Pergunta 10: qual teste tem mais poder no G4 e isso muda com o efeito?

**Onde mostrar:** seção 5, G4.

Depende da situação e do efeito. Na situação normal, o Pearson tem mais poder e, no efeito 0,5, chega a 82,69% contra 77,52% do Spearman. Na situação base, Pearson fica um pouco à frente nos efeitos 0,1 e 0,2, mas Spearman passa na frente a partir de 0,3 e chega a 63,60% contra 42,27%. Com outliers, a vantagem do Spearman cresce muito: no efeito 0,5, fica em 51,27% contra 23,30%.

## Pergunta 12: o que mudaria no G3 e no G4 com α = 0,01?

**Onde mostrar:** seções 4 e 5, linhas de referência do G3 e do G4.

Com α igual a 0,01, a regra para rejeitar H₀ ficaria mais exigente. No G3, a referência desceria de 5% para 1%, então esperaríamos aproximadamente 1% de falsos positivos se os testes continuassem calibrados. No G4, todas as curvas tenderiam a descer, porque menos p-valores passariam pelo novo limite; portanto, o erro tipo I diminuiria, mas o erro tipo II aumentaria e seria necessário um efeito ou uma amostra maior para alcançar 80% de poder. A ordem entre os testes provavelmente seria parecida, mas precisaria ser simulada novamente.

## Pergunta 13: a simulação confirmou o esperado e o que explica a diferença?

**Onde mostrar:** expectativa na seção 1, G3 na seção 4 e G4 na seção 5.

Confirmou em parte. Esperávamos vantagem do Spearman nos dados parecidos com o KC1, e isso ocorreu na situação base para efeitos maiores e ficou ainda mais claro com outliers. Porém, no cenário normal o Pearson teve maior poder, porque ali sua relação linear e seus pressupostos são atendidos. A diferença ocorre porque Pearson usa os valores e é sensível às caudas e aos pontos extremos, enquanto Spearman usa postos e preserva melhor uma tendência monotônica quando os dados são assimétricos.

## Pergunta 15: qual é a recomendação, quando ela mudaria e qual é a principal limitação?

**Onde mostrar:** seções 5 e 7.

Para dados como os do KC1, com forte assimetria, muitos zeros e módulos extremos, eu recomendaria Spearman como teste principal e Pearson como análise de sensibilidade. A recomendação mudaria para Pearson se os dados fossem aproximadamente normais, a relação fosse linear e não houvesse outliers influentes. A principal limitação é que o gerador foi calibrado com uma amostra de apenas 30 classes de um único sistema, então não podemos generalizar automaticamente a vantagem para todos os projetos.

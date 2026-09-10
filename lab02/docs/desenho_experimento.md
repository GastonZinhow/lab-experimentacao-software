# Desenho do Experimento - Lab02

## GQM e métricas

Goal: Analisar o uso de assistentes de IA generativa na resolução de katas Java, comparando produtividade, qualidade funcional e qualidade estrutural.

RQ1 - Tempo:
- Métrica primária: tempo ate passar todos os testes.
- Trials sem sucesso em 35 minutos serão registrados como censurados em 2100 segundos.
- Agregacao: mediana e IQR por tratamento.

RQ2 - Defeitos:
- Métrica primária: taxa de sucesso dos testes ao final do time-box.
- Métrica complementar: número absoluto de testes falhando.

RQ3 - Estrutura:
- Complexidade ciclomática via CK.
- Duplicacão via PMD CPD.
- LOC como métrica de controle.

## Hipóteses

- H0 RQ1: o uso de assistente de IA não reduz o tempo até passar nos testes.
- H1 RQ1: o uso de assistente de IA reduz o tempo até passar nos testes.

- H0 RQ2: o uso de assistente de IA não reduz a quantidade de defeitos no código produzido.
- H1 RQ2: o uso de assistente de IA reduz a quantidade de defeitos no código produzido, aumentando a taxa de sucesso dos testes.

- H0 RQ3: o uso de assistente de IA não altera a complexidade ciclomática, a duplicacão ou o LOC do código produzido.
- H1 RQ3: o uso de assistente de IA altera a complexidade ciclomática, a duplicacão ou o LOC do código produzido.

## Variáveis

- Variável independente: uso de assistente de IA (`IA` ou `Manual`).
- Variáveis dependentes: tempo ate passar nos testes, testes passando, testes falhando, taxa de sucesso, complexidade ciclomática, duplicacao e LOC.
- Variáveis de controle: linguagem Java, JUnit 5, time-box de 35 minutos, mesmas katas e mesmo ambiente base.

## Tratamentos

- `IA`: participante pode usar o assistente definido pelo grupo.
- `Manual`: participante nao pode usar assistente de IA durante o trial.

## Projeto experimental

O desenho e `within-subject` com contrabalanceamento. Cada participante resolve
as 6 katas, sendo 3 com IA e 3 manualmente.

| Participante | K1 | K2 | K3 | K4 | K5 | K6 |
|---|---|---|---|---|---|---|
| Matheus | IA | Manual | IA | Manual | IA | Manual |
| Mirelly | Manual | IA | Manual | IA | Manual | IA |
| Luisa | IA | Manual | Manual | IA | Manual | IA |

## Medições

- Total: 18 trials.
- Time-box: 35 minutos por trial.
- Trial que não passar todos os testes ao final do time-box deve ser registrado como censurado em 2100 segundos.

## Ameaças a validade

- Efeito de aprendizado entre katas.
- Familiaridade desigual com Java, JUnit ou ferramenta de IA.
- Vazamento de soluçõees já conhecidas.
- Diferença real de dificuldade entre katas.
- Interrupções ou diferenças de ambiente durante a execução.
- **Memorização (ameaça aceita e documentada):** os 6 katas escolhidos
  (`katas.md`) são problemas clássicos e amplamente indexados do LeetCode,
  reaproveitados de um trabalho prático de FPAA já resolvido e publicado
  no GitHub por um integrante do grupo. Isso diverge da recomendação do
  enunciado do Lab02 de preferir katas autorais/pouco indexados. O
  assistente de IA pode reproduzir uma solução memorizada durante seu
  treinamento em vez de raciocinar sobre o problema, o que pode inflar
  artificialmente o desempenho do tratamento `IA` nas RQ1 e RQ2. O grupo
  optou conscientemente por essa mescla de dificuldades (fácil, média e
  difícil) em vez de katas inéditos de dificuldade homogênea, e essa
  limitação deve ser retomada na discussão do Relatório Final.


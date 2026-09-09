# scripts

Script de cronometragem e coleta de trials do experimento (LAB02, issue #20).

## Requisitos

- Python 3.8+ (sem dependências externas)
- Maven no PATH (usado para rodar os testes de aceitação do kata)
- Projeto [`../katas-java`](../katas-java) com o kata já com o esqueleto e
  os testes de aceitação (ver issue #22)

## Uso

Iniciar um trial:

```
python register_trial.py start --integrante Mirelly --kata k01 --tratamento IA
```

- `--kata` é o nome do pacote em `katas-java/src/main/java/katas/<kata>`
  (ex.: `k01` para `katas.k01`).
- `--tratamento` é `IA` ou `Manual`.
- `--timebox` (opcional, em segundos, default 2100 = 35 min) só pode ser
  usado para **reduzir** o time-box, nunca para aumentá-lo — o script
  recusa valores acima de 2100.

Durante o trial, o participante resolve o kata normalmente no projeto
`katas-java`. Ao final (ou ao bater o time-box):

```
python register_trial.py stop
```

O `stop` roda `mvn test -Dtest=katas.<kata>.*Test`, lê o resultado no
surefire e grava uma linha em
[`../data/raw/trials.csv`](../data/raw/README.md) com: tempo decorrido
(truncado no time-box e marcado como `censurado=True` se os 2100s foram
atingidos), nº de testes passando/total e taxa de sucesso.

Exemplo de sessão completa:

```
python register_trial.py start --integrante Mirelly --kata k00example --tratamento Manual
# ... participante resolve o kata ...
python register_trial.py stop --observacao "3 prompts trocados com a IA"
```

Saída esperada do `stop`:

```
Trial encerrado: Mirelly-k00example-Manual
Tempo: 33.4s (censurado=False)
Testes: 7/7 passando (1.0000)
```

Outros comandos:

```
python register_trial.py status   # mostra o trial em andamento e o tempo decorrido
python register_trial.py abort    # cancela o trial em andamento sem gravar dados
```

Use `stop --sem-testes` se quiser registrar apenas o tempo sem rodar
`mvn test` (ex.: kata em outra linguagem, coletado manualmente).

## Estado do trial em andamento

Enquanto um trial está em andamento, `start` grava um arquivo local
`.trial_state.json` (não versionado) com integrante, kata, tratamento e
horário de início. Ele é apagado automaticamente por `stop` ou `abort`. Só é
possível ter um trial em andamento por vez — isso é intencional, para
impedir que dois cronômetros fiquem rodando ao mesmo tempo por engano.

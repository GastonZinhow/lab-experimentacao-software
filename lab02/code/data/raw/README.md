# data/raw/

Dados brutos coletados durante o experimento (Passo 3, Sprint S02).

`trials.csv` é gerado automaticamente por
[`../../scripts/register_trial.py`](../../scripts/register_trial.py)
(issue #20) na primeira vez que um trial é encerrado com `stop` — não é
versionado vazio neste diretório, apenas esta documentação do formato.

## Esquema de `trials.csv`

| Coluna | Descrição |
|---|---|
| `trial_id` | `<integrante>-<kata>-<tratamento>`, ex.: `Mirelly-k01-IA` |
| `integrante` | Nome do integrante que executou o trial |
| `kata` | Identificador do kata (pacote em `katas-java`, ex.: `k01`) |
| `tratamento` | `IA` ou `Manual` |
| `timebox_segundos` | Time-box usado no trial (segundos; ≤ 2100 = 35 min) |
| `inicio` / `fim` | Timestamps ISO 8601 do início e fim do trial |
| `tempo_segundos` / `tempo_min` | Tempo decorrido, truncado no time-box se censurado |
| `censurado` | `True` se o trial atingiu o time-box (2100s) sem terminar |
| `testes_passando` / `testes_total` | Resultado do `mvn test` ao final do trial |
| `taxa_sucesso` | `testes_passando / testes_total` |
| `observacoes` | Texto livre (ex.: nº de prompts usados com a IA) |

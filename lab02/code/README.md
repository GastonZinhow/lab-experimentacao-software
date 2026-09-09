# Lab02 - Assistentes de IA vs codificacao manual

Projeto base em Java para executar o experimento controlado do Lab02.

## Estrutura

```text
code/
├── pom.xml
├── src/
│   ├── main/java/br/edu/lab02/katas/   # stubs das 6 katas
│   └── test/java/br/edu/lab02/katas/   # testes de aceitacao JUnit 5
├── trials/                             # solucoes finais por participante/trial
├── data/
│   ├── raw/trials.csv                  # coleta manual/automatizada dos trials
│   └── processed/                      # metricas, resultados e graficos
└── scripts/
    ├── run_tests.ps1
    ├── run_static_metrics.ps1
    ├── analyze_results.py
    └── dashboard.py
```

## Como rodar os testes

```powershell
cd lab02/code
mvn test
```

Os testes devem falhar no projeto inicial, porque as classes de `src/main`
possuem apenas stubs. Durante cada trial, o participante implementa as katas
atribuídas e registra o resultado em `data/raw/trials.csv`.

## Como registrar um trial

Para cada combinacao participante + kata + tratamento:

1. Abrir a issue correspondente no GitHub Projects.
2. Iniciar o cronometro.
3. Implementar a kata sob a condicao definida: `IA` ou `Manual`.
4. Parar em `time-to-green` ou em 35 minutos.
5. Rodar os testes com `scripts/run_tests.ps1`.
6. Salvar a solucao final em `trials/<participante>/KXX/<tratamento>/`.
7. Preencher `data/raw/trials.csv`.
8. Fazer commit referenciando a issue, por exemplo: `Resolve K01 manual #12`.

## Analise

Depois da execucao, rode:

```powershell
python scripts/analyze_results.py
python scripts/dashboard.py
```

Exemplo de registro manual via script:

```powershell
python scripts/register_trial.py --participant Matheus --kata K01 --treatment IA --order 1 --seconds 870 --total-tests 3 --passed-tests 3 --issue-number 12 --commit-sha abc123
```

As metricas estaticas Java devem ser coletadas com CK e PMD CPD:

```powershell
scripts/run_static_metrics.ps1 -CkJarPath C:\tools\ck\ck.jar -PmdBinPath C:\tools\pmd\bin\pmd.bat
```

Detalhes de instalacao, saidas esperadas e interpretacao estao em
[`../docs/metricas_estaticas.md`](../docs/metricas_estaticas.md).

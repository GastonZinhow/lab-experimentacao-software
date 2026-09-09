# Metricas estaticas - CK e PMD CPD

Esta documentacao cobre a issue #21 do Lab02: preparar a coleta das metricas
estruturais usadas na RQ3.

## Ferramentas

### CK

O CK coleta metricas estaticas de codigo Java. Para este laboratorio, o grupo
deve usar principalmente:

- complexidade ciclomatica por metodo;
- LOC como metrica de controle;
- metricas agregadas por classe/metodo para comparar `IA` e `Manual`.

Como obter:

1. Acessar o repositorio do CK: https://github.com/mauricioaniche/ck
2. Baixar o arquivo `.jar` da versao/release escolhida.
3. Salvar em um caminho local conhecido, por exemplo `C:\tools\ck\ck.jar`.

### PMD CPD

O PMD CPD detecta duplicacao de codigo. Para este laboratorio, o grupo deve
registrar se houve duplicacao e comparar o volume de duplicacao entre os
tratamentos.

Como obter:

1. Acessar o site do PMD: https://pmd.github.io/
2. Baixar a distribuicao binaria do PMD.
3. Extrair em um caminho local conhecido, por exemplo `C:\tools\pmd`.
4. Usar o executavel `C:\tools\pmd\bin\pmd.bat`.

## Script

Rodar a partir de `lab02/code`:

```powershell
scripts/run_static_metrics.ps1 -CkJarPath C:\tools\ck\ck.jar -PmdBinPath C:\tools\pmd\bin\pmd.bat
```

Para analisar uma solucao final especifica:

```powershell
scripts/run_static_metrics.ps1 -SourcePath trials\matheus\K01\IA -RunId matheus-k01-ia -CkJarPath C:\tools\ck\ck.jar -PmdBinPath C:\tools\pmd\bin\pmd.bat
```

## Saidas

O script salva os arquivos em `lab02/code/data/processed`:

- `static_metrics_runs.csv`: resumo de cada execucao;
- `ck/<run_id>/`: arquivos CSV gerados pelo CK;
- `ck-<run_id>.log`: log da execucao do CK;
- `cpd-<run_id>.xml`: resultado do PMD CPD;
- `cpd-<run_id>.log`: log do PMD CPD.

## Registro no experimento

Para cada trial da S02, registrar no dataset final:

- participante;
- kata;
- tratamento;
- caminho da solucao final;
- metricas CK relevantes;
- resultado de duplicacao do PMD CPD;
- LOC.

As comparacoes da RQ3 devem usar mediana e IQR por tratamento, mantendo LOC
como controle para evitar interpretar codigo maior como necessariamente melhor
ou pior.


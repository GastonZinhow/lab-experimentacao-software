# Lab05 — Confiabilidade operacional: GitHub × GitLab

Análise dos dados de operação publicados nas páginas de status do GitHub
(<https://www.githubstatus.com>) e do GitLab (<https://status.gitlab.com>),
com triangulação nos relatórios oficiais de incidentes.

## Estrutura

```text
lab05/
├── docs/                      # enunciado, proposta, GQM, ameaças, documento final
│   └── apresentacao/
└── code/
    ├── coleta/                # coletores das páginas de status (1 req/s no máximo)
    ├── etapas/                # NN_nome.py com main(), chamadas pelo comando único
    ├── secoes/                # secao_<N>_<nome>.py com render() para o dashboard
    ├── dados/
    │   ├── brutos/github/     # respostas originais, sem alteração
    │   ├── brutos/gitlab/
    │   └── processados/       # incidentes.csv no formato comum
    ├── resultados/
    │   ├── tabelas/
    │   └── figuras/
    └── tests/
```

## Instalação

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows (PowerShell)
python -m pip install -r lab05/code/requirements.txt
```

## Comando único

Execute todas as etapas disponíveis, em ordem numérica:

```bash
python lab05/code/run_all.py
```

Para executar o pipeline duas vezes e confirmar que as saídas são idênticas:

```bash
python lab05/code/run_all.py --verificar-reprodutibilidade
```

Enquanto os coletores não geram os dados reais, use
`lab05/code/dados/processados/exemplo_incidentes.csv`. Os registros desse arquivo
são fictícios e servem somente para permitir o trabalho paralelo.

## Dashboard

*Em construção.*

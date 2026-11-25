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

Etapas atuais:

| Etapa | O que faz | Saída |
|---|---|---|
| `etapas/01_coletar.py` | Chama os dois coletores para a janela, **só com o cache** (não acessa a internet) | `dados/brutos/resumo_coleta.json` (data da coleta e incidentes por mês) |
| `etapas/02_normalizar.py` | Converte os dados brutos no formato comum, aplica o mapa de componentes e as regras pelo título, valida | `dados/processados/incidentes.csv`, `resultados/tabelas/validacao.md` |
| `etapas/03_triangulacao.py` | Extrai os 12 relatórios mensais locais e cruza com a normalização | `dados/brutos/github/relatorios_mensais.csv` e `resultados/tabelas/triangulacao.csv` |

Para baixar o que falta no cache (a única etapa que usa a internet, 1 req/s):

```bash
python lab05/code/etapas/01_coletar.py --baixar
```

`dados/processados/exemplo_incidentes.csv` tem registros fictícios e só é usado
pelo dashboard quando `incidentes.csv` não existe.

## Coleta

Os coletores ficam em `coleta/` e só acessam a internet quando o arquivo ainda
não está em `dados/brutos/<plataforma>/` (regras em `lab05/docs/plano_coleta.md`):

```bash
cd lab05/code
python -m coleta.github --inicio 2026-10-01T00:00:00Z --fim 2026-10-31T23:59:59Z
python -m coleta.github --inicio 2025-11-01T00:00:00Z --fim 2026-10-31T23:59:59Z --so-listar
python -m coleta.gitlab --inicio 2026-10-01T00:00:00Z --fim 2026-10-31T23:59:59Z
```

O `all.ics` do GitLab está em um caminho bloqueado pelo robots.txt; ele foi salvo
à mão pelo navegador em `dados/brutos/gitlab/all.ics` e o coletor só lê o arquivo.

## Dashboard

Na raiz do repositório (para usar o tema claro do grupo):

```bash
python -m streamlit run lab05/code/dashboard.py
```

Cada seção é um arquivo `secoes/secao_<N>_<nome>.py` com uma função `render()`;
o `dashboard.py` não precisa ser editado. Seções ainda inexistentes aparecem como
"em construção". Cores, janela e leitura dos dados ficam em `dashboard_comum.py`.
O plano de análise está em `lab05/docs/plano_analise.md`.

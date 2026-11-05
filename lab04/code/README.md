# Lab04 — Testes de hipótese por dentro

Este laboratório compara as correlações de Pearson e de Spearman no cenário
de tamanho do módulo (LOC) e número de defeitos. Os dados, simulações e
resultados são reproduzíveis com a semente `numpy.random.default_rng(42)`.

## Instalação

Na raiz do repositório, crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

No Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install -r lab04/code/requirements.txt
```

## Comando único

Execute todas as etapas disponíveis, na ordem numérica:

```bash
python lab04/code/run_all.py
```

O comando descobre automaticamente os arquivos no formato
`lab04/code/etapas/NN_nome.py` e chama a função `main()` de cada um. Portanto,
continua funcionando à medida que novas etapas são adicionadas.

Para conferir a reprodutibilidade, execute o pipeline duas vezes e compare os
arquivos gerados em `dados/` e `resultados/`:

```bash
python lab04/code/run_all.py --verificar-reprodutibilidade
```

## Dashboard

Abra o dashboard com:

```bash
python -m streamlit run lab04/code/dashboard.py
```

Cada seção fica em `lab04/code/secoes/secao_<N>_<nome>.py` e expõe uma função
`render()`. Se uma seção ainda não existir ou apresentar erro, as demais
continuam disponíveis e o dashboard mostra um aviso no lugar dela.

Os links exibidos no topo podem ser definidos sem alterar o código:

- `DASHBOARD_URL`: endereço da versão publicada;
- `REPOSITORY_URL`: endereço do repositório (já possui um valor padrão);
- `GITHUB_PROJECTS_URL`: endereço do GitHub Projects do grupo.

# Amostra-ouro

O sorteio usa uma pontuação SHA-256 combinada com a seed. Assim, o resultado
não depende da ordem das linhas nos CSVs nem da versão do pandas.

Com os parâmetros padrão, o arquivo tem 300 linhas: 60 repositórios e 5
releases por repositório. Cada linha representa uma release; por isso os
rótulos do repositório são repetidos nas cinco linhas correspondentes.

Execute depois de concluir e conferir a coleta da amostra final:

```bash
python validacao/gerar_amostra_ouro.py
```

O comando lê `data/metadados.csv` e `data/releases.csv` e grava
`validacao/amostra_sorteada.csv`. O arquivo contém somente identificadores,
datas e links públicos. Ele não contém resultados da heurística automática.

Cada avaliador deve copiar a mesma amostra antes de preencher os rótulos:

```powershell
Copy-Item validacao/amostra_sorteada.csv validacao/rotulos_matheus.csv
```

Valores permitidos durante a rotulagem:

- `tipo_projeto`: `biblioteca_framework`, `aplicacao_servico`,
  `ferramenta_cli` ou `outro`;
- `releases_representam_entregas`: `sim`, `nao` ou `incerto`;
- `release_corretiva`: `sim` ou `nao`;
- `observacoes`: texto livre ou `sem_observacoes`.

Não consulte os arquivos dos outros avaliadores nem a saída da heurística
antes de commitar o arquivo individual.

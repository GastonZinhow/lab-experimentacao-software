# Guia de rotulagem da amostra-ouro

Issue #59 · seção 6 do enunciado. Leia uma vez antes de começar e mantenha aberto durante a rotulagem.

## Regras

1. **Rotule sozinho.** Não converse com os colegas sobre os itens até a reunião de consenso.
2. **Não olhe a heurística.** Não abra `releases.csv` com colunas da heurística, nem o código ou as saídas da #61, antes de commitar a sua planilha.
3. Copie `planilha_rotulagem.csv` para `rotulos_<seu_nome>.csv` (ex.: `rotulos_luisa.csv`). Não mude a ordem, a quantidade de linhas, nem as colunas de identificação.
4. Preencha **todas** as células das colunas `tipo_projeto`, `entregas_reais` e `corretiva`. Na dúvida, escolha a opção mais provável e explique em `observacoes`.
5. Commite o arquivo **antes** da reunião de consenso, referenciando a sua Issue (#58, #60 ou #62). A data do commit comprova que a rotulagem foi independente.

## Colunas

Cada linha é uma release. As duas primeiras colunas de rótulo descrevem o **repositório** e devem se repetir iguais nas 5 linhas do mesmo repositório.

| Coluna | Valores aceitos | Pergunta |
|---|---|---|
| `tipo_projeto` | `biblioteca`, `aplicacao`, `cli`, `outro` | O que o repositório entrega? |
| `entregas_reais` | `sim`, `nao`, `incerto` | As releases desse repositório representam entregas reais ao usuário? |
| `corretiva` | `sim`, `nao` | O objetivo principal **desta** release é corrigir um defeito recente? |
| `observacoes` | texto livre | Dúvidas e justificativas (opcional). |

Acentos e maiúsculas são ignorados pelo script (`Não` = `nao`), mas use os valores da tabela.

### `tipo_projeto`

- **biblioteca**: biblioteca, framework, SDK, plugin, componente ou pacote consumido por **outro código** (npm, PyPI, Maven, crates, Go modules…).
- **aplicacao**: aplicação ou serviço usado diretamente por pessoas ou implantado como serviço: app desktop/mobile/web, servidor, banco de dados, sistema auto-hospedado, jogo, extensão de navegador.
- **cli**: a entrega principal é uma ferramenta de linha de comando (inclui *linters*, *bundlers* e ferramentas de *build*, mesmo que também tenham API).
- **outro**: documentação, listas *awesome*, dados, modelos/pesos, configurações, temas, cursos.

Se o repositório entrega mais de uma coisa, escolha o **produto principal** descrito no README.

### `entregas_reais`

Pense em DORA: cada release corresponde a uma versão que chega ao usuário?

- **sim**: as releases publicam artefatos (binários, pacotes no registry, imagens) ou anunciam versões que os usuários instalam/atualizam.
- **nao**: releases automáticas ou de rotina que não mudam o que o usuário recebe (ex.: *nightly* publicado como release, *snapshot* de dados, tag de sincronização, repositório que só espelha versões de outro lugar).
- **incerto**: não dá para decidir pelas release notes e pelo README.

### `corretiva`

Leia as *release notes* (`release_url`) e a lista de commits (`commits_url`, comparação com a release anterior).

- **sim**: o objetivo **principal** da release é corrigir defeito(s) introduzido(s) recentemente: notas como "fix crash in 2.3.0", "hotfix", "revert", uma release lançada logo depois da anterior só com correções.
- **nao**: release com funcionalidades novas, release de manutenção periódica que mistura melhorias e correções, atualização de dependências, documentação.

Uma release com algumas correções no meio de várias novidades **não** é corretiva. O número da versão (ex.: só o *patch* mudou) é um indício, não uma regra: decida pelo conteúdo.

**Monorepos e séries paralelas.** A `tag_anterior` é a release publicada imediatamente antes, em ordem cronológica (a mesma usada no *lead time*). Em monorepos que publicam um pacote por release (`TanStack/virtual`, `fuma-nama/fumadocs`, `0xPlaygrounds/rig`…) ou em projetos com várias séries mantidas em paralelo (`hibernate/hibernate-orm`, `pypa/setuptools`), ela pode ser de outro pacote ou de outra série, e o `commits_url` mistura mudanças de pacotes diferentes. Nesses casos, decida pelas *release notes* e anote em `observacoes`.

## Depois de rotular

```bash
cd lab03/code
python -m rotulagem.concordancia --config config.yaml
```

O script confere a sua planilha (células vazias, valores inválidos, rótulos de repositório diferentes entre linhas) e, quando as três planilhas estiverem completas, calcula o kappa de Fleiss e lista as divergências para a reunião. Veja o protocolo em [`docs/protocolo_consenso.md`](../docs/protocolo_consenso.md).

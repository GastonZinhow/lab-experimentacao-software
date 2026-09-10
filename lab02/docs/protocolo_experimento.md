# Protocolo do Experimento (Ambiente, IA e Execucao)

Issue #23 do Lab02: fechar a metodologia reprodutivel da S01, fixando o
ambiente, o assistente de IA unico do grupo e as regras de execucao dos
trials.

## IDE

- **IntelliJ IDEA Community Edition**, mesma versao para os tres
  integrantes durante todos os trials (evita diferencas de produtividade
  causadas por familiaridade desigual com a IDE).
- Plugins de IA (Copilot) devem estar instalados e atualizados antes do
  inicio da S02, para nao impactar o tempo medido durante um trial.

## Assistente de IA

- **GitHub Copilot**, via GitHub Student Developer Pack (plano gratuito
  para estudantes), integrado ao IntelliJ IDEA (autocomplete inline + chat
  do Copilot).
- **Modelo do Copilot Chat: GPT-5**, fixado no seletor de modelo do chat
  para todos os trials `IA` (o autocomplete inline usa o modelo padrao do
  Copilot, que nao e configuravel).
- O mesmo assistente e o mesmo modelo sao usados por todos os integrantes
  em todos os trials `IA`, conforme exigido no enunciado (tratamento
  comparavel dentro do proprio experimento).
- Versao do plugin e data de uso devem ser registradas no Relatorio Final
  (Passo 5), junto com prints/observacoes relevantes, para permitir
  reproducao.

## Versoes fixas do ambiente

- **Java:** 21 (`maven.compiler.release=21` em
  `lab02/code/katas-java/pom.xml`). Qualquer JDK que suporte
  `--release 21` (ex.: JDK 21 ou 25) pode ser usado para compilar/rodar.
- **Maven:** 3.6+.
- **JUnit:** 5.10.2 (`junit-jupiter`).
- **Maven Surefire Plugin:** 3.2.5.

Cada integrante deve conferir `java -version` e `mvn -version` antes do
inicio da S02 e registrar a saida no relatorio.

## Regras do tratamento `Manual`

Durante um trial `Manual`, o participante:

- **nao** pode usar o Copilot (autocomplete de IA e chat desabilitados na
  IDE antes de iniciar o cronometro);
- **nao** pode consultar chatbots de IA generativa (ChatGPT, Claude,
  Gemini, etc.) em nenhuma aba/janela durante o trial;
- **pode** usar recursos nativos, nao generativos, da IDE: autocomplete
  estatico de simbolos, refatoracao automatica, navegacao de codigo,
  atalhos e o proprio JDK/Javadoc;
- **pode** consultar documentacao oficial (Javadoc da linguagem/JDK), mas
  **nao** pode pesquisar a solucao do kata especifico em buscadores, foruns
  ou repositorios publicos;
- deve manter o Copilot desabilitado (nao apenas ignorar as sugestoes) para
  eliminar qualquer influencia, mesmo indireta, do assistente de IA.

## Regras do tratamento `IA`

- o Copilot deve estar habilitado (autocomplete inline e/ou chat) desde o
  inicio do cronometro;
- o participante pode aceitar, editar ou rejeitar sugestoes livremente;
- recomenda-se (opcional, nao obrigatorio) registrar o numero aproximado de
  prompts/interacoes com o assistente na observacao do trial
  (`register_trial.py stop --observacao "..."`), para discussao
  qualitativa no Relatorio Final.

## Time-box

- **35 minutos por trial**, fixo, conforme `lab02/docs/desenho_experimento.md`
  e implementado em `lab02/code/scripts/register_trial.py`
  (`--timebox` so aceita valores menores ou iguais a 2100 segundos).
- Ao final do tempo, o trial e encerrado independentemente do resultado e
  registrado como censurado em 2100s se os testes de aceitacao ainda nao
  passarem 100%.

## Rastreabilidade

- Cada trial da S02 deve ser registrado como uma Issue individual no
  GitHub Projects do grupo (uma Issue por kata/tratamento/participante),
  atribuida ao integrante responsavel.
- Commits relacionados a esta issue devem referenciar `#23` na mensagem.

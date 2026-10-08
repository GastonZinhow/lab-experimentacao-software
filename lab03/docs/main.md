# Minerando métricas DORA em repositórios open-source: o quanto podemos confiar nos *proxies*?

**Luisa Clara de Paula Lara Silva, Matheus Gaston, Mirelly Alvarenga**

Curso de Engenharia de Software — Laboratório de Experimentação de Software

> Versão em Markdown do artigo (template SBC, Overleaf). Introdução e hipóteses
> registradas em **07/10/2026, antes da coleta e da análise dos dados** (Issue #53).
> A versão LaTeX está em [`artigo/introducao_hipoteses_2026-10-07.tex`](artigo/introducao_hipoteses_2026-10-07.tex).

**Resumo.** *A ser escrito na entrega final, depois dos resultados.*

# 1. Introdução

As métricas DORA (*DevOps Research and Assessment*) tornaram-se a referência
mais usada para medir o desempenho de entrega de software. Popularizadas por
[@forsgren2018] e revisadas anualmente pelos relatórios *Accelerate State of
DevOps*, elas descrevem a entrega em duas dimensões: **velocidade**, medida
pela frequência de *deploy* e pelo *lead time* das mudanças, e
**estabilidade**, medida pela taxa de falha das mudanças (*change failure
rate*, CFR) e pelo tempo de recuperação após um *deploy* que falhou
[@dora2024]. Em 2024 o DORA acrescentou uma quinta métrica, a *deployment
rework rate*, que mede a proporção de *deploys* não planejados feitos para
corrigir problemas. Uma das afirmações centrais desse corpo de pesquisa é que
velocidade e estabilidade não competem entre si: as equipes de melhor
desempenho seriam rápidas *e* estáveis ao mesmo tempo.

Nas organizações, essas métricas costumam ser obtidas de ferramentas internas
que registram cada *deploy* em produção e cada incidente. Em projetos
open-source isso não existe. O GitHub não registra "*deploys* em produção"
nem "falhas em produção"; ele registra *releases*, *tags*, *commits* e
execuções de *workflows* de integração contínua (CI). Quem quiser calcular
métricas DORA a partir desses dados precisa usar ***proxies***, isto é,
medidas indiretas no lugar das que não podem ser observadas. Neste trabalho,
uma *release* publicada faz o papel de *deploy* e uma execução de CI que
falhou faz o papel de falha.

Esses *proxies* têm limitações conhecidas. Primeiro, **release não é
deploy**: uma biblioteca que publica uma versão por mês não coloca nada em
produção; quem faz isso são os projetos que a utilizam, cada um no seu ritmo.
Segundo, **CI não é produção**: uma execução de *pipeline* que falha no
branch principal indica um teste quebrado, um problema de infraestrutura ou
um teste instável (*flaky*), e não necessariamente um defeito percebido pelo
usuário. Terceiro, as datas disponíveis são imperfeitas: *rebase* e *squash
merge* reescrevem a data dos *commits* e distorcem o *lead time*. Por isso, o
valor de uma métrica DORA minerada depende da definição operacional
escolhida, e duas definições igualmente razoáveis podem levar a conclusões
diferentes sobre o mesmo repositório.

O **objetivo** deste estudo é minerar as métricas DORA de repositórios
open-source populares que usam GitHub Actions, numa janela de observação de
12 meses (30/09/2025 a 30/09/2026), e avaliar o quanto esses valores são
confiáveis. Além de calcular as métricas, (i) validamos o critério automático
de *release* corretiva contra uma amostra rotulada manualmente por três
avaliadores e (ii) medimos o quanto a classificação DORA de cada repositório
muda quando a definição operacional muda. O estudo é guiado pelas seguintes
questões de pesquisa (RQs):

- **RQ01.** Qual a frequência de *deploys* dos repositórios populares que usam CI/CD?
- **RQ02.** Qual o tempo entre um *commit* e seu respectivo *deploy*?
- **RQ03.** Qual a taxa de falha das mudanças entregues por esses repositórios?
- **RQ04.** Qual o tempo de recuperação após uma execução de CI/CD com falha?
- **RQ05.** Repositórios com maior frequência de *deploy* apresentam maior ou menor taxa de falha?
- **RQ06.** Quais características dos repositórios estão associadas a um melhor desempenho DORA?
- **RQ07.** O quanto a classificação DORA de um repositório depende da definição operacional escolhida?
- **RQ08 (bônus).** Qual a *rework rate* dos repositórios e em que ela difere do CFR baseado em *releases*?

## 1.1 Hipóteses informais

As hipóteses abaixo foram registradas em 07/10/2026, antes da coleta e da
análise dos dados, e expressam o que o grupo *espera* encontrar. A Seção de
Discussão as confronta com os resultados. As categorias citadas (Elite, High,
Medium, Low) seguem a tabela de referência da disciplina.

**H1 (RQ01, frequência de *deploy*).** Esperamos uma mediana entre uma
*release* por mês e uma por semana (categoria Medium), com distribuição muito
assimétrica à direita. A maior parte dos projetos populares é biblioteca ou
*framework* e agrupa mudanças em versões planejadas; só uma cauda pequena, com
publicação automatizada a cada *merge* (*nightly builds* ou ferramentas como
*semantic-release*), deve chegar a Elite.

**H2 (RQ02, *lead time*).** Esperamos *lead times* da ordem de semanas, com a
variante (a), por *release*, sistematicamente maior que a variante (b), por
*commit*, em praticamente todos os repositórios. A variante (a) é determinada
pelo *commit* mais antigo incluído na *release*, e basta um *commit*
"esquecido" para inflá-la; a (b) é dominada pela massa de *commits* feitos
pouco antes da publicação. Assim, a variante (a) deve situar a maioria dos
repositórios em Medium ou Low, e a (b), em High ou Medium.

**H3 (RQ03, taxa de falha).** Esperamos CFR (a), o *proxy* de CI, com mediana
entre 10% e 25%. As execuções consideradas são as de *push* no branch
principal, e boa parte das mudanças já passou pelos *checks* do *pull
request* antes do *merge*; ainda assim, testes instáveis e falhas de
infraestrutura mantêm a taxa acima de zero. Para o CFR (b), o *proxy* de
entrega, esperamos valores de mesma ordem, mas pouco correlacionados com o
CFR (a), porque as duas variantes medem fenômenos diferentes: quebra de
*pipeline* e correção rápida de uma versão publicada.

**H4 (RQ04, tempo de recuperação).** Esperamos mediana de algumas horas
(categoria High). Em projetos ativos, uma falha no branch principal costuma
ser corrigida pelo *commit* seguinte ou resolvida reexecutando o *workflow*.
Esperamos também uma cauda longa e uma proporção não desprezível de episódios
censurados, vindos de *workflows* secundários (documentação, *lint*,
*benchmarks*) que permanecem quebrados por semanas sem bloquear o
desenvolvimento.

**H5 (RQ05, velocidade × estabilidade).** Para o CFR (a), esperamos
correlação de Spearman fraca ou nula (|ρ| < 0,3), o que seria compatível com
a afirmação do DORA de que velocidade e estabilidade não são um *trade-off*.
Para o CFR (b), esperamos correlação positiva, mas por um artefato da
definição: quem publica *releases* com muita frequência tem mais chance de ter
qualquer *release* seguida, em até 7 dias, por outra que só muda o *patch*,
mesmo que nenhuma delas corrija um defeito.

**H6 (RQ06, fatores associados ao desempenho).** Esperamos que o número de
contribuidores esteja associado a maior frequência de *deploy* e a menor
tempo de recuperação, porque mais pessoas produzem mais mudanças e reagem
mais rápido a quebras. Esperamos também diferenças por linguagem, com
ecossistemas de publicação automatizada (JavaScript/TypeScript, Go e Rust)
publicando com mais frequência, e repositórios mais antigos com processos de
*release* mais lentos e cerimoniosos. Mesmo quando as diferenças forem
significativas após a correção de Holm, esperamos tamanhos de efeito pequenos
(ε² < 0,06), já que nenhum fator isolado deve explicar muito da variação.

**H7 (RQ07, sensibilidade às definições).** Esperamos que a classificação
DORA seja sensível à definição operacional: pelo menos 30% dos repositórios
devem mudar de categoria em algum par de combinações, com kappa de Cohen
ponderado apenas moderado (entre 0,4 e 0,6). A troca mais instável deve ser a
que usa *tags* como unidade de *deploy*, pois muitos projetos criam *tags*
sem publicar *release*, o que altera a frequência e, por consequência, o
*lead time*.

**H8 (RQ08, *rework rate*).** Esperamos *rework rate* maior que o CFR (b), na
faixa de 20% a 35% das *releases*. A *rework rate* conta todas as *releases*
corretivas, inclusive as publicadas mais de 7 dias depois da versão que
corrigem e as que corrigem outra *release* corretiva; o CFR (b) só conta a
*release* original quando a correção chega dentro da janela de 7 dias.

O restante do artigo está organizado da seguinte forma: a Seção 2 descreve a
metodologia (fonte de dados, funil de seleção, definições operacionais e
validação manual); a Seção 3 apresenta os resultados por RQ; a Seção 4
discute os resultados frente às hipóteses; a Seção 5 trata das ameaças à
validade; e a Seção 6 relata a replicação cruzada do estudo.

# 2. Metodologia

*Lab03S02.*

# 3. Resultados

*Lab03S03.*

# 4. Discussão

*Lab03S03.*

# 5. Ameaças à validade

*Entrega final.*

# 6. Replicação cruzada

*Entrega final.*

# Referências

- **[forsgren2018]** Forsgren, N., Humble, J. e Kim, G. (2018). *Accelerate: The Science of Lean Software and DevOps*. IT Revolution.
- **[dora2024]** DORA (2024). DORA's software delivery metrics: the four keys. <https://dora.dev/guides/dora-metrics-four-keys/>.

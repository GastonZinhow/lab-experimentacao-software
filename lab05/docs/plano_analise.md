# Plano de análise

> Issue #103. Define, **antes de olhar os dados completos**, como cada métrica do [GQM](gqm.md) será descrita e testada. A escolha dos testes vem da escala da métrica, do desenho do estudo e da distribuição esperada, nunca do p-valor obtido.
> Escrito em 2026-11-19. Até esta data só foi visto o piloto do GitHub (outubro/2026, 25 incidentes) e a contagem mensal do histórico do GitHub, sem filtro de componente. Nenhum dado do GitLab foi analisado.

## 1. Decisões gerais

| Decisão | Valor | Por quê |
|---|---|---|
| Nível de significância | **α = 0,05**, bilateral | As hipóteses do GQM são bilaterais: não há razão prévia para apostar em uma plataforma. |
| Hipóteses confirmatórias | Só duas: **H-F** (frequência, Q1) e **H-R** (recuperação, Q2) | O resto (Q3, Q4, M4) é **exploratório** e é apresentado como descrição, sem prometer conclusão por p-valor. |
| Multiplicidade | p de H-F e H-R também reportados com **ajuste de Holm**; testes exploratórios de uma mesma família também usam Holm | Evita "pescar" significância entre vários testes. |
| Intervalos de confiança | **95% por bootstrap percentil**, B = 10 000, `numpy.random.default_rng(42)` | Não supõe normalidade; com a semente fixa, o resultado se repete (combinado do grupo). |
| Amostra principal | Incidentes com `inicio_utc` na janela, em categorias de `componente_equivalente` presentes nas duas plataformas, um registro por `(plataforma, id)` | Regras de derivação do GQM. |
| Unidade de comparação | Plataforma (GitHub.com × GitLab.com) | É a variável independente do estudo; não é manipulada (estudo observacional). |
| Software | `scipy.stats` (testes) e `numpy` (bootstrap), em `lab05/code/etapas/` | Reprodutível pelo comando único. |

## 2. Estatística descritiva por escala

Só são calculadas as estatísticas que a escala permite ([gqm.md](gqm.md#métricas)).

| Escala | Métricas | O que é mostrado | O que **não** é feito |
|---|---|---|---|
| Nominal | `plataforma`, `componente_equivalente` | Frequência absoluta e relativa, moda | Média, mediana |
| Ordinal | `impacto` (M5) | Frequência por classe, proporção acumulada, classe mediana **dentro de cada plataforma** | Média de impacto; comparar classes do GitHub com classes do GitLab como se fossem a mesma escala (são escalas diferentes, ver [componentes.md](componentes.md#escala-de-impacto-relacionado)) |
| Razão, contagem | Incidentes por mês (M1) | Mediana, IQR, mínimo, máximo, média, total no ano, **razão variância/média** (dispersão) | — |
| Razão, contínua | Duração (M2), tempo entre incidentes (M4) | **Mediana e IQR** (resumo principal), mínimo, máximo, p90, média (MTTR, M3) | Desvio-padrão como resumo principal: a distribuição é assimétrica |
| Razão, proporção | Proporção por impacto (M6), disponibilidade (M9) | Proporção com IC 95% de **Wilson** (M6); disponibilidade em % e minutos de indisponibilidade (M9) | — |

Gráficos previstos: série mensal das contagens (barras lado a lado), boxplot + pontos das durações em escala log, ECDF da duração, barras empilhadas por impacto. Sempre com título, eixos com nome e unidade, legenda e as cores combinadas (GitHub `#6e40c9`, GitLab `#fc6d26`).

## 3. Testes de hipótese

### 3.1 Frequência (Q1, M1): H₀-F × H₁-F

**Dados:** 12 pares (mês, contagem GitHub, contagem GitLab), nos mesmos meses.

| Papel | Teste | Por quê |
|---|---|---|
| **Principal** | **Wilcoxon signed-rank pareado** por mês, bilateral (`scipy.stats.wilcoxon`, `zero_method="wilcox"`, método exato quando não houver empates nem zeros) | A H₀-F do GQM foi escrita como "mediana das diferenças pareadas = 0". Os meses são o mesmo calendário para as duas plataformas, então parear controla o que é comum ao mês (feriados, fim de ano, picos de uso). Não supõe normalidade nem distribuição de Poisson. |
| Complementar | **Teste exato de razão de taxas de Poisson** (condicional: dado o total N, a contagem do GitHub ~ Binomial(N, 0,5) sob H₀, pois a exposição é a mesma, 12 meses) | Usa o total do ano e tem mais poder, **mas** supõe Poisson (variância = média). No piloto, a contagem mensal do GitHub teve variância/média = **1,82** (sobredispersão), o que torna esse teste otimista demais. Por isso ele é só complementar e vem com o valor de dispersão ao lado. |

**Tamanho do efeito:** **razão de taxas** `RT = incidentes/mês do GitHub ÷ incidentes/mês do GitLab`, com IC 95% por **bootstrap pareado por mês** (reamostra os 12 meses com reposição, mantendo o par). Também é mostrada a mediana das diferenças mensais (incidentes/mês).

**Cuidado:** com n = 12 o poder é limitado. O resultado é lido pelo IC da razão de taxas, não só pelo p-valor.

### 3.2 Tempo de recuperação (Q2, M2): H₀-R × H₁-R

**Dados:** duração em minutos de cada incidente, em duas amostras independentes (um incidente pertence a uma plataforma só).

| Papel | Teste | Por quê |
|---|---|---|
| **Principal** | **Mann-Whitney U**, bilateral (`scipy.stats.mannwhitneyu`, `method="auto"`) | A duração é de razão, mas **muito assimétrica**: no piloto (GitHub, out/2026, n = 22), média 147,8 min × mediana 84,1 min, assimetria 1,93 e Shapiro-Wilk p = 0,0001. O t de Student/Welch depende da média, que é puxada por poucos incidentes longos. O Mann-Whitney compara postos e testa exatamente a H₀-R do GQM (mesma distribuição). |
| Sensibilidade | **Welch t no log da duração** | No piloto, o log da duração ficou próximo da normal (Shapiro p = 0,995). Se os dois testes concordam, a conclusão é mais robusta; se discordam, isso é relatado. |

**Tamanho do efeito:**
- **Cliff's delta** (δ), com IC 95% por bootstrap, lido com os limiares de Romano et al. (2006): |δ| < 0,147 desprezível; < 0,33 pequeno; < 0,474 médio; acima disso grande. É o tamanho de efeito natural do Mann-Whitney (δ = 2·AUC − 1).
- **Diferença das medianas** em minutos, com IC 95% por bootstrap (reamostragem independente em cada plataforma). É o número que vai para o impacto (seção 7 do dashboard).
- **Razão dos MTTR** (média GitHub ÷ média GitLab), só descritiva.

**Observação:** o Mann-Whitney só pode ser lido como "diferença de medianas" se as duas distribuições tiverem formato parecido. Por isso a interpretação principal é a de dominância (δ: probabilidade de um incidente de uma plataforma durar mais que um da outra), e a diferença de medianas vem com o IC próprio.

### 3.3 Análises exploratórias (sem hipótese confirmatória)

| Pergunta | Métrica | Análise |
|---|---|---|
| Q2 | Tempo entre incidentes (M4, proxy de MTBF) | Descritiva por escala; Mann-Whitney + Cliff's delta como exploração. Sobreposições (M4 = 0) contadas à parte. |
| Q3 | Proporção por impacto (M6) | Proporções com IC de Wilson **dentro de cada plataforma**; sem teste entre plataformas, porque as escalas de impacto não são equivalentes. |
| Q3 | Duração por impacto (M7) | Kruskal-Wallis dentro de cada plataforma (duração × classe de impacto) + correlação de Spearman entre a ordem do impacto e a duração; Holm na família. |
| Q4 | Diferença entre fontes (M8, M9) | Descritiva: diferença de contagem (absoluta e %) e de disponibilidade (pontos percentuais) entre página de status e fonte independente/relatório oficial. |
| Q1 | Frequência por categoria | Mesma descrição de M1 por `componente_equivalente`, sem teste (n pequeno por categoria). |

## 4. Análises de sensibilidade (pré-definidas)

Cada uma refaz os testes principais e mostra se a conclusão muda:

1. **Incidentes retroativos** (GitHub: publicados depois do fato, sem duração estruturada; 3 de 25 no piloto de outubro): entram na frequência, ficam fora da duração. Sensibilidade: frequência sem eles.
2. **Incidentes sem componente** (9 de 25 no piloto): com e sem os que forem classificados à mão pelo título.
3. **Incidentes multicomponente:** total da plataforma (conta 1 vez) × por categoria (conta 1 vez em cada).
4. **Sobreposições e borda da janela:** incidentes iniciados antes de 2025-11-01 só entram aqui (regra do GQM).
5. **Categoria `web` unificada × separada** (decisão da issue #99).

## 5. Por que esses testes: o que veio do Lab04

No Lab04 simulamos o erro tipo I e o poder do Pearson × Spearman em dados assimétricos (KC1). O aprendizado aplicado aqui:

- **Com dados assimétricos e valores extremos, o teste baseado em postos mantém o erro tipo I perto de α e tem mais poder** que o teste baseado na média. A duração dos incidentes tem a mesma forma do LOC do KC1 (cauda longa à direita), por isso o teste principal de Q2 é de postos (Mann-Whitney), e o teste paramétrico entra só como sensibilidade, no log.
- **Não existe teste vencedor universal; o pressuposto decide:** no Lab04, quando os dados eram normais e a relação linear, o Pearson teve mais poder que o Spearman. A escolha depende de os pressupostos valerem ou não. Aqui, o teste de Poisson ficou como complementar porque o piloto já mostrou sobredispersão, e o Welch entra só no log, onde o piloto ficou próximo da normal.
- **Tamanho do efeito com IC**, não só "rejeita/não rejeita": reportamos δ e razão de taxas com IC 95%, que dizem *quanto* as plataformas diferem.
- **Reprodutibilidade:** semente 42, comando único e verificação de que duas execuções geram saídas idênticas, como no Lab04.

Se sobrar tempo na S02, reaproveitamos o simulador do Lab04 para estimar o **poder do Wilcoxon pareado com n = 12** para razões de taxa entre 1,2 e 2,0, reamostrando as contagens reais.

## 6. Onde cada resultado aparece

| Resultado | Arquivo gerado (comando único) | Seção do dashboard |
|---|---|---|
| Descritiva de frequência, Wilcoxon, Poisson, razão de taxas | `resultados/tabelas/frequencia_*.csv` | 4. Frequência |
| Descritiva de duração, Mann-Whitney, Welch-log, Cliff's δ, diferença de medianas | `resultados/tabelas/recuperacao_*.csv` | 5. Tempo de recuperação |
| Comparação com relatórios oficiais (M8, M9) | `resultados/tabelas/triangulacao_*.csv` | 6. Triangulação |
| Tradução para horas de trabalho afetadas | `resultados/tabelas/impacto_*.csv` | 7. Impacto |
| Sensibilidades e ameaças | `resultados/tabelas/sensibilidade_*.csv` | 8. Ameaças e conclusão |

## 7. Estrutura do dashboard

O dashboard (`lab05/code/dashboard.py`) segue o formato do Lab04: cada seção é um arquivo `secoes/secao_<N>_<nome>.py` com uma função `render()`, carregado na ordem abaixo. Seção que ainda não existe aparece como "em construção"; seção com erro mostra o erro sem derrubar as outras. Ninguém precisa editar o `dashboard.py` para incluir sua seção.

| Nº | Título | Arquivo esperado |
|---|---|---|
| 1 | Software | `secao_1_software.py` (pronto, serve de exemplo) |
| 2 | Pergunta e método | `secao_2_<nome>.py` |
| 3 | Dados e coleta | `secao_3_<nome>.py` |
| 4 | Frequência | `secao_4_<nome>.py` |
| 5 | Tempo de recuperação | `secao_5_<nome>.py` |
| 6 | Triangulação | `secao_6_<nome>.py` |
| 7 | Impacto | `secao_7_<nome>.py` |
| 8 | Ameaças e conclusão | `secao_8_<nome>.py` |

Peças comuns ficam em `lab05/code/dashboard_comum.py`: `CORES`, `NOMES`, janela do estudo e `carregar_incidentes()`, que lê `incidentes.csv` ou, se ele ainda não existir, o `exemplo_incidentes.csv`, devolvendo `eh_exemplo=True` para a seção chamar `avisar_se_exemplo()`.

Para abrir: `python -m streamlit run lab05/code/dashboard.py` (na raiz do repositório, para usar o tema claro do grupo).

"""Seção 6 do dashboard: os dois testes aplicados à amostra real do KC1."""
import pandas as pd
import streamlit as st

from analise_dados_reais import ARQUIVO_RESULTADO

NOMES_TESTE = {"pearson": "Pearson", "spearman": "Spearman"}
SIMBOLOS = {"pearson": "r", "spearman": "ρ"}
NOMES_CONJUNTO = {"amostra": "Amostra completa", "sem_maior_classe": "Sem a maior classe (sensibilidade)"}


def _br(valor, casas=2):
    return f"{valor:.{casas}f}".replace(".", ",")


def _p_valor(p):
    if p < 0.001:
        return "< 0,001"
    return _br(p, 3)


def ler_resultado(arquivo=ARQUIVO_RESULTADO):
    if not arquivo.exists():
        return pd.DataFrame()
    return pd.read_csv(arquivo)


def tabela_secao_6(resultado):
    """Estatística, p-valor, tamanho do efeito e conclusão de cada teste, como pede a seção 6."""
    return pd.DataFrame({
        "Conjunto": resultado["conjunto"].map(NOMES_CONJUNTO),
        "Teste": resultado["teste"].map(NOMES_TESTE),
        "n": resultado["n"],
        "Estatística (t)": [_br(t) for t in resultado["estatistica_t"]],
        "p-valor": [_p_valor(p) for p in resultado["p_valor"]],
        "Tamanho do efeito": [
            f"{SIMBOLOS[t]} = {_br(c)} ({m})" for t, c, m in
            zip(resultado["teste"], resultado["coeficiente"], resultado["magnitude"])
        ],
        "IC 95% do efeito": [f"{_br(i)} a {_br(s)}" for i, s in zip(resultado["ic95_inferior"], resultado["ic95_superior"])],
        "Conclusão (α = 0,05)": ["Rejeita H₀" if r else "Não rejeita H₀" for r in resultado["rejeita_h0"]],
    })


def texto_secao_6(resultado):
    linhas = resultado.set_index(["conjunto", "teste"])
    r, rho = linhas.loc[("amostra", "pearson")], linhas.loc[("amostra", "spearman")]
    r_sem, rho_sem = linhas.loc[("sem_maior_classe", "pearson")], linhas.loc[("sem_maior_classe", "spearman")]
    amostra = resultado[resultado["conjunto"] == "amostra"]
    if amostra["rejeita_h0"].all():
        concordancia = "Os dois testes rejeitam H₀ nos dados reais: classes maiores tendem a ter mais defeitos registrados"
    elif not amostra["rejeita_h0"].any():
        concordancia = "Nenhum dos dois testes rejeita H₀ nos dados reais"
    else:
        concordancia = "Os dois testes discordam nos dados reais"
    sensibilidade = "e os dois continuam rejeitando H₀" if resultado["rejeita_h0"].all() else "e a decisão muda"
    return (
        f"{concordancia}, com r = {_br(r['coeficiente'])} e ρ = {_br(rho['coeficiente'])}. "
        f"O r é inflado por uma única classe, a maior da amostra: sem ela, cai para {_br(r_sem['coeficiente'])}, "
        f"enquanto o ρ quase não muda ({_br(rho_sem['coeficiente'])}), {sensibilidade}. "
        "Na prática, um ρ em torno de 0,5 indica uma tendência clara, mas não determinística: o tamanho ajuda a "
        "priorizar revisões e testes nas classes maiores, mas não prevê quantos defeitos cada uma terá. "
        f"O intervalo do ρ é largo ({_br(rho['ic95_inferior'])} a {_br(rho['ic95_superior'])}) porque a amostra "
        f"tem só {int(rho['n'])} classes."
    )


def render():
    st.header("6. Dados reais")
    resultado = ler_resultado()
    if resultado.empty:
        st.info("Ainda não há resultado nos dados reais. Rode `python lab04/code/run_all.py` para gerá-lo.")
        return
    st.dataframe(tabela_secao_6(resultado), hide_index=True, width="stretch")
    st.write(texto_secao_6(resultado))
    st.caption(
        "Testes bicaudais com α = 0,05. O tamanho do efeito é o próprio r ou ρ, com magnitude pelos limiares de "
        "Cohen (1988). O intervalo usa a transformação z de Fisher (no Spearman, com a correção de Bonett e Wright). "
        "Retirar a maior classe é uma análise de sensibilidade decidida depois de ver os dados, não o resultado principal."
    )

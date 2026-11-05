"""Leitura, amostragem e calibração dos dados reais (KC1, nível de classe)."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize, stats

PASTA_DADOS = Path(__file__).resolve().parent / "dados"
ARQUIVO_BRUTO = PASTA_DADOS / "brutos" / "kc1-class-level-numericdefect.arff"
ARQUIVO_AMOSTRA = PASTA_DADOS / "amostra_kc1.csv"
ARQUIVO_PARAMETROS = PASTA_DADOS / "parametros.json"

TAMANHO_AMOSTRA = 30
SEMENTE = 42


def ler_arff(caminho=ARQUIVO_BRUTO):
    """Devolve uma linha por classe, com `linha_arff`, `loc` e `defeitos`."""
    linhas = Path(caminho).read_text(encoding="ascii").splitlines()
    atributos = [l.split()[1] for l in linhas if l.lower().startswith("@attribute")]
    inicio = next(i for i, l in enumerate(linhas) if l.lower().startswith("@data")) + 1
    registros = [l.split(",") for l in linhas[inicio:] if l.strip() and not l.startswith("%")]
    tabela = pd.DataFrame(registros, columns=atributos).apply(pd.to_numeric)
    return pd.DataFrame({
        "linha_arff": np.arange(len(tabela)),
        "loc": tabela["sumLOC_TOTAL"].astype(int),
        "defeitos": tabela["NUMDEFECTS"].astype(int),
    })


def sortear_amostra(populacao, tamanho=TAMANHO_AMOSTRA, semente=SEMENTE):
    """Amostra aleatória simples, sem reposição e reproduzível."""
    rng = np.random.default_rng(semente)
    posicoes = np.sort(rng.choice(len(populacao), size=tamanho, replace=False))
    return populacao.iloc[posicoes].reset_index(drop=True)


def ajustar_lognormal(valores):
    """Estimadores de máxima verossimilhança da lognormal."""
    logs = np.log(np.asarray(valores, dtype=float))
    return float(logs.mean()), float(logs.std(ddof=1))


def ajustar_binomial_negativa(valores):
    """Devolve a média e a dispersão `k` por máxima verossimilhança.

    Na binomial negativa, o estimador de máxima verossimilhança da média é a
    média da amostra, então só `k` precisa de otimização numérica.
    """
    valores = np.asarray(valores)
    media = float(valores.mean())

    def verossimilhanca_negativa(log_k):
        k = np.exp(log_k)
        return -stats.nbinom.logpmf(valores, k, k / (k + media)).sum()

    resultado = optimize.minimize_scalar(verossimilhanca_negativa, bounds=(-7, 7), method="bounded")
    return media, float(np.exp(resultado.x))


def descrever(serie):
    """Estatísticas descritivas usadas no cenário e no dashboard."""
    q1, q3 = np.percentile(serie, [25, 75])
    return {
        "n": int(len(serie)),
        "media": float(np.mean(serie)),
        "mediana": float(np.median(serie)),
        "desvio_padrao": float(np.std(serie, ddof=1)),
        "q1": float(q1),
        "q3": float(q3),
        "minimo": float(np.min(serie)),
        "maximo": float(np.max(serie)),
        "assimetria": float(stats.skew(serie)),
        "outliers_iqr": int(np.sum(serie > q3 + 1.5 * (q3 - q1))),
        "proporcao_zeros": float(np.mean(np.asarray(serie) == 0)),
    }


def amostrar_copula(mu, sigma, media, k, efeito, n, rng):
    """Sorteia LOC e defeitos com margens fixas e associação dada por `efeito`.

    `efeito` é a correlação das normais latentes da cópula gaussiana. Com
    `efeito = 0` as duas variáveis são independentes.
    """
    z_loc = rng.standard_normal(n)
    z_defeitos = efeito * z_loc + np.sqrt(1 - efeito**2) * rng.standard_normal(n)
    loc = np.maximum(np.rint(np.exp(mu + sigma * z_loc)), 1).astype(int)
    defeitos = stats.nbinom.ppf(stats.norm.cdf(z_defeitos), k, k / (k + media)).astype(int)
    return loc, defeitos


def calibrar_efeito(rho_alvo, mu, sigma, media, k, semente=SEMENTE, n=200_000):
    """Acha o `efeito` latente cujo ρ de Spearman simulado se aproxima do alvo."""

    def diferenca(efeito):
        rng = np.random.default_rng(semente)
        loc, defeitos = amostrar_copula(mu, sigma, media, k, efeito, n, rng)
        return stats.spearmanr(loc, defeitos).statistic - rho_alvo

    return float(optimize.brentq(diferenca, 0.0, 0.98, xtol=1e-3))


def calibrar(amostra):
    """Calcula os parâmetros do gerador a partir da amostra real."""
    mu, sigma = ajustar_lognormal(amostra["loc"])
    media, k = ajustar_binomial_negativa(amostra["defeitos"])
    rho = float(stats.spearmanr(amostra["loc"], amostra["defeitos"]).statistic)
    return {
        "fonte": "amostra_kc1.csv",
        "loc": {"distribuicao": "lognormal", "mu": mu, "sigma": sigma},
        "defeitos": {"distribuicao": "binomial_negativa", "media": media, "k": k},
        "associacao": {
            "rho_spearman_amostra": rho,
            "efeito_calibrado": calibrar_efeito(rho, mu, sigma, media, k),
        },
    }


def preparar(caminho_bruto=ARQUIVO_BRUTO, arquivo_amostra=ARQUIVO_AMOSTRA, arquivo_parametros=ARQUIVO_PARAMETROS):
    """Gera a amostra e os parâmetros a partir do arquivo bruto."""
    amostra = sortear_amostra(ler_arff(caminho_bruto))
    amostra.to_csv(arquivo_amostra, index=False)
    parametros = calibrar(amostra)
    Path(arquivo_parametros).write_text(
        json.dumps(parametros, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return amostra, parametros

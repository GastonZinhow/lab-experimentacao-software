"""
Heurística de release corretiva (RQ 03 b, Issue #61).

Uma release corretiva é aquela cujo objetivo principal é corrigir um defeito
recente. A heurística usa só o que o pipeline coleta: o nome da tag da
release e o da anterior, a primeira linha das mensagens dos commits entre as
duas e, a partir da v3, o texto das release notes (campo `body` da API).
O histórico das versões e o P/R/F1 de cada uma frente à amostra-ouro estão em
docs/versoes_heuristica.md.
"""
import re
from typing import Iterable, List, Optional, Tuple

VERSAO_ATUAL = "v3"

# Último "X.Y" ou "X.Y.Z" da tag: aceita prefixos de pacote (rig-core-v0.1.2,
# @scope/pkg@1.2.3, dulwich-0.24.2) e ignora sufixos (-rc.1, +build, .Final).
_VERSAO = re.compile(r"(?<![\d.])(\d+)\.(\d+)(?:\.(\d+))?")

# v1: palavras de correção no começo de palavra ("fix", "fixes", "hotfix",
# "Revert"), mas não "prefix".
_CORRECAO_V1 = re.compile(r"\b(revert|hotfix|fix)", re.IGNORECASE)

# v2/v3: sinais de correção e de funcionalidade em commits e linhas das notas.
_CORRECAO = re.compile(r"\b(revert|hotfix|fix|bug|regression|crash|broken|workaround)", re.IGNORECASE)
_FUNCIONALIDADE = re.compile(
    r"\b(feat|features?|add|adds|added|new|implement|introduc|support|highlights?|improve|enhance)",
    re.IGNORECASE,
)
# Linhas que não dizem nada sobre o propósito da release: manutenção,
# dependências, merges, commits de versão e o texto padrão das notas do GitHub.
_RUIDO = re.compile(
    r"^(chore|build|ci|docs|style|test|refactor|merge|release|version|prepare|\[skip ci\]|new crowdin)"
    r"|dependabot|renovate|\bbump\b|^v?\d+\.\d+"
    r"|full changelog|what's changed|new contributors|made their first contribution|^contributors",
    re.IGNORECASE,
)
# Marcadores de lista e de título do Markdown no início das linhas das notas
_MARCADOR = re.compile(r"^[\s>*#+\-\d.)]+")

# Limiares da v2/v3 (escolhidos por validação cruzada agrupada por repositório,
# ver docs/versoes_heuristica.md)
MAX_COMMITS_SIGNIFICATIVOS = 5
MAX_FUNCIONALIDADE_POR_CORRECAO = 0.5

Versao = Tuple[int, int, int]


def _versao_e_pacote(tag: Optional[str]) -> Optional[Tuple[str, Versao]]:
    if not tag:
        return None
    encontrados = list(_VERSAO.finditer(tag))
    if not encontrados:
        return None
    m = encontrados[-1]
    pacote = re.sub(r"[-_@/ ]*v?$", "", tag[:m.start()].lower())
    return pacote, (int(m.group(1)), int(m.group(2)), int(m.group(3) or 0))


def parse_versao(tag: Optional[str]) -> Optional[Versao]:
    """
    Extrai (major, minor, patch) do nome de uma tag. O patch ausente vale 0
    ("v3.0" → (3, 0, 0)). Retorna None para tags fora do SemVer, como
    "unlshd-083", "october-2025" ou "nightly".
    """
    resultado = _versao_e_pacote(tag)
    return resultado[1] if resultado else None


def pacote_da_tag(tag: Optional[str]) -> Optional[str]:
    """Prefixo da tag antes da versão ("" em "v1.2.3", "rig-core" em "rig-core-v0.1.2")."""
    resultado = _versao_e_pacote(tag)
    return resultado[0] if resultado else None


def tipo_incremento(
    tag_anterior: Optional[str], tag: Optional[str], mesmo_pacote: bool = False
) -> Optional[str]:
    """
    Compara as versões de duas tags e devolve "major", "minor" ou "patch",
    conforme o componente mais significativo que aumentou. Devolve None se
    alguma das tags estiver fora do SemVer, se a versão não aumentou (série
    paralela mais antiga) ou, com mesmo_pacote=True, se as tags forem de
    pacotes diferentes de um monorepo.
    """
    anterior, atual = _versao_e_pacote(tag_anterior), _versao_e_pacote(tag)
    if anterior is None or atual is None:
        return None
    if mesmo_pacote and anterior[0] != atual[0]:
        return None
    (_, va), (_, vb) = anterior, atual
    if vb <= va:
        return None
    if vb[0] != va[0]:
        return "major"
    if vb[1] != va[1]:
        return "minor"
    return "patch"


def tem_commit_corretivo(mensagens: Iterable[Optional[str]]) -> bool:
    """True se algum commit menciona revert, hotfix ou fix (v1)."""
    return any(m and _CORRECAO_V1.search(m) for m in mensagens)


def linhas_significativas(textos: Iterable[Optional[str]]) -> List[str]:
    """
    Quebra os textos em linhas, tira marcadores de lista/título e descarta
    linhas vazias e de ruído (manutenção, dependências, merges, texto padrão).
    """
    linhas = []
    for texto in textos:
        for linha in (texto or "").splitlines():
            linha = _MARCADOR.sub("", linha).strip()
            if linha and not _RUIDO.search(linha):
                linhas.append(linha)
    return linhas


def contar_sinais(linhas: Iterable[str]) -> Tuple[int, int]:
    """(nº de linhas com sinal de correção, nº de linhas só com sinal de funcionalidade)."""
    correcao = funcionalidade = 0
    for linha in linhas:
        if _CORRECAO.search(linha):
            correcao += 1
        elif _FUNCIONALIDADE.search(linha):
            funcionalidade += 1
    return correcao, funcionalidade


def e_corretiva_v1(
    tag: Optional[str],
    tag_anterior: Optional[str],
    mensagens: Iterable[Optional[str]],
    notas: Optional[str] = None,
) -> bool:
    """
    v1 (enunciado): a release é corretiva se muda só o patch do SemVer
    (2.3.0 → 2.3.1) e/ou há commits com revert, hotfix ou fix entre ela e a
    anterior. Tags fora do SemVer caem só no critério dos commits.
    """
    return tipo_incremento(tag_anterior, tag) == "patch" or tem_commit_corretivo(mensagens)


def _corretiva_por_sinais(
    tag: Optional[str],
    tag_anterior: Optional[str],
    mensagens: Iterable[Optional[str]],
    notas: Optional[str],
    incrementos: Tuple[Optional[str], ...],
) -> bool:
    if tipo_incremento(tag_anterior, tag, mesmo_pacote=True) not in incrementos:
        return False
    commits = linhas_significativas(mensagens)
    if len(commits) > MAX_COMMITS_SIGNIFICATIVOS:
        return False
    correcao, funcionalidade = contar_sinais(commits + linhas_significativas([notas]))
    return correcao > 0 and funcionalidade <= MAX_FUNCIONALIDADE_POR_CORRECAO * correcao


def e_corretiva_v2(
    tag: Optional[str],
    tag_anterior: Optional[str],
    mensagens: Iterable[Optional[str]],
    notas: Optional[str] = None,
) -> bool:
    """
    v2 (só commits): a release é corretiva se
      - a versão muda só o patch, comparando tags do mesmo pacote, ou a tag
        está fora do SemVer;
      - tem no máximo MAX_COMMITS_SIGNIFICATIVOS commits que não são ruído;
      - há ao menos um commit de correção e no máximo
        MAX_FUNCIONALIDADE_POR_CORRECAO commits de funcionalidade por commit
        de correção.
    """
    return _corretiva_por_sinais(tag, tag_anterior, mensagens, None, ("patch", None))


def e_corretiva_v3(
    tag: Optional[str],
    tag_anterior: Optional[str],
    mensagens: Iterable[Optional[str]],
    notas: Optional[str] = None,
) -> bool:
    """
    v3 (commits + release notes): igual à v2, mas conta também os sinais de
    correção e de funcionalidade nas linhas das release notes e aceita
    incremento de minor (só o major fica de fora).
    """
    return _corretiva_por_sinais(tag, tag_anterior, mensagens, notas, ("patch", "minor", None))


VERSOES = {
    "v1": e_corretiva_v1,
    "v2": e_corretiva_v2,
    "v3": e_corretiva_v3,
}


def e_corretiva(
    tag: Optional[str],
    tag_anterior: Optional[str],
    mensagens: Iterable[Optional[str]],
    notas: Optional[str] = None,
) -> bool:
    """Heurística na versão atual (VERSAO_ATUAL), usada no CFR (b)."""
    return VERSOES[VERSAO_ATUAL](tag, tag_anterior, list(mensagens), notas)

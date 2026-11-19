"""Acesso à internet compartilhado pelos coletores, seguindo o plano de coleta.

Regras (``lab05/docs/plano_coleta.md``, seção 3):

1. no máximo 1 requisição por segundo, somando todos os coletores;
2. User-Agent genérico, sem nome nem e-mail;
3. cache local: se o arquivo já existe em ``dados/brutos/<plataforma>/``, a
   internet não é acessada;
4. robots.txt respeitado, inclusive com curingas (``*`` e ``$``), que o
   ``urllib.robotparser`` da biblioteca padrão não entende;
5. erros 4xx não são repetidos; erros 5xx e falhas de rede têm no máximo uma
   nova tentativa depois de 60 s;
6. cada requisição real vira uma linha em ``manifesto.csv``.
"""

from __future__ import annotations

import csv
import hashlib
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import requests

USER_AGENT = "lab05-coleta/1.0 (pesquisa academica)"
INTERVALO_MINIMO_S = 1.1
ESPERA_NOVA_TENTATIVA_S = 60.0
CAMPOS_MANIFESTO = ("url", "data_hora_utc", "status_http", "arquivo", "sha256")


class ErroColeta(RuntimeError):
    """A resposta não pôde ser obtida (erro HTTP ou de rede)."""


class CaminhoBloqueado(ErroColeta):
    """O robots.txt do site não permite que um robô acesse o endereço."""


# --------------------------------------------------------------------------- #
# robots.txt
# --------------------------------------------------------------------------- #


@dataclass
class RegrasRobots:
    """Regras do grupo ``User-agent: *`` de um robots.txt."""

    permitir: list[str] = field(default_factory=list)
    bloquear: list[str] = field(default_factory=list)

    @classmethod
    def de_texto(cls, texto: str) -> RegrasRobots:
        regras = cls()
        agentes: list[str] = []
        lendo_agentes = False
        for linha in texto.splitlines():
            linha = linha.split("#", 1)[0].strip()
            if ":" not in linha:
                continue
            chave, valor = (parte.strip() for parte in linha.split(":", 1))
            chave = chave.lower()
            if chave == "user-agent":
                if not lendo_agentes:
                    agentes = []
                agentes.append(valor)
                lendo_agentes = True
                continue
            lendo_agentes = False
            if "*" not in agentes or not valor:
                continue
            if chave == "disallow":
                regras.bloquear.append(valor)
            elif chave == "allow":
                regras.permitir.append(valor)
        return regras

    def permite(self, caminho: str) -> bool:
        """Aplica a regra mais longa que casa com o caminho (RFC 9309)."""
        melhor_tamanho, permitido = -1, True
        for padrao, valor in [(p, True) for p in self.permitir] + [
            (p, False) for p in self.bloquear
        ]:
            if _casa(padrao, caminho) and (
                len(padrao) > melhor_tamanho
                or (len(padrao) == melhor_tamanho and valor)
            ):
                melhor_tamanho, permitido = len(padrao), valor
        return permitido


def _casa(padrao: str, caminho: str) -> bool:
    regex = re.escape(padrao).replace(r"\*", ".*")
    if regex.endswith(r"\$"):
        regex = regex[:-2] + "$"
    return re.match(regex, caminho) is not None


# --------------------------------------------------------------------------- #
# Cliente
# --------------------------------------------------------------------------- #


def agora_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


class ClienteEducado:
    """Baixa arquivos para uma pasta de dados brutos, com cache e manifesto."""

    _ultima_requisicao = 0.0  # compartilhado entre instâncias: 1 req/s no total

    def __init__(
        self,
        pasta: Path,
        sessao: requests.Session | None = None,
        dormir=time.sleep,
        relogio=time.monotonic,
    ) -> None:
        self.pasta = Path(pasta)
        self.sessao = sessao
        self._dormir = dormir
        self._relogio = relogio
        self._robots: dict[str, RegrasRobots] = {}
        self.requisicoes = 0

    # -- infraestrutura ----------------------------------------------------- #

    def _sessao(self) -> requests.Session:
        if self.sessao is None:
            self.sessao = requests.Session()
        self.sessao.headers["User-Agent"] = USER_AGENT
        return self.sessao

    def _esperar_vez(self) -> None:
        decorrido = self._relogio() - ClienteEducado._ultima_requisicao
        if decorrido < INTERVALO_MINIMO_S:
            self._dormir(INTERVALO_MINIMO_S - decorrido)
        ClienteEducado._ultima_requisicao = self._relogio()

    def _registrar(
        self, url: str, status: int | str, arquivo: str, resumo: str, data_hora: str | None = None
    ) -> None:
        manifesto = self.pasta / "manifesto.csv"
        novo = not manifesto.exists()
        self.pasta.mkdir(parents=True, exist_ok=True)
        with manifesto.open("a", newline="", encoding="utf-8") as saida:
            escritor = csv.writer(saida, lineterminator="\n")
            if novo:
                escritor.writerow(CAMPOS_MANIFESTO)
            escritor.writerow([url, data_hora or agora_utc(), status, arquivo, resumo])

    def _requisitar(self, url: str) -> requests.Response:
        """Uma requisição, com no máximo uma nova tentativa para erros 5xx/rede."""
        for tentativa in (1, 2):
            self._esperar_vez()
            self.requisicoes += 1
            try:
                resposta = self._sessao().get(url, timeout=60)
            except requests.RequestException as erro:
                self._registrar(url, f"erro:{type(erro).__name__}", "", "")
                if tentativa == 2:
                    raise ErroColeta(f"Falha de rede em {url}: {erro}") from erro
                self._dormir(ESPERA_NOVA_TENTATIVA_S)
                continue
            if resposta.status_code < 500 or tentativa == 2:
                return resposta
            self._registrar(url, resposta.status_code, "", "")
            self._dormir(ESPERA_NOVA_TENTATIVA_S)
        raise AssertionError("inalcançável")

    def regras_robots(self, url: str) -> RegrasRobots:
        partes = urlsplit(url)
        base = f"{partes.scheme}://{partes.netloc}"
        if base not in self._robots:
            resposta = self._requisitar(base + "/robots.txt")
            self._registrar(base + "/robots.txt", resposta.status_code, "", sha256(resposta.content))
            if resposta.status_code >= 400:
                # Sem robots.txt legível, não arriscamos: tudo é tratado como bloqueado.
                self._robots[base] = RegrasRobots(bloquear=["/"])
            else:
                self._robots[base] = RegrasRobots.de_texto(resposta.text)
        return self._robots[base]

    def permitido(self, url: str) -> bool:
        partes = urlsplit(url)
        caminho = partes.path + (f"?{partes.query}" if partes.query else "")
        return self.regras_robots(url).permite(caminho or "/")

    # -- uso pelos coletores ----------------------------------------------- #

    def obter(self, url: str, arquivo: str) -> bytes:
        """Devolve o conteúdo de ``arquivo``; baixa de ``url`` só se não estiver no cache."""
        destino = self.pasta / arquivo
        if destino.exists():
            return destino.read_bytes()

        if not self.permitido(url):
            raise CaminhoBloqueado(
                f"O robots.txt bloqueia {url}. Salve o arquivo manualmente em {destino} "
                "(opção C do plano de coleta) ou aguarde a decisão do professor."
            )

        resposta = self._requisitar(url)
        if resposta.status_code >= 400:
            self._registrar(url, resposta.status_code, "", "")
            raise ErroColeta(f"HTTP {resposta.status_code} em {url}")

        conteudo = resposta.content
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(conteudo)
        self._registrar(url, resposta.status_code, arquivo, sha256(conteudo))
        return conteudo

    def registrar_arquivo_manual(self, url: str, arquivo: str) -> None:
        """Anota no manifesto um arquivo salvo por uma pessoa no navegador.

        A data anotada é a da última modificação do arquivo (quando foi salvo).
        """
        destino = self.pasta / arquivo
        manifesto = self.pasta / "manifesto.csv"
        if manifesto.exists() and f",{arquivo}," in manifesto.read_text(encoding="utf-8"):
            return
        salvo_em = datetime.fromtimestamp(destino.stat().st_mtime, timezone.utc)
        self._registrar(
            url, "manual", arquivo, sha256(destino.read_bytes()),
            salvo_em.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

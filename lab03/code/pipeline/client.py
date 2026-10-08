import os
import re
import subprocess
import time
import requests
from typing import Callable, Dict, Any, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse
from pipeline.cache import ResponseCache


def parse_last_page(link_header: Optional[str]) -> Optional[int]:
    """
    Lê o número da última página no cabeçalho `Link` da API do GitHub.

    Ex.: '<https://api.github.com/...&page=2>; rel="next",
          <https://api.github.com/...&page=523>; rel="last"' -> 523

    Retorna None quando não há `rel="last"` (resposta de página única
    ou já na última página).
    """
    if not link_header:
        return None
    for part in link_header.split(","):
        match = re.search(r'<([^>]+)>\s*;\s*rel="last"', part)
        if match:
            page = parse_qs(urlparse(match.group(1)).query).get("page")
            if page:
                return int(page[0])
    return None


def _gh_cli_token() -> str:
    """Token do GitHub CLI (`gh auth token`), se ele estiver instalado e logado."""
    try:
        result = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, timeout=10
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


class GitHubClient:
    def __init__(
        self,
        token: Optional[str] = None,
        cache: Optional[ResponseCache] = None,
        max_retries: int = 5,
    ):
        self.token = token or os.environ.get("GITHUB_TOKEN", "") or _gh_cli_token()
        if not self.token:
            raise ValueError(
                "Token do GitHub não encontrado. Defina a variável de ambiente "
                "GITHUB_TOKEN (PowerShell: $env:GITHUB_TOKEN = \"seu_token\"; "
                "bash: export GITHUB_TOKEN=seu_token) ou faça login com `gh auth login`."
            )

        self.cache = cache
        self.max_retries = max_retries

        self.total_requests = 0
        self.network_requests = 0
        self.cache_hits = 0

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "DORA-Metrics-Mining-Script",
        })

    def _handle_rate_limit(self, response: requests.Response) -> None:
        remaining = int(response.headers.get("X-RateLimit-Remaining", 1))
        reset_time = int(response.headers.get("X-RateLimit-Reset", 0))

        if remaining == 0:
            sleep_duration = max(0, reset_time - int(time.time())) + 2
            print(
                f"[Rate Limit] Cota esgotada. Pausando execução por {sleep_duration}s..."
            )
            time.sleep(sleep_duration)

    @staticmethod
    def _is_rate_limited(response: requests.Response) -> bool:
        if response.status_code not in (403, 429):
            return False
        return (
            response.headers.get("X-RateLimit-Remaining") == "0"
            or "Retry-After" in response.headers
            or "rate limit" in response.text.lower()
        )

    def request_with_retry(
        self, url: str, params: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        full_req = requests.Request("GET", url, params=params).prepare()
        full_url = full_req.url

        backoff = 1
        for attempt in range(self.max_retries):
            try:
                resp = self.session.get(full_url, timeout=60)
            except (requests.ConnectionError, requests.Timeout) as e:
                # Queda de rede é temporária como um 5xx: mesmo backoff.
                if attempt == self.max_retries - 1:
                    raise
                print(f"[Rede] {e.__class__.__name__}; nova tentativa em {backoff}s")
                time.sleep(backoff)
                backoff *= 2
                continue
            self._handle_rate_limit(resp)

            if resp.ok or resp.status_code == 404:
                return resp
            elif 500 <= resp.status_code < 600 or self._is_rate_limited(resp):
                time.sleep(int(resp.headers.get("Retry-After", backoff)))
                backoff *= 2
            else:
                # 403 que não é rate limit (ex.: lista de contribuidores
                # grande demais) não melhora com nova tentativa.
                resp.raise_for_status()

        resp.raise_for_status()
        return resp

    def get_json(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        transform: Optional[Callable[[Any], Any]] = None,
    ) -> Tuple[Any, bool]:
        """`transform` reduz a resposta antes de ela ir para o cache."""
        full_req = requests.Request("GET", url, params=params).prepare()
        cache_key = full_req.url
        self.total_requests += 1

        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                self.cache_hits += 1
                return cached, True

        self.network_requests += 1
        resp = self.request_with_retry(url, params=params)
        data = resp.json()
        if transform is not None and resp.status_code == 200:
            data = transform(data)

        if self.cache and resp.status_code == 200:
            self.cache.set(cache_key, data)

        return data, False

    def count_items(
        self, url: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[int]:
        """
        Conta os itens de um endpoint paginado sem baixar a lista inteira:
        com `per_page=1`, o número da última página no cabeçalho `Link`
        é o total de itens. Retorna None se o recurso não existir (404).
        """
        params = {**(params or {}), "per_page": 1}
        full_req = requests.Request("GET", url, params=params).prepare()
        cache_key = f"{full_req.url}#count"
        self.total_requests += 1

        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                self.cache_hits += 1
                return cached["count"]

        self.network_requests += 1
        resp = self.request_with_retry(url, params=params)
        if resp.status_code == 404:
            return None

        count = parse_last_page(resp.headers.get("Link"))
        if count is None:
            # Página única: 0 ou 1 item (204 = repositório vazio).
            count = len(resp.json()) if resp.status_code == 200 else 0

        if self.cache:
            self.cache.set(cache_key, {"count": count})
        return count

    def paginate(
        self, url: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        items: List[Any] = []
        next_url: Optional[str] = url
        current_params = params

        while next_url:
            full_req = requests.Request(
                "GET", next_url, params=current_params
            ).prepare()
            cache_key = full_req.url
            self.total_requests += 1

            cached_data = self.cache.get(cache_key) if self.cache else None
            if cached_data is not None:
                self.cache_hits += 1
                items.extend(cached_data.get("items", []))
                next_url = cached_data.get("next_url")
                current_params = None
                continue

            self.network_requests += 1
            resp = self.request_with_retry(next_url, params=current_params)
            data = resp.json()

            if isinstance(data, dict):
                page_items = data.get(
                    "workflow_runs", data.get("commits", data.get("items", []))
                )
            else:
                page_items = data

            next_link = resp.links.get("next", {}).get("url")

            if self.cache and resp.status_code == 200:
                self.cache.set(
                    cache_key, {"items": page_items, "next_url": next_link}
                )

            items.extend(page_items)
            next_url = next_link
            current_params = None

        return items
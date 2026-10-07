import os
import time
import requests
from typing import Dict, Any, List, Optional
from pipeline.cache import ResponseCache

class GitHubClient:
    def __init__(self, token: Optional[str] = None, cache: Optional[ResponseCache] = None, max_retries: int = 5):
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        if not self.token:
            raise ValueError("Token do GitHub não encontrado nas variáveis de ambiente.")
        self.cache = cache
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "DORA-Metrics-Mining-Script"
        })

    def _handle_rate_limit(self, response: requests.Response) -> None:
        remaining = int(response.headers.get("X-RateLimit-Remaining", 1))
        reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
        if remaining == 0:
            sleep_duration = max(0, reset_time - int(time.time())) + 2
            print(f"[Rate Limit] Cota esgotada. Aguardando {sleep_duration}s...")
            time.sleep(sleep_duration)

    def request_with_retry(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        full_req = requests.Request("GET", url, params=params).prepare()
        full_url = full_req.url

        backoff = 1
        for attempt in range(self.max_retries):
            resp = self.session.get(full_url)
            self._handle_rate_limit(resp)

            if resp.status_code in [200, 404]:
                return resp
            elif 500 <= resp.status_code < 600 or resp.status_code == 403:
                time.sleep(backoff)
                backoff *= 2
            else:
                resp.raise_for_status()

        resp.raise_for_status()
        return resp

    def get_json(self, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        full_req = requests.Request("GET", url, params=params).prepare()
        cache_key = full_req.url

        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached, True

        resp = self.request_with_retry(url, params=params)
        data = resp.json()
        if self.cache and resp.status_code == 200:
            self.cache.set(cache_key, data)
        return data, False

    def paginate(self, url: str, params: Optional[Dict[str, Any]] = None) -> List[Any]:
        items = []
        next_url = url
        current_params = params

        while next_url:
            full_req = requests.Request("GET", next_url, params=current_params).prepare()
            cache_key = full_req.url

            cached_data = self.cache.get(cache_key) if self.cache else None
            if cached_data is not None:
                page_data = cached_data
                items.extend(page_data.get("items", []))
                next_url = page_data.get("next_url")
                current_params = None
                continue

            resp = self.request_with_retry(next_url, params=current_params)
            data = resp.json()
            page_items = data.get("workflow_runs", data) if isinstance(data, dict) else data

            next_link = resp.links.get("next", {}).get("url")
            if self.cache and resp.status_code == 200:
                self.cache.set(cache_key, {"items": page_items, "next_url": next_link})

            items.extend(page_items)
            next_url = next_link
            current_params = None

        return items
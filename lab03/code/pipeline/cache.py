import json
import os
import sqlite3
import threading
from typing import Any, Optional


class ResponseCache:
    def __init__(self, db_path: str = ".cache/api_cache.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self._lock = threading.Lock()
        # Uma única conexão reaproveitada (antes: uma nova por get/set).
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                url TEXT PRIMARY KEY,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self._conn.commit()

    def get(self, url: str) -> Optional[Any]:
        with self._lock:
            row = self._conn.execute(
                "SELECT data FROM cache WHERE url = ?", (url,)
            ).fetchone()
        return json.loads(row[0]) if row else None

    def set(self, url: str, data: Any) -> None:
        payload = json.dumps(data)
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO cache (url, data) VALUES (?, ?)",
                (url, payload),
            )
            self._conn.commit()
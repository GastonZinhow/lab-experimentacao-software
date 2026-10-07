import sqlite3
import json
from typing import Optional, Any

class ResponseCache:
    def __init__(self, db_path: str = ".cache/api_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    url TEXT PRIMARY KEY,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def get(self, url: str) -> Optional[Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM cache WHERE url = ?", (url,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
        return None

    def set(self, url: str, data: Any) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (url, data) VALUES (?, ?)",
                (url, json.dumps(data))
            )
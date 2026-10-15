import os
import shutil
import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd

from pipeline.client import NotFoundError

_ENV = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}  # nunca pedir senha (repo apagado/privado)


def _utc(iso: Optional[str]) -> Optional[str]:
    """Converte data ISO com offset para UTC no formato da API (…Z)."""
    if not iso:
        return None
    return datetime.fromisoformat(iso).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class GitRepo:
    def __init__(self, owner: str, repo: str, base_dir: str):
        self.owner, self.repo = owner, repo
        self.base_dir = base_dir
        self.path = os.path.join(base_dir, f"{owner}__{repo}.git")

    def _git(self, *args: str, input: Optional[str] = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", "-C", self.path, *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            input=input, env=_ENV,
        )

    def ensure_cloned(self) -> bool:
        """Clone bare sem blobs (só commits/árvores). Reaproveita clone existente."""
        if os.path.isdir(self.path):
            return True
        os.makedirs(self.base_dir, exist_ok=True)
        tmp = self.path + ".tmp"
        shutil.rmtree(tmp, ignore_errors=True)
        r = subprocess.run(
            ["git", "clone", "--bare", "--filter=blob:none", "--quiet",
             f"https://github.com/{self.owner}/{self.repo}.git", tmp],
            capture_output=True, text=True, encoding="utf-8", errors="replace", env=_ENV,
        )
        if r.returncode != 0:
            print(f"[Git] falha ao clonar {self.owner}/{self.repo}: {r.stderr.strip()[:200]}")
            shutil.rmtree(tmp, ignore_errors=True)
            return False
        os.rename(tmp, self.path)
        print(f"[Git] clonado {self.owner}/{self.repo}")
        return True

    def compare_commits(self, base: str, head: str) -> List[Dict[str, Any]]:
        """
        Equivalente a compare/base...head da API: commits de head que não estão
        em base, do mais antigo ao mais novo, no mesmo formato de dict da API.
        Lança NotFoundError se alguma das tags não existir.
        """
        r = self._git(
            "log", "--reverse",
            "--format=%H%x1f%aI%x1f%cI%x1f%B%x1e",
            f"refs/tags/{base}..refs/tags/{head}",
        )
        if r.returncode != 0:
            raise NotFoundError(f"{base}...{head}: {r.stderr.strip()[:200]}")
        commits = []
        for reg in r.stdout.split("\x1e"):
            reg = reg.lstrip("\n")
            if not reg.strip():
                continue
            sha, adate, cdate, msg = reg.split("\x1f", 3)
            commits.append({
                "sha": sha,
                "commit": {
                    "author": {"date": _utc(adate)},
                    "committer": {"date": _utc(cdate)},
                    "message": msg.strip("\n"),
                },
            })
        return commits

    def tags(self, max_tags: Optional[int] = None) -> List[Dict[str, Any]]:
        r = self._git(
            "for-each-ref", "--sort=-creatordate",
            "--format=%(refname:strip=2)%09%(objecttype)%09%(objectname)%09%(*objecttype)%09%(*objectname)",
            "refs/tags",
        )
        rows = []
        for line in r.stdout.splitlines():
            nome, tipo, obj, tipo_p, obj_p = (line.split("\t") + [""] * 5)[:5]
            sha = obj if tipo == "commit" else (obj_p if tipo_p == "commit" else None)
            rows.append({"name": nome, "sha": sha})
        if max_tags is not None:
            rows = rows[:max_tags]
        return rows

    def commit_dates(self, shas: List[str]) -> Dict[str, tuple]:
        if not shas:
            return {}
        r = self._git("log", "--no-walk=unsorted", "--stdin",
                      "--format=%H%x1f%aI%x1f%cI", input="\n".join(shas) + "\n")
        out = {}
        for line in r.stdout.splitlines():
            parts = line.split("\x1f")
            if len(parts) == 3:
                out[parts[0]] = (_utc(parts[1]), _utc(parts[2]))
        return out


def collect_repo_tags_git(git: GitRepo, owner: str, repo: str,
                          max_tags: Optional[int] = None) -> pd.DataFrame:
    """Mesmo retorno de collect_repo_tags, sem nenhuma chamada à API."""
    nome = f"{owner}/{repo}"
    tags = git.tags(max_tags)
    datas = git.commit_dates(sorted({t["sha"] for t in tags if t["sha"]}))
    linhas = []
    for t in tags:
        a, c = datas.get(t["sha"], (None, None))
        linhas.append({
            "repo": nome, "tag_name": t["name"], "sha": t["sha"],
            "commit_author_date": a, "commit_committer_date": c,
        })
    sem_data = sum(1 for l in linhas if l["commit_author_date"] is None)
    print(f"[Tags/git] {nome}: {len(linhas)} tags ({sem_data} sem data do commit)")
    return pd.DataFrame(linhas)
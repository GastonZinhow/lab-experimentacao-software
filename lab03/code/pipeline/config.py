import os
from typing import Any, Dict

import yaml


def load_config(path: str) -> Dict[str, Any]:
    """
    Lê o config.yaml e resolve `cache_dir` e `output_dir` em relação à pasta
    do próprio arquivo, para os comandos funcionarem de qualquer diretório.
    """
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    base = os.path.dirname(os.path.abspath(path))
    for key, default in [("cache_dir", ".cache"), ("output_dir", "data")]:
        cfg[key] = os.path.join(base, cfg.get(key, default))
    return cfg

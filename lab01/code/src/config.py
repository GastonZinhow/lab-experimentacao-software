import os
from pathlib import Path

from dotenv import load_dotenv


ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)


def get_github_token():
    token = os.getenv("GITHUB_TOKEN")
    if token:
        print("GITHUB_TOKEN lido!")
    else:
        raise ValueError(
            "GITHUB_TOKEN não encontrado. "
            "Configure a variável de ambiente ou adicione no arquivo .env."
        )

    return token

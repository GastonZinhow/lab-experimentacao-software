import time

import requests


GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


def execute_query(token, query, variables=None):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": query,
        "variables": variables or {},
    }

    for attempt in range(3):
        response = requests.post(
            GITHUB_GRAPHQL_URL,
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            if "errors" in data:
                raise RuntimeError(
                    f"Erro GraphQL retornado pela API do GitHub: {data['errors']}"
                )

            return data

        if response.status_code in [502, 503, 504]:
            time.sleep(2)
            continue

        raise RuntimeError(
            f"Erro HTTP ao consultar GitHub GraphQL: "
            f"{response.status_code} - {response.text}"
        )

    raise RuntimeError(
        "Erro temporário ao consultar GitHub GraphQL. "
        "A API retornou 502/503/504 após 3 tentativas."
    )
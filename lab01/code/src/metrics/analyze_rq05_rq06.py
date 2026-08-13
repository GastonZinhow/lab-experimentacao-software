import json
import statistics


REPOSITORIES_FOR_ANALYSIS = {
    "vercel/next.js",
    "excalidraw/excalidraw",
    "kubernetes/kubernetes",
    "Hack-with-Github/Awesome-Hacking",
    "mrdoob/three.js",
    "sst/opencode",
    "yt-dlp/yt-dlp",
    "huggingface/transformers",
}

# Fonte: TIOBE Index, ranking de agosto/2026 (top 10)
# https://www.tiobe.com/tiobe-index/
POPULAR_LANGUAGES = {
    "Python",
    "C",
    "C++",
    "Java",
    "C#",
    "JavaScript",
    "Visual Basic",
    "SQL",
    "R",
    "Rust",
}


def analyze_rq05(selected_repositories):
    print("== Analise RQ05 ==\n")

    total = len(selected_repositories)
    matches = 0
    sem_linguagem = 0

    for repo in selected_repositories:
        repo_name = f"{repo.get('owner')}/{repo.get('name')}"
        language = repo.get("primary_language")

        if language is None:
            sem_linguagem += 1
            status = "sem linguagem definida"
        elif language in POPULAR_LANGUAGES:
            matches += 1
            status = "esta entre as populares (TIOBE top 10)"
        else:
            status = "NAO esta entre as populares (TIOBE top 10)"

        print(f"Repositorio: {repo_name}")
        print(f"  - Linguagem primaria: {language}")
        print(f"  - Status: {status}\n")

    considerados = total - sem_linguagem
    percentual = round((matches / considerados) * 100, 2) if considerados > 0 else 0

    print(f"Total analisado: {total}")
    print(f"Sem linguagem definida: {sem_linguagem}")
    print(f"Escritos em linguagem popular: {matches}/{considerados} ({percentual}%)\n")


def analyze_rq06(selected_repositories):
    print("== Analise RQ06 ==\n")

    closed_ratios = []

    for repo in selected_repositories:
        repo_name = f"{repo.get('owner')}/{repo.get('name')}"

        issues_count = repo.get("issues_count", 0)
        closed_issues_count = repo.get("closed_issues_count", 0)

        if issues_count > 0:
            closed_ratio = round((closed_issues_count / issues_count) * 100, 2)
            closed_ratios.append(closed_ratio)
        else:
            closed_ratio = None

        print(f"Repositorio: {repo_name}")
        print(f"  - Total de issues: {issues_count}")
        print(f"  - Issues fechadas: {closed_issues_count}")
        print(f"  - Percentual de issues fechadas: {closed_ratio}%\n")

    mediana = round(statistics.median(closed_ratios), 2) if closed_ratios else None

    print(f"Total de repositorios analisados: {len(selected_repositories)}")
    print(f"Mediana do percentual de issues fechadas: {mediana}%")


def analyze_rq05_rq06(json_path):
    with open(json_path, "r", encoding="utf-8") as file:
        repositories = json.load(file)

    selected_repositories = [
        repo for repo in repositories
        if f"{repo.get('owner')}/{repo.get('name')}" in REPOSITORIES_FOR_ANALYSIS
    ]

    analyze_rq05(selected_repositories)
    analyze_rq06(selected_repositories)


if __name__ == "__main__":
    analyze_rq05_rq06("data/raw/top_100_repositories.json")
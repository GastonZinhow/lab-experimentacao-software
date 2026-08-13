from datetime import datetime, timezone
import json


def analyze_sample(json_path):
  with open(json_path, 'r', encoding='utf-8') as f:
    repositories = json.load(f)

  sample = repositories[:5]
  now = datetime.now(timezone.utc)

  print('== Validação Amostral do RQ03 e RQ04: ==\n')

  for repo in sample:
    repo_name = f"{repo.get('owner')}/{repo.get('name')}"

    total_releases = repo.get('releases_count', 0)

    pushed_at_str = repo.get('pushed_at')
    days_since_update = None

    if pushed_at_str:
      pushed_dt = datetime.fromisoformat(pushed_at_str.replace('Z', '+00:00'))
      days_since_update = (now - pushed_dt).days

    print(f'Repositório: {repo_name}')
    print(f'  - Total de Releases: {total_releases}')
    print(f'  - Data do último push: {pushed_at_str}')
    print(f'  - Dias desde a última atualização: {days_since_update} dias\n')


if __name__ == '__main__':
  analyze_sample('data/raw/top_100_repositories.json')
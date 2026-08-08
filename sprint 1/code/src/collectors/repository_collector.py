from src.github_client import execute_query
from src.queries import TOP_REPOSITORIES_QUERY


def collect_top_repositories(token, total_repositories=100, page_size=10):
    collected_repositories = []
    has_next_page = True
    after_cursor = None

    while has_next_page and len(collected_repositories) < total_repositories:
        variables = {
            "first": page_size,
            "after": after_cursor,
        }

        response = execute_query(token, TOP_REPOSITORIES_QUERY, variables)

        search_data = response["data"]["search"]
        repositories = search_data["nodes"]

        for repository in repositories:
            collected_repositories.append({
                "name": repository["name"],
                "owner": repository["owner"]["login"],
                "url": repository["url"],
                "stars": repository["stargazerCount"],
                "releases_count": repository["releases"]["totalCount"],
                'pushed_at': repository.get('pushedAt'),
                "pull_requests_count": repository["pullRequests"]["totalCount"],
                "issues_count": repository["issues"]["totalCount"],
            })

            if len(collected_repositories) >= total_repositories:
                break

        page_info = search_data["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        after_cursor = page_info["endCursor"]

    return collected_repositories
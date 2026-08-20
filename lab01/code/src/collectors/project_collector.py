from src.github_client import execute_query
from src.project_queries import PROJECT_ITEMS_QUERY


def collect_project_items(token, login, project_number, page_size=50):
    collected_items = []
    has_next_page = True
    after_cursor = None

    while has_next_page:
        variables = {
            "login": login,
            "number": project_number,
            "first": page_size,
            "after": after_cursor,
        }

        response = execute_query(token, PROJECT_ITEMS_QUERY, variables)
        items_data = response["data"]["user"]["projectV2"]["items"]

        for item in items_data["nodes"]:
            content = item.get("content")

            if not content:
                continue

            assignees = [
                assignee["login"]
                for assignee in content["assignees"]["nodes"]
            ]

            collected_items.append({
                "issue_number": content["number"],
                "title": content["title"],
                "url": content["url"],
                "assignees": ", ".join(assignees),
                "status": item["status"]["name"] if item.get("status") else None,
            })

        page_info = items_data["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        after_cursor = page_info["endCursor"]

    return collected_items

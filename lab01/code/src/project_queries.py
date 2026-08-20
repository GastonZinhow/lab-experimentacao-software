PROJECT_ITEMS_QUERY = """
query($login: String!, $number: Int!, $first: Int!, $after: String) {
  user(login: $login) {
    projectV2(number: $number) {
      items(first: $first, after: $after) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          content {
            ... on Issue {
              number
              title
              url
              assignees(first: 5) {
                nodes {
                  login
                }
              }
            }
          }
          status: fieldValueByName(name: "Status") {
            ... on ProjectV2ItemFieldSingleSelectValue {
              name
            }
          }
        }
      }
    }
  }
}
"""

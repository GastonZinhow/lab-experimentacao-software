TOP_REPOSITORIES_QUERY = """
query($first: Int!, $after: String) {
  search(
    query: "stars:>0 sort:stars-desc",
    type: REPOSITORY,
    first: $first,
    after: $after
  ) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      ... on Repository {
        name
        owner {
          login
        }
        url
        stargazerCount
        releases {
          totalCount
        }
        pullRequests {
          totalCount
        }
        issues {
          totalCount
        }
      }
    }
  }
}
"""
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "httpx>=0.27,<1",
# ]
# ///
"""GitHub GraphQL API client with pagination and common operations.

Requires GITHUB_TOKEN environment variable for authentication.
GitHub GraphQL API: https://docs.github.com/en/graphql
"""

import argparse
import json
import os
import sys

import httpx

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

BUILTIN_OPERATIONS = {
    "repos": {
        "description": "List repositories for an owner",
        "query": """
query($owner: String!, $first: Int!, $after: String) {
  repositoryOwner(login: $owner) {
    repositories(first: $first, after: $after, orderBy: {field: UPDATED_AT, direction: DESC}) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes { name description url stargazerCount forkCount primaryLanguage { name } updatedAt isArchived }
    }
  }
}""",
    },
    "issues": {
        "description": "List issues for a repository",
        "query": """
query($owner: String!, $repo: String!, $first: Int!, $after: String, $states: [IssueState!]) {
  repository(owner: $owner, name: $repo) {
    issues(first: $first, after: $after, states: $states, orderBy: {field: UPDATED_AT, direction: DESC}) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes { number title state url author { login } labels(first: 5) { nodes { name } } createdAt updatedAt }
    }
  }
}""",
    },
    "prs": {
        "description": "List pull requests for a repository",
        "query": """
query($owner: String!, $repo: String!, $first: Int!, $after: String, $states: [PullRequestState!]) {
  repository(owner: $owner, name: $repo) {
    pullRequests(first: $first, after: $after, states: $states, orderBy: {field: UPDATED_AT, direction: DESC}) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes { number title state url author { login } mergeable isDraft createdAt updatedAt }
    }
  }
}""",
    },
    "viewer": {
        "description": "Get authenticated user info",
        "query": """
query {
  viewer { login name email bio company url repositories(first: 0) { totalCount } followers(first: 0) { totalCount } }
  rateLimit { limit cost remaining resetAt }
}""",
    },
    "rate-limit": {
        "description": "Check current rate limit status",
        "query": """
query {
  rateLimit { limit cost remaining resetAt nodeCount }
}""",
    },
}


def build_parser() -> argparse.ArgumentParser:
    ops_list = "\n".join(f"    {k:14s} {v['description']}" for k, v in BUILTIN_OPERATIONS.items())
    p = argparse.ArgumentParser(
        prog="github_graphql",
        description="Query the GitHub GraphQL API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""Built-in operations:
{ops_list}

Examples:
  uv run scripts/github_graphql.py --query '{{ viewer {{ login }} }}'
  uv run scripts/github_graphql.py --operation repos --owner torvalds --first 5
  uv run scripts/github_graphql.py --operation issues --owner facebook --repo react --state OPEN --first 10
  uv run scripts/github_graphql.py --operation rate-limit
  uv run scripts/github_graphql.py --query-file my_query.graphql --variables '{{"org": "anthropics"}}'

Exit codes:
  0  Success
  1  Client error (bad arguments, missing token)
  2  Network or server error
  3  GraphQL errors in response""",
    )
    p.add_argument("--query", help="Raw GraphQL query string")
    p.add_argument("--query-file", help="Path to a .graphql file")
    p.add_argument("--operation", choices=list(BUILTIN_OPERATIONS.keys()), help="Use a built-in operation")
    p.add_argument("--variables", help="JSON string of query variables")
    p.add_argument("--owner", help="Repository owner (for built-in ops)")
    p.add_argument("--repo", help="Repository name (for built-in ops)")
    p.add_argument("--first", type=int, default=10, help="Number of items to fetch (default: 10, max: 100)")
    p.add_argument("--state", help="Filter state: OPEN, CLOSED, MERGED (for issues/prs)")
    p.add_argument("--paginate", action="store_true", help="Auto-paginate through all results")
    p.add_argument("--max-pages", type=int, default=10, help="Max pages when paginating (default: 10)")
    p.add_argument("--cost-estimate", action="store_true", help="Show rate limit cost after query")
    p.add_argument("--output", help="Write response to file instead of stdout")
    p.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"), help="GitHub token (default: $GITHUB_TOKEN)")
    return p


def resolve_query_and_variables(args: argparse.Namespace) -> tuple[str, dict]:
    if args.operation:
        op = BUILTIN_OPERATIONS[args.operation]
        query = op["query"]
        variables: dict = {}
        if args.owner:
            variables["owner"] = args.owner
        if args.repo:
            variables["repo"] = args.repo
        variables["first"] = min(args.first, 100)
        if args.state:
            variables["states"] = [args.state.upper()]
        return query, variables

    if args.query:
        query = args.query
    elif args.query_file:
        try:
            with open(args.query_file) as f:
                query = f.read()
        except FileNotFoundError:
            print(f"Error: Query file not found: {args.query_file}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: --query, --query-file, or --operation is required.", file=sys.stderr)
        sys.exit(1)

    variables = {}
    if args.variables:
        try:
            variables = json.loads(args.variables)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in --variables: {e}", file=sys.stderr)
            sys.exit(1)
    return query, variables


def execute_query(client: httpx.Client, token: str, query: str, variables: dict) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload: dict = {"query": query}
    if variables:
        payload["variables"] = variables

    try:
        resp = client.post(GITHUB_GRAPHQL_URL, json=payload, headers=headers)
        resp.raise_for_status()
    except httpx.ConnectError as e:
        print(f"Error: Could not connect to GitHub API: {e}", file=sys.stderr)
        sys.exit(2)
    except httpx.HTTPStatusError as e:
        print(f"Error: HTTP {e.response.status_code} from GitHub API", file=sys.stderr)
        try:
            print(json.dumps(e.response.json(), indent=2), file=sys.stderr)
        except Exception:
            print(e.response.text[:2000], file=sys.stderr)
        sys.exit(2)

    try:
        return resp.json()
    except json.JSONDecodeError:
        print("Error: GitHub returned non-JSON response.", file=sys.stderr)
        sys.exit(2)


def find_page_info(data: dict) -> tuple[dict | None, str | None]:
    """Recursively find pageInfo in the response for pagination."""
    if isinstance(data, dict):
        if "pageInfo" in data:
            return data["pageInfo"], "after"
        for v in data.values():
            result = find_page_info(v)
            if result[0]:
                return result
    return None, None


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.token:
        print("Error: GITHUB_TOKEN environment variable is required.", file=sys.stderr)
        print("Create one at: https://github.com/settings/tokens", file=sys.stderr)
        sys.exit(1)

    query, variables = resolve_query_and_variables(args)

    all_results = []
    with httpx.Client(timeout=30) as client:
        page = 0
        while True:
            data = execute_query(client, args.token, query, variables)

            if "errors" in data and "data" not in data:
                print(json.dumps(data, indent=2))
                sys.exit(3)

            all_results.append(data)

            if not args.paginate:
                break

            page_info, cursor_key = find_page_info(data.get("data", {}))
            if not page_info or not page_info.get("hasNextPage"):
                break

            page += 1
            if page >= args.max_pages:
                print(f"Warning: Reached max pages ({args.max_pages}). Use --max-pages to increase.", file=sys.stderr)
                break

            variables[cursor_key or "after"] = page_info["endCursor"]

    if args.cost_estimate:
        cost_query = "{ rateLimit { limit cost remaining resetAt } }"
        cost_data = execute_query(client, args.token, cost_query, {})
        rate = cost_data.get("data", {}).get("rateLimit", {})
        print(
            f"Rate limit: {rate.get('remaining', '?')}/{rate.get('limit', '?')} remaining, resets at {rate.get('resetAt', '?')}",
            file=sys.stderr,
        )

    output_data = all_results[0] if len(all_results) == 1 else {"pages": all_results}
    output = json.dumps(output_data, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output + "\n")
        print(f"Response written to {args.output}", file=sys.stderr)
    else:
        print(output)

    if "errors" in (all_results[0] if all_results else {}):
        sys.exit(3)


if __name__ == "__main__":
    main()

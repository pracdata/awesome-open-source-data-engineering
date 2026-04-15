# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "httpx>=0.27,<1",
# ]
# ///
"""Universal GraphQL query executor for any endpoint.

Works with Hasura, PostGraphile, Apollo Router, GraphQL Mesh,
WunderGraph, Grafbase, Tailcall, Graphweaver, or any spec-compliant
GraphQL server.
"""

import argparse
import json
import os
import sys

import httpx


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="graphql_query",
        description="Execute a GraphQL query against any endpoint.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  uv run scripts/graphql_query.py --endpoint https://api.example.com/graphql --query '{ users { id name } }'
  uv run scripts/graphql_query.py --endpoint https://hasura.example.com/v1/graphql --query '{ users { id } }' --header 'x-hasura-admin-secret: secret'
  uv run scripts/graphql_query.py --endpoint https://api.example.com/graphql --query-file query.graphql --variables '{"id": "123"}'

Exit codes:
  0  Success
  1  Client error (bad arguments, file not found)
  2  Network or server error
  3  GraphQL errors in response""",
    )
    p.add_argument(
        "--endpoint",
        default=os.environ.get("GRAPHQL_ENDPOINT"),
        help="GraphQL endpoint URL (default: $GRAPHQL_ENDPOINT)",
    )
    p.add_argument("--query", help="GraphQL query string")
    p.add_argument("--query-file", help="Path to a .graphql file containing the query")
    p.add_argument("--variables", help="JSON string of query variables")
    p.add_argument("--variables-file", help="Path to a JSON file of variables")
    p.add_argument("--operation", help="Operation name (for documents with multiple operations)")
    p.add_argument("--header", action="append", default=[], help="HTTP header as 'Key: Value' (repeatable)")
    p.add_argument(
        "--bearer-token",
        default=os.environ.get("GRAPHQL_BEARER_TOKEN"),
        help="Bearer token for Authorization header (default: $GRAPHQL_BEARER_TOKEN)",
    )
    p.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds (default: 30)")
    p.add_argument("--output", help="Write response to file instead of stdout")
    return p


def parse_headers(raw: list[str], bearer: str | None) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    for h in raw:
        if ":" not in h:
            print(f"Error: Invalid header format: '{h}'. Expected 'Key: Value'.", file=sys.stderr)
            sys.exit(1)
        key, value = h.split(":", 1)
        headers[key.strip()] = value.strip()
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"
    return headers


def load_query(args: argparse.Namespace) -> str:
    if args.query:
        return args.query
    if args.query_file:
        try:
            with open(args.query_file) as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: Query file not found: {args.query_file}", file=sys.stderr)
            sys.exit(1)
    print("Error: --query or --query-file is required.", file=sys.stderr)
    sys.exit(1)


def load_variables(args: argparse.Namespace) -> dict | None:
    if args.variables:
        try:
            return json.loads(args.variables)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in --variables: {e}", file=sys.stderr)
            sys.exit(1)
    if args.variables_file:
        try:
            with open(args.variables_file) as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Variables file not found: {args.variables_file}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in variables file: {e}", file=sys.stderr)
            sys.exit(1)
    return None


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.endpoint:
        print("Error: --endpoint is required (or set $GRAPHQL_ENDPOINT).", file=sys.stderr)
        sys.exit(1)

    query = load_query(args)
    variables = load_variables(args)
    headers = parse_headers(args.header, args.bearer_token)

    payload: dict = {"query": query}
    if variables:
        payload["variables"] = variables
    if args.operation:
        payload["operationName"] = args.operation

    try:
        with httpx.Client(timeout=args.timeout) as client:
            resp = client.post(args.endpoint, json=payload, headers=headers)
            resp.raise_for_status()
    except httpx.ConnectError as e:
        print(f"Error: Could not connect to {args.endpoint}: {e}", file=sys.stderr)
        sys.exit(2)
    except httpx.HTTPStatusError as e:
        print(f"Error: HTTP {e.response.status_code} from {args.endpoint}", file=sys.stderr)
        try:
            print(json.dumps(e.response.json(), indent=2), file=sys.stderr)
        except Exception:
            print(e.response.text[:2000], file=sys.stderr)
        sys.exit(2)
    except httpx.TimeoutException:
        print(f"Error: Request timed out after {args.timeout}s.", file=sys.stderr)
        sys.exit(2)

    try:
        data = resp.json()
    except json.JSONDecodeError:
        print("Error: Response is not valid JSON.", file=sys.stderr)
        print(resp.text[:2000], file=sys.stderr)
        sys.exit(2)

    output = json.dumps(data, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output + "\n")
        print(f"Response written to {args.output}", file=sys.stderr)
    else:
        print(output)

    if "errors" in data:
        print(f"Warning: Response contains {len(data['errors'])} GraphQL error(s).", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()

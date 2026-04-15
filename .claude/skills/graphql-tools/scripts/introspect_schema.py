# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "httpx>=0.27,<1",
#   "graphql-core>=3.2,<4",
# ]
# ///
"""Introspect any GraphQL endpoint and output the schema as SDL or JSON.

Works with any spec-compliant GraphQL server including Hasura, PostGraphile,
Apollo Router, GraphQL Mesh, WunderGraph, Grafbase, Tailcall, and Graphweaver.
"""

import argparse
import json
import os
import sys

import httpx
from graphql import build_client_schema, print_schema
from graphql import get_introspection_query as gql_introspection_query


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="introspect_schema",
        description="Introspect a GraphQL endpoint and output the schema.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  uv run scripts/introspect_schema.py --endpoint https://api.example.com/graphql
  uv run scripts/introspect_schema.py --endpoint https://api.example.com/graphql --format sdl --output schema.graphql
  uv run scripts/introspect_schema.py --endpoint https://hasura.example.com/v1/graphql --header 'x-hasura-admin-secret: secret' --format json
  uv run scripts/introspect_schema.py --endpoint https://api.example.com/graphql --types-only
  uv run scripts/introspect_schema.py --from-json introspection.json --format sdl

Exit codes:
  0  Success
  1  Client error (bad arguments)
  2  Network or server error
  3  Schema build error""",
    )
    source = p.add_argument_group("source")
    source.add_argument(
        "--endpoint",
        default=os.environ.get("GRAPHQL_ENDPOINT"),
        help="GraphQL endpoint URL (default: $GRAPHQL_ENDPOINT)",
    )
    source.add_argument("--from-json", help="Build schema from a saved introspection JSON file instead of querying")

    p.add_argument(
        "--format",
        choices=["sdl", "json"],
        default="sdl",
        help="Output format: sdl (GraphQL Schema Definition Language) or json (default: sdl)",
    )
    p.add_argument(
        "--types-only",
        action="store_true",
        help="Only output user-defined types (exclude built-in scalars and introspection types)",
    )
    p.add_argument("--header", action="append", default=[], help="HTTP header as 'Key: Value' (repeatable)")
    p.add_argument(
        "--bearer-token", default=os.environ.get("GRAPHQL_BEARER_TOKEN"), help="Bearer token for Authorization header"
    )
    p.add_argument("--output", help="Write output to file instead of stdout")
    p.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds (default: 30)")
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


def introspect_remote(endpoint: str, headers: dict, timeout: int) -> dict:
    query = gql_introspection_query(descriptions=True)
    payload = {"query": query}

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(endpoint, json=payload, headers=headers)
            resp.raise_for_status()
    except httpx.ConnectError as e:
        print(f"Error: Could not connect to {endpoint}: {e}", file=sys.stderr)
        sys.exit(2)
    except httpx.HTTPStatusError as e:
        print(f"Error: HTTP {e.response.status_code} from {endpoint}", file=sys.stderr)
        sys.exit(2)
    except httpx.TimeoutException:
        print(f"Error: Request timed out after {timeout}s.", file=sys.stderr)
        sys.exit(2)

    try:
        data = resp.json()
    except json.JSONDecodeError:
        print("Error: Response is not valid JSON.", file=sys.stderr)
        sys.exit(2)

    if "errors" in data:
        for err in data["errors"]:
            print(f"GraphQL Error: {err.get('message', err)}", file=sys.stderr)
        if "data" not in data:
            sys.exit(3)

    return data["data"]


def load_introspection_json(path: str) -> dict:
    try:
        with open(path) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)

    if "__schema" in data:
        return data
    if "data" in data and "__schema" in data["data"]:
        return data["data"]
    print("Error: JSON file does not contain introspection data (__schema).", file=sys.stderr)
    sys.exit(1)


BUILTIN_TYPES = {
    "String",
    "Int",
    "Float",
    "Boolean",
    "ID",
    "__Schema",
    "__Type",
    "__Field",
    "__InputValue",
    "__EnumValue",
    "__Directive",
    "__DirectiveLocation",
}


def filter_user_types(sdl: str) -> str:
    lines = sdl.split("\n")
    result = []
    skip = False
    for line in lines:
        if any(
            line.startswith(f"{kw} {t}")
            for kw in ("type", "scalar", "enum", "input", "interface", "union")
            for t in BUILTIN_TYPES
        ):
            skip = True
            continue
        if skip:
            if line.startswith("}") or (line.strip() == "" and not line.startswith(" ")):
                skip = False
            continue
        result.append(line)
    return "\n".join(result).strip() + "\n"


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.from_json:
        introspection_data = load_introspection_json(args.from_json)
    elif args.endpoint:
        headers = parse_headers(args.header, args.bearer_token)
        introspection_data = introspect_remote(args.endpoint, headers, args.timeout)
    else:
        print("Error: --endpoint (or $GRAPHQL_ENDPOINT) or --from-json is required.", file=sys.stderr)
        sys.exit(1)

    try:
        schema = build_client_schema(introspection_data)
    except Exception as e:
        print(f"Error: Failed to build schema from introspection data: {e}", file=sys.stderr)
        sys.exit(3)

    if args.format == "sdl":
        output = print_schema(schema)
        if args.types_only:
            output = filter_user_types(output)
    else:
        output = json.dumps(introspection_data, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output + "\n")
        print(f"Schema written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()

# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "psycopg[binary]>=3.1,<4",
# ]
# ///
"""Neon Postgres 18 pg_graphql client.

Executes GraphQL queries against a Neon Postgres database using the
pg_graphql extension (graphql.resolve function). Requires the pg_graphql
extension to be enabled on the database.

Neon pg_graphql docs: https://neon.tech/docs/extensions/pg_graphql
"""

import argparse
import json
import os
import sys

import psycopg


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="neon_pg_graphql",
        description="Execute GraphQL queries on Neon Postgres via pg_graphql extension.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  uv run scripts/neon_pg_graphql.py --database-url "$DATABASE_URL" --query '{ usersCollection(first: 10) { edges { node { id name } } } }'
  uv run scripts/neon_pg_graphql.py --host ep-example.us-east-2.aws.neon.tech --dbname mydb --user myuser --query '{ __typename }'
  uv run scripts/neon_pg_graphql.py --database-url "$DATABASE_URL" --query-file query.graphql --variables '{"first": 5}'
  uv run scripts/neon_pg_graphql.py --database-url "$DATABASE_URL" --ensure-extension
  uv run scripts/neon_pg_graphql.py --database-url "$DATABASE_URL" --introspect

Exit codes:
  0  Success
  1  Client error (bad arguments, missing params)
  2  Connection or database error
  3  GraphQL errors in response""",
    )
    conn = p.add_argument_group("connection")
    conn.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL"),
        help="Postgres connection URL (default: $DATABASE_URL)",
    )
    conn.add_argument("--host", help="Database host (alternative to --database-url)")
    conn.add_argument("--port", type=int, default=5432, help="Database port (default: 5432)")
    conn.add_argument("--dbname", help="Database name")
    conn.add_argument("--user", help="Database user")
    conn.add_argument(
        "--password", default=os.environ.get("NEON_PASSWORD"), help="Database password (default: $NEON_PASSWORD)"
    )
    conn.add_argument("--sslmode", default="require", help="SSL mode (default: require, recommended for Neon)")

    query_group = p.add_argument_group("query")
    query_group.add_argument("--query", help="GraphQL query string")
    query_group.add_argument("--query-file", help="Path to a .graphql file")
    query_group.add_argument("--variables", help="JSON string of query variables")
    query_group.add_argument("--operation", help="Operation name for multi-operation documents")

    actions = p.add_argument_group("actions")
    actions.add_argument(
        "--ensure-extension", action="store_true", help="Create pg_graphql extension if not exists, then exit"
    )
    actions.add_argument("--introspect", action="store_true", help="Run introspection query and output schema")
    actions.add_argument("--list-types", action="store_true", help="List all GraphQL types exposed by pg_graphql")

    p.add_argument("--output", help="Write response to file instead of stdout")
    p.add_argument("--raw", action="store_true", help="Output raw SQL result without JSON parsing")
    return p


INTROSPECTION_QUERY = """{
  __schema {
    types {
      name
      kind
      fields { name type { name kind ofType { name kind } } }
    }
    queryType { name }
    mutationType { name }
  }
}"""

LIST_TYPES_QUERY = """{
  __schema {
    types {
      name
      kind
      description
    }
  }
}"""


def get_connection_string(args: argparse.Namespace) -> str:
    if args.database_url:
        return args.database_url
    if args.host and args.dbname and args.user:
        password_part = f":{args.password}" if args.password else ""
        return f"postgresql://{args.user}{password_part}@{args.host}:{args.port}/{args.dbname}?sslmode={args.sslmode}"
    print(
        "Error: --database-url (or $DATABASE_URL) is required, or provide --host, --dbname, and --user.",
        file=sys.stderr,
    )
    sys.exit(1)


def load_query(args: argparse.Namespace) -> str:
    if args.introspect:
        return INTROSPECTION_QUERY
    if args.list_types:
        return LIST_TYPES_QUERY
    if args.query:
        return args.query
    if args.query_file:
        try:
            with open(args.query_file) as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: Query file not found: {args.query_file}", file=sys.stderr)
            sys.exit(1)
    print("Error: --query, --query-file, --introspect, or --list-types is required.", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    conninfo = get_connection_string(args)

    try:
        conn = psycopg.connect(conninfo)
    except psycopg.OperationalError as e:
        print(f"Error: Could not connect to database: {e}", file=sys.stderr)
        print("Hint: Neon requires sslmode=require. Check your connection string.", file=sys.stderr)
        sys.exit(2)

    try:
        if args.ensure_extension:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS pg_graphql CASCADE;")
                conn.commit()
                cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'pg_graphql';")
                row = cur.fetchone()
                if row:
                    print(json.dumps({"status": "ok", "extension": row[0], "version": row[1]}, indent=2))
                else:
                    print(
                        json.dumps(
                            {
                                "status": "error",
                                "message": "Extension creation reported success but extension not found",
                            },
                            indent=2,
                        )
                    )
                    sys.exit(2)
            return

        query = load_query(args)

        variables = {}
        if args.variables:
            try:
                variables = json.loads(args.variables)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON in --variables: {e}", file=sys.stderr)
                sys.exit(1)

        # pg_graphql resolves queries via the graphql.resolve() SQL function
        sql = "SELECT graphql.resolve($1);"
        gql_payload = json.dumps(
            {
                "query": query,
                "variables": variables,
                **({"operationName": args.operation} if args.operation else {}),
            }
        )

        with conn.cursor() as cur:
            cur.execute(sql, (gql_payload,))
            row = cur.fetchone()

        if row is None:
            print("Error: No result returned from graphql.resolve().", file=sys.stderr)
            sys.exit(2)

        result = row[0]

        if args.raw:
            output = str(result)
        elif isinstance(result, str):
            try:
                parsed = json.loads(result)
                output = json.dumps(parsed, indent=2)
                result = parsed
            except json.JSONDecodeError:
                output = result
        elif isinstance(result, dict):
            output = json.dumps(result, indent=2)
        else:
            output = json.dumps(result, indent=2, default=str)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output + "\n")
            print(f"Response written to {args.output}", file=sys.stderr)
        else:
            print(output)

        if isinstance(result, dict) and "errors" in result:
            print(f"Warning: Response contains {len(result['errors'])} GraphQL error(s).", file=sys.stderr)
            sys.exit(3)

    except psycopg.errors.UndefinedFunction:
        print("Error: graphql.resolve() function not found.", file=sys.stderr)
        print(
            "Hint: Enable pg_graphql first: uv run scripts/neon_pg_graphql.py --database-url $DATABASE_URL --ensure-extension",
            file=sys.stderr,
        )
        sys.exit(2)
    except psycopg.Error as e:
        print(f"Error: Database error: {e}", file=sys.stderr)
        sys.exit(2)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

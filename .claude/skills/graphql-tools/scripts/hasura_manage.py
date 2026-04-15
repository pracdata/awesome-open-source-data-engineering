# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "httpx>=0.27,<1",
# ]
# ///
"""Hasura GraphQL Engine metadata management tool.

Manage Hasura metadata: track/untrack tables, export/apply metadata,
reload metadata, and check health. Uses the Hasura Metadata API v2.

Hasura Metadata API: https://hasura.io/docs/latest/api-reference/metadata-api/
"""

import argparse
import json
import os
import sys

import httpx

ACTIONS = {
    "export-metadata": "Export full Hasura metadata as JSON",
    "reload-metadata": "Reload metadata from the database",
    "clear-metadata": "Clear all Hasura metadata (destructive!)",
    "track-table": "Track a database table in Hasura (requires --table, --schema)",
    "untrack-table": "Untrack a table from Hasura (requires --table, --schema)",
    "list-tables": "List all tracked tables",
    "health": "Check Hasura health status",
    "run-sql": "Run raw SQL via Hasura (requires --sql or --sql-file)",
}


def build_parser() -> argparse.ArgumentParser:
    action_list = "\n".join(f"    {k:20s} {v}" for k, v in ACTIONS.items())
    p = argparse.ArgumentParser(
        prog="hasura_manage",
        description="Manage Hasura GraphQL Engine metadata and tables.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""Actions:
{action_list}

Examples:
  uv run scripts/hasura_manage.py --endpoint https://hasura.example.com --action health
  uv run scripts/hasura_manage.py --endpoint https://hasura.example.com --action export-metadata --output metadata.json
  uv run scripts/hasura_manage.py --endpoint https://hasura.example.com --action track-table --table users --schema public
  uv run scripts/hasura_manage.py --endpoint https://hasura.example.com --action list-tables
  uv run scripts/hasura_manage.py --endpoint https://hasura.example.com --action run-sql --sql "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
  uv run scripts/hasura_manage.py --endpoint https://hasura.example.com --action clear-metadata --confirm

Exit codes:
  0  Success
  1  Client error (bad arguments)
  2  Network or API error""",
    )
    p.add_argument("--endpoint", required=True, help="Hasura endpoint base URL (e.g. https://hasura.example.com)")
    p.add_argument("--action", required=True, choices=list(ACTIONS.keys()), help="Action to perform")
    p.add_argument(
        "--admin-secret",
        default=os.environ.get("HASURA_ADMIN_SECRET"),
        help="Hasura admin secret (default: $HASURA_ADMIN_SECRET)",
    )
    p.add_argument("--table", help="Table name (for track-table/untrack-table)")
    p.add_argument("--schema", default="public", help="Database schema (default: public)")
    p.add_argument("--source", default="default", help="Hasura data source name (default: default)")
    p.add_argument("--sql", help="SQL query string (for run-sql)")
    p.add_argument("--sql-file", help="Path to SQL file (for run-sql)")
    p.add_argument("--confirm", action="store_true", help="Confirm destructive operations")
    p.add_argument("--output", help="Write output to file instead of stdout")
    p.add_argument("--dry-run", action="store_true", help="Show what would be sent without executing")
    return p


def make_request(endpoint: str, path: str, body: dict, admin_secret: str | None, dry_run: bool = False) -> dict:
    url = f"{endpoint.rstrip('/')}{path}"
    headers = {"Content-Type": "application/json"}
    if admin_secret:
        headers["x-hasura-admin-secret"] = admin_secret

    if dry_run:
        print(json.dumps({"url": url, "body": body}, indent=2))
        sys.exit(0)

    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(url, json=body, headers=headers)
            resp.raise_for_status()
    except httpx.ConnectError as e:
        print(f"Error: Could not connect to {url}: {e}", file=sys.stderr)
        sys.exit(2)
    except httpx.HTTPStatusError as e:
        print(f"Error: HTTP {e.response.status_code} from {url}", file=sys.stderr)
        try:
            print(json.dumps(e.response.json(), indent=2), file=sys.stderr)
        except Exception:
            print(e.response.text[:2000], file=sys.stderr)
        sys.exit(2)

    try:
        return resp.json()
    except (json.JSONDecodeError, ValueError):
        return {"raw": resp.text}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.action == "health":
        url = f"{args.endpoint.rstrip('/')}/healthz"
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(url)
                print(
                    json.dumps(
                        {
                            "status": "healthy" if resp.status_code == 200 else "unhealthy",
                            "http_status": resp.status_code,
                        },
                        indent=2,
                    )
                )
        except httpx.ConnectError as e:
            print(json.dumps({"status": "unreachable", "error": str(e)}, indent=2))
            sys.exit(2)
        return

    if not args.admin_secret:
        print("Error: --admin-secret or $HASURA_ADMIN_SECRET is required for this action.", file=sys.stderr)
        sys.exit(1)

    result: dict = {}

    if args.action == "export-metadata":
        result = make_request(
            args.endpoint,
            "/v1/metadata",
            {
                "type": "export_metadata",
                "version": 2,
                "args": {},
            },
            args.admin_secret,
            args.dry_run,
        )

    elif args.action == "reload-metadata":
        result = make_request(
            args.endpoint,
            "/v1/metadata",
            {
                "type": "reload_metadata",
                "args": {"reload_remote_schemas": True},
            },
            args.admin_secret,
            args.dry_run,
        )

    elif args.action == "clear-metadata":
        if not args.confirm:
            print("Error: --confirm is required for clear-metadata (destructive operation).", file=sys.stderr)
            sys.exit(1)
        result = make_request(
            args.endpoint,
            "/v1/metadata",
            {
                "type": "clear_metadata",
                "args": {},
            },
            args.admin_secret,
            args.dry_run,
        )

    elif args.action == "track-table":
        if not args.table:
            print("Error: --table is required for track-table.", file=sys.stderr)
            sys.exit(1)
        result = make_request(
            args.endpoint,
            "/v1/metadata",
            {
                "type": "pg_track_table",
                "args": {
                    "source": args.source,
                    "table": {"schema": args.schema, "name": args.table},
                },
            },
            args.admin_secret,
            args.dry_run,
        )

    elif args.action == "untrack-table":
        if not args.table:
            print("Error: --table is required for untrack-table.", file=sys.stderr)
            sys.exit(1)
        result = make_request(
            args.endpoint,
            "/v1/metadata",
            {
                "type": "pg_untrack_table",
                "args": {
                    "source": args.source,
                    "table": {"schema": args.schema, "name": args.table},
                },
            },
            args.admin_secret,
            args.dry_run,
        )

    elif args.action == "list-tables":
        metadata = make_request(
            args.endpoint,
            "/v1/metadata",
            {
                "type": "export_metadata",
                "version": 2,
                "args": {},
            },
            args.admin_secret,
            args.dry_run,
        )
        tables = []
        for source in metadata.get("metadata", {}).get("sources", []):
            for table in source.get("tables", []):
                t = table.get("table", {})
                tables.append(
                    {
                        "source": source.get("name"),
                        "schema": t.get("schema"),
                        "name": t.get("name"),
                    }
                )
        result = {"tables": tables, "count": len(tables)}

    elif args.action == "run-sql":
        sql = args.sql
        if not sql and args.sql_file:
            try:
                with open(args.sql_file) as f:
                    sql = f.read()
            except FileNotFoundError:
                print(f"Error: SQL file not found: {args.sql_file}", file=sys.stderr)
                sys.exit(1)
        if not sql:
            print("Error: --sql or --sql-file is required for run-sql.", file=sys.stderr)
            sys.exit(1)
        result = make_request(
            args.endpoint,
            "/v2/query",
            {
                "type": "run_sql",
                "args": {"source": args.source, "sql": sql},
            },
            args.admin_secret,
            args.dry_run,
        )

    output = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output + "\n")
        print(f"Output written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()

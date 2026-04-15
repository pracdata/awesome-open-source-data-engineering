# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "psycopg[binary]>=3.1,<4",
# ]
# ///
"""Setup Neon Postgres with pgvector + pg_graphql for tool embeddings.

Creates the extensions, tables, and indexes needed for embedding-based
tool search following the Anthropic tool-search-with-embeddings pattern
and Neon's AI embeddings guide.

Supports both pgvector 0.8.1 (PG18) and pg_graphql 1.5.12 (PG18).
"""

import argparse
import json
import os
import sys

import psycopg

SETUP_SQL = """
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_graphql CASCADE;

-- Tool registry: stores tool definitions with their embeddings
CREATE TABLE IF NOT EXISTS graphql_tools (
    id SERIAL PRIMARY KEY,
    tool_name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    parameters TEXT,
    category TEXT,
    script_path TEXT,
    full_text TEXT NOT NULL,
    embedding vector(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- IVFFlat index for fast approximate nearest neighbor search (cosine similarity)
-- lists = sqrt(num_rows) is a good default; 10 is fine for < 100 tools
CREATE INDEX IF NOT EXISTS graphql_tools_embedding_idx
    ON graphql_tools USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 10);

-- Index on category for filtered searches
CREATE INDEX IF NOT EXISTS graphql_tools_category_idx
    ON graphql_tools (category);

-- Search history: tracks queries for analytics and refinement
CREATE TABLE IF NOT EXISTS tool_search_log (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    query_embedding vector(384),
    results_returned INTEGER,
    top_tool TEXT,
    top_similarity FLOAT,
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- UDA metadata registry: stores schema mappings following Netflix UDA patterns
CREATE TABLE IF NOT EXISTS uda_schema_registry (
    id SERIAL PRIMARY KEY,
    schema_name TEXT NOT NULL,
    schema_type TEXT NOT NULL CHECK (schema_type IN ('graphql', 'avro', 'rdf', 'json')),
    content TEXT NOT NULL,
    uda_uri TEXT,
    embedding vector(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS uda_schema_embedding_idx
    ON uda_schema_registry USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 10);

-- Comment for pg_graphql to expose via GraphQL API
COMMENT ON TABLE graphql_tools IS
    '@graphql({"totalCount": {"enabled": true}})';
COMMENT ON TABLE uda_schema_registry IS
    '@graphql({"totalCount": {"enabled": true}})';
"""

VERIFY_SQL = """
SELECT
    e.extname,
    e.extversion
FROM pg_extension e
WHERE e.extname IN ('vector', 'pg_graphql')
ORDER BY e.extname;
"""

TABLE_CHECK_SQL = """
SELECT
    t.tablename,
    (SELECT count(*) FROM information_schema.columns c
     WHERE c.table_name = t.tablename AND c.table_schema = 'public') as column_count
FROM pg_tables t
WHERE t.schemaname = 'public'
    AND t.tablename IN ('graphql_tools', 'tool_search_log', 'uda_schema_registry')
ORDER BY t.tablename;
"""

TEARDOWN_SQL = """
DROP TABLE IF EXISTS tool_search_log CASCADE;
DROP TABLE IF EXISTS uda_schema_registry CASCADE;
DROP TABLE IF EXISTS graphql_tools CASCADE;
"""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="neon_setup_vectors",
        description="Setup Neon Postgres with pgvector + pg_graphql for tool embeddings.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  uv run scripts/neon_setup_vectors.py --database-url "$DATABASE_URL" --setup
  uv run scripts/neon_setup_vectors.py --database-url "$DATABASE_URL" --verify
  uv run scripts/neon_setup_vectors.py --database-url "$DATABASE_URL" --teardown --confirm
  uv run scripts/neon_setup_vectors.py --database-url "$DATABASE_URL" --dry-run

Exit codes:
  0  Success
  1  Client error
  2  Database error""",
    )
    p.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL"),
        help="Neon Postgres connection URL (default: $DATABASE_URL)",
    )
    action = p.add_mutually_exclusive_group(required=True)
    action.add_argument("--setup", action="store_true", help="Create extensions, tables, and indexes")
    action.add_argument("--verify", action="store_true", help="Verify setup is complete")
    action.add_argument("--teardown", action="store_true", help="Drop all tables (destructive!)")
    p.add_argument("--confirm", action="store_true", help="Confirm destructive operations")
    p.add_argument("--dry-run", action="store_true", help="Print SQL without executing")
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.database_url:
        print("Error: --database-url or $DATABASE_URL is required.", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        if args.setup:
            print(SETUP_SQL)
        elif args.teardown:
            print(TEARDOWN_SQL)
        else:
            print(VERIFY_SQL)
            print(TABLE_CHECK_SQL)
        return

    try:
        conn = psycopg.connect(args.database_url)
    except psycopg.OperationalError as e:
        print(f"Error: Could not connect: {e}", file=sys.stderr)
        print("Hint: Neon requires sslmode=require in the connection string.", file=sys.stderr)
        sys.exit(2)

    try:
        if args.setup:
            print("Setting up pgvector + pg_graphql schema...", file=sys.stderr)
            with conn.cursor() as cur:
                cur.execute(SETUP_SQL)
                conn.commit()
            print("Setup complete.", file=sys.stderr)

            # Verify
            with conn.cursor() as cur:
                cur.execute(VERIFY_SQL)
                extensions = cur.fetchall()
                cur.execute(TABLE_CHECK_SQL)
                tables = cur.fetchall()

            result = {
                "status": "ok",
                "extensions": [{"name": r[0], "version": r[1]} for r in extensions],
                "tables": [{"name": r[0], "columns": r[1]} for r in tables],
            }
            print(json.dumps(result, indent=2))

        elif args.verify:
            with conn.cursor() as cur:
                cur.execute(VERIFY_SQL)
                extensions = cur.fetchall()
                cur.execute(TABLE_CHECK_SQL)
                tables = cur.fetchall()
                cur.execute("SELECT count(*) FROM graphql_tools;")
                tool_count = cur.fetchone()[0]

            result = {
                "status": "ok",
                "extensions": [{"name": r[0], "version": r[1]} for r in extensions],
                "tables": [{"name": r[0], "columns": r[1]} for r in tables],
                "tool_count": tool_count,
            }

            missing_ext = {"vector", "pg_graphql"} - {r[0] for r in extensions}
            if missing_ext:
                result["status"] = "incomplete"
                result["missing_extensions"] = list(missing_ext)

            missing_tables = {"graphql_tools", "tool_search_log", "uda_schema_registry"} - {r[0] for r in tables}
            if missing_tables:
                result["status"] = "incomplete"
                result["missing_tables"] = list(missing_tables)

            print(json.dumps(result, indent=2))

        elif args.teardown:
            if not args.confirm:
                print("Error: --confirm is required for teardown (destructive operation).", file=sys.stderr)
                sys.exit(1)
            with conn.cursor() as cur:
                cur.execute(TEARDOWN_SQL)
                conn.commit()
            print(
                json.dumps(
                    {
                        "status": "ok",
                        "action": "teardown",
                        "tables_dropped": ["graphql_tools", "tool_search_log", "uda_schema_registry"],
                    },
                    indent=2,
                )
            )

    except psycopg.Error as e:
        print(f"Error: Database error: {e}", file=sys.stderr)
        sys.exit(2)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

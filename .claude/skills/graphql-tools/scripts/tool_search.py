# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "httpx>=0.27,<1",
#   "psycopg[binary]>=3.1,<4",
# ]
# ///
"""Semantic tool search using Neon pgvector cosine similarity.

Find the best graphql-tools script for a task using natural language queries.
Embeds the query via HuggingFace, then uses pgvector's cosine distance
operator (<=> ) to find the most similar tools.

Follows the Anthropic tool-search-with-embeddings pattern:
- Claude calls tool_search with a natural language description
- This script embeds the query and searches pgvector
- Returns ranked tool references for Claude to use

Usage as a Claude tool_search handler:
  Query: "I need to check if my schema has breaking changes"
  Result: schema_diff (0.87), validate_operations (0.72), introspect_schema (0.65)
"""

import argparse
import json
import os
import sys

import httpx
import psycopg

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tool_search",
        description="Semantic tool search using Neon pgvector cosine similarity.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  uv run scripts/tool_search.py --database-url "$DATABASE_URL" --hf-token "$HF_TOKEN" --query "query GitHub repositories"
  uv run scripts/tool_search.py --database-url "$DATABASE_URL" --hf-token "$HF_TOKEN" --query "find breaking changes in schema" --top-k 3
  uv run scripts/tool_search.py --database-url "$DATABASE_URL" --hf-token "$HF_TOKEN" --query "setup database" --category setup
  uv run scripts/tool_search.py --database-url "$DATABASE_URL" --hf-token "$HF_TOKEN" --query "generate TypeScript types" --format json
  uv run scripts/tool_search.py --database-url "$DATABASE_URL" --hf-token "$HF_TOKEN" --query "Neon Postgres GraphQL" --threshold 0.5
  uv run scripts/tool_search.py --database-url "$DATABASE_URL" --hf-token "$HF_TOKEN" --query "Netflix UDA schema" --search-uda

Exit codes:
  0  Results found
  1  Client error
  2  Database or API error
  3  No results above threshold""",
    )
    p.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL"),
        help="Neon Postgres connection URL (default: $DATABASE_URL)",
    )
    p.add_argument("--hf-token", default=os.environ.get("HF_TOKEN"), help="HuggingFace API token (default: $HF_TOKEN)")
    p.add_argument("--query", required=True, help="Natural language description of what tool you need")
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"Embedding model (default: {DEFAULT_MODEL})")
    p.add_argument("--top-k", type=int, default=5, help="Number of results to return (default: 5)")
    p.add_argument("--threshold", type=float, default=0.3, help="Minimum similarity score 0-1 (default: 0.3)")
    p.add_argument(
        "--category",
        help="Filter by tool category (query, schema, management, federation, codegen, validation, setup, embeddings, search)",
    )
    p.add_argument(
        "--format",
        choices=["text", "json", "tool_reference"],
        default="text",
        help="Output format (default: text). tool_reference outputs Anthropic tool_reference format",
    )
    p.add_argument("--search-uda", action="store_true", help="Search UDA schema registry instead of tools")
    p.add_argument("--log", action="store_true", help="Log this search query for analytics")
    p.add_argument("--output", help="Write output to file instead of stdout")
    return p


def generate_embedding_hf_api(text: str, model: str, token: str) -> list[float]:
    """Generate embedding via HuggingFace Inference API."""
    url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"inputs": text, "options": {"wait_for_model": True}}

    resp = httpx.post(url, json=payload, headers=headers, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"HuggingFace API error {resp.status_code}: {resp.text[:500]}")

    result = resp.json()
    if isinstance(result, list) and len(result) > 0:
        if isinstance(result[0], list):
            return result[0]
        return result
    raise RuntimeError(f"Unexpected API response format: {type(result)}")


TOOL_SEARCH_SQL = """
SELECT
    tool_name,
    description,
    parameters,
    category,
    script_path,
    1 - (embedding <=> %s::vector) AS similarity_score
FROM graphql_tools
WHERE embedding IS NOT NULL
    AND 1 - (embedding <=> %s::vector) > %s
"""

TOOL_SEARCH_CATEGORY_SQL = """
    AND category = %s
"""

TOOL_SEARCH_ORDER_SQL = """
ORDER BY embedding <=> %s::vector
LIMIT %s
"""

UDA_SEARCH_SQL = """
SELECT
    schema_name,
    schema_type,
    content,
    uda_uri,
    1 - (embedding <=> %s::vector) AS similarity_score
FROM uda_schema_registry
WHERE embedding IS NOT NULL
    AND 1 - (embedding <=> %s::vector) > %s
ORDER BY embedding <=> %s::vector
LIMIT %s
"""

LOG_SQL = """
INSERT INTO tool_search_log (query_text, query_embedding, results_returned, top_tool, top_similarity)
VALUES (%s, %s, %s, %s, %s)
"""


def search_tools(
    conn, query_embedding: list[float], top_k: int, threshold: float, category: str | None = None
) -> list[dict]:
    formatted = f"[{','.join(str(x) for x in query_embedding)}]"

    sql = TOOL_SEARCH_SQL
    params: list = [formatted, formatted, threshold]

    if category:
        sql += TOOL_SEARCH_CATEGORY_SQL
        params.append(category)

    sql += TOOL_SEARCH_ORDER_SQL
    params.extend([formatted, top_k])

    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    return [
        {
            "tool_name": row[0],
            "description": row[1],
            "parameters": row[2],
            "category": row[3],
            "script_path": row[4],
            "similarity_score": round(float(row[5]), 4),
        }
        for row in rows
    ]


def search_uda(conn, query_embedding: list[float], top_k: int, threshold: float) -> list[dict]:
    formatted = f"[{','.join(str(x) for x in query_embedding)}]"

    with conn.cursor() as cur:
        cur.execute(UDA_SEARCH_SQL, [formatted, formatted, threshold, formatted, top_k])
        rows = cur.fetchall()

    return [
        {
            "schema_name": row[0],
            "schema_type": row[1],
            "content_preview": row[2][:200] + "..." if len(row[2]) > 200 else row[2],
            "uda_uri": row[3],
            "similarity_score": round(float(row[4]), 4),
        }
        for row in rows
    ]


def format_text(results: list[dict], query: str, is_uda: bool = False) -> str:
    lines = [f'Search: "{query}"', f"Results: {len(results)}", ""]

    if not results:
        lines.append("No matching tools found above threshold.")
        return "\n".join(lines)

    if is_uda:
        for i, r in enumerate(results, 1):
            lines.append(f"  {i}. {r['schema_name']} ({r['schema_type']}) -- similarity: {r['similarity_score']}")
            lines.append(f"     URI: {r['uda_uri']}")
            lines.append(f"     Preview: {r['content_preview'][:100]}")
    else:
        for i, r in enumerate(results, 1):
            lines.append(f"  {i}. {r['tool_name']} -- similarity: {r['similarity_score']}")
            lines.append(f"     {r['description'][:100]}...")
            lines.append(f"     Script: {r['script_path']}  Category: {r['category']}")

    return "\n".join(lines)


def format_tool_references(results: list[dict]) -> list[dict]:
    """Format results as Anthropic tool_reference objects for Claude tool_search."""
    return [{"type": "tool_reference", "tool_name": r["tool_name"]} for r in results]


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.database_url:
        print("Error: --database-url or $DATABASE_URL is required.", file=sys.stderr)
        sys.exit(1)

    if not args.hf_token:
        print("Error: --hf-token or $HF_TOKEN is required.", file=sys.stderr)
        sys.exit(1)

    # Generate query embedding
    print(f'Embedding query: "{args.query}"...', file=sys.stderr)
    try:
        query_embedding = generate_embedding_hf_api(args.query, args.model, args.hf_token)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    # Connect and search
    try:
        conn = psycopg.connect(args.database_url)
    except psycopg.OperationalError as e:
        print(f"Error: Could not connect: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        if args.search_uda:
            results = search_uda(conn, query_embedding, args.top_k, args.threshold)
        else:
            results = search_tools(conn, query_embedding, args.top_k, args.threshold, args.category)

        # Log the search if requested
        if args.log and not args.search_uda:
            formatted_emb = f"[{','.join(str(x) for x in query_embedding)}]"
            top_tool = results[0]["tool_name"] if results else None
            top_sim = results[0]["similarity_score"] if results else None
            with conn.cursor() as cur:
                cur.execute(LOG_SQL, [args.query, formatted_emb, len(results), top_tool, top_sim])
            conn.commit()

        # Format output
        if args.format == "json":
            output_data = {
                "query": args.query,
                "model": args.model,
                "results": results,
                "count": len(results),
            }
            output = json.dumps(output_data, indent=2)
        elif args.format == "tool_reference":
            if args.search_uda:
                print("Error: tool_reference format not supported for UDA search.", file=sys.stderr)
                sys.exit(1)
            refs = format_tool_references(results)
            output = json.dumps(refs, indent=2)
        else:
            output = format_text(results, args.query, is_uda=args.search_uda)

        if args.output:
            from pathlib import Path as P

            P(args.output).write_text(output + "\n")
            print(f"Output written to {args.output}", file=sys.stderr)
        else:
            print(output)

        if not results:
            sys.exit(3)

    except psycopg.Error as e:
        print(f"Error: Database error: {e}", file=sys.stderr)
        sys.exit(2)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

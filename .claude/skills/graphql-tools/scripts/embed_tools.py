# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "httpx>=0.27,<1",
#   "psycopg[binary]>=3.1,<4",
# ]
# ///
"""Generate tool embeddings via HuggingFace and store in Neon pgvector.

Converts each graphql-tools script into a text representation (name,
description, parameters, category) and generates embeddings using the
HuggingFace Inference API or a local sentence-transformers model.

Follows the Anthropic tool-search-with-embeddings cookbook pattern:
https://github.com/anthropics/claude-cookbooks/blob/main/tool_use/tool_search_with_embeddings.ipynb

Stores embeddings in Neon Postgres pgvector for semantic similarity search.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import httpx
import psycopg

# Default model: all-MiniLM-L6-v2 (384 dimensions, fast, good quality)
DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# Tool definitions -- the complete registry of graphql-tools scripts
# Following Anthropic cookbook pattern: each tool is name + description + parameters
TOOL_REGISTRY = [
    {
        "tool_name": "graphql_query",
        "description": "Universal GraphQL query executor for any endpoint. Send queries to Hasura, PostGraphile, Apollo Router, GraphQL Mesh, WunderGraph, Grafbase, Tailcall, or Graphweaver.",
        "parameters": "endpoint, query, query-file, variables, variables-file, operation, header, bearer-token, timeout, output",
        "category": "query",
        "script_path": "scripts/graphql_query.py",
    },
    {
        "tool_name": "github_graphql",
        "description": "GitHub GraphQL API client with pagination and built-in operations. Query repositories, issues, pull requests, users, and rate limits using GitHub's GraphQL endpoint.",
        "parameters": "query, query-file, operation (repos/issues/prs/viewer/rate-limit), owner, repo, first, state, paginate, max-pages, cost-estimate, token",
        "category": "query",
        "script_path": "scripts/github_graphql.py",
    },
    {
        "tool_name": "neon_pg_graphql",
        "description": "Neon Postgres 18 pg_graphql client. Execute GraphQL queries against a Neon database using the pg_graphql extension via SQL-based graphql.resolve() function. Supports collections, filtering, and mutations.",
        "parameters": "database-url, host, port, dbname, user, password, query, query-file, variables, operation, ensure-extension, introspect, list-types",
        "category": "query",
        "script_path": "scripts/neon_pg_graphql.py",
    },
    {
        "tool_name": "introspect_schema",
        "description": "Introspect any GraphQL endpoint and output the schema as SDL or JSON. Works with any spec-compliant server. Can build schema from saved introspection JSON files.",
        "parameters": "endpoint, from-json, format (sdl/json), types-only, header, bearer-token, output",
        "category": "schema",
        "script_path": "scripts/introspect_schema.py",
    },
    {
        "tool_name": "schema_diff",
        "description": "Compare two GraphQL schemas and detect breaking changes. Reports type removals, field changes, argument modifications, enum changes, and union member changes. Similar to GraphQL Inspector diff.",
        "parameters": "old, new, format (text/json), breaking-only, output",
        "category": "schema",
        "script_path": "scripts/schema_diff.py",
    },
    {
        "tool_name": "hasura_manage",
        "description": "Hasura GraphQL Engine metadata management. Track and untrack tables, export and apply metadata, reload metadata, run SQL queries, and check Hasura health status via the Metadata API v2.",
        "parameters": "endpoint, action (export-metadata/reload-metadata/clear-metadata/track-table/untrack-table/list-tables/health/run-sql), admin-secret, table, schema, source, sql, confirm, dry-run",
        "category": "management",
        "script_path": "scripts/hasura_manage.py",
    },
    {
        "tool_name": "apollo_compose",
        "description": "Apollo Federation supergraph composition and subgraph validation. Compose multiple subgraph schemas into a supergraph, validate federation directives (@key, @external, @requires), check directive usage, and merge schemas.",
        "parameters": "config, validate, check-directives, merge, subgraph, schema, output",
        "category": "federation",
        "script_path": "scripts/apollo_compose.py",
    },
    {
        "tool_name": "tailcall_gen",
        "description": "Generate Tailcall GraphQL configuration from REST or gRPC endpoint definitions. Convert OpenAPI specs to Tailcall .graphql config files with @server, @upstream, and @http directives.",
        "parameters": "from-openapi, from-endpoints, scaffold, base-url, output, port, hostname",
        "category": "codegen",
        "script_path": "scripts/tailcall_gen.py",
    },
    {
        "tool_name": "codegen_types",
        "description": "Generate TypeScript or Python types from a GraphQL schema. Produces typed interfaces, dataclasses, enums, and union types from SDL schema files. Similar to GraphQL Code Generator.",
        "parameters": "schema, lang (typescript/python), output, no-builtins",
        "category": "codegen",
        "script_path": "scripts/codegen_types.py",
    },
    {
        "tool_name": "validate_operations",
        "description": "Validate GraphQL operation files (.graphql) against a schema. Checks queries, mutations, and subscriptions for syntax errors, unknown fields, type mismatches, missing required arguments, and undefined variables.",
        "parameters": "schema, operations (file/directory/inline), format (text/json), output",
        "category": "validation",
        "script_path": "scripts/validate_operations.py",
    },
    {
        "tool_name": "neon_setup_vectors",
        "description": "Setup Neon Postgres with pgvector and pg_graphql extensions for tool embeddings. Creates tables, indexes, and schema for embedding-based tool search and UDA schema registry.",
        "parameters": "database-url, setup, verify, teardown, confirm, dry-run",
        "category": "setup",
        "script_path": "scripts/neon_setup_vectors.py",
    },
    {
        "tool_name": "embed_tools",
        "description": "Generate embeddings for graphql-tools scripts using HuggingFace sentence-transformers and store them in Neon Postgres pgvector. Supports HuggingFace Inference API and local models.",
        "parameters": "database-url, hf-token, model, embed-all, embed-tool, embed-uda, list, source (api/local)",
        "category": "embeddings",
        "script_path": "scripts/embed_tools.py",
    },
    {
        "tool_name": "tool_search",
        "description": "Semantic tool search using Neon pgvector cosine similarity. Find the best graphql-tools script for a task using natural language queries. Returns ranked results with similarity scores.",
        "parameters": "database-url, hf-token, query, model, top-k, threshold, category, format (text/json)",
        "category": "search",
        "script_path": "scripts/tool_search.py",
    },
]


def tool_to_text(tool: dict) -> str:
    """Convert a tool definition to embeddable text.

    Following Anthropic cookbook pattern: combine name, description, and
    parameters into a single text string for embedding generation.
    """
    parts = [
        f"Tool: {tool['tool_name']}",
        f"Description: {tool['description']}",
    ]
    if tool.get("parameters"):
        parts.append(f"Parameters: {tool['parameters']}")
    if tool.get("category"):
        parts.append(f"Category: {tool['category']}")
    return "\n".join(parts)


def generate_embedding_hf_api(text: str, model: str, token: str) -> list[float]:
    """Generate embedding via HuggingFace Inference API."""
    url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"inputs": text, "options": {"wait_for_model": True}}

    resp = httpx.post(url, json=payload, headers=headers, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"HuggingFace API error {resp.status_code}: {resp.text[:500]}")

    result = resp.json()
    # API returns nested array for sentence-transformers; take first element
    if isinstance(result, list) and len(result) > 0:
        if isinstance(result[0], list):
            return result[0]
        return result
    raise RuntimeError(f"Unexpected API response format: {type(result)}")


def generate_embeddings_batch_hf(texts: list[str], model: str, token: str) -> list[list[float]]:
    """Generate embeddings for a batch of texts via HuggingFace Inference API."""
    url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"inputs": texts, "options": {"wait_for_model": True}}

    resp = httpx.post(url, json=payload, headers=headers, timeout=120)
    if resp.status_code != 200:
        raise RuntimeError(f"HuggingFace API error {resp.status_code}: {resp.text[:500]}")

    result = resp.json()
    if isinstance(result, list) and len(result) == len(texts):
        return result
    raise RuntimeError(f"Unexpected API response: expected {len(texts)} embeddings, got {type(result)}")


def generate_embedding_local(text: str, model_name: str) -> list[float]:
    """Generate embedding using local sentence-transformers model."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("Error: sentence-transformers not installed. Use --source api or install:", file=sys.stderr)
        print("  uv pip install sentence-transformers", file=sys.stderr)
        sys.exit(1)

    model = SentenceTransformer(model_name)
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="embed_tools",
        description="Generate tool embeddings via HuggingFace and store in Neon pgvector.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  uv run scripts/embed_tools.py --database-url "$DATABASE_URL" --hf-token "$HF_TOKEN" --embed-all
  uv run scripts/embed_tools.py --database-url "$DATABASE_URL" --hf-token "$HF_TOKEN" --embed-tool graphql_query
  uv run scripts/embed_tools.py --database-url "$DATABASE_URL" --hf-token "$HF_TOKEN" --embed-uda
  uv run scripts/embed_tools.py --list
  uv run scripts/embed_tools.py --database-url "$DATABASE_URL" --hf-token "$HF_TOKEN" --embed-all --source local

Exit codes:
  0  Success
  1  Client error
  2  Database or API error""",
    )
    p.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL"),
        help="Neon Postgres connection URL (default: $DATABASE_URL)",
    )
    p.add_argument("--hf-token", default=os.environ.get("HF_TOKEN"), help="HuggingFace API token (default: $HF_TOKEN)")
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"Embedding model (default: {DEFAULT_MODEL})")
    p.add_argument(
        "--source",
        choices=["api", "local"],
        default="api",
        help="Embedding source: api (HuggingFace Inference API) or local (sentence-transformers)",
    )

    action = p.add_mutually_exclusive_group(required=True)
    action.add_argument("--embed-all", action="store_true", help="Generate and store embeddings for all tools")
    action.add_argument("--embed-tool", help="Generate embedding for a single tool by name")
    action.add_argument(
        "--embed-uda", action="store_true", help="Embed Netflix UDA schema files from assets/uda-intro-blog/"
    )
    action.add_argument("--list", action="store_true", help="List all tools in the registry (no DB needed)")

    p.add_argument("--output", help="Write result to file instead of stdout")
    return p


def upsert_tool(conn, tool: dict, embedding: list[float]) -> None:
    """Insert or update a tool with its embedding."""
    full_text = tool_to_text(tool)
    formatted = f"[{','.join(str(x) for x in embedding)}]"

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO graphql_tools (tool_name, description, parameters, category, script_path, full_text, embedding, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (tool_name) DO UPDATE SET
                description = EXCLUDED.description,
                parameters = EXCLUDED.parameters,
                category = EXCLUDED.category,
                script_path = EXCLUDED.script_path,
                full_text = EXCLUDED.full_text,
                embedding = EXCLUDED.embedding,
                updated_at = CURRENT_TIMESTAMP
        """,
            (
                tool["tool_name"],
                tool["description"],
                tool.get("parameters"),
                tool.get("category"),
                tool.get("script_path"),
                full_text,
                formatted,
            ),
        )
    conn.commit()


def embed_uda_schemas(conn, model: str, token: str | None, source: str) -> list[dict]:
    """Embed Netflix UDA schema files from assets directory."""
    assets_dir = Path(__file__).parent.parent / "assets" / "uda-intro-blog"
    if not assets_dir.exists():
        print(f"Error: UDA assets not found at {assets_dir}", file=sys.stderr)
        sys.exit(1)

    schema_files = {
        "onepiece.graphqls": "graphql",
        "onepiece.avro": "avro",
        "onepiece.ttl": "rdf",
        "onepiece_character_data_container.ttl": "rdf",
        "onepiece_character_mappings.ttl": "rdf",
    }

    results = []
    for filename, schema_type in schema_files.items():
        filepath = assets_dir / filename
        if not filepath.exists():
            print(f"Warning: {filename} not found, skipping.", file=sys.stderr)
            continue

        content = filepath.read_text()
        embed_text = f"Schema: {filename}\nType: {schema_type}\nContent: {content[:2000]}"

        print(f"  Embedding {filename} ({schema_type})...", file=sys.stderr)

        if source == "api":
            if not token:
                print("Error: --hf-token or $HF_TOKEN required for API source.", file=sys.stderr)
                sys.exit(1)
            embedding = generate_embedding_hf_api(embed_text, model, token)
        else:
            embedding = generate_embedding_local(embed_text, model)

        formatted = f"[{','.join(str(x) for x in embedding)}]"

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO uda_schema_registry (schema_name, schema_type, content, uda_uri, embedding)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """,
                (
                    filename,
                    schema_type,
                    content,
                    f"https://rdf.netflix.net/onto/onepiece#{filename.split('.')[0]}",
                    formatted,
                ),
            )
        conn.commit()
        results.append({"file": filename, "type": schema_type, "dimensions": len(embedding)})

    return results


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.list:
        output = json.dumps(
            {
                "tools": [{k: v for k, v in t.items()} for t in TOOL_REGISTRY],
                "count": len(TOOL_REGISTRY),
                "model": args.model,
                "dimensions": EMBEDDING_DIM,
            },
            indent=2,
        )
        if args.output:
            Path(args.output).write_text(output + "\n")
        else:
            print(output)
        return

    if not args.database_url:
        print("Error: --database-url or $DATABASE_URL is required.", file=sys.stderr)
        sys.exit(1)

    if args.source == "api" and not args.hf_token:
        print("Error: --hf-token or $HF_TOKEN is required for API source.", file=sys.stderr)
        sys.exit(1)

    try:
        conn = psycopg.connect(args.database_url)
    except psycopg.OperationalError as e:
        print(f"Error: Could not connect: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        if args.embed_all:
            print(f"Generating embeddings for {len(TOOL_REGISTRY)} tools using {args.model}...", file=sys.stderr)
            texts = [tool_to_text(t) for t in TOOL_REGISTRY]

            if args.source == "api":
                print("  Using HuggingFace Inference API (batch)...", file=sys.stderr)
                try:
                    embeddings = generate_embeddings_batch_hf(texts, args.model, args.hf_token)
                except RuntimeError:
                    print("  Batch failed, falling back to individual requests...", file=sys.stderr)
                    embeddings = []
                    for i, text in enumerate(texts):
                        print(f"  [{i + 1}/{len(texts)}] {TOOL_REGISTRY[i]['tool_name']}...", file=sys.stderr)
                        embeddings.append(generate_embedding_hf_api(text, args.model, args.hf_token))
            else:
                print("  Using local sentence-transformers...", file=sys.stderr)
                try:
                    from sentence_transformers import SentenceTransformer
                except ImportError:
                    print("Error: Install sentence-transformers: uv pip install sentence-transformers", file=sys.stderr)
                    sys.exit(1)
                model = SentenceTransformer(args.model)
                embeddings_np = model.encode(texts, convert_to_numpy=True)
                embeddings = [e.tolist() for e in embeddings_np]

            results = []
            for tool, embedding in zip(TOOL_REGISTRY, embeddings):
                upsert_tool(conn, tool, embedding)
                results.append({"tool": tool["tool_name"], "dimensions": len(embedding)})
                print(f"  Stored: {tool['tool_name']} ({len(embedding)} dims)", file=sys.stderr)

            output = json.dumps({"status": "ok", "tools_embedded": results, "model": args.model}, indent=2)

        elif args.embed_tool:
            tool = next((t for t in TOOL_REGISTRY if t["tool_name"] == args.embed_tool), None)
            if not tool:
                print(f"Error: Unknown tool '{args.embed_tool}'. Use --list to see available tools.", file=sys.stderr)
                sys.exit(1)

            text = tool_to_text(tool)
            print(f"Generating embedding for {args.embed_tool}...", file=sys.stderr)

            if args.source == "api":
                embedding = generate_embedding_hf_api(text, args.model, args.hf_token)
            else:
                embedding = generate_embedding_local(text, args.model)

            upsert_tool(conn, tool, embedding)
            output = json.dumps(
                {"status": "ok", "tool": args.embed_tool, "dimensions": len(embedding), "model": args.model}, indent=2
            )

        elif args.embed_uda:
            print(f"Embedding Netflix UDA schemas using {args.model}...", file=sys.stderr)
            results = embed_uda_schemas(conn, args.model, args.hf_token, args.source)
            output = json.dumps({"status": "ok", "schemas_embedded": results, "model": args.model}, indent=2)

        else:
            parser.print_help()
            sys.exit(1)

        if args.output:
            Path(args.output).write_text(output + "\n")
        else:
            print(output)

    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except psycopg.Error as e:
        print(f"Error: Database error: {e}", file=sys.stderr)
        sys.exit(2)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

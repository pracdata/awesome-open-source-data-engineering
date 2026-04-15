---
name: graphql-tools
description: Query, introspect, validate, and manage GraphQL APIs across systems including Hasura, PostGraphile, Apollo Federation, GitHub GraphQL, Neon Postgres 18 pg_graphql, Tailcall, GraphQL Mesh, WunderGraph, Grafbase, and Graphweaver. Includes embedding-based semantic tool search using HuggingFace + Neon pgvector, and Netflix UDA unified data architecture patterns. Use when working with GraphQL endpoints, schemas, federation, code generation, embeddings, or data APIs.
license: MIT
compatibility: Requires Python 3.10+ and uv. Network access needed for remote GraphQL endpoints. HuggingFace premium token for embeddings. Neon Postgres 18 for pgvector + pg_graphql.
allowed-tools: Bash(uv:*) Read Write Edit
metadata:
  author: agentwarehouses
  version: "2.0"
---

# GraphQL Tools

Programmatic tools for querying, introspecting, validating, and managing GraphQL APIs across different systems.

## Available scripts

- **`scripts/graphql_query.py`** -- Universal GraphQL query executor for any endpoint (Hasura, PostGraphile, Apollo, Mesh, WunderGraph, Grafbase, Tailcall, Graphweaver)
- **`scripts/github_graphql.py`** -- GitHub GraphQL API client with pagination and common operations
- **`scripts/neon_pg_graphql.py`** -- Neon Postgres 18 pg_graphql client via SQL-based GraphQL resolution
- **`scripts/introspect_schema.py`** -- Introspect any GraphQL endpoint and output SDL or JSON
- **`scripts/schema_diff.py`** -- Compare two GraphQL schemas and detect breaking changes
- **`scripts/hasura_manage.py`** -- Hasura GraphQL Engine metadata management (track tables, permissions, migrations)
- **`scripts/apollo_compose.py`** -- Apollo Federation supergraph composition and subgraph validation
- **`scripts/tailcall_gen.py`** -- Generate Tailcall GraphQL configuration from REST/gRPC endpoint definitions
- **`scripts/codegen_types.py`** -- Generate TypeScript or Python types from a GraphQL schema
- **`scripts/validate_operations.py`** -- Validate GraphQL operation files (.graphql) against a schema
- **`scripts/neon_setup_vectors.py`** -- Setup Neon Postgres with pgvector + pg_graphql for embedding-based tool search
- **`scripts/embed_tools.py`** -- Generate tool embeddings via HuggingFace and store in Neon pgvector
- **`scripts/tool_search.py`** -- Semantic tool search using Neon pgvector cosine similarity

All scripts are self-contained with PEP 723 inline dependencies. Run with:

```bash
uv run scripts/<script_name>.py --help
```

## Common workflows

### Query any GraphQL endpoint

```bash
uv run scripts/graphql_query.py \
  --endpoint https://your-hasura-instance.com/v1/graphql \
  --query '{ users { id name email } }' \
  --header "x-hasura-admin-secret: $HASURA_ADMIN_SECRET"
```

### Query GitHub GraphQL API

```bash
uv run scripts/github_graphql.py \
  --query '{ viewer { login repositories(first: 5) { nodes { name stargazerCount } } } }'
```

Requires `GITHUB_TOKEN` env var. Use `--operation` for common shortcuts:

```bash
uv run scripts/github_graphql.py --operation repos --owner myorg --first 10
uv run scripts/github_graphql.py --operation issues --owner myorg --repo myrepo --state OPEN
```

### Query Neon Postgres with pg_graphql

```bash
uv run scripts/neon_pg_graphql.py \
  --query '{ usersCollection(first: 10) { edges { node { id name } } } }' \
  --database-url "$DATABASE_URL"
```

Or pass connection params individually:

```bash
uv run scripts/neon_pg_graphql.py \
  --query '{ usersCollection { edges { node { id } } } }' \
  --host ep-example-123.us-east-2.aws.neon.tech \
  --dbname mydb --user myuser --password "$NEON_PASSWORD"
```

### Introspect and diff schemas

```bash
# Introspect to SDL
uv run scripts/introspect_schema.py --endpoint https://api.example.com/graphql --format sdl --output schema.graphql

# Diff two schemas for breaking changes
uv run scripts/schema_diff.py --old schema-v1.graphql --new schema-v2.graphql
```

### Hasura metadata management

```bash
# Export metadata
uv run scripts/hasura_manage.py --endpoint https://hasura.example.com --action export-metadata

# Track a table
uv run scripts/hasura_manage.py --endpoint https://hasura.example.com --action track-table --table users --schema public
```

### Apollo Federation composition

```bash
# Compose supergraph from subgraph schemas
uv run scripts/apollo_compose.py --config supergraph.yaml --output supergraph.graphql

# Validate a subgraph
uv run scripts/apollo_compose.py --validate --subgraph accounts --schema accounts.graphql
```

### Generate types from schema

```bash
# TypeScript types
uv run scripts/codegen_types.py --schema schema.graphql --lang typescript --output types.ts

# Python dataclasses
uv run scripts/codegen_types.py --schema schema.graphql --lang python --output types.py
```

### Validate operations

```bash
uv run scripts/validate_operations.py --schema schema.graphql --operations queries/
```

## Embedding-based tool search (Anthropic cookbook pattern)

Setup once, then use semantic search to find the right tool for any task.
Uses HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (384 dims) + Neon pgvector.

### Step 1: Setup Neon with pgvector + pg_graphql

```bash
uv run scripts/neon_setup_vectors.py --database-url "$DATABASE_URL" --setup
```

### Step 2: Embed all tools

```bash
uv run scripts/embed_tools.py --database-url "$DATABASE_URL" --hf-token "$HF_TOKEN" --embed-all
```

### Step 3: Search for tools by natural language

```bash
uv run scripts/tool_search.py --database-url "$DATABASE_URL" --hf-token "$HF_TOKEN" \
    --query "I need to check if my schema has breaking changes"
# Returns: schema_diff (0.87), validate_operations (0.72), ...
```

### Embed Netflix UDA schemas

```bash
uv run scripts/embed_tools.py --database-url "$DATABASE_URL" --hf-token "$HF_TOKEN" --embed-uda
uv run scripts/tool_search.py --database-url "$DATABASE_URL" --hf-token "$HF_TOKEN" \
    --query "character entity with relationships" --search-uda
```

For Claude tool_search integration, use `--format tool_reference` to get
Anthropic-compatible tool reference objects that Claude can immediately use.

For Netflix UDA patterns and schema format details, see [references/UDA.md](references/UDA.md).

## Gotchas

- **Hasura**: Admin secret goes in `x-hasura-admin-secret` header, not `Authorization`. The metadata API is at `/v1/metadata`, not `/v1/graphql`.
- **GitHub GraphQL**: Rate limit is 5,000 points/hour (not requests). Nested connections multiply cost. Use `--cost-estimate` flag to preview.
- **Neon pg_graphql**: The extension must be enabled first (`CREATE EXTENSION IF NOT EXISTS pg_graphql`). It resolves against the `public` schema by default. Connection requires SSL (`sslmode=require`).
- **Apollo Federation**: Subgraphs must use `@key` directives for entity resolution. Composition fails silently on missing `@external` fields.
- **PostGraphile**: Uses inflection to map PostgreSQL `snake_case` to GraphQL `camelCase`. Column `user_id` becomes field `userId`.
- **Tailcall**: Config uses `.graphql` files with `@server`, `@upstream`, and `@http` directives, not YAML/JSON.
- **GraphQL Mesh**: Source handlers (openapi, grpc, json-schema) each have distinct config shapes. Check `references/REFERENCE.md` for patterns.
- **pgvector on Neon PG18**: Use `vector(384)` for all-MiniLM-L6-v2. The ivfflat index requires `lists` param (use `sqrt(rows)`, minimum 10). Always `ANALYZE` after bulk inserts.
- **HuggingFace Inference API**: Batch requests may fail for large payloads; the script auto-falls back to individual requests. First request may take ~20s while the model loads (`wait_for_model: true`).
- **Netflix UDA**: The `@udaUri` directive is not standard GraphQL -- it's a Netflix-specific extension. Strip it before feeding schemas to non-UDA tooling.

## Environment variables

| Variable | Used by | Purpose |
|---|---|---|
| `GITHUB_TOKEN` | github_graphql.py | GitHub API authentication |
| `DATABASE_URL` | neon_pg_graphql.py, neon_setup_vectors.py, embed_tools.py, tool_search.py | Neon Postgres connection string |
| `HASURA_ADMIN_SECRET` | hasura_manage.py, graphql_query.py | Hasura admin authentication |
| `GRAPHQL_ENDPOINT` | graphql_query.py | Default endpoint (override with `--endpoint`) |
| `HF_TOKEN` | embed_tools.py, tool_search.py | HuggingFace API token (premium) |

For detailed API patterns, see [references/REFERENCE.md](references/REFERENCE.md).
For Netflix UDA architecture, see [references/UDA.md](references/UDA.md).

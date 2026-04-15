---
name: crud-eval
description: Evaluate CRUD operations across GraphQL, API, SDK, and CLI interfaces for Claude platform entities (skills, plugins, connectors, mcps, subagents, hooks, sessions, memories, agent-teams). Use when testing, validating, or benchmarking CRUD management across interfaces.
license: MIT
compatibility: Requires Python 3.10+ and uv. ant CLI for CLI evals. ANTHROPIC_API_KEY for API/SDK evals.
allowed-tools: Bash(uv:*) Bash(ant:*) Read Write Edit
metadata:
  author: agentwarehouses
  version: "1.0"
---

# CRUD Eval

Evaluation framework for CRUD management of Claude platform entities across
4 interfaces (GraphQL, API, SDK, CLI) and 9 entity types.

## Eval matrix

**Interfaces:** `graphql`, `api`, `sdk`, `cli`
**Entities:** `skills`, `plugins`, `connectors`, `mcps`, `subagents`, `hooks`, `sessions`, `memories`, `agent-teams`
**Operations:** `create`, `read`, `update`, `delete`

Total: 4 interfaces x 9 entities x 4 operations = **144 eval cells**

## Available scripts

- **`scripts/generate_eval_matrix.py`** -- Generate the full eval matrix as evals.json with test cases and assertions
- **`scripts/run_eval.py`** -- Execute a single eval test case (with_skill or without_skill) and capture outputs
- **`scripts/grade_eval.py`** -- Grade eval outputs against assertions, produce grading.json
- **`scripts/benchmark.py`** -- Aggregate grading results into benchmark.json with pass rates and deltas
- **`scripts/crud_operations.py`** -- Execute CRUD operations across all 4 interfaces (the core tool)

## Quick start

### Step 1: Generate the eval matrix

```bash
uv run scripts/generate_eval_matrix.py --output evals/evals.json
```

### Step 2: Run evals for a specific interface + entity

```bash
# Run all CRUD operations for cli-sessions
uv run scripts/run_eval.py --eval-id cli-sessions-create --workspace workspace/iteration-1
uv run scripts/run_eval.py --eval-id cli-sessions-read --workspace workspace/iteration-1
uv run scripts/run_eval.py --eval-id cli-sessions-update --workspace workspace/iteration-1
uv run scripts/run_eval.py --eval-id cli-sessions-delete --workspace workspace/iteration-1
```

### Step 3: Grade results

```bash
uv run scripts/grade_eval.py --workspace workspace/iteration-1 --eval-id cli-sessions-create
```

### Step 4: Aggregate benchmarks

```bash
uv run scripts/benchmark.py --workspace workspace/iteration-1
```

## CRUD operations by interface

### CLI (`ant` command)

```bash
uv run scripts/crud_operations.py --interface cli --entity sessions --operation create \
    --params '{"agent": "agent_01...", "environment": "env_01...", "title": "test session"}'
```

Underlying commands:
- **Create**: `ant beta:<entity> create [--flags or < yaml]`
- **Read**: `ant beta:<entity> retrieve --<entity>-id <id>` or `ant beta:<entity> list`
- **Update**: `ant beta:<entity> update --<entity>-id <id> --version <v> [< yaml]`
- **Delete**: `ant beta:<entity> delete --<entity>-id <id>`

### API (REST)

```bash
uv run scripts/crud_operations.py --interface api --entity agents --operation create \
    --params '{"name": "test-agent", "model": {"id": "claude-sonnet-4-6"}}'
```

Underlying endpoints:
- **Create**: `POST /v1/beta/<entity>`
- **Read**: `GET /v1/beta/<entity>/<id>` or `GET /v1/beta/<entity>`
- **Update**: `PUT /v1/beta/<entity>/<id>`
- **Delete**: `DELETE /v1/beta/<entity>/<id>`

### SDK (Python)

```bash
uv run scripts/crud_operations.py --interface sdk --entity agents --operation create \
    --params '{"name": "test-agent", "model": {"id": "claude-sonnet-4-6"}}'
```

Underlying calls:
- **Create**: `client.beta.agents.create(**params)`
- **Read**: `client.beta.agents.retrieve(agent_id=id)` or `client.beta.agents.list()`
- **Update**: `client.beta.agents.update(agent_id=id, **params)`
- **Delete**: `client.beta.agents.delete(agent_id=id)`

### GraphQL (via pg_graphql or custom gateway)

```bash
uv run scripts/crud_operations.py --interface graphql --entity skills --operation create \
    --params '{"name": "test-skill", "description": "A test skill"}' \
    --endpoint "$GRAPHQL_ENDPOINT"
```

Uses GraphQL mutations/queries against a GraphQL API layer over the entity store.

## Eval structure (per agentskills.io spec)

```
crud-eval-workspace/
└── iteration-1/
    ├── eval-cli-sessions-create/
    │   ├── with_skill/
    │   │   ├── outputs/
    │   │   ├── timing.json
    │   │   └── grading.json
    │   └── without_skill/
    │       ├── outputs/
    │       ├── timing.json
    │       └── grading.json
    ├── eval-api-agents-read/
    │   └── ...
    ├── feedback.json
    └── benchmark.json
```

## Gotchas

- **CLI beta resources**: All managed agent resources live under `ant beta:` prefix. Omitting `beta:` will 404.
- **Version locking**: Update operations require the current `version` number from the last retrieve. Always read before updating.
- **Sessions are stateful**: Creating a session starts a container. Delete when done to avoid resource waste.
- **Hooks are local-only**: Claude Code hooks live in `settings.json`, not the API. CLI/API CRUD doesn't apply -- use file-based CRUD instead.
- **Memories**: Currently experimental. SDK methods may change between API versions.
- **Agent-teams**: Defined via `AGENTS.md` files, not API resources. CRUD is file-based for local, API-based for managed.
- **Connectors**: MCP-powered. Create via settings.json `mcpServers` config or the Connectors directory on claude.com.

## Environment variables

| Variable | Used by | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | crud_operations.py, run_eval.py | Claude API authentication |
| `GRAPHQL_ENDPOINT` | crud_operations.py | GraphQL gateway endpoint |
| `DATABASE_URL` | crud_operations.py | Neon Postgres for GraphQL entity store |

For interface-specific CRUD patterns, see [references/CRUD_PATTERNS.md](references/CRUD_PATTERNS.md).

# CRUD Patterns by Interface

Detailed CRUD operation patterns for each interface targeting Claude platform entities.

## CLI Interface (`ant` command)

The `ant` CLI follows a `resource action` pattern. Beta resources use `beta:` prefix.

### Resource mapping

| Entity | CLI Resource | Notes |
|---|---|---|
| skills | `beta:skills` | Managed agent skills |
| plugins | `beta:plugins` | Tool plugins |
| connectors | `beta:connectors` | MCP connectors |
| mcps | `beta:mcp_servers` | MCP server configs |
| subagents | `beta:agents` | Same as agents |
| hooks | N/A (file-based) | Edit settings.json |
| sessions | `beta:sessions` | + `beta:sessions:events` |
| memories | `beta:memories` | Experimental |
| agent-teams | `beta:agent_teams` | Multi-agent configs |

### CRUD commands

```bash
# Create
ant beta:agents create --name "My Agent" --model '{id: claude-sonnet-4-6}'
ant beta:agents create < agent.yaml

# Read (single)
ant beta:agents retrieve --agent-id agent_01...

# Read (list)
ant beta:agents list --transform "{id,name}" --format jsonl

# Update (requires version)
VERSION=$(ant beta:agents retrieve --agent-id agent_01... --transform version --format yaml)
echo '{"name": "Updated Agent"}' | ant beta:agents update --agent-id agent_01... --version $VERSION

# Delete
ant beta:agents delete --agent-id agent_01...
```

### Sessions lifecycle

```bash
# Create session
ant beta:sessions create \
    --agent agent_01... \
    --environment env_01... \
    --title "Test session"

# Send message
ant beta:sessions:events send \
    --session-id session_01... \
    --event '{type: user.message, content: [{type: text, text: "Hello"}]}'

# List events
ant beta:sessions:events list --session-id session_01...

# Stream events
ant beta:sessions stream --session-id session_01...
```

## API Interface (REST)

All managed agent resources at `https://api.anthropic.com/v1/beta/`.

### Headers

```
x-api-key: sk-ant-api03-...
anthropic-version: 2023-06-01
anthropic-beta: managed-agents-2026-04-01
content-type: application/json
```

### Endpoints

| Operation | Method | Endpoint |
|---|---|---|
| Create | POST | `/v1/beta/{resource}` |
| Read | GET | `/v1/beta/{resource}/{id}` |
| List | GET | `/v1/beta/{resource}` |
| Update | PUT | `/v1/beta/{resource}/{id}` |
| Delete | DELETE | `/v1/beta/{resource}/{id}` |

### Example: Agent CRUD

```bash
# Create
curl -X POST https://api.anthropic.com/v1/beta/agents \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: managed-agents-2026-04-01" \
  -d '{"name": "My Agent", "model": {"id": "claude-sonnet-4-6"}}'

# Read
curl https://api.anthropic.com/v1/beta/agents/agent_01... \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: managed-agents-2026-04-01"

# Update (with version)
curl -X PUT https://api.anthropic.com/v1/beta/agents/agent_01... \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: managed-agents-2026-04-01" \
  -d '{"name": "Updated Agent", "version": 1}'

# Delete
curl -X DELETE https://api.anthropic.com/v1/beta/agents/agent_01... \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: managed-agents-2026-04-01"
```

## SDK Interface (Python)

Uses the `anthropic` Python SDK with `client.beta.*` namespace.

```python
import anthropic

client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

# Create
agent = client.beta.agents.create(
    name="My Agent",
    model={"id": "claude-sonnet-4-6"},
    tools=[{"type": "agent_toolset_20260401"}],
)

# Read
agent = client.beta.agents.retrieve(agent_id="agent_01...")

# List
for agent in client.beta.agents.list():
    print(agent.id, agent.name)

# Update (with version)
agent = client.beta.agents.update(
    agent_id="agent_01...",
    name="Updated Agent",
    version=1,
)

# Delete
client.beta.agents.delete(agent_id="agent_01...")
```

### Sessions via SDK

```python
# Create session
session = client.beta.sessions.create(
    agent={"type": "agent", "id": "agent_01...", "version": 1},
    environment="env_01...",
    title="Test session",
)

# Send message
client.beta.sessions.events.send(
    session_id=session.id,
    event={
        "type": "user.message",
        "content": [{"type": "text", "text": "Hello"}],
    },
)

# List events
for event in client.beta.sessions.events.list(session_id=session.id):
    print(event.type, event.content)
```

## GraphQL Interface

GraphQL CRUD via pg_graphql on Neon Postgres or a custom GraphQL gateway.

### Schema pattern

```graphql
type Skill {
  id: ID!
  name: String!
  description: String
  created_at: DateTime
  updated_at: DateTime
}

type Query {
  skill(id: ID!): Skill
  skillsCollection(first: Int, after: String): SkillConnection
}

type Mutation {
  createSkill(input: CreateSkillInput!): Skill
  updateSkill(id: ID!, input: UpdateSkillInput!): Skill
  deleteSkill(id: ID!): DeleteResult
}
```

### Operations

```graphql
# Create
mutation {
  insertIntoSkillsCollection(objects: [{name: "test", description: "A test skill"}]) {
    records { id name }
  }
}

# Read
query {
  skillsCollection(filter: {id: {eq: "123"}}) {
    edges { node { id name description } }
  }
}

# Update
mutation {
  updateSkillsCollection(filter: {id: {eq: "123"}}, set: {description: "Updated"}) {
    records { id name description }
  }
}

# Delete
mutation {
  deleteFromSkillsCollection(filter: {id: {eq: "123"}}) {
    records { id }
  }
}
```

## File-based CRUD (hooks, agent-teams)

Some entities are file-based rather than API-based.

### Hooks (settings.json)

```json
{
  "hooks": {
    "PreToolUse": [
      {"matcher": "Bash", "command": "echo 'pre-hook fired'"}
    ],
    "PostToolUse": [
      {"matcher": "Write", "command": "echo 'post-hook fired'"}
    ]
  }
}
```

CRUD = read/write settings.json via file operations.

### Agent-teams (AGENTS.md)

```markdown
# Agent Team

## Leader
Role: Coordinator
Model: claude-opus-4-6

## Researcher
Role: Information gathering
Model: claude-sonnet-4-6
```

CRUD = read/write AGENTS.md or `.claude/agents/` directory.

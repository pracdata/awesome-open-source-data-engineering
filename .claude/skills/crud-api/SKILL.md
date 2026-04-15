---
name: crud-api
description: >
  Routes to the correct API CRUD skill based on the resource type.
  Use when managing Claude Code resources via api without specifying which resource.
disable-model-invocation: false
---

# CRUD Router (API)

## Available Resources

- **Skills**: `/crud-api-skills`
- **Plugins**: `/crud-api-plugins`
- **Connectors**: `/crud-api-connectors`
- **MCP Servers**: `/crud-api-mcps`
- **Subagents**: `/crud-api-subagents`
- **Hooks**: `/crud-api-hooks`
- **Sessions**: `/crud-api-sessions`
- **Memories**: `/crud-api-memories`
- **Agent Teams**: `/crud-api-agent-teams`

## How to Choose
- Identify the resource type you want to manage
- Use the corresponding skill above
- Each skill covers Create, Read, Update, and Delete operations

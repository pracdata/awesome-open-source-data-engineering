---
name: crud-graphql
description: >
  Routes to the correct GRAPHQL CRUD skill based on the resource type.
  Use when managing Claude Code resources via graphql without specifying which resource.
disable-model-invocation: false
---

# CRUD Router (GRAPHQL)

## Available Resources

- **Skills**: `/crud-graphql-skills`
- **Plugins**: `/crud-graphql-plugins`
- **Connectors**: `/crud-graphql-connectors`
- **MCP Servers**: `/crud-graphql-mcps`
- **Subagents**: `/crud-graphql-subagents`
- **Hooks**: `/crud-graphql-hooks`
- **Sessions**: `/crud-graphql-sessions`
- **Memories**: `/crud-graphql-memories`
- **Agent Teams**: `/crud-graphql-agent-teams`

## How to Choose
- Identify the resource type you want to manage
- Use the corresponding skill above
- Each skill covers Create, Read, Update, and Delete operations

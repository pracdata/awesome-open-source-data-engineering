---
name: crud-cli
description: >
  Routes to the correct CLI CRUD skill based on the resource type.
  Use when managing Claude Code resources via cli without specifying which resource.
disable-model-invocation: false
---

# CRUD Router (CLI)

## Available Resources

- **Skills**: `/crud-cli-skills`
- **Plugins**: `/crud-cli-plugins`
- **Connectors**: `/crud-cli-connectors`
- **MCP Servers**: `/crud-cli-mcps`
- **Subagents**: `/crud-cli-subagents`
- **Hooks**: `/crud-cli-hooks`
- **Sessions**: `/crud-cli-sessions`
- **Memories**: `/crud-cli-memories`
- **Agent Teams**: `/crud-cli-agent-teams`

## How to Choose
- Identify the resource type you want to manage
- Use the corresponding skill above
- Each skill covers Create, Read, Update, and Delete operations

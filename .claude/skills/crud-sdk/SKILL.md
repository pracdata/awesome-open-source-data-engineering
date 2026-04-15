---
name: crud-sdk
description: >
  Routes to the correct SDK CRUD skill based on the resource type.
  Use when managing Claude Code resources via sdk without specifying which resource.
disable-model-invocation: false
---

# CRUD Router (SDK)

## Available Resources

- **Skills**: `/crud-sdk-skills`
- **Plugins**: `/crud-sdk-plugins`
- **Connectors**: `/crud-sdk-connectors`
- **MCP Servers**: `/crud-sdk-mcps`
- **Subagents**: `/crud-sdk-subagents`
- **Hooks**: `/crud-sdk-hooks`
- **Sessions**: `/crud-sdk-sessions`
- **Memories**: `/crud-sdk-memories`
- **Agent Teams**: `/crud-sdk-agent-teams`

## How to Choose
- Identify the resource type you want to manage
- Use the corresponding skill above
- Each skill covers Create, Read, Update, and Delete operations

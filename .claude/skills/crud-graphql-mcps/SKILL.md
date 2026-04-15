---
name: crud-graphql-mcps
description: >
  CRUD operations for Claude Code MCP Servers via GRAPHQL.
  Use when creating, reading, updating, or deleting mcps using
  the graphql interface.
disable-model-invocation: false
---

# CRUD MCP Servers (GRAPHQL)

## When to use
- Creating new mcps via graphql
- Listing or inspecting existing mcps
- Updating mcps configuration
- Removing mcps

## Create
mutation createMcpServer(input: McpServerInput!) { ... }

## Read
query { mcpServers { name status scope tools { name description } } }

## Update
mutation updateMcpServer(name: String!, input: McpServerInput!) { ... }

## Delete
mutation deleteMcpServer(name: String!) { ... }

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

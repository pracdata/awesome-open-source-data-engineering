---
name: crud-api-mcps
description: >
  CRUD operations for Claude Code MCP Servers via API.
  Use when creating, reading, updating, or deleting mcps using
  the api interface.
disable-model-invocation: false
---

# CRUD MCP Servers (API)

## When to use
- Creating new mcps via api
- Listing or inspecting existing mcps
- Updating mcps configuration
- Removing mcps

## Create
`claude --mcp-config ./mcp.json -p 'task'` or `claude mcp add`

## Read
`claude mcp list`

## Update
Edit mcp.json, re-invoke with `--mcp-config`

## Delete
`claude mcp remove {name}`

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

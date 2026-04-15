---
name: crud-cli-mcps
description: >
  CRUD operations for Claude Code MCP Servers via CLI.
  Use when creating, reading, updating, or deleting mcps using
  the cli interface.
disable-model-invocation: false
---

# CRUD MCP Servers (CLI)

## When to use
- Creating new mcps via cli
- Listing or inspecting existing mcps
- Updating mcps configuration
- Removing mcps

## Create
`claude mcp add {name} -s {scope} -- {command} {args}`
Or create `.mcp.json` with mcpServers config

## Read
`claude mcp list` or `/mcp` to view server status and tools

## Update
Edit `.mcp.json` or re-run `claude mcp add` with updated config

## Delete
`claude mcp remove {name} -s {scope}`

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

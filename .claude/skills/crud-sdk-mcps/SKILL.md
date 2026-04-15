---
name: crud-sdk-mcps
description: >
  CRUD operations for Claude Code MCP Servers via SDK.
  Use when creating, reading, updating, or deleting mcps using
  the sdk interface.
disable-model-invocation: false
---

# CRUD MCP Servers (SDK)

## When to use
- Creating new mcps via sdk
- Listing or inspecting existing mcps
- Updating mcps configuration
- Removing mcps

## Create
Pass `mcp_servers={'name': McpStdioConfig(command='cmd', args=[...])}` to ClaudeAgentOptions

## Read
Call `client.get_mcp_status()` to get McpStatusResponse

## Update
Modify mcp_servers dict and create new query session

## Delete
Remove server from mcp_servers dict

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

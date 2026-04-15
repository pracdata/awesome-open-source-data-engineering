---
name: crud-cli-connectors
description: >
  CRUD operations for Claude Code Connectors via CLI.
  Use when creating, reading, updating, or deleting connectors using
  the cli interface.
disable-model-invocation: false
---

# CRUD Connectors (CLI)

## When to use
- Creating new connectors via cli
- Listing or inspecting existing connectors
- Updating connectors configuration
- Removing connectors

## Create
Configure via claude.ai Settings > Connectors (platform-level feature)

## Read
View connected services at claude.ai/settings/connectors

## Update
Modify connector permissions or scopes via platform UI

## Delete
Disconnect via claude.ai Settings > Connectors

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

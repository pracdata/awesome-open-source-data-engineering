---
name: crud-cli-plugins
description: >
  CRUD operations for Claude Code Plugins via CLI.
  Use when creating, reading, updating, or deleting plugins using
  the cli interface.
disable-model-invocation: false
---

# CRUD Plugins (CLI)

## When to use
- Creating new plugins via cli
- Listing or inspecting existing plugins
- Updating plugins configuration
- Removing plugins

## Create
Create plugin directory with `.claude-plugin/plugin.json` manifest

## Read
`claude plugin list` or `/plugin` to view installed plugins

## Update
Edit `plugin.json`, run `/reload-plugins` to refresh

## Delete
`claude plugin uninstall {name}`

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

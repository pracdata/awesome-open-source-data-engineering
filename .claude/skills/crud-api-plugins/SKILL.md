---
name: crud-api-plugins
description: >
  CRUD operations for Claude Code Plugins via API.
  Use when creating, reading, updating, or deleting plugins using
  the api interface.
disable-model-invocation: false
---

# CRUD Plugins (API)

## When to use
- Creating new plugins via api
- Listing or inspecting existing plugins
- Updating plugins configuration
- Removing plugins

## Create
`claude --plugin-dir ./my-plugin -p 'test plugin'`

## Read
`claude -p 'list plugins'`

## Update
Modify plugin files, re-run with `--plugin-dir`

## Delete
Remove `--plugin-dir` flag from invocation

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

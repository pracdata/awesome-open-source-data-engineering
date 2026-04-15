---
name: crud-cli-hooks
description: >
  CRUD operations for Claude Code Hooks via CLI.
  Use when creating, reading, updating, or deleting hooks using
  the cli interface.
disable-model-invocation: false
---

# CRUD Hooks (CLI)

## When to use
- Creating new hooks via cli
- Listing or inspecting existing hooks
- Updating hooks configuration
- Removing hooks

## Create
Add hook config to `.claude/settings.json` under `hooks` key with event, matcher, and handlers

## Read
`/hooks` to view all configured hooks, or read `.claude/settings.json`

## Update
Edit hooks section in settings.json — modify matcher, handler command, or timeout

## Delete
Remove hook entry from settings.json hooks section

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

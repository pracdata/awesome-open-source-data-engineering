---
name: crud-api-hooks
description: >
  CRUD operations for Claude Code Hooks via API.
  Use when creating, reading, updating, or deleting hooks using
  the api interface.
disable-model-invocation: false
---

# CRUD Hooks (API)

## When to use
- Creating new hooks via api
- Listing or inspecting existing hooks
- Updating hooks configuration
- Removing hooks

## Create
Edit `.claude/settings.json` then run `claude -p` (hooks load from settings)

## Read
Hooks execute during `claude -p` runs; check via `--output-format stream-json`

## Update
Edit settings.json hooks section, re-run

## Delete
Remove from settings.json or set `disableAllHooks: true`

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

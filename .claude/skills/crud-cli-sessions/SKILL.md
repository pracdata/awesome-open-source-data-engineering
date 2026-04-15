---
name: crud-cli-sessions
description: >
  CRUD operations for Claude Code Sessions via CLI.
  Use when creating, reading, updating, or deleting sessions using
  the cli interface.
disable-model-invocation: false
---

# CRUD Sessions (CLI)

## When to use
- Creating new sessions via cli
- Listing or inspecting existing sessions
- Updating sessions configuration
- Removing sessions

## Create
`claude` starts new session, or `claude 'prompt'` with initial message

## Read
`claude -r` to list sessions, `/resume` to browse, `/context` for current

## Update
`/rename <name>` to rename, `/compact` to summarize context

## Delete
Sessions auto-expire; no direct delete CLI command

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

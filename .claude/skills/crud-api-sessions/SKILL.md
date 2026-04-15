---
name: crud-api-sessions
description: >
  CRUD operations for Claude Code Sessions via API.
  Use when creating, reading, updating, or deleting sessions using
  the api interface.
disable-model-invocation: false
---

# CRUD Sessions (API)

## When to use
- Creating new sessions via api
- Listing or inspecting existing sessions
- Updating sessions configuration
- Removing sessions

## Create
`claude -p 'task'` creates ephemeral session, `claude -p --session-id <uuid>` for named

## Read
`claude -p --output-format json` returns session_id in result

## Update
`claude -c -p 'follow-up'` continues session, `--fork-session` for branching

## Delete
Use `--no-session-persistence` to prevent saving

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

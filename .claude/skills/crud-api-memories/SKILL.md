---
name: crud-api-memories
description: >
  CRUD operations for Claude Code Memories via API.
  Use when creating, reading, updating, or deleting memories using
  the api interface.
disable-model-invocation: false
---

# CRUD Memories (API)

## When to use
- Creating new memories via api
- Listing or inspecting existing memories
- Updating memories configuration
- Removing memories

## Create
Memory persists across `claude -c` (continue) sessions automatically

## Read
Auto-memory visible in `~/.claude/auto-memories/`

## Update
Memories update as sessions progress

## Delete
`rm ~/.claude/auto-memories/*` or specific agent memory dirs

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

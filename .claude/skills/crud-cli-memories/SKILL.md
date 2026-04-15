---
name: crud-cli-memories
description: >
  CRUD operations for Claude Code Memories via CLI.
  Use when creating, reading, updating, or deleting memories using
  the cli interface.
disable-model-invocation: false
---

# CRUD Memories (CLI)

## When to use
- Creating new memories via cli
- Listing or inspecting existing memories
- Updating memories configuration
- Removing memories

## Create
Set `memory: user|project|local` in agent frontmatter; MEMORY.md created on first write

## Read
Read `.claude/agent-memory/{name}/MEMORY.md` or `~/.claude/agent-memory/{name}/`

## Update
Agent writes to MEMORY.md automatically; or edit file directly

## Delete
Remove `MEMORY.md` file or entire agent-memory directory

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

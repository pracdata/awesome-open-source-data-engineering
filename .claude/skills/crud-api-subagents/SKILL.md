---
name: crud-api-subagents
description: >
  CRUD operations for Claude Code Subagents via API.
  Use when creating, reading, updating, or deleting subagents using
  the api interface.
disable-model-invocation: false
---

# CRUD Subagents (API)

## When to use
- Creating new subagents via api
- Listing or inspecting existing subagents
- Updating subagents configuration
- Removing subagents

## Create
`claude -p --agents '{"name":{"description":"...","prompt":"..."}}'`

## Read
`claude agents` to list configured agents

## Update
Re-invoke with updated `--agents` JSON

## Delete
Remove from `--agents` JSON or delete `.claude/agents/{name}.md`

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

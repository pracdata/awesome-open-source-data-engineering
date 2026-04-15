---
name: crud-sdk-memories
description: >
  CRUD operations for Claude Code Memories via SDK.
  Use when creating, reading, updating, or deleting memories using
  the sdk interface.
disable-model-invocation: false
---

# CRUD Memories (SDK)

## When to use
- Creating new memories via sdk
- Listing or inspecting existing memories
- Updating memories configuration
- Removing memories

## Create
Set `memory='user'|'project'|'local'` in AgentDefinition (Python only)

## Read
Memory loaded automatically into agent system prompt (first 200 lines/25KB)

## Update
Agent updates MEMORY.md during execution

## Delete
Remove memory files from disk

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

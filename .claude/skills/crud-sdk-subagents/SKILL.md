---
name: crud-sdk-subagents
description: >
  CRUD operations for Claude Code Subagents via SDK.
  Use when creating, reading, updating, or deleting subagents using
  the sdk interface.
disable-model-invocation: false
---

# CRUD Subagents (SDK)

## When to use
- Creating new subagents via sdk
- Listing or inspecting existing subagents
- Updating subagents configuration
- Removing subagents

## Create
Use `AgentDefinition(description=..., prompt=..., tools=[...], model=...)` in agents dict

## Read
Agents listed when Claude calls Agent tool; check via session transcript

## Update
Modify AgentDefinition fields and create new query session

## Delete
Remove agent from agents dict in ClaudeAgentOptions

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

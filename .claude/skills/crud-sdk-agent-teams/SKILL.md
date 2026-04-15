---
name: crud-sdk-agent-teams
description: >
  CRUD operations for Claude Code Agent Teams via SDK.
  Use when creating, reading, updating, or deleting agent-teams using
  the sdk interface.
disable-model-invocation: false
---

# CRUD Agent Teams (SDK)

## When to use
- Creating new agent-teams via sdk
- Listing or inspecting existing agent-teams
- Updating agent-teams configuration
- Removing agent-teams

## Create
Multiple `query()` sessions with shared TaskCreate/SendMessage tools

## Read
Monitor via TaskGet/TaskList tools in agent loop

## Update
TaskUpdate tool to modify task status and dependencies

## Delete
TaskStop tool to terminate running tasks

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

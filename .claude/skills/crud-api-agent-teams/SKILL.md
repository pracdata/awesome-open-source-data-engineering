---
name: crud-api-agent-teams
description: >
  CRUD operations for Claude Code Agent Teams via API.
  Use when creating, reading, updating, or deleting agent-teams using
  the api interface.
disable-model-invocation: false
---

# CRUD Agent Teams (API)

## When to use
- Creating new agent-teams via api
- Listing or inspecting existing agent-teams
- Updating agent-teams configuration
- Removing agent-teams

## Create
Multiple `claude -p` processes with shared task files for coordination

## Read
Check task output files for status

## Update
Use lock files for task claiming (parallel agent pattern)

## Delete
Kill processes to stop team members

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

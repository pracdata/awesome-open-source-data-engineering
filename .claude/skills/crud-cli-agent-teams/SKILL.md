---
name: crud-cli-agent-teams
description: >
  CRUD operations for Claude Code Agent Teams via CLI.
  Use when creating, reading, updating, or deleting agent-teams using
  the cli interface.
disable-model-invocation: false
---

# CRUD Agent Teams (CLI)

## When to use
- Creating new agent-teams via cli
- Listing or inspecting existing agent-teams
- Updating agent-teams configuration
- Removing agent-teams

## Create
Set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, use `--teammate-mode auto|in-process|tmux`

## Read
Team status visible in session; press Ctrl+T for task list

## Update
Use SendMessage tool to communicate between team members

## Delete
Stop teammates via Ctrl+X Ctrl+K or TaskStop tool

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

---
name: crud-cli-subagents
description: >
  CRUD operations for Claude Code Subagents via CLI.
  Use when creating, reading, updating, or deleting subagents using
  the cli interface.
disable-model-invocation: false
---

# CRUD Subagents (CLI)

## When to use
- Creating new subagents via cli
- Listing or inspecting existing subagents
- Updating subagents configuration
- Removing subagents

## Create
Create `.claude/agents/{name}.md` with YAML frontmatter (name, description, tools, model)

## Read
`claude agents` to list all, or read `.claude/agents/*.md` files

## Update
Edit the agent .md file — modify frontmatter fields or system prompt

## Delete
Remove the agent file: `rm .claude/agents/{name}.md`

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

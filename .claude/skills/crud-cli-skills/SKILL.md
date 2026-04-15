---
name: crud-cli-skills
description: >
  CRUD operations for Claude Code Skills via CLI.
  Use when creating, reading, updating, or deleting skills using
  the cli interface.
disable-model-invocation: false
---

# CRUD Skills (CLI)

## When to use
- Creating new skills via cli
- Listing or inspecting existing skills
- Updating skills configuration
- Removing skills

## Create
Create `.claude/skills/{name}/SKILL.md` with YAML frontmatter (name, description)

## Read
List skills with `/help` or inspect `.claude/skills/*/SKILL.md` files

## Update
Edit the SKILL.md file directly — update frontmatter or instructions

## Delete
Remove the skill directory: `rm -r .claude/skills/{name}/`

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

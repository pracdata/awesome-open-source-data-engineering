---
name: crud-api-skills
description: >
  CRUD operations for Claude Code Skills via API.
  Use when creating, reading, updating, or deleting skills using
  the api interface.
disable-model-invocation: false
---

# CRUD Skills (API)

## When to use
- Creating new skills via api
- Listing or inspecting existing skills
- Updating skills configuration
- Removing skills

## Create
Write SKILL.md to filesystem via `claude -p 'create skill named X'`

## Read
`claude -p --disable-slash-commands 'list skills'` or `ls .claude/skills/`

## Update
`claude -p 'update the skill named X to include Y'`

## Delete
`rm -r .claude/skills/{name}/`

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

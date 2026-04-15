---
name: crud-sdk-skills
description: >
  CRUD operations for Claude Code Skills via SDK.
  Use when creating, reading, updating, or deleting skills using
  the sdk interface.
disable-model-invocation: false
---

# CRUD Skills (SDK)

## When to use
- Creating new skills via sdk
- Listing or inspecting existing skills
- Updating skills configuration
- Removing skills

## Create
Add skill files to project, load via `setting_sources=['project']` in ClaudeAgentOptions

## Read
Skills are auto-discovered from `.claude/skills/` when settingSources includes 'project'

## Update
Modify SKILL.md files, call `/reload-plugins` to refresh

## Delete
Remove skill directory, restart session to unload

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

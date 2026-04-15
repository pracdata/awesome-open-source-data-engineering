---
name: crud-graphql-skills
description: >
  CRUD operations for Claude Code Skills via GRAPHQL.
  Use when creating, reading, updating, or deleting skills using
  the graphql interface.
disable-model-invocation: false
---

# CRUD Skills (GRAPHQL)

## When to use
- Creating new skills via graphql
- Listing or inspecting existing skills
- Updating skills configuration
- Removing skills

## Create
mutation createSkill(input: SkillInput!) { createSkill(input: $input) { name } }

## Read
query { skills { name description disableModelInvocation } }

## Update
mutation updateSkill(name: String!, input: SkillInput!) { updateSkill(...) { name } }

## Delete
mutation deleteSkill(name: String!) { deleteSkill(name: $name) }

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

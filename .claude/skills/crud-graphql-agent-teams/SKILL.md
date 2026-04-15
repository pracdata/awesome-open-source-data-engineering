---
name: crud-graphql-agent-teams
description: >
  CRUD operations for Claude Code Agent Teams via GRAPHQL.
  Use when creating, reading, updating, or deleting agent-teams using
  the graphql interface.
disable-model-invocation: false
---

# CRUD Agent Teams (GRAPHQL)

## When to use
- Creating new agent-teams via graphql
- Listing or inspecting existing agent-teams
- Updating agent-teams configuration
- Removing agent-teams

## Create
mutation createTeam(input: TeamInput!) { ... }

## Read
query { teams { name members { name status } tasks { subject status } } }

## Update
mutation updateTeam(name: String!, input: TeamInput!) { ... }

## Delete
mutation deleteTeam(name: String!) { ... }

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

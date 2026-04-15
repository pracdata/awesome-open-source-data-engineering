---
name: crud-graphql-subagents
description: >
  CRUD operations for Claude Code Subagents via GRAPHQL.
  Use when creating, reading, updating, or deleting subagents using
  the graphql interface.
disable-model-invocation: false
---

# CRUD Subagents (GRAPHQL)

## When to use
- Creating new subagents via graphql
- Listing or inspecting existing subagents
- Updating subagents configuration
- Removing subagents

## Create
mutation createAgent(input: AgentInput!) { createAgent(input: $input) { name model } }

## Read
query { agents { name description tools model skills memory } }

## Update
mutation updateAgent(name: String!, input: AgentInput!) { ... }

## Delete
mutation deleteAgent(name: String!) { deleteAgent(name: $name) }

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

---
name: crud-graphql-sessions
description: >
  CRUD operations for Claude Code Sessions via GRAPHQL.
  Use when creating, reading, updating, or deleting sessions using
  the graphql interface.
disable-model-invocation: false
---

# CRUD Sessions (GRAPHQL)

## When to use
- Creating new sessions via graphql
- Listing or inspecting existing sessions
- Updating sessions configuration
- Removing sessions

## Create
mutation createSession(input: SessionInput!) { ... }

## Read
query { sessions { id name status model createdAt } }

## Update
mutation updateSession(id: String!, input: SessionInput!) { ... }

## Delete
mutation deleteSession(id: String!) { ... }

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

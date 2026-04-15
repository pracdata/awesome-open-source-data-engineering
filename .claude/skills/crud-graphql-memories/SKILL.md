---
name: crud-graphql-memories
description: >
  CRUD operations for Claude Code Memories via GRAPHQL.
  Use when creating, reading, updating, or deleting memories using
  the graphql interface.
disable-model-invocation: false
---

# CRUD Memories (GRAPHQL)

## When to use
- Creating new memories via graphql
- Listing or inspecting existing memories
- Updating memories configuration
- Removing memories

## Create
mutation createMemory(input: MemoryInput!) { ... }

## Read
query { memories { scope agentName content path } }

## Update
mutation updateMemory(scope: String!, agentName: String!, content: String!) { ... }

## Delete
mutation deleteMemory(scope: String!, agentName: String!) { ... }

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

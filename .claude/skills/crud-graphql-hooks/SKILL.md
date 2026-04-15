---
name: crud-graphql-hooks
description: >
  CRUD operations for Claude Code Hooks via GRAPHQL.
  Use when creating, reading, updating, or deleting hooks using
  the graphql interface.
disable-model-invocation: false
---

# CRUD Hooks (GRAPHQL)

## When to use
- Creating new hooks via graphql
- Listing or inspecting existing hooks
- Updating hooks configuration
- Removing hooks

## Create
mutation createHook(input: HookInput!) { createHook(input: $input) { event matcher } }

## Read
query { hooks { event matcher handlers { type command timeout } } }

## Update
mutation updateHook(event: String!, input: HookInput!) { ... }

## Delete
mutation deleteHook(event: String!, matcher: String!) { ... }

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

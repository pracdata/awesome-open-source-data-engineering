---
name: crud-graphql-plugins
description: >
  CRUD operations for Claude Code Plugins via GRAPHQL.
  Use when creating, reading, updating, or deleting plugins using
  the graphql interface.
disable-model-invocation: false
---

# CRUD Plugins (GRAPHQL)

## When to use
- Creating new plugins via graphql
- Listing or inspecting existing plugins
- Updating plugins configuration
- Removing plugins

## Create
mutation createPlugin(input: PluginInput!) { createPlugin(input: $input) { name version } }

## Read
query { plugins { name version description author { name } skills { name } } }

## Update
mutation updatePlugin(name: String!, input: PluginInput!) { ... }

## Delete
mutation deletePlugin(name: String!) { deletePlugin(name: $name) }

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

---
name: crud-graphql-connectors
description: >
  CRUD operations for Claude Code Connectors via GRAPHQL.
  Use when creating, reading, updating, or deleting connectors using
  the graphql interface.
disable-model-invocation: false
---

# CRUD Connectors (GRAPHQL)

## When to use
- Creating new connectors via graphql
- Listing or inspecting existing connectors
- Updating connectors configuration
- Removing connectors

## Create
mutation createConnector(input: ConnectorInput!) { ... }

## Read
query { connectors { name type status scopes } }

## Update
mutation updateConnector(name: String!, input: ConnectorInput!) { ... }

## Delete
mutation deleteConnector(name: String!) { ... }

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

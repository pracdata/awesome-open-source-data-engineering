---
name: crud-api-connectors
description: >
  CRUD operations for Claude Code Connectors via API.
  Use when creating, reading, updating, or deleting connectors using
  the api interface.
disable-model-invocation: false
---

# CRUD Connectors (API)

## When to use
- Creating new connectors via api
- Listing or inspecting existing connectors
- Updating connectors configuration
- Removing connectors

## Create
REST API: POST to platform connector endpoints

## Read
REST API: GET connector status and configuration

## Update
REST API: PATCH connector configuration

## Delete
REST API: DELETE connector

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

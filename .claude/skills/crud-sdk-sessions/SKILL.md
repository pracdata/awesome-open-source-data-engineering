---
name: crud-sdk-sessions
description: >
  CRUD operations for Claude Code Sessions via SDK.
  Use when creating, reading, updating, or deleting sessions using
  the sdk interface.
disable-model-invocation: false
---

# CRUD Sessions (SDK)

## When to use
- Creating new sessions via sdk
- Listing or inspecting existing sessions
- Updating sessions configuration
- Removing sessions

## Create
Call `query(prompt='...')` to create new session

## Read
`list_sessions()` returns SDKSessionInfo list, `get_session_messages()` for transcripts

## Update
`rename_session(session_id, title)`, `tag_session(session_id, tag)`

## Delete
Sessions managed by retention policy; no direct delete API

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

---
name: crud-sdk-hooks
description: >
  CRUD operations for Claude Code Hooks via SDK.
  Use when creating, reading, updating, or deleting hooks using
  the sdk interface.
disable-model-invocation: false
---

# CRUD Hooks (SDK)

## When to use
- Creating new hooks via sdk
- Listing or inspecting existing hooks
- Updating hooks configuration
- Removing hooks

## Create
Pass `hooks={HookEvent: [HookMatcher(...)]}` to ClaudeAgentOptions

## Read
Hooks fire automatically; check via PostToolUse/PreToolUse output

## Update
Modify hooks dict and create new query session

## Delete
Remove hook from hooks dict

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

---
name: crud-sdk-plugins
description: >
  CRUD operations for Claude Code Plugins via SDK.
  Use when creating, reading, updating, or deleting plugins using
  the sdk interface.
disable-model-invocation: false
---

# CRUD Plugins (SDK)

## When to use
- Creating new plugins via sdk
- Listing or inspecting existing plugins
- Updating plugins configuration
- Removing plugins

## Create
Use `SdkPluginConfig(type='local', path='./plugin-dir')` in ClaudeAgentOptions.plugins

## Read
Plugins listed in session init data via SystemMessage

## Update
Modify plugin files, restart session

## Delete
Remove from plugins list in ClaudeAgentOptions

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed

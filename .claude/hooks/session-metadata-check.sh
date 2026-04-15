#!/bin/bash
# PostToolUse hook: ensure generated session metadata.json has trailing newline
# Triggered on Write tool calls that target sessions/

if [ -n "$FILE_PATH" ] && [[ "$FILE_PATH" == */sessions/session_*/metadata.json ]]; then
    # Ensure trailing newline (pre-commit end-of-file-fixer compatibility)
    if [ -f "$FILE_PATH" ] && [ -s "$FILE_PATH" ]; then
        tail -c1 "$FILE_PATH" | read -r _ || echo "" >> "$FILE_PATH"
    fi
fi

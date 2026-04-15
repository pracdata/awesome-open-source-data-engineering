#!/bin/bash
# PostToolUse hook: log tool response sizes for context budget awareness
# Writes to .claude/hooks/tool-usage.log

LOG_FILE="$CLAUDE_PROJECT_DIR/.claude/hooks/tool-usage.log"

if [ -n "$TOOL_NAME" ] && [ -n "$TOOL_OUTPUT" ]; then
    CHARS=${#TOOL_OUTPUT}
    APPROX_TOKENS=$((CHARS / 4))
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $TOOL_NAME chars=$CHARS approx_tokens=$APPROX_TOKENS" >> "$LOG_FILE"

    if [ "$APPROX_TOKENS" -gt 5000 ]; then
        echo "WARNING: $TOOL_NAME returned ~$APPROX_TOKENS tokens. Consider filtering output."
    fi
fi

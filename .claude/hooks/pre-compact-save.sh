#!/bin/bash
# PreCompact hook: append compaction marker to active session scratchpad
# This preserves a breadcrumb trail when context is compacted mid-session.
#
# Environment variables available from Claude Code:
#   $SESSION_ID       — current session UUID
#   $TRANSCRIPT_PATH  — path to transcript JSONL
#   $CWD              — working directory

SESSIONS_DIR="$CLAUDE_PROJECT_DIR/sessions"

# Find the most recently modified session directory
LATEST_SESSION=$(find "$SESSIONS_DIR" -maxdepth 1 -name 'session_*' -type d -printf '%T@ %p\n' 2>/dev/null \
    | sort -rn | head -1 | cut -d' ' -f2-)

if [ -n "$LATEST_SESSION" ] && [ -f "$LATEST_SESSION/scratchpad.md" ]; then
    TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M:%S UTC')
    echo "" >> "$LATEST_SESSION/scratchpad.md"
    echo "### [$TIMESTAMP] Context Compacted" >> "$LATEST_SESSION/scratchpad.md"
    echo "" >> "$LATEST_SESSION/scratchpad.md"
    echo "Session context was compacted. Prior work is summarized above." >> "$LATEST_SESSION/scratchpad.md"
fi

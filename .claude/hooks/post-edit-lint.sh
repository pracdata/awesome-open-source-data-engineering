#!/bin/bash
# PostToolUse hook for Edit/Write: run ruff on changed Python files

if [ -n "$FILE_PATH" ] && [[ "$FILE_PATH" == *.py ]]; then
    ruff check --fix "$FILE_PATH" 2>/dev/null || true
fi

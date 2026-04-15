#!/bin/bash
# SessionStart hook — install dependencies via uv + npm
# Runs on session start and resume. install-dev includes:
#   - Core: scrapy, orjson, rbloom, colorlog
#   - Models: pydantic
#   - Warehouse (CPU): fastembed, onnxruntime, psycopg, sqlmodel, networkx, httpx, mempalace
#   - Dev: ruff, mypy, pytest, pytest-benchmark, pre-commit
# Node.js: @cubejs-client/core, @neondatabase/serverless, zod, typescript

set -e
cd "$CLAUDE_PROJECT_DIR" || exit 1

# ── Python deps (CPU-optimized, no torch) ──────────────────────
if command -v uv &>/dev/null; then
    uv pip install --system -e ".[dev,models,warehouse]" --quiet 2>/dev/null
else
    pip install -e ".[dev,models,warehouse]" --quiet 2>/dev/null
fi

# ── Node.js deps (Cube.js, Neon, Zod, GraphQL, MCP, Claude SDK) ──
if command -v npm &>/dev/null && [ -f package.json ]; then
    npm install --prefer-offline --no-audit 2>/dev/null
fi

# ── MCP + Claude Agent SDKs + TikTok Business API ────────────
if command -v uv &>/dev/null; then
    uv pip install --system -e ".[mcp,social]" --quiet 2>/dev/null || true
elif command -v pip &>/dev/null; then
    pip install -e ".[mcp,social]" --quiet 2>/dev/null || true
fi

# ── Java MCP SDK (optional, only if Gradle available) ────────
GRADLE_CMD="${GRADLE_CMD:-$(command -v gradle 2>/dev/null || echo /opt/gradle/bin/gradle)}"
if [ -x "$GRADLE_CMD" ] && [ -f java/build.gradle.kts ]; then
    (cd java && "$GRADLE_CMD" build --no-daemon -x test --quiet 2>/dev/null) || true
fi

# ── Pre-commit hooks ──────────────────────────────────────────
if [ -f .pre-commit-config.yaml ] && command -v pre-commit &>/dev/null; then
    pre-commit install --install-hooks --quiet 2>/dev/null
    pre-commit install --hook-type pre-push --quiet 2>/dev/null
fi

exit 0

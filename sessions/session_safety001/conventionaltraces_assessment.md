---
title: "ConventionalTraces: Honest Assessment and Design Sketch"
date: "2026-04-15"
session_id: "safety001"
surface: "Web"
model: "claude-opus-4-6"
tags: ["conventional-commits", "conventional-traces", "agent-sdk", "research"]
---

# ConventionalTraces: Honest Assessment

## The Honest Answer

**Yes, but only if scoped correctly.** Here's my reasoning:

### What actually happened in this session

We made 8 commits across 12+ files. The *session trace* I wrote manually
captures something no tool currently captures automatically:

1. **User intent** — what the human actually wanted (not what the diff shows)
2. **Semantic mapping** — which user prompt produced which code change
3. **Decision rationale** — why we chose `as` type assertions vs generics,
   why we excluded generation from coverage instead of writing tests for it
4. **Cross-session continuity** — this session was compacted and resumed,
   and the trace survived

Conventional commits capture `feat(sessions): add surface lookup table`.
That's the *what*. ConventionalTraces would capture *why that feature exists,
what user prompt triggered it, what alternatives were considered, and how to
verify it works*.

### The real gap

| Layer | Tool | What it captures | What it misses |
|-------|------|-----------------|----------------|
| Commit | conventional-commits | type, scope, description | user intent, alternatives considered |
| PR | GitHub PR template | summary, test plan | multi-session continuity, decision rationale |
| Session | Claude Code transcript | full conversation | structured extraction, cross-session linking |
| Circuit | circuit-tracer | model internals | developer-facing session provenance |
| **Trace** | **nothing exists** | - | **the full chain: prompt -> intent -> decision -> code -> test** |

The gap is real. The research-agent demo generates structured tool call logs
with `parent_tool_use_id` linking — that's the right primitive, but it doesn't
produce a *reusable human-readable trace format*.

### Why it would save alignment engineers time

Alignment researchers at Anthropic use Claude Code for:
- Iterating on eval frameworks (bloom, petri)
- Analyzing model behavior (persona_vectors, circuit-tracer)
- Multi-session research that spans days

Their pain: when they resume a session or hand off work, the context of *why*
decisions were made is lost. Conventional commits don't capture "I tried
approach X first, it failed because Y, so I pivoted to Z." ConventionalTraces
would.

### What would NOT work

- **A full spec like conventional-commits.** Too heavy. Sessions are messier
  than commits — they have dead ends, tangents, compactions. Forcing structure
  on every turn would slow people down.
- **Automatic generation from transcript.** The raw transcript is too noisy.
  The value is in the *curated* trace — what mattered, what didn't.
- **A standalone CLI tool.** It needs to be a Claude Code hook/plugin, not
  a separate workflow step people forget to run.

### What WOULD work

**A Claude Code hook that triggers on commit and produces a structured trace
entry.** Here's the design:

```
conventionaltraces/
  spec/
    TRACE_SPEC.md          — the format specification
  parser/
    trace_parser.py        — parse trace entries (like @conventional-commits/parser)
    trace_parser.ts        — TypeScript version
  hooks/
    post-commit-trace.sh   — Claude Code PostToolUse hook for Bash(git commit)
  sdk/
    trace_session.py       — Agent SDK integration (Python)
    trace_session.ts       — Agent SDK integration (TypeScript v2)
  templates/
    trace_entry.md         — single commit trace template
    session_trace.md       — multi-commit session trace template
```

### The Trace Format (v0.1 sketch)

```yaml
trace: "1.0"
session_id: "01ND5GMDiyDk96XCE3zMDw4B"
surface: "web"
model: "claude-opus-4-6"

entries:
  - commit: "99dd2fb"
    type: "feat"
    scope: "models"
    prompt: "Audit this repo as it's not in sync with changelog.md"
    intent: "Parse changelog bullets for 2.1.105-2.1.107, apply model changes"
    decisions:
      - considered: "Add all changelog items as code"
        chosen: "Only items with data model impact; skip UI-only bullets"
        reason: "This repo models data types, not UI behavior"
    files: ["settings.py", "hooks.py", "plugins.py", "skills.py"]
    tests: ["test_pre_compact_input", "test_plugin_manifest_with_monitors"]
    verified: true

  - commit: "78e930b"
    type: "fix"
    scope: "ci"
    prompt: "(CI webhook) Pre-commit Checks failed"
    intent: "Fix 4 independent CI root causes"
    decisions:
      - considered: "Write proper generic types for TS adapters"
        chosen: "Use `as` type assertions"
        reason: "Social adapters are thin wrappers; full generics add complexity for no safety gain"
      - considered: "Write tests for generation module in CI"
        chosen: "pytest.importorskip to skip when deps missing"
        reason: "CI installs .[dev,models,warehouse] not .[generation]; adding generation deps would bloat CI"
    files: ["tiktok.ts", "youtube.ts", "instagram.ts", "graphql-client.ts", "pyproject.toml"]
    tests: ["npx tsc --noEmit", "mypy --strict", "pre-commit run --all-files"]
    verified: true
```

### Integration Points

1. **PostToolUse hook (Bash matcher for `git commit`)**: Auto-generates trace
   entry from the commit diff + recent conversation context
2. **PreCompact hook**: Appends compaction marker to trace (already built)
3. **Agent SDK hooks**: `pre_tool_use` / `post_tool_use` capture tool call
   graph with `parent_tool_use_id` (research-agent pattern)
4. **CI integration**: Validate trace entries exist for each commit in PR
5. **Session resume**: Load trace on `-c` / `-r` to restore decision context

### Comparison to Existing Tools

| Tool | Scope | Format | Enforcement | Cross-session |
|------|-------|--------|-------------|---------------|
| conventional-commits | commit msg | text | commitlint | no |
| GitHub PR template | PR body | markdown | CI check | no |
| circuit-tracer | model internals | attribution graph | n/a | n/a |
| research-agent logs | tool calls | JSON | hooks | no |
| **conventionaltraces** | **session->commit chain** | **YAML+markdown** | **hooks+CI** | **yes** |

### Verdict

**Build it, but as a Claude Code plugin/hook — not a standalone spec.**

The conventional commits spec succeeded because:
1. It's dead simple (one line: `type(scope): description`)
2. It's enforceable (commitlint)
3. It enables automation (changelogs, semver)

ConventionalTraces should follow the same pattern:
1. Simple format (YAML trace entry per commit)
2. Enforceable (PostToolUse hook auto-generates, CI validates)
3. Enables automation (session summaries, handoff docs, audit trails)

The name "ConventionalTraces" is better than "ConventionalSessions" because:
- "Session" implies a single conversation; traces span sessions
- "Trace" aligns with circuit-tracer and attribution graph terminology
- "Trace" implies provenance — where did this code come from and why

### Concrete Next Steps for a Future PR

1. Create `conventionaltraces/` package in this repo as proof-of-concept
2. Implement PostToolUse hook that auto-generates trace YAML on `git commit`
3. Implement parser (Python + TypeScript) for the trace format
4. Add CI check that validates trace entries exist for PR commits
5. Publish as Claude Code plugin (anthropics/skills marketplace)
6. Write spec doc modeled on conventionalcommits.org

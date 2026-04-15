## Model Tier Directive

Only Opus 4.6 performs codegen (Edit, Write, NotebookEdit).
Subagents that only advise, analyze, or coordinate MUST use `model: sonnet` or `model: haiku`.

### Tier Assignment Rules

| Task Type | Model | Tools Allowed |
|-----------|-------|---------------|
| Codegen (edit files, write code) | opus | All |
| Code review, architecture advice | sonnet | Read, Grep, Glob, Bash |
| Pattern matching, quick lookups | haiku | Read, Grep, Glob |
| Exploration, search | sonnet | Read, Grep, Glob, Bash |

### Subagent Design

- Advisory personas (amodei, bezos, shannon, etc.) → `model: sonnet`
- Code reviewers (crawl-reviewer, page-analyzer) → `model: sonnet`
- Coordinators that dispatch to other agents → `model: sonnet`
- Only the main conversation or explicitly codegen-flagged agents use opus

### Context Budget

- Use TodoWrite for multi-step tasks (3+ steps)
- Subagents get clean context — use for investigation, return summaries under 2000 tokens
- Prefer skills over CLAUDE.md for reference material (skills cost nothing until invoked)
- CLAUDE.md costs every request — keep under 200 lines

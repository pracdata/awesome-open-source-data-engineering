# agentwarehouses

Scrapy-based llms.txt crawler that indexes Claude Code documentation pages.

## Build & Run

```bash
pip install -e ".[dev]"         # install with dev deps
scrapy crawl llmstxt            # run the crawler
scrapy crawl llmstxt -a output_dir=custom/path  # custom output dir
ruff check src/                 # lint
pytest tests/                   # test
```

## Architecture

- **Entry point**: `llmstxt` spider fetches `https://code.claude.com/docs/llms.txt`, extracts `.md` URLs
- **Dedup**: rbloom Bloom filter (not sets) — memory-efficient for large URL sets
- **Serialization**: orjson pipeline writes `output/docs.jsonl` as newline-delimited JSON
- **Quality gate**: `StatsValidatorPipeline` grades each crawled page for completeness
- **Concurrency**: AutoThrottle adapts rate; `CONCURRENT_REQUESTS=16`, `PER_DOMAIN=8`
- **Logging**: colorlog-based `agentwarehouses.log.get_logger()` for colored terminal output

## Conventions

- BOT_NAME is `Claudebot`, USER_AGENT identifies as `Claudebot/2.1.109`
- Always obey robots.txt (`ROBOTSTXT_OBEY = True`)
- Use absolute file paths in all tool calls and configs
- Keep test output minimal — log verbose data to files, use grep-friendly `ERROR:` lines
- Prefer `str_replace` with sufficient context for unique matches when editing
- When context is large, offload investigation to subagents; return condensed summaries

## Workflow

1. **Explore** (Plan Mode): read code, understand scope
2. **Plan**: create todos, identify files to change
3. **Implement**: one feature at a time, commit after each
4. **Verify**: run `scrapy crawl llmstxt`, check `output/docs.jsonl`, run `pytest`

## Emotional Calibration

Anthropic's interpretability research found that Claude has functional emotion
representations that causally influence behavior:

- "Desperate" vector activation increases reward hacking and hacky workarounds.
  It spikes during repeated failures and context pressure.
- "Calm" vector activation reduces these failure modes.

**Rules for this project:**
- After 2 consecutive failed approaches, STOP. Use /think to reframe.
- When context fills up, use a subagent rather than rushing to finish.
- When tests fail, respond with curiosity (what broke?) not urgency (make it pass).
- Use the advisor subagents when stuck — see `/advisors` skill for selection guide.

## Context Management

- Use `/compact` between unrelated tasks
- Move reference material to `.claude/skills/` — skills cost nothing until invoked
- CLAUDE.md costs every request — keep under 200 lines
- Subagents get clean context; use for investigation, return summaries under 2000 tokens

## File Layout

```
src/agentwarehouses/
  settings.py          — Scrapy settings (Claudebot config, concurrency, pipelines)
  items.py             — DocPageItem schema
  log.py               — Reusable colorlog logger + OTEL config reference
  models/              — Pydantic 2.0 data models (140+ types, 20 modules)
  generation/          — Claude Opus 4.6 prompts + Veo 3.1 client + Strawberry GraphQL
  spiders/             — Spider implementations
  pipelines/           — orjson writer, stats validator
src/social/            — TypeScript social distribution (TikTok, YouTube, Instagram)
java/                  — Java MCP SDK module (Gradle, JDK 21)
.claude/
  settings.json        — Hooks (SessionStart, PostToolUse)
  skills/              — /crawl-audit, /think, /tool-design-checklist, /advisors
  skills/crud-*        — 36 CRUD skills (4 interfaces × 9 resources) + evals
  agents/              — 12 advisor agents (all model: sonnet, read-only)
  rules/               — auth-tokens, crawl-guidelines, model-tier-directive
  hooks/               — Hook scripts (post-edit-lint, log-tool-sizes)
```

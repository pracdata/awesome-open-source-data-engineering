---
name: tool-design-checklist
description: Checklist for reviewing Scrapy spider, pipeline, and MCP tool quality
disable-model-invocation: false
---
# Tool Design Checklist

## When to use
When creating or reviewing spiders, pipelines, items, or MCP tool integrations.
Based on patterns from "Writing effective tools for agents" and "Advanced tool use."

## Spider checklist
- [ ] `name` is lowercase, descriptive, unique
- [ ] `allowed_domains` is set (prevents crawling off-site)
- [ ] `start_urls` uses absolute URLs
- [ ] URL deduplication uses rbloom (not sets) for memory efficiency
- [ ] `custom_settings` overrides only what's needed
- [ ] Error handling: log and skip bad responses, don't crash
- [ ] Structured extraction: regex patterns handle missing matches gracefully

## Pipeline checklist
- [ ] `open_spider` creates output directories with `exist_ok=True`
- [ ] `close_spider` flushes and closes all file handles
- [ ] `process_item` returns the item (enables pipeline chaining)
- [ ] Uses orjson for serialization (not stdlib json)
- [ ] Output format is token-efficient (JSONL, not pretty-printed)
- [ ] Logs byte count on close for quick size auditing

## Item checklist
- [ ] Fields have clear, semantic names (not `data`, `info`, `content`)
- [ ] Required fields are documented
- [ ] `crawled_at` uses ISO 8601 UTC timestamps
- [ ] No UUIDs where URLs serve as natural keys

## Tool description quality (for MCP tools)
- [ ] Description reads like instructions to a new hire
- [ ] Parameter names are unambiguous (`page_url` not `url`)
- [ ] Return values are token-efficient (filter before returning)
- [ ] Error messages are actionable ("URL returned 404, check if page was moved")
- [ ] Pagination/filtering available for large result sets

## Context efficiency
- [ ] Tool results fit comfortably in context (under 2000 tokens ideally)
- [ ] Large data logged to files, summaries returned inline
- [ ] Consolidate multi-step operations where possible

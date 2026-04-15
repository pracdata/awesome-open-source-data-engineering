---
name: think
description: Structured thinking tool for complex multi-step decisions in crawler development
disable-model-invocation: false
---
# Think

## When to use
Before taking action on complex decisions — especially after receiving tool results
that require analysis before the next step. Creates dedicated space for reasoning
during multi-step tool chains.

## Instructions

Pause and reason through the problem using this structure:

1. **List applicable rules**: What project conventions, Scrapy settings, or constraints apply?
2. **Check collected information**: What have I learned from tool results so far?
3. **Verify compliance**: Does my planned action follow CLAUDE.md conventions and robots.txt?
4. **Consider alternatives**: Are there simpler approaches? (Simplest solution first principle)
5. **Predict side effects**: Will this change break existing spiders, pipelines, or tests?
6. **State conclusion**: What specific action will I take and why?

## Examples

### Example: Adding a new spider
```
Think: I need to add a spider for a new documentation source.
1. Rules: BOT_NAME=Claudebot, ROBOTSTXT_OBEY=True, use rbloom for dedup
2. Info: The new source has ~200 pages, structured as a sitemap
3. Compliance: Must use Claudebot UA, must check robots.txt first
4. Alternatives: Could extend existing spider vs new spider — new is cleaner
5. Side effects: Need to register in SPIDER_MODULES, no pipeline changes needed
6. Action: Create new spider in spiders/, reuse Bloom filter pattern, test with scrapy crawl
```

### Example: Debugging empty body_markdown
```
Think: Pages are returning empty body_markdown.
1. Rules: body_markdown must be non-empty per crawl-audit checks
2. Info: response.text returns HTML, not markdown — the server is serving HTML for .md URLs
3. Compliance: Still obeying robots.txt, no issue there
4. Alternatives: Use response.css/xpath to extract, or adjust Accept headers
5. Side effects: Changing Accept header might affect other requests
6. Action: Add Accept: text/markdown header to doc page requests only
```

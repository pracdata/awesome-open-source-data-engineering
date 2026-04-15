# agentwarehouses

Scrapy-based documentation crawler and Kimball dimensional warehouse for agent data engineering.

Crawls llms.txt, sitemaps, and documentation pages from Claude Code, Neon Postgres,
and Anthropic — deduplicates with rbloom Bloom filters, stores as JSONL, and models
the data in a Kimball star schema ready for Neon Postgres 18 with pgvector embeddings.

## Quick Start

```bash
make install-dev    # CPU-optimized: fastembed/ONNX, no torch (~130 MB)
make test           # 95 tests, parallel
make crawl          # Crawl code.claude.com/docs/llms.txt
make crawl-neon     # Crawl neon.com (llms.txt + sitemap, rbloom dedup)
```

## Install Tiers

| Command | What | Size |
|---|---|---|
| `make install` | Core crawl (scrapy, orjson, rbloom) | ~30 MB |
| `make install-dev` | CPU warehouse + test tools (fastembed/ONNX) | ~130 MB |
| `make install-gpu` | Full GPU (torch + sentence-transformers + dspy) | ~2.5 GB |
| `make install-node` | Cube.js, Neon serverless driver, Zod | ~15 MB |
| `make install-all` | Python CPU + Node.js | ~145 MB |

## Architecture

```
Source Layer (llms.txt, sitemaps, changelogs)
       │
  Scrapy Layer (llmstxt_spider, neon_docs_spider, rbloom dedup)
       │
  Pipeline Layer (orjson writer, stats validator, content-hash skip)
       │
  Neon Postgres 18 (star schema, pgvector, pg_trgm, bloom indexes)
       │
  Retrieval Layer (hybrid BM25 + vector search, RRF fusion)
       │
  Agent Harness (Claude Code dispatch tiers, subagents, telemetry)
```

## Crawl Targets

| Target | Command | Pages |
|---|---|---|
| Claude Code docs | `make crawl` | 117 |
| Neon docs (all sources) | `make crawl-neon-all` | 2,014 |
| Neon docs (llms + sitemap) | `make crawl-neon` | ~1,100 |

## Schema (Kimball Star Schema)

28 SQL files in `schema/` using the triple-dash format (Cube.js YAML + Postgres DDL):

```bash
make migrate-kimball   # requires DATABASE_URL
```

**Dimensions**: dim_date, dim_source (SCD2), dim_entity_type, dim_content_type, dim_plugin, dim_persona

**Facts**: fact_doc_crawls, fact_entity_extractions, fact_searches, fact_social_posts, fact_social_metrics, fact_social_ads

**Operational**: telemetry_spans, palace_drawers (HNSW+bloom+trgm), customer_insights

**Aggregates**: agg_monthly_source, agg_weekly_persona, wbr_reports

## File Layout

```
src/agentwarehouses/
  settings.py          — Scrapy settings (Claudebot config, concurrency)
  items.py             — DocPageItem schema
  log.py               — Colorlog logger + OTEL config
  models/              — Pydantic 2.0 data models (125 types, 19 modules)
  spiders/             — llmstxt_spider, neon_docs_spider
  pipelines/           — orjson writer, stats validator
schema/                — 28 Kimball DDL files + migration orchestrator
scripts/               — neon_repo_inventory, generate_crud_skills
tests/                 — 95 tests (unit, integration, models, evals)
.claude/
  agents/              — 10 persona subagents
  skills/              — 48 skills (CRUD + specialized)
  rules/               — Scoped project rules
```

## Key Dependencies

**Python (CPU tier)**: scrapy, orjson, rbloom, fastembed, onnxruntime, psycopg, sqlmodel, networkx, httpx, mempalace

**Node.js**: @cubejs-client/core, @neondatabase/serverless, zod, typescript

## License

MIT

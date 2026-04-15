.DEFAULT_GOAL := help
SHELL := /bin/bash
PYTHON := python
UV := uv
GRADLE := /opt/gradle/bin/gradle
NPROC := $(shell nproc 2>/dev/null || echo 4)

# ──────────────────────────────────────────────
# Install — tiered for CPU/GPU/dev profiles
# ──────────────────────────────────────────────
# Tiers:
#   install       → core crawl deps only (scrapy, orjson, rbloom)
#   install-dev   → core + warehouse-CPU + test tooling (fastembed/ONNX, no torch)
#   install-gpu   → full torch + sentence-transformers + dspy (CUDA workloads)
#   install-node  → Node.js deps (Cube.js, Neon, Zod)
#   install-all   → everything (Python CPU + Node.js)
#
# CPU profile uses fastembed (ONNX Runtime, ~50 MB) instead of
# sentence-transformers + torch (~2 GB). Same all-MiniLM-L6-v2 model.
# See: https://github.com/qdrant/fastembed

.PHONY: install
install: ## Install core crawl deps (scrapy, orjson, rbloom)
	$(UV) pip install --system -e ".[models]"

.PHONY: install-dev
install-dev: ## Install CPU warehouse + dev tooling (fast, no torch)
	$(UV) pip install --system -e ".[dev,models,warehouse]"
	@command -v npm >/dev/null && npm install --prefer-offline --no-audit || true

.PHONY: install-gpu
install-gpu: ## Install full GPU tier (torch + sentence-transformers + dspy)
	$(UV) pip install --system -e ".[dev,models,gpu]"

.PHONY: install-node
install-node: ## Install Node.js deps (Cube.js, Neon, Zod, TypeScript)
	npm install --prefer-offline --no-audit

.PHONY: install-sdks
install-sdks: ## Install MCP + Claude + TikTok SDKs (Python + Node.js)
	$(UV) pip install --system -e ".[mcp,social,generation]"
	npm install --prefer-offline --no-audit

.PHONY: install-java
install-java: ## Build Java MCP SDK module (requires JDK 21 + Gradle)
	cd java && $(GRADLE) build --no-daemon

.PHONY: install-lsp
install-lsp: ## Install LSP servers (pylsp, typescript-language-server)
	$(UV) pip install --system -e ".[lsp]"
	npm install -g typescript-language-server

.PHONY: install-all
install-all: install-dev install-node install-sdks ## Install everything (Python CPU + Node.js + SDKs)

.PHONY: install-ci
install-ci: ## Install for CI (no editable, CPU-only, no torch)
	$(UV) pip install --system ".[dev,models,warehouse]"

# ──────────────────────────────────────────────
# Test
# ──────────────────────────────────────────────

.PHONY: test
test: ## Run tests with parallel workers (auto-detect CPUs)
	$(PYTHON) -m pytest tests/ -n auto --timeout=30 -q

.PHONY: test-cov
test-cov: ## Run tests with coverage report (fail under 90%)
	$(PYTHON) -m pytest tests/ -n auto --timeout=30 \
		--cov=agentwarehouses --cov-report=term-missing --cov-fail-under=90

.PHONY: test-unit
test-unit: ## Run unit tests only
	$(PYTHON) -m pytest tests/ -m unit -n auto -q

.PHONY: test-models
test-models: ## Run Pydantic model tests only
	$(PYTHON) -m pytest tests/ -m models -n auto -q

.PHONY: test-integration
test-integration: ## Run integration tests only
	$(PYTHON) -m pytest tests/ -m integration -q

.PHONY: test-evals
test-evals: ## Run eval schema validation tests
	$(PYTHON) -m pytest tests/ -m evals -q

# ──────────────────────────────────────────────
# Lint & Type Check
# ──────────────────────────────────────────────

.PHONY: lint
lint: ## Run ruff linter
	ruff check src/ tests/ scripts/

.PHONY: lint-fix
lint-fix: ## Auto-fix lint issues
	ruff check --fix src/ tests/ scripts/

.PHONY: typecheck
typecheck: ## Run mypy strict type checking
	mypy src/agentwarehouses/

.PHONY: typecheck-ts
typecheck-ts: ## Run TypeScript type checking
	npx tsc --noEmit

.PHONY: graphql-codegen
graphql-codegen: ## Generate TypeScript types from GraphQL schema
	npx graphql-codegen --config codegen.ts

# ──────────────────────────────────────────────
# Crawl
# ──────────────────────────────────────────────

.PHONY: crawl
crawl: ## Run the llmstxt spider (code.claude.com)
	scrapy crawl llmstxt

.PHONY: crawl-neon
crawl-neon: ## Crawl Neon docs (llms.txt + sitemap, rbloom dedup)
	scrapy crawl neon_docs

.PHONY: crawl-neon-all
crawl-neon-all: ## Crawl all Neon sources (llms + sitemap + blog + pg tutorials)
	scrapy crawl neon_docs -a sources=llms,sitemap,blog_sitemap,pg_sitemap

.PHONY: neon-inventory
neon-inventory: ## Print neondatabase repo inventory (194 repos, refactor candidates)
	$(PYTHON) scripts/neon_repo_inventory.py

.PHONY: crawl-audit
crawl-audit: ## Audit crawl output for quality
	@$(PYTHON) -c "\
	import orjson; \
	from pathlib import Path; \
	data = Path('output/docs.jsonl').read_bytes().strip().split(b'\n'); \
	pages = [orjson.loads(l) for l in data]; \
	urls = [p['url'] for p in pages]; \
	print(f'Pages: {len(pages)}'); \
	print(f'Unique: {len(set(urls))}'); \
	print(f'Dupes: {len(urls) - len(set(urls))}'); \
	empty = sum(1 for p in pages if not p.get('title')); \
	short = sum(1 for p in pages if len(p.get('body_markdown','')) < 100); \
	print(f'Empty titles: {empty}'); \
	print(f'Short bodies: {short}'); \
	print('PASS' if not empty and not short and len(urls) == len(set(urls)) else 'FAIL')"

# ──────────────────────────────────────────────
# Database & Schema
# ──────────────────────────────────────────────

.PHONY: migrate-kimball
migrate-kimball: ## Create Kimball star schema in Neon (requires DATABASE_URL)
	cd schema && psql "$$DATABASE_URL" -f migrate.sql

# ──────────────────────────────────────────────
# Generate
# ──────────────────────────────────────────────

.PHONY: generate-skills
generate-skills: ## Generate 36 CRUD skills from resource profiles
	$(PYTHON) scripts/generate_crud_skills.py

# ──────────────────────────────────────────────
# CI
# ──────────────────────────────────────────────

.PHONY: ci
ci: lint test-cov ## Run full CI pipeline (lint + test with coverage)

# ──────────────────────────────────────────────
# Clean
# ──────────────────────────────────────────────

.PHONY: clean
clean: ## Remove build artifacts and caches
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache .ruff_cache
	find src tests -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# ──────────────────────────────────────────────
# Help
# ──────────────────────────────────────────────

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

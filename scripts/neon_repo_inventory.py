#!/usr/bin/env python3
"""Neon repository inventory — catalogs neondatabase/* repos by type.

Classifies 194 repos into: core, template, example, integration, tool, action, fork, archived.
Identifies repos with git info (boilerplate) that could be refactored into shared templates.

Usage:
    python scripts/neon_repo_inventory.py
    python scripts/neon_repo_inventory.py --format json > output/neon_repos.json

Output: Grouped inventory with refactoring recommendations.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass, field

# ── Repository data (from GitHub GraphQL search, April 2026) ──────────
# 194 repos in neondatabase org — top 90 by stars included here.


@dataclass
class NeonRepo:
    name: str
    stars: int
    language: str
    description: str
    archived: bool = False
    is_fork: bool = False
    topics: list[str] = field(default_factory=list)
    category: str = ""
    has_template_boilerplate: bool = False
    refactor_note: str = ""


# Classification rules
TEMPLATE_PATTERNS = re.compile(
    r"(template|starter|example|demo|guide-|neon-auth-|preview-branches|"
    r"clerk-|auth0-|stack-|workos-|social-|hanno-|vercel-marketplace|"
    r"neon-vercel-|cloudflare-drizzle|db-per-tenant|rls-demo)"
)

EXAMPLE_PATTERNS = re.compile(
    r"(example|sample|notebook|tutorial|overview|naturesnap|"
    r"ping-thing|yc-idea-matcher|ask-neon|neon-chatbot|sql-query)"
)

ACTION_PATTERNS = re.compile(r"(action|gh-workflow|github-automation)")

INTEGRATION_PATTERNS = re.compile(
    r"(mcp-server|mcp-neon|agent-skills|ai-rules|add-mcp|"
    r"postgres-skills|neon-js|neon-api-python|toolkit|neon-pkgs|better-env)"
)

TOOL_PATTERNS = re.compile(
    r"(neonctl|psqlsh|psql-describe|pg-import|semicolons|elephantshark|"
    r"instant-postgres|instagres|claude_astgrep|pg-prechecks|neon_local)"
)

CORE_REPOS = {
    "neon",
    "postgres",
    "serverless",
    "autoscaling",
    "wsproxy",
    "neonvm",
    "tokio-epoll-uring",
    "helm-charts",
    "rfcs",
    "pgrag",
    "pg_embedding",
    "pg_session_jwt",
    "postgresql_anonymizer",
    "website",
    "dev-actions",
    "go-chef",
    "neon-pkgs",
}


def classify_repo(repo: NeonRepo) -> NeonRepo:
    """Classify a repo into a category and flag template boilerplate."""
    name = repo.name

    if repo.archived:
        repo.category = "archived"
        repo.refactor_note = "Archived — skip"
        return repo

    if repo.is_fork:
        repo.category = "fork"
        return repo

    if name in CORE_REPOS:
        repo.category = "core"
        return repo

    if ACTION_PATTERNS.search(name):
        repo.category = "action"
        return repo

    if INTEGRATION_PATTERNS.search(name):
        repo.category = "integration"
        return repo

    if TOOL_PATTERNS.search(name):
        repo.category = "tool"
        return repo

    if TEMPLATE_PATTERNS.search(name):
        repo.category = "template"
        repo.has_template_boilerplate = True
        repo.refactor_note = (
            "Template repo — git init boilerplate (.github/, README badges, "
            "LICENSE, .gitignore) could be generated from a shared template. "
            "Content-specific code is the only unique value."
        )
        return repo

    if EXAMPLE_PATTERNS.search(name):
        repo.category = "example"
        repo.has_template_boilerplate = True
        repo.refactor_note = (
            "Example repo — shares scaffolding (package.json, tsconfig, "
            ".env.example, CI workflow) with other examples. Consider a "
            "monorepo or cookiecutter template."
        )
        return repo

    # Default: check topics for hints
    if any(t in repo.topics for t in ["neon-rls", "preview-deploy", "template"]):
        repo.category = "template"
        repo.has_template_boilerplate = True
        repo.refactor_note = "Tagged as template/preview by topics."
        return repo

    repo.category = "other"
    return repo


# ── Repo data from GitHub search results ──────────────────────────────
REPOS: list[NeonRepo] = [
    NeonRepo(
        "neon",
        21470,
        "Rust",
        "Serverless Postgres — separated storage and compute",
        topics=["database", "postgres", "rust", "serverless"],
    ),
    NeonRepo("appdotbuild-agent", 751, "Python", "App generation agent"),
    NeonRepo("pg_embedding", 578, "C", "HNSW vector similarity search in PostgreSQL", archived=True),
    NeonRepo("mcp-server-neon", 578, "TypeScript", "MCP server for Neon Management API and databases"),
    NeonRepo(
        "serverless",
        519,
        "JavaScript",
        "Connect to Neon from serverless/edge functions",
        topics=["cloudflare-workers", "serverless", "typescript"],
    ),
    NeonRepo("website", 305, "JavaScript", "Official docs and website for Neon"),
    NeonRepo("autoscaling", 244, "Go", "Postgres vertical autoscaling in k8s"),
    NeonRepo("postgres-sample-dbs", 210, "PLpgSQL", "Sample Postgres databases for learning"),
    NeonRepo(
        "yc-idea-matcher",
        163,
        "TypeScript",
        "YC idea matcher with pgvector",
        topics=["nextjs", "openai", "pgvector", "vercel-deployment"],
    ),
    NeonRepo("add-mcp", 150, "TypeScript", "Open MCP config tool — npx add-mcp"),
    NeonRepo("wsproxy", 142, "Go", "WebSocket proxy"),
    NeonRepo("elephantshark", 134, "Ruby", "Postgres network traffic monitor"),
    NeonRepo("neonctl", 107, "TypeScript", "Neon CLI tool"),
    NeonRepo("pgrag", 99, "Rust", "Postgres RAG pipeline extensions", topics=["chunking", "embeddings", "rag"]),
    NeonRepo("ai-rules", 81, "TypeScript", "AI rules for Neon database contexts"),
    NeonRepo("drizzle-overview", 76, "TypeScript", "Demo Drizzle ORM + Hono + Neon API"),
    NeonRepo(
        "examples",
        71,
        "TypeScript",
        "Examples and code snippets for Neon integrations",
        topics=["ai", "django", "langchain", "nextjs", "python"],
    ),
    NeonRepo("pg_session_jwt", 65, "Rust", "Postgres Extension for JWT Sessions"),
    NeonRepo("tokio-epoll-uring", 63, "Rust", "io_uring from vanilla tokio"),
    NeonRepo(
        "db-per-tenant",
        62,
        "TypeScript",
        "Chat-with-pdf app — db per user with pgvector",
        topics=["multitenancy", "pgvector"],
    ),
    NeonRepo("ask-neon", 60, "TypeScript", "Chatbot: search knowledge base by semantic similarity"),
    NeonRepo("helm-charts", 59, "Go Template", "Neon helm charts"),
    NeonRepo("cloudflare-drizzle-neon", 58, "TypeScript", "API using Cloudflare Workers + Drizzle + Neon"),
    NeonRepo("create-branch-action", 51, "TypeScript", "GitHub Action to create a new Neon branch"),
    NeonRepo("agent-skills", 49, "TypeScript", "Agent Skills for Neon Serverless Postgres"),
    NeonRepo("neon-pkgs", 48, "TypeScript", "CLI to instantiate a database with a single command"),
    NeonRepo(
        "preview-branches-with-vercel",
        43,
        "TypeScript",
        "Branch for every Vercel preview deployment",
        topics=["branching", "preview-deploy", "vercel"],
    ),
    NeonRepo("psql-describe", 38, "JavaScript", "psql \\d commands ported to JavaScript"),
    NeonRepo("neon-auth-nextjs-template", 37, "TypeScript", "Template for Neon Auth + Next.js"),
    NeonRepo("postgres", 37, "", "PostgreSQL in Neon"),
    NeonRepo("serverless-cfworker-demo", 31, "HTML", "Demo for @neondatabase/serverless on CF Workers"),
    NeonRepo("psqlsh", 30, "TypeScript", "psql.sh — browser-native PostgreSQL client"),
    NeonRepo("neon-chatbot", 28, "TypeScript", "Neon chatbot"),
    NeonRepo("neon_local", 27, "JavaScript", "Neon local development"),
    NeonRepo("neon-auth-demo-app", 27, "TypeScript", "Demo of Neon Auth"),
    NeonRepo(
        "preview-branches-with-fly",
        24,
        "TypeScript",
        "Branch for every Fly preview app",
        topics=["fly", "preview-deploy"],
    ),
    NeonRepo("better-env", 21, "TypeScript", "Better environment variables"),
    NeonRepo("ping-thing", 21, "JavaScript", "Ping Neon via Vercel Edge Function"),
    NeonRepo("claude_astgrep", 19, "", "ast-grep rules generation with Claude Code"),
    NeonRepo("neon-api-python", 19, "Python", "Python client for the Neon API"),
    NeonRepo("neonvm", 18, "Go", "QEMU-based virtualization for Kubernetes", archived=True),
    NeonRepo("naturesnap", 18, "TypeScript", "NatureSnap app"),
    NeonRepo("postgresql_anonymizer", 18, "PLpgSQL", "Neon fork of postgresql_anonymizer"),
    NeonRepo("neon-vercel-kysely", 18, "TypeScript", "Neon + Vercel Edge + Kysely"),
    NeonRepo("vercel-marketplace-neon", 17, "TypeScript", "Next.js + Vercel + Neon template"),
    NeonRepo("toolkit", 17, "TypeScript", "Neon toolkit"),
    NeonRepo(
        "azure-tenant-ai-chat",
        13,
        "TypeScript",
        "Multi-user RAG chat on Azure + Neon",
        topics=["azure", "pgvector", "rag"],
    ),
    NeonRepo("rls-demo-custom-jwt", 13, "TypeScript", "Demo of Neon RLS with custom JWTs", topics=["neon-rls"]),
    NeonRepo("neon-data-api-neon-auth", 14, "TypeScript", "Note taking app — Neon Data API + Auth"),
    NeonRepo("postgres-open-library-search", 12, "TypeScript", "Instant search with ParadeDB pg_search"),
    NeonRepo("instant-postgres", 12, "TypeScript", "Instant Postgres"),
    NeonRepo("clerk-nextjs-neon-rls", 12, "TypeScript", "Todo list — Clerk + Next.js + Neon RLS", topics=["neon-rls"]),
    NeonRepo("appdotbuild-website", 11, "TypeScript", "app.build website"),
    NeonRepo("preview-branches-with-cloudflare", 11, "TypeScript", "Branch for every CF preview deployment"),
    NeonRepo("neon-js", 10, "TypeScript", "JavaScript client for Neon Auth and Data API"),
    NeonRepo("pg-import", 10, "JavaScript", "CLI tool for importing between PostgreSQL databases"),
    NeonRepo("neon_local_vs_code_extension", 9, "TypeScript", "VS Code extension for neon_local"),
    NeonRepo("multi-agent-ai-azure-neon-openai", 9, "Python", "Multi-agent AI with LangChain + AutoGen + Azure + Neon"),
    NeonRepo("schema-diff-action", 6, "TypeScript", "GitHub Action to post schema changes in PR comments"),
    NeonRepo("delete-branch-action", 8, "TypeScript", "GitHub Action to delete Neon branch"),
    NeonRepo("fastapi-apprunner-neon", 7, "Python", "FastAPI + AWS App Runner + Neon"),
    NeonRepo("guide-neon-drizzle", 5, "TypeScript", "Example application for Neon with Drizzle"),
    NeonRepo("postgres-skills", 3, "Python", "Postgres skills"),
    NeonRepo("mcp-neon-azure-ai-agent", 5, "Python", "Azure AI Agent + MCP + Neon"),
    NeonRepo("guide-neon-next-clerk", 3, "TypeScript", "How to use Clerk with Neon"),
]


def build_inventory() -> dict[str, list[NeonRepo]]:
    """Classify all repos and group by category."""
    for repo in REPOS:
        classify_repo(repo)

    groups: dict[str, list[NeonRepo]] = {}
    for repo in REPOS:
        groups.setdefault(repo.category, []).append(repo)

    # Sort each group by stars desc
    for repos in groups.values():
        repos.sort(key=lambda r: r.stars, reverse=True)

    return groups


def print_report(groups: dict[str, list[NeonRepo]], fmt: str = "text") -> None:
    """Print inventory report."""
    if fmt == "json":
        data = {cat: [asdict(r) for r in repos] for cat, repos in groups.items()}
        print(json.dumps(data, indent=2))
        return

    total = sum(len(v) for v in groups.values())
    template_count = sum(1 for r in REPOS if r.has_template_boilerplate)

    print(f"# Neon Repository Inventory ({total} repos)")
    print()

    category_order = ["core", "integration", "tool", "action", "template", "example", "archived", "other"]
    for cat in category_order:
        repos = groups.get(cat, [])
        if not repos:
            continue
        print(f"## {cat.upper()} ({len(repos)} repos)")
        print()
        print("| Repo | Stars | Language | Refactorable |")
        print("|------|-------|----------|-------------|")
        for r in repos:
            flag = "Yes" if r.has_template_boilerplate else ""
            print(f"| {r.name} | {r.stars} | {r.language} | {flag} |")
        print()

    print("## REFACTORING SUMMARY")
    print()
    print(f"- **{template_count} repos** have template/example boilerplate that could be")
    print("  refactored into shared templates or a monorepo")
    print("- Common boilerplate: .github/workflows, tsconfig.json, .env.example,")
    print("  package.json scaffolding, README badges, LICENSE")
    print()
    print("### Recommended template groups:")
    print()

    # Group templates by pattern
    nextjs_templates = [r for r in REPOS if r.has_template_boilerplate and "TypeScript" in r.language]
    python_templates = [r for r in REPOS if r.has_template_boilerplate and "Python" in r.language]

    print(f"**Next.js + Neon templates ({len(nextjs_templates)}):**")
    for r in nextjs_templates:
        print(f"  - {r.name} ({r.stars} stars)")
    print()
    print(f"**Python + Neon templates ({len(python_templates)}):**")
    for r in python_templates:
        print(f"  - {r.name} ({r.stars} stars)")


if __name__ == "__main__":
    fmt = "json" if "--format" in sys.argv and "json" in sys.argv else "text"
    groups = build_inventory()
    print_report(groups, fmt)

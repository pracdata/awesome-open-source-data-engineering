-- schema/00_extensions.sql
-- Neon Postgres 18 extensions for AI workloads
-- Order matters: pgvector before pg_graphql (Ch 3.7)
--
-- Reference: Chapter 3 — Neon Postgres 18 Extensions

CREATE EXTENSION IF NOT EXISTS vector;          -- pgvector: embedding similarity search
CREATE EXTENSION IF NOT EXISTS pg_trgm;         -- fuzzy text matching via trigrams
CREATE EXTENSION IF NOT EXISTS bloom;           -- compact multi-column equality indexes
CREATE EXTENSION IF NOT EXISTS pg_graphql;      -- auto-generated GraphQL API (last — introspects all types)

-- pg_cron requires neon.allow_unstable_extensions or preloaded shared library
-- CREATE EXTENSION IF NOT EXISTS pg_cron;      -- scheduled SQL jobs inside Postgres
-- pg_stat_statements is preloaded on Neon
-- CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- schema/migrate.sql
-- Migration orchestrator: runs all schema files in dependency order.
-- Usage: psql "$DATABASE_URL" -f schema/migrate.sql
--
-- Dependency order:
--   1. Extensions (pgvector, pg_trgm, bloom, pg_graphql)
--   2. Dimensions (no foreign keys to other tables)
--   3. Staging/ODS (may reference crawl_runs)
--   4. Fact tables (reference dimensions + staging)
--   5. Aggregates (derived from fact tables)
--   6. Views (join facts + dimensions)
--
-- All statements use IF NOT EXISTS / ON CONFLICT DO NOTHING
-- for idempotent re-runs.

\echo '=== Kimball Dimensional Warehouse Migration ==='
\echo ''

-- Phase 1: Extensions
\echo '--- Phase 1: Extensions ---'
\i 00_extensions.sql

-- Phase 2: Dimension tables (no foreign key dependencies)
\echo '--- Phase 2: Dimension Tables ---'
\i dim_date.sql
\i dim_source.sql
\i dim_entity_type.sql
\i dim_content_type.sql
\i dim_plugin.sql
\i dim_persona.sql

-- Phase 3: Staging / ODS tables
\echo '--- Phase 3: Staging / ODS Tables ---'
\i crawl_runs.sql
\i doc_pages.sql
\i doc_sources.sql
\i doc_entities.sql
\i bloom_filter_state.sql

-- Phase 4: Fact tables (reference dimensions + staging)
\echo '--- Phase 4: Fact Tables ---'
\i fact_doc_crawls.sql
\i fact_entity_extractions.sql
\i fact_searches.sql
\i telemetry_spans.sql
\i palace_drawers.sql
\i customer_insights.sql
\i fact_emotion_probes.sql

-- Phase 5: Social analytics fact tables (reference dim_persona + dim_date)
\echo '--- Phase 5: Social Analytics ---'
\i fact_social_posts.sql
\i fact_social_metrics.sql
\i fact_social_ads.sql

-- Phase 6: Aggregate tables (derived from fact tables)
\echo '--- Phase 6: Aggregates ---'
\i agg_monthly_source.sql
\i agg_weekly_persona.sql
\i wbr_reports.sql

-- Phase 7: Views (join facts + dimensions)
\echo '--- Phase 7: Views ---'
\i view_unified_social_metrics.sql
\i view_unified_social_ads.sql

\echo ''
\echo '=== Migration complete ==='

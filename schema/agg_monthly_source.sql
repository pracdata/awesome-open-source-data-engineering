-- schema/agg_monthly_source.sql
-- Monthly rollup per source for crawl volume dashboards (Ch 12.3)
-- Kimball rule: derived from fact_doc_crawls only, never from other aggregates.
---
cubes:
  - name: monthly_source_metrics
    sql_table: public.agg_monthly_source
    measures:
      - name: total_crawls
        type: sum
        sql: "{CUBE}.total_crawls"
      - name: total_pages
        type: sum
        sql: "{CUBE}.total_pages"
      - name: total_bytes
        type: sum
        sql: "{CUBE}.total_bytes"
      - name: avg_body_length
        type: avg
        sql: "{CUBE}.avg_body_length"
    dimensions:
      - name: id
        sql: "{CUBE}.id"
        type: string
        primary_key: true
      - name: source_key
        sql: "{CUBE}.source_key"
        type: string
      - name: month_key
        sql: "{CUBE}.month_key"
        type: number
    pre_aggregations:
      - name: monthly_rollup
        measures: [total_crawls, total_pages]
        dimensions: [source_key]
        time_dimension: month_key
        granularity: month
        refresh_key:
          every: "1 day"
    meta:
      kimball: aggregate_fact
---
CREATE TABLE IF NOT EXISTS agg_monthly_source (
  id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  source_key      text REFERENCES dim_source(source_key),
  month_key       integer NOT NULL,            -- YYYYMM format
  total_crawls    integer DEFAULT 0,
  total_pages     integer DEFAULT 0,
  total_bytes     bigint DEFAULT 0,
  avg_body_length numeric(10,2),
  total_entities  integer DEFAULT 0,
  avg_duration_ms numeric(10,2),
  refreshed_at    timestamptz DEFAULT now(),
  UNIQUE(source_key, month_key)
);

CREATE INDEX IF NOT EXISTS idx_agg_monthly_source_month
  ON agg_monthly_source(month_key);

COMMENT ON TABLE agg_monthly_source IS
  'Monthly rollup per source for crawl volume dashboards. '
  'Grain: one row per source per month. '
  'Derived from fact_doc_crawls (Kimball aggregate navigation, Ch 12.3).';

-- Refresh via pg_cron (daily at 3:30 AM UTC):
-- SELECT cron.schedule(
--   'daily-dim-refresh',
--   '30 3 * * *',
--   $$REFRESH MATERIALIZED VIEW CONCURRENTLY agg_monthly_source$$
-- );

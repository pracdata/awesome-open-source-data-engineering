-- schema/crawl_runs.sql
-- Crawl run tracking for ETL audit (Ch 6.4)
-- State machine: PENDING -> RUNNING -> FINISHED | FAILED
---
cubes:
  - name: crawl_runs
    sql_table: public.crawl_runs
    measures:
      - name: count
        type: count
      - name: total_pages
        type: sum
        sql: "{CUBE}.pages_count"
      - name: avg_pages
        type: avg
        sql: "{CUBE}.pages_count"
    dimensions:
      - name: id
        sql: "{CUBE}.id"
        type: string
        primary_key: true
      - name: source
        sql: "{CUBE}.source"
        type: string
      - name: spider_name
        sql: "{CUBE}.spider_name"
        type: string
      - name: status
        sql: "{CUBE}.status"
        type: string
      - name: started_at
        sql: "{CUBE}.started_at"
        type: time
    meta:
      kimball: error_event_schema
---
CREATE TABLE IF NOT EXISTS crawl_runs (
  id            uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  source        text NOT NULL,
  spider_name   text NOT NULL,
  status        text NOT NULL DEFAULT 'running',  -- running/finished/failed
  started_at    timestamptz DEFAULT now(),
  finished_at   timestamptz,
  pages_count   integer DEFAULT 0,
  error_message text,
  etl_batch_id  uuid
);

CREATE INDEX IF NOT EXISTS idx_crawl_runs_status
  ON crawl_runs(status);
CREATE INDEX IF NOT EXISTS idx_crawl_runs_started
  ON crawl_runs(started_at);

COMMENT ON TABLE crawl_runs IS
  'Crawl run tracking (Kimball error event schema, Subsystem 5). '
  'State machine: running -> finished | failed. '
  'Grain: one row per spider execution.';

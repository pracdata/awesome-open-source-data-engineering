-- schema/fact_social_metrics.sql
-- Periodic snapshot fact: daily metrics per post per platform (Ch 20.2)
-- Captures engagement metrics at daily granularity for WBR analysis.
---
cubes:
  - name: social_metrics
    sql_table: public.fact_social_metrics
    measures:
      - name: total_views
        type: sum
        sql: "{CUBE}.views"
      - name: total_likes
        type: sum
        sql: "{CUBE}.likes"
      - name: total_comments
        type: sum
        sql: "{CUBE}.comments"
      - name: total_shares
        type: sum
        sql: "{CUBE}.shares"
      - name: avg_completion_rate
        type: avg
        sql: "{CUBE}.completion_rate"
      - name: total_follows
        type: sum
        sql: "{CUBE}.follows_from_post"
    dimensions:
      - name: id
        sql: "{CUBE}.id"
        type: string
        primary_key: true
    joins:
      - name: dim_date
        sql: "{CUBE}.date_key = {dim_date}.date_key"
        relationship: many_to_one
    meta:
      kimball: periodic_snapshot_fact
---
CREATE TABLE IF NOT EXISTS fact_social_metrics (
  id                  uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  post_id             uuid REFERENCES fact_social_posts(post_id),
  date_key            integer REFERENCES dim_date(date_key),
  views               integer DEFAULT 0,
  likes               integer DEFAULT 0,
  comments            integer DEFAULT 0,
  shares              integer DEFAULT 0,
  saves               integer DEFAULT 0,
  watch_time_seconds  integer DEFAULT 0,
  completion_rate     numeric(5,4),            -- 0.0000 to 1.0000
  click_through_rate  numeric(5,4),
  follows_from_post   integer DEFAULT 0,
  etl_loaded_at       timestamptz DEFAULT now(),
  UNIQUE(post_id, date_key)                    -- one snapshot per post per day
);

CREATE INDEX IF NOT EXISTS idx_social_metrics_post
  ON fact_social_metrics(post_id);
CREATE INDEX IF NOT EXISTS idx_social_metrics_date
  ON fact_social_metrics(date_key);

COMMENT ON TABLE fact_social_metrics IS
  'Periodic snapshot fact: daily engagement metrics per post per platform. '
  'Grain: one row per post per platform per day. '
  'SCD Type 2 pattern — daily snapshots capture metric evolution.';

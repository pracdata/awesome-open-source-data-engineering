-- schema/agg_weekly_persona.sql
-- Weekly rollup per persona per platform for WBR (Ch 20.2, 20.4)
-- Aggregate derived from fact_social_posts + fact_social_metrics.
-- Kimball rule: aggregates derive from atomic facts only, never other aggregates.
---
cubes:
  - name: weekly_persona
    sql_table: public.agg_weekly_persona
    measures:
      - name: total_views
        type: sum
        sql: "{CUBE}.total_views"
      - name: total_follows
        type: sum
        sql: "{CUBE}.total_follows"
      - name: avg_engagement
        type: avg
        sql: "{CUBE}.avg_engagement_rate"
      - name: total_revenue
        type: sum
        sql: "{CUBE}.revenue_cents / 100.0"
      - name: total_ad_spend
        type: sum
        sql: "{CUBE}.total_ad_spend_cents / 100.0"
    dimensions:
      - name: id
        sql: "{CUBE}.id"
        type: string
        primary_key: true
      - name: platform
        sql: "{CUBE}.platform"
        type: string
      - name: week_start
        sql: "{CUBE}.week_start"
        type: time
    joins:
      - name: dim_persona
        sql: "{CUBE}.persona_key = {dim_persona}.persona_key"
        relationship: many_to_one
    pre_aggregations:
      - name: monthly_rollup
        measures: [total_views, total_follows]
        dimensions: [platform]
        time_dimension: week_start
        granularity: week
        refresh_key:
          every: "1 day"
    meta:
      kimball: aggregate_fact
---
CREATE TABLE IF NOT EXISTS agg_weekly_persona (
  id                      uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  persona_key             integer REFERENCES dim_persona(persona_key),
  week_start              date NOT NULL,
  platform                text NOT NULL,
  posts_published         integer DEFAULT 0,
  total_views             integer DEFAULT 0,
  total_likes             integer DEFAULT 0,
  total_comments          integer DEFAULT 0,
  total_shares            integer DEFAULT 0,
  total_follows           integer DEFAULT 0,
  avg_completion_rate     numeric(5,4),
  avg_engagement_rate     numeric(5,4),
  total_ad_spend_cents    integer DEFAULT 0,
  revenue_cents           integer DEFAULT 0,
  followers_eow           integer DEFAULT 0,         -- end-of-week follower count
  wow_follower_growth     numeric(5,4),              -- week-over-week growth rate
  trailing_4w_avg_views   numeric(12,2),
  UNIQUE(persona_key, week_start, platform)
);

CREATE INDEX IF NOT EXISTS idx_agg_weekly_persona_week
  ON agg_weekly_persona(week_start);

COMMENT ON TABLE agg_weekly_persona IS
  'Weekly rollup per persona per platform for WBR. '
  'Grain: one row per persona per platform per week. '
  'Derived from fact_social_posts + fact_social_metrics (never from other aggregates).';

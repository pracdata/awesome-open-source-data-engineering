-- schema/fact_social_ads.sql
-- Ad performance fact with video completion funnel (Ch 20.10)
-- Tracks paid amplification metrics per post per platform.
---
cubes:
  - name: social_ads
    sql_table: public.fact_social_ads
    measures:
      - name: count
        type: count
      - name: total_spend
        type: sum
        sql: "{CUBE}.spend_cents / 100.0"
      - name: total_impressions
        type: sum
        sql: "{CUBE}.impressions"
      - name: total_clicks
        type: sum
        sql: "{CUBE}.clicks"
      - name: total_conversions
        type: sum
        sql: "{CUBE}.conversions"
      - name: avg_cpm
        type: avg
        sql: "{CUBE}.cpm_cents / 100.0"
    dimensions:
      - name: id
        sql: "{CUBE}.id"
        type: string
        primary_key: true
      - name: platform
        sql: "{CUBE}.platform"
        type: string
      - name: ad_format
        sql: "{CUBE}.ad_format"
        type: string
    joins:
      - name: dim_date
        sql: "{CUBE}.date_key = {dim_date}.date_key"
        relationship: many_to_one
      - name: dim_persona
        sql: "{CUBE}.persona_key = {dim_persona}.persona_key"
        relationship: many_to_one
    meta:
      kimball: transaction_fact
---
CREATE TABLE IF NOT EXISTS fact_social_ads (
  id                  uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  post_id             uuid REFERENCES fact_social_posts(post_id),
  persona_key         integer REFERENCES dim_persona(persona_key),
  date_key            integer REFERENCES dim_date(date_key),
  platform            text NOT NULL CHECK (platform IN ('youtube_shorts', 'instagram_reels', 'tiktok')),
  ad_format           text,                    -- 'in_feed', 'discovery', 'spark_ad'
  spend_cents         integer DEFAULT 0,
  impressions         integer DEFAULT 0,
  clicks              integer DEFAULT 0,
  conversions         integer DEFAULT 0,
  cpm_cents           integer DEFAULT 0,       -- cost per mille
  cpc_cents           integer DEFAULT 0,       -- cost per click
  video_views_25pct   integer DEFAULT 0,       -- completion funnel
  video_views_50pct   integer DEFAULT 0,
  video_views_75pct   integer DEFAULT 0,
  video_views_100pct  integer DEFAULT 0,
  roas                numeric(8,4),            -- return on ad spend
  etl_loaded_at       timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_social_ads_date
  ON fact_social_ads(date_key);
CREATE INDEX IF NOT EXISTS idx_social_ads_persona
  ON fact_social_ads(persona_key);

COMMENT ON TABLE fact_social_ads IS
  'Ad performance fact with video completion funnel. '
  'Grain: one row per ad campaign per post per day. '
  'Tracks paid amplification metrics for WBR ROAS analysis (Ch 20.4).';

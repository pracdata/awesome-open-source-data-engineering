-- schema/fact_social_posts.sql
-- Transaction fact: one row per post per platform (Ch 20.2)
-- 6 personas x 3 platforms = up to 18 rows per changelog release.
---
cubes:
  - name: social_posts
    sql_table: public.fact_social_posts
    measures:
      - name: count
        type: count
      - name: total_ad_spend
        type: sum
        sql: "{CUBE}.ad_spend_cents / 100.0"
    dimensions:
      - name: post_id
        sql: "{CUBE}.post_id"
        type: string
        primary_key: true
      - name: platform
        sql: "{CUBE}.platform"
        type: string
      - name: content_phase
        sql: "{CUBE}.content_phase"
        type: string
      - name: changelog_version
        sql: "{CUBE}.changelog_version"
        type: string
      - name: published_at
        sql: "{CUBE}.published_at"
        type: time
    joins:
      - name: dim_persona
        sql: "{CUBE}.persona_key = {dim_persona}.persona_key"
        relationship: many_to_one
      - name: dim_date
        sql: "{CUBE}.date_key = {dim_date}.date_key"
        relationship: many_to_one
    meta:
      kimball: transaction_fact
---
CREATE TABLE IF NOT EXISTS fact_social_posts (
  post_id             uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  persona_key         integer REFERENCES dim_persona(persona_key),
  date_key            integer REFERENCES dim_date(date_key),
  platform            text NOT NULL CHECK (platform IN ('youtube_shorts', 'instagram_reels', 'tiktok')),
  changelog_version   text NOT NULL,
  script_hash         text NOT NULL,           -- SHA-256 of VideoScript JSON
  video_duration_seconds integer DEFAULT 40,
  scene_count         integer DEFAULT 5,
  hashtag_count       integer NOT NULL,
  caption_length      integer NOT NULL,
  published_at        timestamptz NOT NULL,
  platform_post_id    text,                    -- platform-specific ID
  platform_url        text,                    -- direct link
  content_phase       text DEFAULT 'organic' CHECK (content_phase IN ('organic', 'paid', 'monetized')),
  ad_spend_cents      integer DEFAULT 0,       -- 0 for organic posts
  etl_loaded_at       timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_social_posts_persona
  ON fact_social_posts(persona_key);
CREATE INDEX IF NOT EXISTS idx_social_posts_date
  ON fact_social_posts(date_key);
CREATE INDEX IF NOT EXISTS idx_social_posts_platform
  ON fact_social_posts(platform);

COMMENT ON TABLE fact_social_posts IS
  'Transaction fact: social media posts. '
  'Grain: one row per post per platform. '
  '6 personas x 3 platforms = up to 18 rows per changelog release.';

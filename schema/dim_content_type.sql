-- schema/dim_content_type.sql
-- Content type classification dimension (Ch 1.7)
-- Simple lookup dimension with natural key.
---
cubes:
  - name: dim_content_type
    sql_table: public.dim_content_type
    dimensions:
      - name: content_type_key
        sql: "{CUBE}.content_type_key"
        type: string
        primary_key: true
      - name: display_name
        sql: "{CUBE}.display_name"
        type: string
      - name: description
        sql: "{CUBE}.description"
        type: string
    meta:
      kimball: conformed_dimension
---
CREATE TABLE IF NOT EXISTS dim_content_type (
  content_type_key  text PRIMARY KEY,
  display_name      text NOT NULL,
  description       text
);

COMMENT ON TABLE dim_content_type IS
  'Content type dimension for crawled pages. '
  'Grain: one row per content_type value.';

-- Seed content types
INSERT INTO dim_content_type (content_type_key, display_name, description) VALUES
  ('page',       'Documentation Page',  'Standard documentation page'),
  ('changelog',  'Changelog',           'Version changelog or release notes'),
  ('llms_txt',   'llms.txt Index',      'LLM-optimized documentation index'),
  ('llms_full',  'llms-full.txt',       'Full inline documentation'),
  ('sitemap',    'Sitemap',             'XML sitemap entry'),
  ('api_ref',    'API Reference',       'API endpoint documentation'),
  ('guide',      'Guide',              'Tutorial or how-to guide'),
  ('blog',       'Blog Post',          'Engineering blog post'),
  ('skill',      'Skill Definition',    'Claude Code skill metadata')
ON CONFLICT (content_type_key) DO NOTHING;

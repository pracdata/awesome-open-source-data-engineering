-- schema/dim_plugin.sql
-- Plugin/tool dimension for crawl provenance (Ch 1.7, 1.9)
-- Tracks which spider or plugin triggered a crawl event.
---
cubes:
  - name: dim_plugin
    sql_table: public.dim_plugin
    dimensions:
      - name: plugin_key
        sql: "{CUBE}.plugin_key"
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
CREATE TABLE IF NOT EXISTS dim_plugin (
  plugin_key    text PRIMARY KEY,
  display_name  text NOT NULL,
  description   text
);

COMMENT ON TABLE dim_plugin IS
  'Plugin/spider dimension for crawl provenance. '
  'Grain: one row per plugin or spider name.';

-- Seed plugins from production spiders
INSERT INTO dim_plugin (plugin_key, display_name, description) VALUES
  ('docsync',           'DocSync Spider',      'llms.txt link-following spider'),
  ('fullsync',          'FullSync Spider',     'Comprehensive sitemap + llms.txt spider'),
  ('llmstxt',           'LLMs.txt Spider',     'Basic llms.txt crawler'),
  ('skills_spider',     'Skills Spider',       'skills.sh ecosystem crawler'),
  ('sitemap_spider',    'Sitemap Spider',      'Generic sitemap following spider'),
  ('trademark_spider',  'Trademark Spider',    'USPTO TSDR monitoring spider'),
  ('manual',            'Manual Import',       'Manually imported data')
ON CONFLICT (plugin_key) DO NOTHING;

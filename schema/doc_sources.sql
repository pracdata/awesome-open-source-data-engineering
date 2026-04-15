-- schema/doc_sources.sql
-- Source index entries from llms.txt, sitemaps, and skill registries (Appendix A)
---
cubes:
  - name: doc_sources
    sql_table: public.doc_sources
    measures:
      - name: count
        type: count
    dimensions:
      - name: id
        sql: "{CUBE}.id"
        type: string
        primary_key: true
      - name: source
        sql: "{CUBE}.source"
        type: string
      - name: url
        sql: "{CUBE}.url"
        type: string
      - name: category
        sql: "{CUBE}.category"
        type: string
      - name: parsed_at
        sql: "{CUBE}.parsed_at"
        type: time
    meta:
      kimball: staging_ods
---
CREATE TABLE IF NOT EXISTS doc_sources (
  id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  source          text NOT NULL,
  url             text NOT NULL UNIQUE,
  title           text,
  description     text,
  category        text,
  parsed_at       timestamptz DEFAULT now(),
  etl_loaded_at   timestamptz DEFAULT now(),
  etl_source      text DEFAULT 'scrapy'
);

COMMENT ON TABLE doc_sources IS
  'Source index entries from llms.txt, sitemaps, and skill registries. '
  'Grain: one row per URL.';

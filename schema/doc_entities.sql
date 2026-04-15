-- schema/doc_entities.sql
-- Extracted entities from crawled pages (Ch 16.2, Appendix A)
-- Populated by regex CTE (Tier 1) and DSPy signatures (Tier 2).
---
cubes:
  - name: doc_entities
    sql_table: public.doc_entities
    measures:
      - name: count
        type: count
      - name: unique_types
        type: count_distinct
        sql: "{CUBE}.entity_type"
    dimensions:
      - name: id
        sql: "{CUBE}.id"
        type: string
        primary_key: true
      - name: entity_type
        sql: "{CUBE}.entity_type"
        type: string
      - name: entity_name
        sql: "{CUBE}.entity_name"
        type: string
      - name: source_domain
        sql: "{CUBE}.source_domain"
        type: string
      - name: etl_source
        sql: "{CUBE}.etl_source"
        type: string
      - name: extracted_at
        sql: "{CUBE}.extracted_at"
        type: time
    meta:
      kimball: staging_ods
---
CREATE TABLE IF NOT EXISTS doc_entities (
  id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  entity_type     text NOT NULL,
  entity_name     text NOT NULL,
  source_url      text NOT NULL,
  source_domain   text NOT NULL,
  context         text,
  extracted_at    timestamptz DEFAULT now(),
  etl_loaded_at   timestamptz DEFAULT now(),
  etl_source      text DEFAULT 'regex_cte',
  UNIQUE (entity_type, entity_name, source_url)
);

COMMENT ON TABLE doc_entities IS
  'Extracted entities from crawled pages. '
  'Grain: entity_type + entity_name + source_url.';

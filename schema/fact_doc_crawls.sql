-- schema/fact_doc_crawls.sql
-- Kimball transaction fact: one row per document crawl event (Ch 1.3, 1.4)
-- Star joins to 4 dimensions: dim_source, dim_content_type, dim_date, dim_plugin.
-- Measures: body_length (additive), entity_count (additive), crawl_duration_ms (additive).
---
cubes:
  - name: fact_doc_crawls
    sql_table: public.fact_doc_crawls
    measures:
      - name: crawl_count
        type: count
        meta:
          kimball: additive_measure
      - name: total_volume_bytes
        sql: "{CUBE}.body_length"
        type: sum
        description: "Total bytes crawled — the canonical volume metric"
        meta:
          kimball: additive_measure
      - name: total_entities
        sql: "{CUBE}.entity_count"
        type: sum
        meta:
          kimball: additive_measure
      - name: avg_duration_ms
        sql: "{CUBE}.crawl_duration_ms"
        type: avg
    dimensions:
      - name: crawl_id
        sql: "{CUBE}.crawl_id"
        type: string
        primary_key: true
      - name: content_changed
        sql: "{CUBE}.content_changed"
        type: boolean
      - name: response_status
        sql: "{CUBE}.response_status"
        type: number
    joins:
      - name: dim_source
        sql: "{CUBE}.source_key = {dim_source}.source_key"
        relationship: many_to_one
      - name: dim_content_type
        sql: "{CUBE}.content_type_key = {dim_content_type}.content_type_key"
        relationship: many_to_one
      - name: dim_date
        sql: "{CUBE}.date_key = {dim_date}.date_key"
        relationship: many_to_one
      - name: dim_plugin
        sql: "{CUBE}.plugin_key = {dim_plugin}.plugin_key"
        relationship: many_to_one
    meta:
      kimball: transaction_fact
---
CREATE TABLE IF NOT EXISTS fact_doc_crawls (
  crawl_id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  doc_page_id       uuid REFERENCES doc_pages(id),
  source_key        text REFERENCES dim_source(source_key),
  content_type_key  text REFERENCES dim_content_type(content_type_key),
  date_key          integer REFERENCES dim_date(date_key),
  body_length       integer,           -- additive measure: bytes fetched
  entity_count      integer,           -- additive measure: entities extracted
  content_changed   boolean,           -- semi-additive flag
  response_status   integer,           -- HTTP status code
  crawl_duration_ms integer,           -- additive measure: fetch latency
  plugin_key        text REFERENCES dim_plugin(plugin_key)
);

CREATE INDEX IF NOT EXISTS idx_fact_crawls_date
  ON fact_doc_crawls(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_crawls_source
  ON fact_doc_crawls(source_key);
CREATE INDEX IF NOT EXISTS idx_fact_crawls_bloom
  ON fact_doc_crawls USING bloom (source_key, content_type_key);

COMMENT ON TABLE fact_doc_crawls IS
  'Kimball transaction fact: one row per document crawl event. '
  'Star joins to 4 dimensions (source, content_type, date, plugin). '
  'Additive measures: body_length, entity_count, crawl_duration_ms.';

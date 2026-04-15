-- schema/doc_pages.sql
-- Crawled documentation pages with pgvector embeddings (Appendix A)
-- Staging/ODS layer — populated by Scrapy docsync/fullsync spiders.
-- Indexes: HNSW (semantic), GIN/trgm (fuzzy), bloom (multi-column).
---
cubes:
  - name: doc_pages
    sql_table: public.doc_pages
    measures:
      - name: count
        type: count
      - name: avg_body_length
        sql: "length({CUBE}.body_text)"
        type: avg
    dimensions:
      - name: id
        sql: "{CUBE}.id"
        type: string
        primary_key: true
      - name: url
        sql: "{CUBE}.url"
        type: string
      - name: source
        sql: "{CUBE}.source"
        type: string
      - name: content_type
        sql: "{CUBE}.content_type"
        type: string
      - name: title
        sql: "{CUBE}.title"
        type: string
      - name: fetched_at
        sql: "{CUBE}.fetched_at"
        type: time
    meta:
      kimball: staging_ods
---
CREATE TABLE IF NOT EXISTS doc_pages (
  id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  url             text NOT NULL,
  source          text NOT NULL,
  content_type    text NOT NULL,
  title           text,
  body_text       text,
  response_json   jsonb NOT NULL DEFAULT '{}'::jsonb,
  content_hash    text,
  fetched_at      timestamptz DEFAULT now(),
  embedding       vector(384),
  etl_loaded_at   timestamptz DEFAULT now(),
  etl_source      text DEFAULT 'scrapy',
  etl_batch_id    uuid,
  crawl_run_id    uuid,
  UNIQUE (url, content_type)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_doc_pages_url_unique
  ON doc_pages(url);
CREATE INDEX IF NOT EXISTS idx_doc_pages_embedding_hnsw
  ON doc_pages USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_doc_pages_body_trgm
  ON doc_pages USING gin (body_text gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_doc_pages_bloom
  ON doc_pages USING bloom (source, content_type);

COMMENT ON TABLE doc_pages IS
  'Crawled documentation pages with pgvector embeddings. '
  'Grain: one row per URL+content_type. Staging/ODS layer.';

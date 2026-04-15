-- schema/palace_drawers.sql
-- Verbatim memory storage with wing/room hierarchy (Ch 6.6, Appendix A)
-- Adapts mempalace project with Neon Postgres + pgvector backend.
-- Only table using all three index types: HNSW, bloom, GIN/trgm (Ch 3.9).
---
cubes:
  - name: palace_drawers
    sql_table: public.palace_drawers
    measures:
      - name: count
        type: count
      - name: avg_content_length
        sql: "length({CUBE}.content)"
        type: avg
    dimensions:
      - name: id
        sql: "{CUBE}.id"
        type: string
        primary_key: true
      - name: wing
        sql: "{CUBE}.wing"
        type: string
      - name: room
        sql: "{CUBE}.room"
        type: string
      - name: source_type
        sql: "{CUBE}.source_type"
        type: string
      - name: source_file
        sql: "{CUBE}.source_file"
        type: string
      - name: mined_at
        sql: "{CUBE}.mined_at"
        type: time
    meta:
      kimball: operational_data_store
---
CREATE TABLE IF NOT EXISTS palace_drawers (
  id            uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  content       text NOT NULL,              -- verbatim text, never summarized
  content_hash  text NOT NULL UNIQUE,       -- SHA-256 for dedup
  wing          text NOT NULL DEFAULT 'general',  -- top-level category
  room          text NOT NULL DEFAULT 'misc',     -- sub-category within wing
  source_file   text,                       -- originating file path
  source_type   text NOT NULL DEFAULT 'file',
  line_start    int,
  line_end      int,
  language      text,
  embedding     vector(384),                -- all-MiniLM-L6-v2
  mined_at      timestamptz DEFAULT now(),
  valid_from    timestamptz,                -- temporal validity
  valid_to      timestamptz,                -- NULL = still valid
  etl_source    text DEFAULT 'mempalace_neon'
);

-- HNSW: semantic search over 384-dim embeddings
CREATE INDEX IF NOT EXISTS idx_palace_drawers_embedding
  ON palace_drawers USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- GIN/trgm: fuzzy text search on drawer content
CREATE INDEX IF NOT EXISTS idx_palace_drawers_trgm
  ON palace_drawers USING gin (content gin_trgm_ops);

-- Bloom: compact multi-column wing/room/source_type filter
CREATE INDEX IF NOT EXISTS idx_palace_drawers_bloom
  ON palace_drawers USING bloom (wing, room, source_type);

CREATE INDEX IF NOT EXISTS idx_palace_drawers_source
  ON palace_drawers (source_file) WHERE source_file IS NOT NULL;

COMMENT ON TABLE palace_drawers IS
  'Verbatim memory storage (mempalace drawers). Wing = topic category, '
  'Room = sub-aspect. Content is never summarized. '
  'Only table using all 3 index types: HNSW + bloom + GIN/trgm (Ch 3.9).';

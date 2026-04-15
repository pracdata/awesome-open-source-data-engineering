-- schema/fact_searches.sql
-- Kimball transaction fact: search analytics (Ch 1.2, Appendix A)
-- Records every search execution for retrieval quality analysis.
---
cubes:
  - name: searches
    sql_table: public.fact_searches
    measures:
      - name: count
        type: count
      - name: avg_results
        type: avg
        sql: "{CUBE}.result_count"
      - name: avg_duration
        type: avg
        sql: "{CUBE}.duration_ms"
    dimensions:
      - name: search_id
        sql: "{CUBE}.search_id"
        type: string
        primary_key: true
      - name: search_type
        sql: "{CUBE}.search_type"
        type: string
      - name: top_source
        sql: "{CUBE}.top_source"
        type: string
      - name: created_at
        sql: "{CUBE}.created_at"
        type: time
    joins:
      - name: dim_date
        sql: "{CUBE}.date_key = {dim_date}.date_key"
        relationship: many_to_one
    meta:
      kimball: transaction_fact
---
CREATE TABLE IF NOT EXISTS fact_searches (
  search_id     uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  query_hash    text NOT NULL,
  query_text    text,
  search_type   text DEFAULT 'hybrid',
  result_count  integer DEFAULT 0,
  top_source    text,
  date_key      integer REFERENCES dim_date(date_key),
  duration_ms   integer,
  created_at    timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_fact_searches_date
  ON fact_searches(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_searches_type
  ON fact_searches(search_type);

COMMENT ON TABLE fact_searches IS
  'Kimball transaction fact: search analytics. '
  'Grain: one row per search execution. '
  'Used for retrieval quality measurement and weight tuning (Ch 11.5).';

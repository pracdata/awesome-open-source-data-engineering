-- schema/customer_insights.sql
-- Customer case studies with pgvector embeddings (Appendix A)
---
cubes:
  - name: customer_insights
    sql_table: public.customer_insights
    measures:
      - name: count
        type: count
    dimensions:
      - name: id
        sql: "{CUBE}.id"
        type: number
        primary_key: true
      - name: company
        sql: "{CUBE}.company"
        type: string
      - name: industry
        sql: "{CUBE}.industry"
        type: string
      - name: use_case
        sql: "{CUBE}.use_case"
        type: string
      - name: created_at
        sql: "{CUBE}.created_at"
        type: time
---
CREATE TABLE IF NOT EXISTS customer_insights (
  id              serial PRIMARY KEY,
  company         text NOT NULL,
  industry        text,
  use_case        text,
  pain_point      text,
  solution        text,
  source_url      text,
  embedding       vector(384),
  created_at      timestamptz DEFAULT now()
);

COMMENT ON TABLE customer_insights IS
  'Customer case studies with pgvector embeddings. '
  'Grain: one row per company + use case.';

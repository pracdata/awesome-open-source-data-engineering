-- schema/fact_entity_extractions.sql
-- Kimball bridge fact: entity-to-document M:N linkage (Ch 1.4, 16.3)
-- Resolves many-to-many between entities and documents.
-- Confidence is a property of the extraction event, not the entity.
---
cubes:
  - name: entity_extractions
    sql_table: public.fact_entity_extractions
    measures:
      - name: count
        type: count
      - name: unique_entities
        type: count_distinct
        sql: "{CUBE}.entity_id"
      - name: avg_confidence
        type: avg
        sql: "{CUBE}.confidence"
    dimensions:
      - name: extraction_id
        sql: "{CUBE}.extraction_id"
        type: string
        primary_key: true
      - name: extraction_method
        sql: "{CUBE}.extraction_method"
        type: string
      - name: confidence
        sql: "{CUBE}.confidence"
        type: number
    joins:
      - name: dim_date
        sql: "{CUBE}.date_key = {dim_date}.date_key"
        relationship: many_to_one
    meta:
      kimball: bridge_fact
---
CREATE TABLE IF NOT EXISTS fact_entity_extractions (
  extraction_id     uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  entity_id         uuid REFERENCES doc_entities(id),
  doc_page_id       uuid REFERENCES doc_pages(id),
  date_key          integer REFERENCES dim_date(date_key),
  confidence        float DEFAULT 1.0,
  extraction_method text DEFAULT 'regex_cte',
  created_at        timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_fact_entity_doc
  ON fact_entity_extractions(doc_page_id);
CREATE INDEX IF NOT EXISTS idx_fact_entity_date
  ON fact_entity_extractions(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_entity_entity
  ON fact_entity_extractions(entity_id);

COMMENT ON TABLE fact_entity_extractions IS
  'Kimball bridge fact: entity-to-document M:N linkage. '
  'Grain: one row per entity+document pair. '
  'Confidence lives here (property of extraction event, not entity).';

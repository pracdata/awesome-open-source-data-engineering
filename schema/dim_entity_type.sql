-- schema/dim_entity_type.sql
-- Entity type classification dimension (Ch 16.7)
-- SCD Type 1: categories update in-place (no history needed).
---
cubes:
  - name: dim_entity_type
    sql_table: public.dim_entity_type
    dimensions:
      - name: entity_type_key
        sql: "{CUBE}.entity_type_key"
        type: number
        primary_key: true
      - name: entity_type
        sql: "{CUBE}.entity_type"
        type: string
      - name: category
        sql: "{CUBE}.category"
        type: string
      - name: display_label
        sql: "{CUBE}.display_label"
        type: string
    meta:
      kimball: conformed_dimension
      kimball_scd: type_1
---
CREATE TABLE IF NOT EXISTS dim_entity_type (
  entity_type_key   serial PRIMARY KEY,
  entity_type       text NOT NULL UNIQUE,
  category          text NOT NULL,
  display_label     text NOT NULL,
  description       text,
  etl_loaded_at     timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_dim_entity_type_type
  ON dim_entity_type(entity_type);

COMMENT ON TABLE dim_entity_type IS
  'Kimball dimension: entity type classification. '
  'Grain: one row per entity_type value.';
COMMENT ON COLUMN dim_entity_type.category IS
  'High-level grouping: technology, business, infrastructure';
COMMENT ON COLUMN dim_entity_type.display_label IS
  'Human-readable label for dashboards';

-- Seed entity types from production data (Ch 16.7)
INSERT INTO dim_entity_type (entity_type, category, display_label, description) VALUES
  ('npm_package',       'technology',      'NPM Package',       'Node.js package from npm registry'),
  ('python_package',    'technology',      'Python Package',    'Python package from PyPI'),
  ('python_import',     'technology',      'Python Import',     'Python import statement'),
  ('pip_package',       'technology',      'Pip Package',       'Python package installed via pip'),
  ('github_repo',       'technology',      'GitHub Repository', 'GitHub repository reference'),
  ('api_endpoint',      'technology',      'API Endpoint',      'REST or GraphQL API endpoint'),
  ('pg_extension',      'infrastructure',  'PG Extension',      'PostgreSQL extension'),
  ('company',           'business',        'Company',           'Organization or company name'),
  ('industry',          'business',        'Industry',          'Industry or sector classification'),
  ('claude_customer',   'business',        'Claude Customer',   'Known Claude/Anthropic customer'),
  ('skills_publisher',  'infrastructure',  'Skills Publisher',  'Publisher of Claude Code skills'),
  ('cli_command',       'infrastructure',  'CLI Command',       'Command-line interface command'),
  ('claude_connector',  'infrastructure',  'Claude Connector',  'Claude Code connector/integration')
ON CONFLICT (entity_type) DO NOTHING;

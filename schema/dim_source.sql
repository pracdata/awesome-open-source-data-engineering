-- schema/dim_source.sql
-- Conformed source dimension with SCD Type 2 history (Ch 1.5, 1.6)
-- Tracks documentation source metadata with full change history.
---
cubes:
  - name: dim_source
    sql_table: public.dim_source
    dimensions:
      - name: source_key
        sql: "{CUBE}.source_key"
        type: string
        primary_key: true
      - name: domain
        sql: "{CUBE}.domain"
        type: string
      - name: base_url
        sql: "{CUBE}.base_url"
        type: string
      - name: category
        sql: "{CUBE}.category"
        type: string
      - name: is_active
        sql: "{CUBE}.is_active"
        type: boolean
      - name: is_current
        sql: "{CUBE}.is_current"
        type: boolean
    meta:
      kimball: conformed_dimension
      kimball_scd: type_2
---
CREATE TABLE IF NOT EXISTS dim_source (
  source_key      text PRIMARY KEY,
  domain          text NOT NULL,
  base_url        text,
  category        text,
  is_active       boolean DEFAULT true,
  effective_date  date DEFAULT CURRENT_DATE,   -- SCD2: when this version became active
  expiry_date     date DEFAULT '9999-12-31',   -- SCD2: when this version was superseded
  is_current      boolean DEFAULT true         -- SCD2: convenience flag for current version
);

COMMENT ON TABLE dim_source IS
  'Conformed source dimension (SCD Type 2). '
  'Grain: one row per source per version. '
  'History preserved via effective_date/expiry_date/is_current.';

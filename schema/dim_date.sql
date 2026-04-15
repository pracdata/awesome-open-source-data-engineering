-- schema/dim_date.sql
-- Kimball gold-standard date dimension (Ch 1.5, Appendix A)
-- Pre-populated 2020-2035 (5,844 rows). Every fact table joins via date_key.
---
cubes:
  - name: dim_date
    sql_table: public.dim_date
    dimensions:
      - name: date_key
        sql: "{CUBE}.date_key"
        type: number
        primary_key: true
      - name: full_date
        sql: "{CUBE}.full_date"
        type: time
      - name: day_name
        sql: "{CUBE}.day_name"
        type: string
      - name: month_name
        sql: "{CUBE}.month_name"
        type: string
      - name: quarter
        sql: "{CUBE}.quarter"
        type: number
      - name: year
        sql: "{CUBE}.year"
        type: number
      - name: fiscal_quarter
        sql: "{CUBE}.fiscal_quarter"
        type: number
      - name: fiscal_year
        sql: "{CUBE}.fiscal_year"
        type: number
      - name: is_weekend
        sql: "{CUBE}.is_weekend"
        type: boolean
      - name: is_holiday
        sql: "{CUBE}.is_holiday"
        type: boolean
    meta:
      kimball: conformed_dimension
---
CREATE TABLE IF NOT EXISTS dim_date (
  date_key            integer     PRIMARY KEY,   -- YYYYMMDD surrogate
  full_date           date        UNIQUE NOT NULL,
  day_of_week         smallint    NOT NULL,       -- 1=Mon, 7=Sun (ISO)
  day_name            text        NOT NULL,
  day_of_month        smallint    NOT NULL,
  day_of_year         smallint    NOT NULL,
  week_of_year        smallint    NOT NULL,       -- ISO week
  month_number        smallint    NOT NULL,
  month_name          text        NOT NULL,
  quarter             smallint    NOT NULL,
  year                smallint    NOT NULL,
  fiscal_quarter      smallint,
  fiscal_year         smallint,
  is_weekend          boolean     NOT NULL DEFAULT false,
  is_holiday          boolean     NOT NULL DEFAULT false,
  holiday_name        text,
  is_current_day      boolean     DEFAULT false,
  is_current_month    boolean     DEFAULT false,
  is_current_quarter  boolean     DEFAULT false,
  is_current_year     boolean     DEFAULT false
);

COMMENT ON TABLE dim_date IS
  'Kimball gold-standard date dimension. Pre-loaded 2020-2035 (5,844 rows). '
  'Grain: one row per calendar date.';

-- Populate dim_date: 2020-01-01 through 2035-12-31
INSERT INTO dim_date (
  date_key, full_date, day_of_week, day_name, day_of_month, day_of_year,
  week_of_year, month_number, month_name, quarter, year,
  fiscal_quarter, fiscal_year, is_weekend
)
SELECT
  TO_CHAR(d, 'YYYYMMDD')::integer AS date_key,
  d AS full_date,
  EXTRACT(ISODOW FROM d)::smallint AS day_of_week,
  TO_CHAR(d, 'Day') AS day_name,
  EXTRACT(DAY FROM d)::smallint AS day_of_month,
  EXTRACT(DOY FROM d)::smallint AS day_of_year,
  EXTRACT(WEEK FROM d)::smallint AS week_of_year,
  EXTRACT(MONTH FROM d)::smallint AS month_number,
  TO_CHAR(d, 'Month') AS month_name,
  EXTRACT(QUARTER FROM d)::smallint AS quarter,
  EXTRACT(YEAR FROM d)::smallint AS year,
  EXTRACT(QUARTER FROM d)::smallint AS fiscal_quarter,
  EXTRACT(YEAR FROM d)::smallint AS fiscal_year,
  EXTRACT(ISODOW FROM d) IN (6, 7) AS is_weekend
FROM generate_series('2020-01-01'::date, '2035-12-31'::date, '1 day'::interval) AS d
ON CONFLICT (date_key) DO NOTHING;

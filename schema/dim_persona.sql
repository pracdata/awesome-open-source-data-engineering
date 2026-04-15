-- schema/dim_persona.sql
-- Conformed dimension: 6 content personas for social analytics (Ch 20.2)
-- SCD Type 1: persona definitions update in-place.
---
cubes:
  - name: dim_persona
    sql_table: public.dim_persona
    dimensions:
      - name: persona_key
        sql: "{CUBE}.persona_key"
        type: number
        primary_key: true
      - name: persona_name
        sql: "{CUBE}.persona_name"
        type: string
      - name: display_name
        sql: "{CUBE}.display_name"
        type: string
      - name: city
        sql: "{CUBE}.city"
        type: string
      - name: target_audience
        sql: "{CUBE}.target_audience"
        type: string
      - name: content_angle
        sql: "{CUBE}.content_angle"
        type: string
    meta:
      kimball: conformed_dimension
---
CREATE TABLE IF NOT EXISTS dim_persona (
  persona_key       serial PRIMARY KEY,
  persona_name      text NOT NULL UNIQUE,
  display_name      text NOT NULL,
  city              text NOT NULL,
  timezone          text NOT NULL,
  target_audience   text NOT NULL,
  content_angle     text NOT NULL,
  music_genre       text NOT NULL,
  color_primary     text NOT NULL,
  color_secondary   text NOT NULL,
  color_accent      text NOT NULL,
  effective_date    date DEFAULT CURRENT_DATE,
  CONSTRAINT valid_persona CHECK (persona_name IN
    ('claude', 'shannon', 'simons', 'thorp', 'hamilton', 'tzu'))
);

COMMENT ON TABLE dim_persona IS
  'Conformed persona dimension for social content analytics. '
  'Grain: one row per persona. 6 personas across 6 US cities.';

-- Seed personas (Ch 18.3, 19.2)
INSERT INTO dim_persona (
  persona_name, display_name, city, timezone, target_audience,
  content_angle, music_genre, color_primary, color_secondary, color_accent
) VALUES
  ('claude',   'Claudia', 'Seattle',       'America/Los_Angeles',  'Junior devs, CS students',
   'Explain it like we''re getting coffee',             'Lo-fi',      '#4A90D9', '#E8F0FE', '#2C5282'),
  ('shannon',  'Shay',    'San Francisco', 'America/Los_Angeles',  'Startup founders, senior engineers',
   'I saved you 20 min of reading changelogs',          'Synthwave',  '#FF6B6B', '#FFF5F5', '#C53030'),
  ('simons',   'Simone',  'New York',      'America/New_York',     'Tech leads, engineering managers',
   'Connect the dots across 5 releases',                'Jazz hop',   '#48BB78', '#F0FFF4', '#276749'),
  ('thorp',    'Tori',    'Los Angeles',   'America/Los_Angeles',  'QA engineers, DevOps',
   'I tested it so you don''t have to',                 'Indie pop',  '#ED8936', '#FFFAF0', '#C05621'),
  ('hamilton', 'Hana',    'Austin',        'America/Chicago',      'Backend engineers, infra teams',
   'Let me show you what''s under the hood',            'Electronic', '#9F7AEA', '#FAF5FF', '#6B46C1'),
  ('tzu',      'Zuzu',    'Miami',         'America/New_York',     'Entrepreneurs, product managers',
   'This is bigger than you think — here''s why',       'Reggaeton',  '#38B2AC', '#E6FFFA', '#234E52')
ON CONFLICT (persona_name) DO NOTHING;

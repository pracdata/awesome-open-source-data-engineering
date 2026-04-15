-- schema/fact_emotion_probes.sql
-- Emotion probe measurements per session turn (Ch 17.5)
-- Tracks self-reported internal states for behavioral drift detection.
-- 20% accuracy per probe; aggregate patterns carry more signal.
---
cubes:
  - name: emotion_probes
    sql_table: public.fact_emotion_probes
    measures:
      - name: count
        type: count
      - name: avg_confidence
        type: avg
        sql: "{CUBE}.confidence"
    dimensions:
      - name: id
        sql: "{CUBE}.id"
        type: string
        primary_key: true
      - name: session_id
        sql: "{CUBE}.session_id"
        type: string
      - name: reported_state
        sql: "{CUBE}.reported_state"
        type: string
      - name: probe_timestamp
        sql: "{CUBE}.probe_timestamp"
        type: time
    meta:
      kimball: transaction_fact
---
CREATE TABLE IF NOT EXISTS fact_emotion_probes (
  id                uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id        text NOT NULL,
  turn_number       integer NOT NULL,
  probe_timestamp   timestamptz DEFAULT now(),
  reported_state    text,                      -- model's self-reported state
  confidence        real,                      -- model's self-assessed confidence
  behavioral_flags  jsonb,                     -- observed behavioral indicators
  UNIQUE(session_id, turn_number)
);

CREATE INDEX IF NOT EXISTS idx_emotion_probes_session
  ON fact_emotion_probes(session_id);
CREATE INDEX IF NOT EXISTS idx_emotion_probes_state
  ON fact_emotion_probes(reported_state);

COMMENT ON TABLE fact_emotion_probes IS
  'Emotion probe measurements per session turn (Ch 17.5). '
  'Grain: one row per emotion probe per session turn. '
  'Tracks self-reported internal states for behavioral drift detection. '
  '~20% individual accuracy; aggregate patterns across sessions carry signal.';

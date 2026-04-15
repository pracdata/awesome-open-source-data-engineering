-- schema/telemetry_spans.sql
-- OTLP trace spans from Agent SDK (Ch 15.2, Appendix A)
-- Dual role: transaction fact table AND audit dimension.
-- Records every agent tool call, model request, and pipeline operation.
---
cubes:
  - name: telemetry_spans
    sql_table: public.telemetry_spans
    measures:
      - name: count
        type: count
      - name: total_cost
        type: sum
        sql: "{CUBE}.estimated_cost_usd"
      - name: avg_duration
        type: avg
        sql: "{CUBE}.duration_ms"
      - name: total_input_tokens
        type: sum
        sql: "{CUBE}.input_tokens"
      - name: total_output_tokens
        type: sum
        sql: "{CUBE}.output_tokens"
    dimensions:
      - name: id
        sql: "{CUBE}.id"
        type: string
        primary_key: true
      - name: trace_id
        sql: "{CUBE}.trace_id"
        type: string
      - name: operation
        sql: "{CUBE}.operation"
        type: string
      - name: agent_tier
        sql: "{CUBE}.agent_tier"
        type: string
      - name: model
        sql: "{CUBE}.model"
        type: string
      - name: status
        sql: "{CUBE}.status"
        type: string
      - name: started_at
        sql: "{CUBE}.started_at"
        type: time
    meta:
      kimball: transaction_fact
      kimball_secondary: audit_dimension
---
CREATE TABLE IF NOT EXISTS telemetry_spans (
  id                 uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  trace_id           text NOT NULL,
  span_id            text NOT NULL,
  parent_span_id     text,
  operation          text NOT NULL,
  service            text,
  agent_tier         text,                    -- matches dispatch tier
  started_at         timestamptz NOT NULL DEFAULT now(),
  duration_ms        integer,
  input_tokens       integer,                 -- additive measure
  output_tokens      integer,                 -- additive measure
  cache_read_tokens  integer,
  cache_write_tokens integer,
  estimated_cost_usd numeric(10,6),           -- semi-additive
  model              text,
  status             text,
  metadata           jsonb,
  UNIQUE (trace_id, span_id)
);

CREATE INDEX IF NOT EXISTS idx_telemetry_time
  ON telemetry_spans(started_at);
CREATE INDEX IF NOT EXISTS idx_telemetry_trace
  ON telemetry_spans(trace_id);
CREATE INDEX IF NOT EXISTS idx_telemetry_operation
  ON telemetry_spans(operation);

COMMENT ON TABLE telemetry_spans IS
  'OTLP trace spans from Agent SDK. Dual role: transaction fact AND audit dimension. '
  'Grain: one row per span. '
  'Additive measures: duration_ms, input_tokens, output_tokens.';

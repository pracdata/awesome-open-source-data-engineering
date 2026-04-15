-- schema/bloom_filter_state.sql
-- Persisted bloom filter state across crawler restarts (Ch 5.6.1)
-- Each crawler maintains one row per (crawler_id, domain).
---
CREATE TABLE IF NOT EXISTS bloom_filter_state (
  filter_id           serial PRIMARY KEY,
  crawler_id          varchar(100) NOT NULL,     -- e.g. 'scrapy-docsync'
  domain              varchar(255) NOT NULL,     -- e.g. 'code.claude.com'
  expected_items      integer NOT NULL,
  false_positive_rate numeric(8,7) NOT NULL,
  hash_functions      smallint NOT NULL,
  bit_array_size      integer NOT NULL,
  items_inserted      integer NOT NULL DEFAULT 0,
  filter_bytes        bytea NOT NULL,            -- serialized bloom binary
  updated_at          timestamptz DEFAULT now(),
  UNIQUE (crawler_id, domain)
);

COMMENT ON TABLE bloom_filter_state IS
  'Persisted rbloom filter state for cross-restart URL dedup. '
  'Grain: one row per crawler_id + domain. '
  'Converts bloom filter from ephemeral to persistent (Ch 5.6.1).';

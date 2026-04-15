-- schema/view_unified_social_metrics.sql
-- Cross-platform normalized view for social analytics (Ch 20.10)
-- Normalizes platform-specific units to a common format:
--   YouTube minutes -> seconds, Instagram ms -> seconds, etc.
---
CREATE OR REPLACE VIEW view_unified_social_metrics AS
SELECT
  p.post_id,
  dp.persona_name,
  dp.display_name,
  dp.city,
  p.platform,
  p.changelog_version,
  p.content_phase,
  p.published_at,
  dd.full_date AS metric_date,
  m.views,
  m.likes,
  m.comments,
  m.shares,
  m.saves,
  m.watch_time_seconds,
  m.completion_rate,
  m.click_through_rate,
  m.follows_from_post,
  -- Engagement rate: (likes + comments + shares) / views
  CASE WHEN m.views > 0
    THEN (m.likes + m.comments + m.shares)::numeric / m.views
    ELSE 0
  END AS engagement_rate,
  p.ad_spend_cents / 100.0 AS ad_spend_usd
FROM fact_social_metrics m
JOIN fact_social_posts p ON m.post_id = p.post_id
JOIN dim_persona dp ON p.persona_key = dp.persona_key
JOIN dim_date dd ON m.date_key = dd.date_key;

COMMENT ON VIEW view_unified_social_metrics IS
  'Cross-platform normalized social metrics. '
  'Joins fact_social_metrics with post and persona dimensions. '
  'Computes engagement_rate inline (Ch 20.10).';

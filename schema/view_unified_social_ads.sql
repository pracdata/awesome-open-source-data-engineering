-- schema/view_unified_social_ads.sql
-- Cross-platform ad performance view (Ch 20.10)
-- Normalizes ad metrics and computes ROAS inline.
---
CREATE OR REPLACE VIEW view_unified_social_ads AS
SELECT
  a.id AS ad_id,
  dp.persona_name,
  dp.display_name,
  dp.city,
  a.platform,
  dd.full_date AS ad_date,
  a.ad_format,
  a.spend_cents / 100.0 AS spend_usd,
  a.impressions,
  a.clicks,
  a.conversions,
  a.cpm_cents / 100.0 AS cpm_usd,
  a.cpc_cents / 100.0 AS cpc_usd,
  -- Video completion funnel
  a.video_views_25pct,
  a.video_views_50pct,
  a.video_views_75pct,
  a.video_views_100pct,
  -- Completion funnel rates
  CASE WHEN a.video_views_25pct > 0
    THEN a.video_views_50pct::numeric / a.video_views_25pct
    ELSE 0
  END AS funnel_25_to_50,
  CASE WHEN a.video_views_50pct > 0
    THEN a.video_views_100pct::numeric / a.video_views_50pct
    ELSE 0
  END AS funnel_50_to_100,
  -- ROAS
  a.roas
FROM fact_social_ads a
JOIN dim_persona dp ON a.persona_key = dp.persona_key
JOIN dim_date dd ON a.date_key = dd.date_key;

COMMENT ON VIEW view_unified_social_ads IS
  'Cross-platform ad performance with video completion funnel. '
  'Normalizes currency from cents to USD. '
  'Computes funnel conversion rates inline (Ch 20.10).';

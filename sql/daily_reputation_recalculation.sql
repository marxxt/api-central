-- File: daily_reputation_recalculation.sql
-- Description: Recalculates percentile-based ranks for users and DAOs
-- Generated: 2025-05-29T17:59:02.059780 UTC

WITH ranked AS (
  SELECT
    subject_type,
    subject_id,
    score,
    PERCENT_RANK() OVER (
      PARTITION BY subject_type
      ORDER BY score DESC
    ) AS pct
  FROM public.reputations
  WHERE score IS NOT NULL
)

UPDATE public.reputations r
SET
  ranking_percentile = ROUND(rk.pct * 100)::text || '%',
  rank = CASE
    WHEN rk.pct >= 0.99 THEN 'SSS'
    WHEN rk.pct >= 0.95 THEN 'SS'
    WHEN rk.pct >= 0.85 THEN 'S'
    WHEN rk.pct >= 0.65 THEN 'A'
    WHEN rk.pct >= 0.40 THEN 'B'
    WHEN rk.pct >= 0.20 THEN 'C'
    WHEN rk.pct >= 0.05 THEN 'D'
    ELSE 'F'
  END,
  updated_at = now()
FROM ranked rk
WHERE
  r.subject_type = rk.subject_type AND
  r.subject_id = rk.subject_id;

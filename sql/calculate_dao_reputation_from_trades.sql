-- File: calculate_dao_reputation_from_trades.sql
-- Description: Calculates and updates DAO reputation based on profitable trades only
-- Generated: 2025-05-29T18:05:16.630250 UTC

-- Assumes there's a field 'dao_id' in the 'trades' table for DAO-originated trades
-- and a 'pnl' (profit and loss) column representing net trade performance

WITH profitable_dao_trades AS (
  SELECT
    dao_id,
    COUNT(*) AS positive_trade_count,
    SUM(pnl) AS total_profit
  FROM public.trades
  WHERE pnl > 0 AND dao_id IS NOT NULL
  GROUP BY dao_id
)

UPDATE public.reputations r
SET score = pdt.total_profit,
    last_updated = now()
FROM profitable_dao_trades pdt
WHERE r.subject_type = 'dao' AND r.subject_id = pdt.dao_id;

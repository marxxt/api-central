CREATE VIEW public.dao_cap_table AS
SELECT
  dth.dao_id,
  dth.user_id,
  u.email,
  dth.token_amount,
  (dth.token_amount / SUM(dth.token_amount) OVER (PARTITION BY dth.dao_id)) AS voting_percent
FROM public.dao_token_holdings dth
JOIN auth.users u ON u.id = dth.user_id;
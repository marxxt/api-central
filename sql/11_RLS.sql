-- === Enable RLS and define basic policies ===

-- Gamification Core Tables


-- Notifications and Limits
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage their notifications" ON public.notifications
  FOR ALL USING (auth.uid() = recipient_id) WITH CHECK (auth.uid() = recipient_id);


-- DAO Voting Epochs
ALTER TABLE public.dao_voting_epochs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow read" ON public.dao_voting_epochs FOR SELECT USING (true);


-- 1. daos
ALTER TABLE public.daos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated can SELECT their daos"
  ON public.daos FOR SELECT
  USING (auth.uid() IS NOT NULL);








-- 9. snft_balances
ALTER TABLE public.snft_balances ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated can SELECT SNFT balances"
  ON public.snft_balances FOR SELECT
  USING (auth.uid() IS NOT NULL);

-- 10. snft_mint_events
ALTER TABLE public.snft_mint_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated can SELECT SNFT mint events"
  ON public.snft_mint_events FOR SELECT
  USING (auth.uid() IS NOT NULL);

-- 11. snft_events
ALTER TABLE public.snft_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated can SELECT SNFT events"
  ON public.snft_events FOR SELECT
  USING (auth.uid() IS NOT NULL);

-- 12. snft_metadata_retry_queue
ALTER TABLE public.snft_metadata_retry_queue ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated can SELECT metadata retry"
  ON public.snft_metadata_retry_queue FOR SELECT
  USING (auth.uid() IS NOT NULL);

-- 13. badges
ALTER TABLE public.badges ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated can SELECT badges"
  ON public.badges FOR SELECT
  USING (auth.uid() IS NOT NULL);

-- 14. user_badges
ALTER TABLE public.user_badges ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated can SELECT their user badges"
  ON public.user_badges FOR SELECT
  USING (auth.uid() IS NOT NULL);

-- 15. badge_voting_roles
ALTER TABLE public.badge_voting_roles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated can SELECT voting roles"
  ON public.badge_voting_roles FOR SELECT
  USING (auth.uid() IS NOT NULL);

-- 16. dao_token_holdings
ALTER TABLE public.dao_token_holdings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated can SELECT token holdings"
  ON public.dao_token_holdings FOR SELECT
  USING (auth.uid() IS NOT NULL);

-- 17. ip_event_log
ALTER TABLE public.ip_event_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated can SELECT IP logs"
  ON public.ip_event_log FOR SELECT
  USING (auth.uid() IS NOT NULL);

-- 18. property_rewards
ALTER TABLE public.property_rewards ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated can SELECT property rewards"
  ON public.property_rewards FOR SELECT
  USING (auth.uid() IS NOT NULL);

-- 19. ohlc_data
ALTER TABLE public.ohlc_data ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated can SELECT OHLC"
  ON public.ohlc_data FOR SELECT
  USING (auth.uid() IS NOT NULL);

-- 20. volume_data
ALTER TABLE public.volume_data ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated can SELECT volume data"
  ON public.volume_data FOR SELECT
  USING (auth.uid() IS NOT NULL);
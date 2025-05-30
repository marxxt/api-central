-- File: gamification_xp_badge_logic.sql
-- Description: XP calculation logic and badge award triggers
-- Generated: 2025-05-29T18:18:39.422442 UTC

-- 1. XP Reward Rules: Define points per action (can be moved to config table later)

-- We'll define rules like:
-- - Comment = +5 XP
-- - Reply = +3 XP
-- - Share = +4 XP
-- - Kudos received = +10 XP
-- - Mention received = +2 XP

-- 2. XP Increment Functions (comment example)

CREATE OR REPLACE FUNCTION public.increment_xp_for_comment()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE public.user_stats
  SET xp = xp + 5,
      last_action_date = CURRENT_DATE,
      activity_streak = CASE
        WHEN last_action_date = CURRENT_DATE - INTERVAL '1 day' THEN activity_streak + 1
        WHEN last_action_date = CURRENT_DATE THEN activity_streak
        ELSE 1
      END,
      last_updated = now()
  WHERE user_id = NEW.user_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_increment_xp_comment
AFTER INSERT ON public.comments
FOR EACH ROW
EXECUTE FUNCTION public.increment_xp_for_comment();

-- Repeat for shares, mentions, kudos, etc.

-- 3. Badge Award Trigger (example: 100 XP badge)

CREATE OR REPLACE FUNCTION public.award_100xp_badge()
RETURNS TRIGGER AS $$
DECLARE
  badge_id uuid;
BEGIN
  SELECT id INTO badge_id FROM public.badges WHERE slug = '100xp' LIMIT 1;
  IF NEW.xp >= 100 THEN
    INSERT INTO public.user_badges(user_id, badge_id)
    VALUES (NEW.user_id, badge_id)
    ON CONFLICT DO NOTHING;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_award_100xp_badge
AFTER UPDATE ON public.user_stats
FOR EACH ROW
WHEN (NEW.xp >= 100 AND OLD.xp < 100)
EXECUTE FUNCTION public.award_100xp_badge();

-- 4. View to Fetch User Profile With Badges

CREATE OR REPLACE VIEW public.user_profile_view AS
SELECT
  u.id AS user_id,
  u.username,
  us.xp,
  us.activity_streak,
  us.rank,
  us.favorite_count,
  us.star_count,
  us.mention_count,
  us.comment_count,
  COALESCE(json_agg(json_build_object(
    'badge', b.name,
    'slug', b.slug,
    'image', b.image_url,
    'earned_at', ub.earned_at
  )) FILTER (WHERE b.id IS NOT NULL), '[]') AS badges
FROM auth.users u
JOIN public.user_stats us ON u.id = us.user_id
LEFT JOIN public.user_badges ub ON ub.user_id = u.id
LEFT JOIN public.badges b ON b.id = ub.badge_id
GROUP BY u.id, us.xp, us.rank, us.activity_streak, us.favorite_count, us.star_count, us.mention_count, us.comment_count;

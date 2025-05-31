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

-- Table for Comments
-- Table for Comments
DROP TABLE IF EXISTS public.comments CASCADE;

CREATE TABLE public.comments (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    asset_type text NOT NULL CHECK (asset_type IN ('snft', 'post', 'property', 'bot_strategy', 'chat_message')),
    asset_id text NOT NULL,
    parent_id uuid REFERENCES public.comments(id) ON DELETE CASCADE, -- for replies
    content text NOT NULL,
    is_edited boolean DEFAULT FALSE,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz
);

DROP INDEX IF EXISTS idx_comments_asset;
DROP INDEX IF EXISTS idx_comments_parent_id;

CREATE INDEX idx_comments_asset ON public.comments(asset_type, asset_id);
CREATE INDEX idx_comments_parent_id ON public.comments(parent_id);

ALTER TABLE public.comments ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view comments" ON public.comments;
DROP POLICY IF EXISTS "Users can comment" ON public.comments;
DROP POLICY IF EXISTS "Users can edit own comments" ON public.comments;
DROP POLICY IF EXISTS "Users can delete own comments" ON public.comments;

CREATE POLICY "Users can view comments" ON public.comments
    FOR SELECT USING (TRUE);  -- or restrict to asset visibility
CREATE POLICY "Users can comment" ON public.comments
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can edit own comments" ON public.comments
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own comments" ON public.comments
    FOR DELETE USING (auth.uid() = user_id);

CREATE TRIGGER set_comments_timestamp
    BEFORE UPDATE ON public.comments
    FOR EACH ROW
    EXECUTE FUNCTION public.set_update_timestamp();

-- Table for Shares
DROP TABLE IF EXISTS public.shares CASCADE;

CREATE TABLE public.shares (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    asset_type text NOT NULL CHECK (asset_type IN ('snft', 'post', 'property', 'bot_strategy')),
    asset_id text NOT NULL,
    shared_with text, -- 'public', 'followers', or a specific DAO ID or user ID
    comment text, -- optional caption or note
    shared_at timestamptz DEFAULT now()
);

DROP INDEX IF EXISTS idx_shares_asset;
DROP INDEX IF EXISTS idx_shares_user_id;

CREATE INDEX idx_shares_asset ON public.shares(asset_type, asset_id);
CREATE INDEX idx_shares_user_id ON public.shares(user_id);

ALTER TABLE public.shares ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view shared assets" ON public.shares;
DROP POLICY IF EXISTS "Users can share assets" ON public.shares;

CREATE POLICY "Users can view shared assets" ON public.shares
    FOR SELECT USING (TRUE); -- or conditionally based on shared_with
CREATE POLICY "Users can share assets" ON public.shares
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE OR REPLACE FUNCTION public.increment_comment_counts()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.parent_id IS NULL THEN
    -- It's a top-level comment
    INSERT INTO public.user_stats (user_id, comment_count)
    VALUES (NEW.user_id, 1)
    ON CONFLICT (user_id)
    DO UPDATE SET comment_count = user_stats.comment_count + 1,
                  last_updated = now();
  ELSE
    -- It's a reply
    INSERT INTO public.user_stats (user_id, reply_count)
    VALUES (NEW.user_id, 1)
    ON CONFLICT (user_id)
    DO UPDATE SET reply_count = user_stats.reply_count + 1,
                  last_updated = now();
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_increment_comment_count
AFTER INSERT ON public.comments
FOR EACH ROW
EXECUTE FUNCTION public.increment_comment_counts();

CREATE OR REPLACE FUNCTION public.increment_share_count()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_stats (user_id, share_count)
  VALUES (NEW.user_id, 1)
  ON CONFLICT (user_id)
  DO UPDATE SET share_count = user_stats.share_count + 1,
                last_updated = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_increment_share_count
AFTER INSERT ON public.shares
FOR EACH ROW
EXECUTE FUNCTION public.increment_share_count();

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
  u.raw_user_meta_data ->> 'username',
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

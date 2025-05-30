-- File: gamification_core.sql
-- Description: CORE gamification foundation for Bridges Market
-- Generated: 2025-05-29T18:17:27.380454 UTC

-- 1. XP + Activity Streaks + Stats in user_stats

ALTER TABLE public.user_stats
ADD COLUMN xp integer DEFAULT 0,
ADD COLUMN activity_streak integer DEFAULT 0,
ADD COLUMN last_action_date date;

-- 2. Badges Table (assignable UI or NFT badges)

CREATE TABLE IF NOT EXISTS public.badges (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    slug text UNIQUE NOT NULL,  -- e.g., 'early-contributor', 'top-1-percent'
    name text NOT NULL,
    description text,
    image_url text,
    is_nft boolean DEFAULT false,
    created_at timestamptz DEFAULT now()
);

-- 3. User-Badge Join Table

CREATE TABLE IF NOT EXISTS public.user_badges (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    badge_id uuid REFERENCES public.badges(id) ON DELETE CASCADE,
    earned_at timestamptz DEFAULT now(),
    UNIQUE(user_id, badge_id)
);

-- 4. Leaderboard View (top users by XP)

CREATE OR REPLACE VIEW public.user_leaderboard AS
SELECT
    u.id AS user_id,
    u.username,
    us.xp,
    us.rank,
    us.favorite_count,
    us.star_count,
    us.mention_count,
    us.comment_count
FROM public.auth.users u
JOIN public.user_stats us ON u.id = us.user_id
ORDER BY us.xp DESC
LIMIT 100;

-- 5. Profile Exposure: to be used in GraphQL and frontend
-- Fields from user_stats and user_badges should be exposed

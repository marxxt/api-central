
-- File: badge_voting_roles.sql

CREATE TABLE IF NOT EXISTS public.badge_voting_roles (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    badge_slug text NOT NULL,
    dao_role text NOT NULL,
    vote_boost integer DEFAULT 0, -- extra votes
    can_create_proposals boolean DEFAULT false,
    can_moderate boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now()
);

CREATE UNIQUE INDEX idx_badge_slug_role ON public.badge_voting_roles(badge_slug, dao_role);

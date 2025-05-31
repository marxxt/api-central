
-- File: property_rewards.sql

CREATE TABLE IF NOT EXISTS public.property_rewards (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    badge_id uuid REFERENCES public.user_badges(id) ON DELETE SET NULL,
    property_id uuid REFERENCES public.properties(id) ON DELETE CASCADE,
    nights_awarded integer NOT NULL DEFAULT 1,
    nights_used integer NOT NULL DEFAULT 0,
    valid_from timestamp with time zone DEFAULT now(),
    valid_to timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);

DROP INDEX IF EXISTS idx_property_rewards_user_id;
DROP INDEX IF EXISTS idx_property_rewards_property_id;

CREATE INDEX idx_property_rewards_user_id ON public.property_rewards(user_id);
CREATE INDEX idx_property_rewards_property_id ON public.property_rewards(property_id);

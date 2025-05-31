-- File: notifications_and_limits.sql
-- Description: Notifications table + abuse protection logic
-- Generated: auto

-- 1. Notifications Table
DROP TABLE IF EXISTS public.notifications;

CREATE TABLE IF NOT EXISTS public.notifications (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    type text NOT NULL CHECK (type IN ('mention', 'xp', 'badge', 'follow', 'snft_status')),
    metadata jsonb,
    is_read boolean DEFAULT FALSE,
    created_at timestamptz DEFAULT now()
);

DROP INDEX IF EXISTS idx_notifications_recipient; 

CREATE INDEX idx_notifications_recipient ON public.notifications(recipient_id);

ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view their notifications" ON public.notifications;

CREATE POLICY "Users can view their notifications" ON public.notifications
    FOR SELECT USING (auth.uid() = recipient_id);

-- 2. Rate Limiting Table (simple IP + event tracker)
DROP TABLE IF EXISTS public.ip_event_log;

CREATE TABLE IF NOT EXISTS public.ip_event_log (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    ip_address inet NOT NULL,
    event_type text NOT NULL CHECK (event_type IN ('comment', 'mention', 'share', 'login')),
    occurred_at timestamptz DEFAULT now()
);

DROP INDEX IF EXISTS idx_ip_event_log;

CREATE INDEX idx_ip_event_log ON public.ip_event_log(ip_address, event_type, occurred_at);

CREATE TABLE public.dao_token_holdings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    dao_id uuid NOT NULL REFERENCES public.daos(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    token_amount numeric NOT NULL DEFAULT 0,
    valuation_at_entry numeric,
    property_invested_ids uuid[],
    created_at timestamptz DEFAULT now()
);
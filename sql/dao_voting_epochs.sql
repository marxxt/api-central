CREATE TABLE public.dao_voting_epochs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    dao_id uuid REFERENCES public.daos(id),
    epoch_name TEXT,
    snapshot_time timestamptz DEFAULT now(),
    total_token_supply NUMERIC,
    total_nav NUMERIC,
    dilution_details JSONB
);
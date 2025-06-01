DROP TABLE IF EXISTS public.ohlc_data CASCADE;
DROP TABLE IF EXISTS public.volume_data CASCADE;

CREATE TABLE public.ohlc_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pair_id UUID NOT NULL REFERENCES public.trading_pairs(id) ON DELETE CASCADE,
    time TIMESTAMPTZ NOT NULL,
    open NUMERIC NOT NULL,
    high NUMERIC NOT NULL,
    low NUMERIC NOT NULL,
    close NUMERIC NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE TABLE public.volume_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pair_id UUID NOT NULL REFERENCES public.trading_pairs(id) ON DELETE CASCADE,
    time TIMESTAMPTZ NOT NULL,
    value NUMERIC NOT NULL,
    color TEXT,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);


DROP INDEX IF EXISTS idx_ohlc_pair_time;
DROP INDEX IF EXISTS idx_volume_pair_time;

CREATE INDEX idx_ohlc_pair_time ON public.ohlc_data(pair_id, time);
CREATE INDEX idx_volume_pair_time ON public.volume_data(pair_id, time);

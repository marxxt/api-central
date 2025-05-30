-- SQL Script to Create Additional Tables
-- Based on types: AIBotConfig, ActiveManualOrder, UserInvestment

-- Ensure you are connected to your Supabase database.
-- These commands are typically run via the Supabase UI SQL Editor or migrations.

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'rank') THEN
    CREATE TYPE rank AS ENUM ('SSS', 'SS', 'S', 'A', 'B', 'C', 'D', 'F');
  END IF;
END$$;



---------------------------------------------------------------------------------
-- Function to set updated_at timestamp (must be created before any triggers use it)
---------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.set_update_timestamp()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = now();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

---------------------------------------------------------------------------------
-- 1. Table for Wallets
-- Inferred from scripts/fake_data_generators.py and app/models/user.py
---------------------------------------------------------------------------------
DROP TABLE IF EXISTS public.wallets CASCADE;

CREATE TABLE public.wallets (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    address text NOT NULL,
    balance numeric NOT NULL,
    currency text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);

CREATE INDEX idx_wallets_user_id ON public.wallets (user_id);

ALTER TABLE public.wallets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own wallets" ON public.wallets
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create their own wallets" ON public.wallets
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own wallets" ON public.wallets
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own wallets" ON public.wallets
    FOR DELETE USING (auth.uid() = user_id);

CREATE TRIGGER set_wallets_timestamp
    BEFORE UPDATE ON public.wallets
    FOR EACH ROW
    EXECUTE FUNCTION public.set_update_timestamp();

---------------------------------------------------------------------------------
-- 2. Table for Reputations
-- Inferred from scripts/fake_data_generators.py and app/models/user.py
---------------------------------------------------------------------------------
DROP TABLE IF EXISTS public.reputations CASCADE;

CREATE TABLE public.reputations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    subject_type text NOT NULL CHECK (subject_type IN ('user', 'dao')),
    subject_id uuid NOT NULL, -- FK to auth.users or daos (informational; not enforced here)

    score numeric,
    rank rank,
    ranking_percentile text,
    last_updated timestamptz DEFAULT now(),

    adjusted_staking_yield text,
    forecast_access_level text,

    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz
);

CREATE UNIQUE INDEX idx_reputations_subject ON public.reputations(subject_type, subject_id);

-- Enable Row Level Security
ALTER TABLE public.reputations ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own reputations
CREATE POLICY "Users can view their own reputations"
ON public.reputations
FOR SELECT
TO authenticated
USING (
  subject_type = 'user' AND subject_id = auth.uid()
);

-- Policy: Users can create their own reputations
CREATE POLICY "Users can create their own reputations"
ON public.reputations
FOR INSERT
TO authenticated
WITH CHECK (
  subject_type = 'user' AND subject_id = auth.uid()
);

-- Policy: Users can update their own reputations
CREATE POLICY "Users can update their own reputations"
ON public.reputations
FOR UPDATE
TO authenticated
USING (
  subject_type = 'user' AND subject_id = auth.uid()
)
WITH CHECK (
  subject_type = 'user' AND subject_id = auth.uid()
);

-- Policy: Users can delete their own reputations
CREATE POLICY "Users can delete their own reputations"
ON public.reputations
FOR DELETE
TO authenticated
USING (
  subject_type = 'user' AND subject_id = auth.uid()
);

CREATE TRIGGER set_reputations_timestamp
    BEFORE UPDATE ON public.reputations
    FOR EACH ROW
    EXECUTE FUNCTION public.set_update_timestamp();

---------------------------------------------------------------------------------
-- 3. Table for Collections
-- Inferred from scripts/fake_data_generators.py
---------------------------------------------------------------------------------
DROP TABLE IF EXISTS public.collections CASCADE;

CREATE TABLE public.collections (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    name text NOT NULL,
    color text,
    count integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);

CREATE INDEX idx_collections_user_id ON public.collections (user_id);

ALTER TABLE public.collections ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own collections" ON public.collections
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create their own collections" ON public.collections
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own collections" ON public.collections
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own collections" ON public.collections
    FOR DELETE USING (auth.uid() = user_id);

CREATE TRIGGER set_collections_timestamp
    BEFORE UPDATE ON public.collections
    FOR EACH ROW
    EXECUTE FUNCTION public.set_update_timestamp();

---------------------------------------------------------------------------------
-- 4. Table for Properties (PropertyAsset)
-- Maps to the PropertyAsset interface
---------------------------------------------------------------------------------
DROP TABLE IF EXISTS public.properties CASCADE;

CREATE TABLE public.properties (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(), -- From SNFT.id or PropertyMarketplaceItem.id
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL, -- Link to the user who owns/listed the property
    name text NOT NULL, -- From SNFT.name or PropertyMarketplaceItem.title
    token_symbol text NOT NULL, -- e.g., "MBV"
    description text, -- From SNFT.description
    image_url text NOT NULL, -- From SNFT.imageUrl or PropertyMarketplaceItem.image
    address text NOT NULL, -- From SNFT.address or PropertyMarketplaceItem.location
    property_type text NOT NULL, -- e.g., 'SFR', 'MultiFamily', 'Commercial' (AssetType enum)
    status text, -- e.g., "For Sale", "Rented"

    -- Financials / Tokenomics
    valuation numeric,
    total_tokens numeric,
    apy numeric,

    -- Linking to original SNFT ID if applicable
    underlying_snft_id uuid, -- If this directly maps to an SNFT in your system

    -- Fields from your PropertyMarketplaceItem
    date_listed timestamp with time zone,

    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);

-- Add indexes for performance
CREATE INDEX idx_properties_user_id ON public.properties (user_id);
CREATE INDEX idx_properties_token_symbol ON public.properties (token_symbol);
CREATE INDEX idx_properties_property_type ON public.properties (property_type);

-- Enable Row Level Security
ALTER TABLE public.properties ENABLE ROW LEVEL SECURITY;

-- RLS Policies (Example: Users can view/manage their own properties)
CREATE POLICY "Users can view their own properties" ON public.properties
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create their own properties" ON public.properties
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own properties" ON public.properties
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own properties" ON public.properties
    FOR DELETE USING (auth.uid() = user_id);

-- Add trigger for updated_at column
CREATE TRIGGER set_properties_timestamp
    BEFORE UPDATE ON public.properties
    FOR EACH ROW
    EXECUTE FUNCTION public.set_update_timestamp();

---------------------------------------------------------------------------------
-- 5. Table for SNFTs
-- Inferred from app/models/snft.py and scripts/fake_data_generators.py
---------------------------------------------------------------------------------
DROP TABLE IF EXISTS public.snfts CASCADE;

CREATE TABLE public.snfts (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_id uuid REFERENCES public.wallets(id) ON DELETE CASCADE NOT NULL,
    owner_id uuid REFERENCES auth.users(id) ON DELETE CASCADE, -- Added owner_id
    name text NOT NULL,
    description text,
    image_url text NOT NULL,
    price numeric NOT NULL,
    currency text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone,
    address text NOT NULL,
    creator text,
    date_listed timestamp with time zone,
    status text,
    category text,
    collection_id uuid REFERENCES public.collections(id) ON DELETE SET NULL, -- Can be null if collection is deleted
    bid_price text,
    numeric_bid_price numeric
);

CREATE INDEX idx_snfts_wallet_id ON public.snfts (wallet_id);
CREATE INDEX idx_snfts_owner_id ON public.snfts (owner_id); -- Added index for owner_id
CREATE INDEX idx_snfts_collection_id ON public.snfts (collection_id);
CREATE INDEX idx_snfts_category ON public.snfts (category);

ALTER TABLE public.snfts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON public.snfts
    FOR SELECT USING (TRUE);
CREATE POLICY "Users can create SNFTs" ON public.snfts
    FOR INSERT WITH CHECK (auth.uid() = owner_id); -- Updated RLS to use owner_id
CREATE POLICY "Users can update their SNFTs" ON public.snfts
    FOR UPDATE USING (auth.uid() = owner_id); -- Updated RLS to use owner_id
CREATE POLICY "Users can delete their SNFTs" ON public.snfts
    FOR DELETE USING (auth.uid() = owner_id); -- Updated RLS to use owner_id

CREATE TRIGGER set_snfts_timestamp
    BEFORE UPDATE ON public.snfts
    FOR EACH ROW
    EXECUTE FUNCTION public.set_update_timestamp();

---------------------------------------------------------------------------------
-- 6. Table for Auctions
-- Inferred from scripts/fake_data_generators.py and app/models/auction.py
---------------------------------------------------------------------------------
DROP TABLE IF EXISTS public.auctions CASCADE;

CREATE TABLE public.auctions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id uuid REFERENCES public.properties(id) ON DELETE CASCADE NOT NULL,
    seller_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    type text NOT NULL, -- e.g., "Whole Project", "Individual Tokens"
    status text NOT NULL, -- e.g., "active", "pending", "closed", "completed"
    start_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone NOT NULL,
    starting_price numeric NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);

CREATE INDEX idx_auctions_property_id ON public.auctions (property_id);
CREATE INDEX idx_auctions_seller_id ON public.auctions (seller_id);
CREATE INDEX idx_auctions_status ON public.auctions (status);

ALTER TABLE public.auctions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON public.auctions
    FOR SELECT USING (TRUE);
CREATE POLICY "Users can create their own auctions" ON public.auctions
    FOR INSERT WITH CHECK (auth.uid() = seller_id);
CREATE POLICY "Users can update their own auctions" ON public.auctions
    FOR UPDATE USING (auth.uid() = seller_id);
CREATE POLICY "Users can delete their own auctions" ON public.auctions
    FOR DELETE USING (auth.uid() = seller_id);

CREATE TRIGGER set_auctions_timestamp
    BEFORE UPDATE ON public.auctions
    FOR EACH ROW
    EXECUTE FUNCTION public.set_update_timestamp();

---------------------------------------------------------------------------------
-- 7. Table for Trades
-- Inferred from scripts/fake_data_generators.py and app/models/trade.py
---------------------------------------------------------------------------------
DROP TABLE IF EXISTS public.trades CASCADE;

CREATE TABLE public.trades (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    asset text NOT NULL,
    type text NOT NULL, -- e.g., "buy", "sell"
    amount numeric NOT NULL,
    executed_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);

CREATE INDEX idx_trades_user_id ON public.trades (user_id);
CREATE INDEX idx_trades_asset ON public.trades (asset);
CREATE INDEX idx_trades_type ON public.trades (type);

ALTER TABLE public.trades ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own trades" ON public.trades
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create their own trades" ON public.trades
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own trades" ON public.trades
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own trades" ON public.trades
    FOR DELETE USING (auth.uid() = user_id);

CREATE TRIGGER set_trades_timestamp
    BEFORE UPDATE ON public.trades
    FOR EACH ROW
    EXECUTE FUNCTION public.set_update_timestamp();

---------------------------------------------------------------------------------
-- 8. Table for TradingPairs
-- Maps to the TradingPair interface
---------------------------------------------------------------------------------
DROP TABLE IF EXISTS public.trading_pairs CASCADE;

CREATE TABLE public.trading_pairs (
    id text PRIMARY KEY, -- e.g., "MBV_USDC"
    base_asset_id uuid REFERENCES public.properties(id) ON DELETE CASCADE NOT NULL, -- Links to the PropertyAsset
    base_asset_symbol text NOT NULL, -- PropertyAsset.tokenSymbol
    quote_asset_symbol text NOT NULL, -- e.g., "USDC", "ETH", "USDT"

    -- Market Data for the Pair
    last_price numeric NOT NULL,
    price_change_24h_percent numeric,
    high_24h numeric,
    low_24h numeric,
    volume_24h_base numeric,
    volume_24h_quote numeric,

    -- Chart History for the Pair (stored as JSONB)
    ohlc_history jsonb,
    volume_history jsonb,

    is_favorite boolean,
    order_book_id text,

    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);

-- Add indexes for performance
CREATE INDEX idx_trading_pairs_base_asset_id ON public.trading_pairs (base_asset_id);
CREATE INDEX idx_trading_pairs_base_asset_symbol ON public.trading_pairs (base_asset_symbol);
CREATE INDEX idx_trading_pairs_quote_asset_symbol ON public.trading_pairs (quote_asset_symbol);

-- Enable Row Level Security
ALTER TABLE public.trading_pairs ENABLE ROW LEVEL SECURITY;

-- RLS Policies (Example: All users can view trading pairs)
CREATE POLICY "Enable read access for all users" ON public.trading_pairs
    FOR SELECT USING (TRUE);

-- Add trigger for updated_at column
CREATE TRIGGER set_trading_pairs_timestamp
    BEFORE UPDATE ON public.trading_pairs
    FOR EACH ROW
    EXECUTE FUNCTION public.set_update_timestamp();

---------------------------------------------------------------------------------
-- 9. Table for AIBotConfig (User's AI Bot Configurations)
-- Maps to the AIBotConfig interface
---------------------------------------------------------------------------------
DROP TABLE IF EXISTS public.ai_bot_configs CASCADE; -- Uncomment to drop and recreate

CREATE TABLE public.ai_bot_configs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL, -- Links to the user who configured the bot
    trading_pair_id text REFERENCES public.trading_pairs(id) ON DELETE CASCADE NOT NULL, -- Links to the trading pair it operates on
    strategy text NOT NULL, -- e.g., 'Grid', 'DCA', 'ML_Trend', 'Arbitrage'
    investment_amount numeric NOT NULL, -- Amount allocated
    quote_asset_for_investment text NOT NULL, -- e.g., 'USDC'
    risk_level text, -- e.g., 'Low', 'Medium', 'High'
    is_active boolean DEFAULT TRUE NOT NULL, -- Is the bot currently active?
    config_params jsonb, -- Flexible storage for strategy-specific parameters
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone,

    -- Optional: Constraint that a user can only have one bot config per trading pair
    CONSTRAINT user_trading_pair_unique UNIQUE (user_id, trading_pair_id)
);

-- Add indexes for performance
CREATE INDEX idx_ai_bot_configs_user_id ON public.ai_bot_configs (user_id);
CREATE INDEX idx_ai_bot_configs_trading_pair_id ON public.ai_bot_configs (trading_pair_id);

-- Enable Row Level Security
ALTER TABLE public.ai_bot_configs ENABLE ROW LEVEL SECURITY;

-- Optional: RLS Policies (Example: Users can see/manage their own bot configs)
CREATE POLICY "Users can view their own bot configs" ON public.ai_bot_configs
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create their own bot configs" ON public.ai_bot_configs
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own bot configs" ON public.ai_bot_configs
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own bot configs" ON public.ai_bot_configs
    FOR DELETE USING (auth.uid() = user_id);

CREATE TRIGGER set_ai_bot_configs_timestamp
    BEFORE UPDATE ON public.ai_bot_configs
    FOR EACH ROW
    EXECUTE FUNCTION public.set_update_timestamp();

---------------------------------------------------------------------------------
-- 10. Table for Orders (Represents Open or Completed Manual/Bot Orders)
-- Maps to the ActiveManualOrder (and implicitly ManualOrderFormState) interfaces
---------------------------------------------------------------------------------
DROP TABLE IF EXISTS public.orders CASCADE; -- Uncomment to drop and recreate

CREATE TABLE public.orders (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL, -- Links to the user who placed the order
    trading_pair_id text REFERENCES public.trading_pairs(id) ON DELETE CASCADE NOT NULL, -- Links to the trading pair the order is for
    order_type text NOT NULL CHECK (order_type IN ('buy', 'sell')), -- 'buy' or 'sell'
    trade_type text NOT NULL CHECK (trade_type IN ('market', 'limit')), -- 'market' or 'limit'
    amount numeric NOT NULL, -- The total size of the order (base asset or quote asset)
    is_amount_in_base boolean NOT NULL, -- True if 'amount' refers to base asset, False for quote asset
    limit_price numeric, -- Required only for limit orders
    status text NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'filled', 'cancelled', 'partial_fill', 'expired')), -- Order status
    filled_amount numeric DEFAULT 0.0 NOT NULL, -- How much of the amount has been filled
    executed_at timestamp with time zone DEFAULT now() NOT NULL, -- Timestamp when the order was placed
    updated_at timestamp with time zone -- Timestamp of last status/fill update
);

CREATE INDEX idx_orders_user_pair_status ON public.orders (user_id, trading_pair_id, status);
CREATE INDEX idx_orders_trading_pair_status ON public.orders (trading_pair_id, status);

-- Add indexes for performance
CREATE INDEX idx_orders_user_id ON public.orders (user_id);
CREATE INDEX idx_orders_trading_pair_id ON public.orders (trading_pair_id);
CREATE INDEX idx_orders_status ON public.orders (status);


-- Enable Row Level Security
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;

-- Optional: RLS Policies (Example: Users can see/manage their own orders)
CREATE POLICY "Users can view their own orders" ON public.orders
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create their own orders" ON public.orders
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own orders" ON public.orders
    FOR UPDATE USING (auth.uid() = user_id); -- May need more complex logic if state transitions matter
CREATE POLICY "Users can delete their own orders" ON public.orders
    FOR DELETE USING (auth.uid() = user_id);

CREATE TRIGGER set_orders_timestamp
    BEFORE UPDATE ON public.orders
    FOR EACH ROW
    EXECUTE FUNCTION public.set_update_timestamp();

---------------------------------------------------------------------------------
-- 11. Table for UserInvestments (User Holdings of Property Assets)
-- Maps to the UserInvestment interface
---------------------------------------------------------------------------------
DROP TABLE IF EXISTS public.user_investments CASCADE; -- Uncomment to drop and recreate

CREATE TABLE public.user_investments (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL, -- Links to the user holding the investment
    property_asset_id uuid REFERENCES public.properties(id) ON DELETE CASCADE NOT NULL, -- Links to the specific property asset token
    tokens_owned numeric NOT NULL DEFAULT 0.0, -- Number of tokens held
    avg_buy_price_per_token numeric, -- Average price paid (in avg_buy_price_currency)
    avg_buy_price_currency text, -- Currency of avg_buy_price_per_token (e.g., 'USDC', 'ETH')
    purchase_date timestamp with time zone, -- Date of first/latest significant purchase for this holding
    status text CHECK (status IN ('Owned', 'Staked', 'ListedForSale', 'InBot')), -- Status of the holding

    -- Constraint: A user should typically only have one investment record per property asset
    CONSTRAINT user_property_asset_unique UNIQUE (user_id, property_asset_id),

    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone -- Timestamp of last update (e.g., tokens owned changed, status changed)
);

-- Add indexes for performance
CREATE INDEX idx_user_investments_user_id ON public.user_investments (user_id);
CREATE INDEX idx_user_investments_property_asset_id ON public.user_investments (property_asset_id);


-- Enable Row Level Security
ALTER TABLE public.user_investments ENABLE ROW LEVEL SECURITY;

-- Optional: RLS Policies (Example: Users can see their own investments)
CREATE POLICY "Users can view their own investments" ON public.user_investments
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create their own investments" ON public.user_investments
    FOR INSERT WITH CHECK (auth.uid() = user_id); -- May need to restrict this or handle carefully
CREATE POLICY "Users can update their own investments" ON public.user_investments
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own investments" ON public.user_investments
    FOR DELETE USING (auth.uid() = user_id);

CREATE TRIGGER set_user_investments_timestamp
    BEFORE UPDATE ON public.user_investments
    FOR EACH ROW
    EXECUTE FUNCTION public.set_update_timestamp();

---------------------------------------------------------------------------------
-- 12. Table for Bid History
-- Inferred from scripts/fake_data_generators.py and app/models/auction.py
---------------------------------------------------------------------------------
DROP TABLE IF EXISTS public.bid_history CASCADE;

CREATE TABLE public.bid_history (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    auction_id uuid REFERENCES public.auctions(id) ON DELETE CASCADE NOT NULL,
    bidder uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    amount numeric NOT NULL,
    time timestamp with time zone DEFAULT now() NOT NULL,
    epoch_timestamp bigint NOT NULL, -- Consider renaming to epoch_timestamp for clarity

    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);

CREATE INDEX idx_bid_history_auction_id ON public.bid_history (auction_id);
CREATE INDEX idx_bid_history_bidder ON public.bid_history (bidder);

ALTER TABLE public.bid_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON public.bid_history
    FOR SELECT USING (TRUE);
CREATE POLICY "Users can create their own bids" ON public.bid_history
    FOR INSERT WITH CHECK (auth.uid() = bidder);
CREATE POLICY "Users can update their own bids" ON public.bid_history
    FOR UPDATE USING (auth.uid() = bidder);
CREATE POLICY "Users can delete their own bids" ON public.bid_history
    FOR DELETE USING (auth.uid() = bidder);

CREATE TRIGGER set_bid_history_timestamp
    BEFORE UPDATE ON public.bid_history
    FOR EACH ROW
    EXECUTE FUNCTION public.set_update_timestamp();

---------------------------------------------------------------------------------
-- 13. Table for Transactions (SNFT Transactions)
-- Inferred from scripts/fake_data_generators.py and app/models/snft.py
---------------------------------------------------------------------------------
DROP TABLE IF EXISTS public.transactions CASCADE; 

CREATE TABLE public.transactions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    snft_id uuid REFERENCES public.snfts(id) ON DELETE CASCADE NOT NULL,
    type text NOT NULL CHECK (type IN ('BUY', 'SELL', 'TRANSFER', 'EXCHANGE', 'MINT', 'OTHER', 'UNKNOWN')),
    amount numeric,
    timestamp timestamp with time zone DEFAULT now(),

    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);

CREATE INDEX idx_transactions_snft_id ON public.transactions (snft_id);
CREATE INDEX idx_transactions_type ON public.transactions (type);

ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;

-- Added RLS Policies for transactions table
CREATE POLICY "Users can view their own transactions" ON public.transactions
    FOR SELECT USING (EXISTS (SELECT 1 FROM public.snfts WHERE public.snfts.id = snft_id AND public.snfts.owner_id = auth.uid()));
CREATE POLICY "Users can insert transactions" ON public.transactions
    FOR INSERT WITH CHECK (EXISTS (SELECT 1 FROM public.snfts WHERE public.snfts.id = snft_id AND public.snfts.owner_id = auth.uid()));

CREATE TRIGGER set_transactions_timestamp
    BEFORE UPDATE ON public.transactions
    FOR EACH ROW
    EXECUTE FUNCTION public.set_update_timestamp();

---------------------------------------------------------------------------------
-- 14. Table for DAO Proposals
-- Inferred from scripts/fake_data_generators.py
---------------------------------------------------------------------------------
DROP TABLE IF EXISTS public.dao_proposals CASCADE;

CREATE TABLE public.dao_proposals (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title text NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);

CREATE INDEX idx_dao_proposals_created_at ON public.dao_proposals (created_at);

ALTER TABLE public.dao_proposals ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON public.dao_proposals
    FOR SELECT USING (TRUE);
CREATE POLICY "Users can create DAO proposals" ON public.dao_proposals
    FOR INSERT WITH CHECK (TRUE); -- Assuming any authenticated user can create proposals

CREATE TRIGGER set_dao_proposals_timestamp
    BEFORE UPDATE ON public.dao_proposals
    FOR EACH ROW
    EXECUTE FUNCTION public.set_update_timestamp();

---------------------------------------------------------------------------------
-- 15. Table for DAO Votes
-- Inferred from scripts/fake_data_generators.py
---------------------------------------------------------------------------------
DROP TABLE IF EXISTS public.dao_votes CASCADE;

CREATE TABLE public.dao_votes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id uuid REFERENCES public.dao_proposals(id) ON DELETE CASCADE NOT NULL,
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    vote text NOT NULL CHECK (vote IN ('yes', 'no', 'abstain')),
    voted_at timestamp with time zone DEFAULT now(),

    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,

    CONSTRAINT user_vote_unique UNIQUE (proposal_id, user_id)
);

CREATE INDEX idx_dao_votes_proposal_id ON public.dao_votes (proposal_id);
CREATE INDEX idx_dao_votes_user_id ON public.dao_votes (user_id);

ALTER TABLE public.dao_votes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own votes" ON public.dao_votes
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create their own votes" ON public.dao_votes
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own votes" ON public.dao_votes
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own votes" ON public.dao_votes
    FOR DELETE USING (auth.uid() = user_id);

CREATE TRIGGER set_dao_votes_timestamp
    BEFORE UPDATE ON public.dao_votes
    FOR EACH ROW
    EXECUTE FUNCTION public.set_update_timestamp();

---------------------------------------------------------------------------------
-- 16. Table for user_stats (per-user metric tracking)
---------------------------------------------------------------------------------
DROP TABLE IF EXISTS public.user_stats CASCADE;

DROP TABLE IF EXISTS public.user_stats CASCADE;

CREATE TABLE public.user_stats (
    user_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Core metrics
    snft_count integer DEFAULT 0,
    trade_count integer DEFAULT 0,
    wallet_count integer DEFAULT 0,

    -- Social metrics
    comment_count integer DEFAULT 0,
    reply_count integer DEFAULT 0,
    share_count integer DEFAULT 0,
    favorite_count integer DEFAULT 0,
    star_count integer DEFAULT 0, -- how many users/DAOs this user has rated
    received_star_count integer DEFAULT 0, -- how many stars the user has received
    average_rating numeric, -- optional running avg of stars received

    last_updated timestamptz DEFAULT now()
);


-- Function to update SNFT count
CREATE OR REPLACE FUNCTION public.increment_snft_count()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_stats (user_id, snft_count)
  VALUES (NEW.owner_id, 1) -- Changed to NEW.owner_id
  ON CONFLICT (user_id)
  DO UPDATE SET snft_count = user_stats.snft_count + 1,
                last_updated = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- FUNCTION: increment_trade_count
CREATE OR REPLACE FUNCTION public.increment_trade_count()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_stats (user_id, trade_count)
  VALUES (NEW.user_id, 1)
  ON CONFLICT (user_id)
  DO UPDATE SET trade_count = user_stats.trade_count + 1,
                last_updated = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- FUNCTION: increment_wallet_count
CREATE OR REPLACE FUNCTION public.increment_wallet_count()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_stats (user_id, wallet_count)
  VALUES (NEW.user_id, 1)
  ON CONFLICT (user_id)
  DO UPDATE SET wallet_count = user_stats.wallet_count + 1,
                last_updated = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- TRIGGER: after insert on snfts
CREATE TRIGGER trg_increment_snft_count
AFTER INSERT ON public.snfts
FOR EACH ROW
EXECUTE FUNCTION public.increment_snft_count();

-- TRIGGER: after insert on trades
CREATE TRIGGER trg_increment_trade_count
AFTER INSERT ON public.trades
FOR EACH ROW
EXECUTE FUNCTION public.increment_trade_count();

-- TRIGGER: after insert on wallets
CREATE TRIGGER trg_increment_wallet_count
AFTER INSERT ON public.wallets
FOR EACH ROW
EXECUTE FUNCTION public.increment_wallet_count();

ALTER TABLE public.user_stats ENABLE ROW LEVEL SECURITY;

---------------------------------------------------------------------------------
-- 17. Table for platform_metrics (global admin stats)
---------------------------------------------------------------------------------
DROP TABLE IF EXISTS public.platform_metrics CASCADE;

CREATE TABLE public.platform_metrics (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    entity text NOT NULL, -- e.g., 'platform', 'user'
    entity_id uuid,       -- optional, used for per-user metrics
    metric_name text NOT NULL, -- e.g., 'total_users'
    metric_value numeric NOT NULL,
    recorded_at timestamp with time zone DEFAULT now()
);

CREATE INDEX idx_platform_metrics_entity ON public.platform_metrics (entity);
CREATE INDEX idx_platform_metrics_entity_id ON public.platform_metrics (entity_id);

ALTER TABLE public.platform_metrics ENABLE ROW LEVEL SECURITY;

ALTER TABLE public.snfts
ADD COLUMN property_id uuid REFERENCES public.properties(id) ON DELETE CASCADE;

DROP TABLE IF EXISTS public.property_token_ownership CASCADE;

CREATE TABLE public.property_token_ownership (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id uuid REFERENCES public.properties(id) ON DELETE CASCADE NOT NULL,
    wallet_id uuid REFERENCES public.wallets(id) ON DELETE CASCADE NOT NULL,
    tokens_owned int NOT NULL CHECK (tokens_owned >= 0),
    last_updated timestamp with time zone DEFAULT now()
);

CREATE UNIQUE INDEX idx_property_wallet_unique ON public.property_token_ownership (property_id, wallet_id);

DROP TABLE IF EXISTS public.property_token_transfers CASCADE;

CREATE TABLE public.property_token_transfers (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id uuid REFERENCES public.properties(id) ON DELETE CASCADE NOT NULL,
    from_wallet_id uuid REFERENCES public.wallets(id),
    to_wallet_id uuid REFERENCES public.wallets(id) NOT NULL,
    tokens_transferred int NOT NULL CHECK (tokens_transferred > 0),
    tx_hash text,
    timestamp timestamp with time zone DEFAULT now()
);

ALTER TABLE public.snfts
ADD COLUMN contract_address text UNIQUE NOT NULL;

-- Create main Contractor table 
DROP TABLE IF EXISTS public.contractors CASCADE;

CREATE TABLE public.contractors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dao_id UUID REFERENCES public.daos(id) ON DELETE SET NULL, -- DAO that governs this contractor

    company TEXT NOT NULL,
    contact TEXT,
    link TEXT,
    type TEXT CHECK (type IN (
        'builder', 'architect', 'plumber', 'electrician', 'landscaper', 'general_contractor', 
        'interior_designer', 'inspector', 'lawyer', 'engineer', 'broker', 'developer', 'accountant', 'property_manager', 'other'
    )) NOT NULL,

    ,
    other_type TEXT NULL,

    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Create main DAOs table
DROP TABLE IF EXISTS public.daos CASCADE;

CREATE TABLE public.daos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    link TEXT,
    description TEXT,
    snft_id UUID REFERENCES public.snfts(id) ON DELETE SET NULL,

    dao_type TEXT CHECK (dao_type IN (
        'single_property',
        'multi_property',
        'contractor',
        'hedge_fund',
        'realtor_team',
        'reit',
        'developer',
        'community',
        'guild',
        'foundation',
        'investor_club'
    )) DEFAULT 'community',

    operational_scope TEXT CHECK (operational_scope IN (
        'local',
        'regional',
        'national',
        'global'
    )) DEFAULT 'local',

    valuation NUMERIC,  -- Total DAO valuation in USD
    currency TEXT DEFAULT 'USD',
    total_token_supply NUMERIC,
    treasury_address TEXT,
    voting_token_address TEXT,
    governance_model TEXT, -- '1-token-1-vote', 'quadratic', etc.

    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Junction table for DAO members
CREATE TABLE public.dao_members (
    dao_id UUID REFERENCES public.daos(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    PRIMARY KEY (dao_id, user_id)
);

-- Junction table for DAO managers
CREATE TABLE public.dao_managers (
    dao_id UUID REFERENCES public.daos(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    PRIMARY KEY (dao_id, user_id)
);

-- Junction table for DAO contractors
CREATE TABLE public.dao_contractors (
    dao_id UUID REFERENCES public.daos(id) ON DELETE CASCADE,
    contractor_id UUID REFERENCES public.contractors(id) ON DELETE CASCADE,
    PRIMARY KEY (dao_id, contractor_id)
);


ALTER TABLE public.snfts
ADD COLUMN dao_id uuid REFERENCES public.daos(id) ON DELETE SET NULL,
ADD COLUMN trust_id uuid; -- Optional if tracked off-chain or abstracted

ALTER TABLE public.snfts
ADD COLUMN total_tokens bigint NOT NULL DEFAULT 100000,
ADD COLUMN tokens_sold bigint DEFAULT 0,
ADD COLUMN token_price numeric, -- Fixed price per token (optional)
ADD COLUMN sale_status text CHECK (sale_status IN ('open', 'closed', 'paused'));

DROP TABLE IF EXISTS public.snft_balances CASCADE;

CREATE TABLE public.snft_balances (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    snft_id uuid REFERENCES public.snfts(id) ON DELETE CASCADE,
    token_count numeric NOT NULL,
    avg_buy_price numeric,
    updated_at timestamp with time zone DEFAULT now(),

    UNIQUE (user_id, snft_id)
);

ALTER TABLE public.snfts
ADD COLUMN metadata_hash text;

DROP TABLE IF EXISTS public.snft_mint_events CASCADE;

CREATE TABLE public.snft_mint_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    snft_id uuid REFERENCES public.snfts(id),
    tx_hash text NOT NULL,
    user_id uuid,
    quantity numeric,
    minted_at timestamp with time zone DEFAULT now(),
    status text CHECK (status IN ('confirmed', 'pending', 'failed')) DEFAULT 'confirmed'
);


ALTER TABLE public.snfts
ADD COLUMN status text DEFAULT 'draft' CHECK (
  status IN (
    'draft', 'property_added', 'docs_uploaded',
    'pending_signature', 'notarized',
    'metadata_ready', 'minted'
  )
),
ADD COLUMN metadata_uri text,
ADD COLUMN metadata_hash text,
ADD COLUMN legal_doc_urls jsonb,        -- { trust_agreement: "...", dao_agreement: "..." }
ADD COLUMN notarization_status text,    -- pending, complete, rejected
ADD COLUMN wizard_progress jsonb;       -- { step: 2, completed: ["property", "images"] }

-- ===============================================================
-- ENHANCEMENTS: SNFT Creation Audit, Contract Sync, Preview Link, Auto-Expire
-- ===============================================================

DROP TABLE IF EXISTS public.snft_events CASCADE;

-- 1. SNFT EVENTS AUDIT TRAIL
CREATE TABLE IF NOT EXISTS public.snft_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    snft_id uuid REFERENCES public.snfts(id) ON DELETE CASCADE NOT NULL,
    event_type text NOT NULL, -- e.g., 'status_change', 'metadata_created', 'contract_deployed'
    event_details jsonb,      -- Flexible structure to log extra context
    created_at timestamp with time zone DEFAULT now()
);

CREATE INDEX public.idx_snft_events_snft_id ON public.snft_events (snft_id);
CREATE INDEX public.idx_snft_events_event_type ON public.snft_events (event_type);

-- 2. CALLBACK-BASED CONTRACT SYNC
-- Triggered manually or from deployment scripts
-- Update snfts table with deployed contract address and deployment timestamp
ALTER TABLE public.snfts
    ADD COLUMN IF NOT EXISTS contract_address text,
    ADD COLUMN IF NOT EXISTS deployed_at timestamp with time zone;

-- 3. PREVIEW METADATA URI
-- Temporary preview URL stored before permanent IPFS pin
ALTER TABLE public.snfts
    ADD COLUMN IF NOT EXISTS preview_uri text;

-- 4. AUTO-EXPIRE DRAFT SNFTS
-- Add expiration timestamp
ALTER TABLE public.snfts
    ADD COLUMN IF NOT EXISTS expires_at timestamp with time zone
        DEFAULT (now() + interval '7 days');

-- Optional: Mark expired drafts with a scheduled CRON or background job
UPDATE public.snfts SET status = 'expired' WHERE status = 'draft' AND expires_at < now();

DROP TABLE IF EXISTS public.snft_metadata_retry_queue CASCADE;

CREATE TABLE public.snft_metadata_retry_queue (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  snft_id uuid REFERENCES public.snfts(id) ON DELETE CASCADE,
  retry_count int DEFAULT 0,
  last_attempt_at timestamptz,
  next_retry_at timestamptz,
  error_log text
);

-- CREATE OR REPLACE FUNCTION public.handle_snft_insert()
-- RETURNS TRIGGER AS $$
-- BEGIN
--   IF NEW.status = 'notarized' THEN
--     PERFORM net.http_post(
--       url := 'https://your-edge-fn-url',
--       headers := jsonb_build_object('Content-Type', 'application/json'),
--       body := jsonb_build_object('snft_id', NEW.id)
--     );
--   END IF;
--   RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;

CREATE TRIGGER trg_snft_insert_metadata_trigger
AFTER INSERT ON public.snfts
FOR EACH ROW
EXECUTE FUNCTION handle_snft_insert();


CREATE OR REPLACE FUNCTION public.handle_snft_update()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status = 'notarized' AND OLD.status IS DISTINCT FROM 'notarized' THEN
    PERFORM net.http_post(
      url := 'https://your-edge-fn-url',
      headers := jsonb_build_object('Content-Type', 'application/json'),
      body := jsonb_build_object('snft_id', NEW.id)
    );
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER public.trg_snft_update_metadata_trigger
AFTER UPDATE ON public.snfts
FOR EACH ROW
WHEN (OLD.status IS DISTINCT FROM NEW.status)
EXECUTE FUNCTION public.handle_snft_update();

CREATE OR REPLACE FUNCTION public.log_snft_mint_event_as_generic()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.snft_events (
    snft_id,
    event_type,
    event_details
  )
  VALUES (
    NEW.snft_id,
    'minted',
    jsonb_build_object(
      'tx_hash', NEW.tx_hash,
      'user_id', NEW.user_id,
      'quantity', NEW.quantity,
      'minted_at', NEW.minted_at,
      'status', NEW.status
    )
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE VIEW ready_snfts AS
SELECT *
FROM snfts
WHERE metadata_status = 'complete'
  AND metadata_uri IS NOT NULL
  AND status = 'ready_for_contract';

DROP TABLE IF EXISTS public.favorites CASCADE;

CREATE TABLE public.favorites (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    asset_type text NOT NULL CHECK (asset_type IN (
        'snft', 'post', 'user', 'property', 'bot_strategy', 'chat_message'
    )),
    asset_id text NOT NULL,
    favorited_at timestamptz DEFAULT now(),

    UNIQUE (user_id, asset_type, asset_id)
);

CREATE INDEX idx_favorites_user_id ON public.favorites(user_id);
CREATE INDEX idx_favorites_asset ON public.favorites(asset_type, asset_id);

ALTER TABLE public.favorites ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own favorites" ON public.favorites
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can favorite assets" ON public.favorites
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can unfavorite assets" ON public.favorites
    FOR DELETE USING (auth.uid() = user_id);

CREATE TRIGGER set_favorites_timestamp
    BEFORE UPDATE ON public.favorites
    FOR EACH ROW
    EXECUTE FUNCTION public.set_update_timestamp();


DROP TABLE IF EXISTS public.favorites CASCADE;

CREATE TABLE public.favorites (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    asset_type text NOT NULL CHECK (asset_type IN (
        'snft', 'post', 'user', 'property', 'bot_strategy', 'chat_message'
    )),
    asset_id text NOT NULL,
    favorited_at timestamptz DEFAULT now(),

    UNIQUE (user_id, asset_type, asset_id)
);

CREATE INDEX idx_favorites_user_id ON public.favorites(user_id);
CREATE INDEX idx_favorites_asset ON public.favorites(asset_type, asset_id);

ALTER TABLE public.favorites ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own favorites" ON public.favorites
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can favorite assets" ON public.favorites
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can unfavorite assets" ON public.favorites
    FOR DELETE USING (auth.uid() = user_id);

CREATE TRIGGER set_favorites_timestamp
    BEFORE UPDATE ON public.favorites
    FOR EACH ROW
    EXECUTE FUNCTION public.set_update_timestamp();

DROP TABLE IF EXISTS public.stars CASCADE;

CREATE TABLE public.stars (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    entity_type text NOT NULL CHECK (entity_type IN ('user', 'dao', 'snft')),
    entity_id uuid NOT NULL,
    value integer NOT NULL CHECK (value BETWEEN 1 AND 5),
    review text, -- Optional text review
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz
);

CREATE UNIQUE INDEX idx_stars_unique ON public.stars(user_id, entity_type, entity_id);
CREATE INDEX idx_stars_entity ON public.stars(entity_type, entity_id);

ALTER TABLE public.stars ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own ratings" ON public.stars
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can leave reviews" ON public.stars
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their review" ON public.stars
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their review" ON public.stars
    FOR DELETE USING (auth.uid() = user_id);

CREATE TRIGGER set_stars_timestamp
    BEFORE UPDATE ON public.stars
    FOR EACH ROW
    EXECUTE FUNCTION public.set_update_timestamp();

CREATE MATERIALIZED VIEW reputation_summary AS
SELECT
    entity_type,
    entity_id,
    COUNT(*) AS total_reviews,
    AVG(value) AS average_rating,
    PERCENT_RANK() OVER (PARTITION BY entity_type ORDER BY AVG(value)) AS percentile
FROM public.stars
GROUP BY entity_type, entity_id;

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

CREATE INDEX idx_comments_asset ON public.comments(asset_type, asset_id);
CREATE INDEX idx_comments_parent_id ON public.comments(parent_id);

ALTER TABLE public.comments ENABLE ROW LEVEL SECURITY;

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

CREATE INDEX idx_shares_asset ON public.shares(asset_type, asset_id);
CREATE INDEX idx_shares_user_id ON public.shares(user_id);

ALTER TABLE public.shares ENABLE ROW LEVEL SECURITY;

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

ALTER TABLE public.user_stats
ADD COLUMN last_active timestamptz DEFAULT now();

CREATE OR REPLACE FUNCTION public.touch_user_last_active()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE public.user_stats
  SET last_active = now(),
      last_updated = now()
  WHERE user_id = NEW.user_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_touch_last_active_on_comment
AFTER INSERT ON public.comments
FOR EACH ROW
EXECUTE FUNCTION public.touch_user_last_active();

CREATE TRIGGER trg_touch_last_active_on_trade
AFTER INSERT ON public.trades
FOR EACH ROW
EXECUTE FUNCTION public.touch_user_last_active();

CREATE TRIGGER trg_touch_last_active_on_share
AFTER INSERT ON public.shares
FOR EACH ROW
EXECUTE FUNCTION public.touch_user_last_active();

DROP TABLE IF EXISTS public.daily_rollup_user_stats CASCADE;

CREATE TABLE public.daily_rollup_user_stats (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    date date NOT NULL,
    
    snft_count integer DEFAULT 0,
    trade_count integer DEFAULT 0,
    wallet_count integer DEFAULT 0,
    comment_count integer DEFAULT 0,
    reply_count integer DEFAULT 0,
    share_count integer DEFAULT 0,
    favorite_count integer DEFAULT 0,
    star_count integer DEFAULT 0,
    received_star_count integer DEFAULT 0,
    average_rating numeric,

    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),

    UNIQUE (user_id, date)
);

ALTER TABLE public.user_stats
ADD COLUMN favorite_count integer DEFAULT 0;

ALTER TABLE public.user_stats
ADD COLUMN favorite_count integer DEFAULT 0;

ALTER TABLE public.user_stats
ADD COLUMN star_count integer DEFAULT 0,
ADD COLUMN received_star_count integer DEFAULT 0,
ADD COLUMN average_rating numeric;

CREATE OR REPLACE FUNCTION public.increment_star_count()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_stats (user_id, star_count)
  VALUES (NEW.user_id, 1)
  ON CONFLICT (user_id)
  DO UPDATE SET star_count = user_stats.star_count + 1,
                last_updated = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_increment_star_count
AFTER INSERT ON public.stars
FOR EACH ROW
EXECUTE FUNCTION public.increment_star_count();

CREATE OR REPLACE FUNCTION public.increment_star_count()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_stats (user_id, star_count)
  VALUES (NEW.user_id, 1)
  ON CONFLICT (user_id)
  DO UPDATE SET star_count = user_stats.star_count + 1,
                last_updated = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_increment_star_count
AFTER INSERT ON public.stars
FOR EACH ROW
EXECUTE FUNCTION public.increment_star_count();

CREATE TABLE IF NOT EXISTS public.dao_stats (
    dao_id uuid PRIMARY KEY REFERENCES public.daos(id) ON DELETE CASCADE,

    snft_count integer DEFAULT 0,
    comment_count integer DEFAULT 0,
    share_count integer DEFAULT 0,
    star_count integer DEFAULT 0,
    received_star_count integer DEFAULT 0,
    average_rating numeric,
    last_updated timestamptz DEFAULT now()
);

DROP TABLE IF EXISTS public.kudos CASCADE;

CREATE TABLE public.kudos (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    from_user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    to_user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,

    context_type text NOT NULL CHECK (context_type IN (
        'chat_message', 'comment', 'post', 'proposal', 'strategy'
    )),
    context_id text NOT NULL, -- The ID of the chat message, comment, etc.

    reason text,             -- Optional: "great advice", "explained concept", etc.
    value integer DEFAULT 1 CHECK (value >= 1), -- Default 1 kudos, or variable weighting

    created_at timestamptz DEFAULT now()
);

-- Prevent double-kudos from the same person in the same context
CREATE UNIQUE INDEX idx_kudos_unique ON public.kudos(from_user_id, context_type, context_id);

CREATE INDEX idx_kudos_to_user ON public.kudos(to_user_id);

ALTER TABLE public.kudos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view kudos given to others" ON public.kudos
    FOR SELECT USING (TRUE);
CREATE POLICY "Users can give kudos" ON public.kudos
    FOR INSERT WITH CHECK (auth.uid() = from_user_id);


CREATE OR REPLACE FUNCTION public.apply_kudos_to_reputation()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE public.reputations
  SET score = COALESCE(score, 0) + NEW.value,
      last_updated = now()
  WHERE subject_type = 'user' AND subject_id = NEW.to_user_id;

  UPDATE public.user_stats
  SET last_updated = now()
  WHERE user_id = NEW.to_user_id;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_apply_kudos_to_reputation
AFTER INSERT ON public.kudos
FOR EACH ROW
EXECUTE FUNCTION public.apply_kudos_to_reputation();

DROP TABLE IF EXISTS public.mentions CASCADE;

CREATE TABLE public.mentions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    context_type text NOT NULL CHECK (context_type IN (
        'chat_message', 'comment', 'post', 'proposal'
    )),
    context_id text NOT NULL,

    mentioned_type text NOT NULL CHECK (mentioned_type IN ('user', 'dao')),
    mentioned_id uuid NOT NULL,

    mentioned_by uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,

    -- Computed or provided by app/Edge Function
    context_url text NOT NULL, -- e.g. /chat/room/abc#message-xyz

    created_at timestamptz DEFAULT now()
);

CREATE INDEX idx_mentions_target ON public.mentions(mentioned_type, mentioned_id);

ALTER TABLE public.user_stats
ADD COLUMN mention_count integer DEFAULT 0;

ALTER TABLE public.dao_stats
ADD COLUMN mention_count integer DEFAULT 0;

CREATE OR REPLACE FUNCTION public.increment_mention_count()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.mentioned_type = 'user' THEN
    INSERT INTO public.user_stats (user_id, mention_count)
    VALUES (NEW.mentioned_id, 1)
    ON CONFLICT (user_id)
    DO UPDATE SET mention_count = user_stats.mention_count + 1,
                  last_updated = now();
  ELSIF NEW.mentioned_type = 'dao' THEN
    INSERT INTO public.dao_stats (dao_id, mention_count)
    VALUES (NEW.mentioned_id, 1)
    ON CONFLICT (dao_id)
    DO UPDATE SET mention_count = dao_stats.mention_count + 1,
                  last_updated = now();
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_increment_mention_count
AFTER INSERT ON public.mentions
FOR EACH ROW
EXECUTE FUNCTION public.increment_mention_count();


ALTER TABLE public.reputations
ADD CONSTRAINT chk_subject_type_valid CHECK (
  subject_type IN ('user', 'dao', 'snft')
);

CREATE TABLE public.snft_stats (
    snft_id uuid PRIMARY KEY REFERENCES public.snfts(id) ON DELETE CASCADE,

    favorite_count integer DEFAULT 0,
    star_count integer DEFAULT 0,
    average_rating numeric,
    comment_count integer DEFAULT 0,
    mention_count integer DEFAULT 0,
    share_count integer DEFAULT 0,

    last_updated timestamptz DEFAULT now()
);

ALTER TABLE public.mentions
ADD CONSTRAINT chk_mention_type_valid CHECK (
  mentioned_type IN ('user', 'dao', 'snft')
);

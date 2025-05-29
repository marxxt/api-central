-- SQL Script to Create Additional Tables
-- Based on types: AIBotConfig, ActiveManualOrder, UserInvestment

-- Ensure you are connected to your Supabase database.
-- These commands are typically run via the Supabase UI SQL Editor or migrations.

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
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    score numeric,
    rank text,
    ranking_percentile text,
    last_updated timestamp with time zone,
    adjusted_staking_yield text,
    forecast_access_level text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);

CREATE INDEX idx_reputations_user_id ON public.reputations (user_id);

ALTER TABLE public.reputations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own reputations" ON public.reputations
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create their own reputations" ON public.reputations
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own reputations" ON public.reputations
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own reputations" ON public.reputations
    FOR DELETE USING (auth.uid() = user_id);

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
    timestamp bigint NOT NULL, -- Consider renaming to epoch_timestamp for clarity

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

CREATE TABLE public.user_stats (
    user_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    snft_count integer DEFAULT 0,
    trade_count integer DEFAULT 0,
    wallet_count integer DEFAULT 0,
    last_updated timestamp with time zone DEFAULT now()
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
ADD COLUMN metadata_uri text,        -- e.g., ipfs://QmXoY...z5v
ADD COLUMN metadata_hash text;       -- Store just the CID or SHA256 hash of metadata

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

CREATE INDEX IF NOT EXISTS public.idx_snft_events_snft_id ON public.snft_events (snft_id);
CREATE INDEX IF NOT EXISTS public.idx_snft_events_event_type ON public.snft_events (event_type);

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

DROP TABLE IF EXISTS public.snft_events CASCADE;

CREATE TABLE public.snft_metadata_retry_queue (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  snft_id uuid REFERENCES public.snfts(id) ON DELETE CASCADE,
  retry_count int DEFAULT 0,
  last_attempt_at timestamptz,
  next_retry_at timestamptz,
  error_log text
);

CREATE OR REPLACE FUNCTION public.handle_snft_insert()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status = 'notarized' THEN
    PERFORM net.http_post(
      url := 'https://your-edge-fn-url',
      headers := jsonb_build_object('Content-Type', 'application/json'),
      body := jsonb_build_object('snft_id', NEW.id)
    );
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

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

SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
const web3 = new Web3Storage({ token: Deno.env.get("WEB3_STORAGE_TOKEN")! });
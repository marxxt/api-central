#!/bin/bash

# This script removes all tables, functions, and triggers defined in
# temp_corrected_schema.sql from your Supabase database.
export DATABASE_URL="postgresql://postgres:Maddygaby75!@db.txqmcpmcduqrdwuvmxeg.supabase.co:5432/postgres"

# Ensure DATABASE_URL environment variable is set.
if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL environment variable is not set."
    echo "Please set it to your Supabase database connection string."
    exit 1
fi

echo "Attempting to clean up Supabase database based on temp_corrected_schema.sql..."

# Drop triggers first
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TRIGGER IF EXISTS trg_increment_snft_count ON public.snfts CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TRIGGER IF EXISTS trg_increment_trade_count ON public.trades CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TRIGGER IF EXISTS trg_increment_wallet_count ON public.wallets CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TRIGGER IF EXISTS set_ai_bot_configs_timestamp ON public.ai_bot_configs CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TRIGGER IF EXISTS set_orders_timestamp ON public.orders CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TRIGGER IF EXISTS set_user_investments_timestamp ON public.user_investments CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TRIGGER IF EXISTS set_properties_timestamp ON public.properties CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TRIGGER IF EXISTS set_snfts_timestamp ON public.snfts CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TRIGGER IF EXISTS set_auctions_timestamp ON public.auctions CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TRIGGER IF EXISTS set_trades_timestamp ON public.trades CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TRIGGER IF EXISTS set_trading_pairs_timestamp ON public.trading_pairs CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TRIGGER IF EXISTS set_bid_history_timestamp ON public.bid_history CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TRIGGER IF EXISTS set_transactions_timestamp ON public.transactions CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TRIGGER IF EXISTS set_dao_proposals_timestamp ON public.dao_proposals CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TRIGGER IF EXISTS set_dao_votes_timestamp ON public.dao_votes CASCADE;"

# Drop tables in reverse dependency order
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TABLE IF EXISTS public.platform_metrics CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TABLE IF EXISTS public.user_stats CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TABLE IF EXISTS public.dao_votes CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TABLE IF EXISTS public.dao_proposals CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TABLE IF EXISTS public.transactions CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TABLE IF EXISTS public.bid_history CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TABLE IF EXISTS public.user_investments CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TABLE IF EXISTS public.orders CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TABLE IF EXISTS public.ai_bot_configs CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TABLE IF EXISTS public.trading_pairs CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TABLE IF EXISTS public.auctions CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TABLE IF EXISTS public.snfts CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TABLE IF EXISTS public.properties CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TABLE IF EXISTS public.collections CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TABLE IF EXISTS public.reputations CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP TABLE IF EXISTS public.wallets CASCADE;"

# Drop functions last
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP FUNCTION IF EXISTS public.increment_snft_count() CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP FUNCTION IF EXISTS public.increment_trade_count() CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP FUNCTION IF EXISTS public.increment_wallet_count() CASCADE;"
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c "DROP FUNCTION IF EXISTS public.set_update_timestamp() CASCADE;"

if [ $? -eq 0 ]; then
    echo "✅ Database cleanup successful."
else
    echo "❌ Database cleanup failed. Please check the error messages above."
    exit 1
fi

#!/bin/bash

echo "🚀 Starting Supabase database reset..."

if [ -z "$DATABASE_URL" ]; then
  echo "❌ DATABASE_URL environment variable is not set."
  exit 1
fi

echo "📄 Executing 01_temp_corrected_schema.sql..."
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -f "sql/01_temp_corrected_schema.sql"

echo "📄 Executing 02_gamification_core.sql..."
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -f "sql/02_gamification_core.sql"

echo "📄 Executing 03_badge_voting_roles.sql..."
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -f "sql/03_badge_voting_roles.sql"

echo "📄 Executing 04_dao_token_holdings.sql..."
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -f "sql/04_dao_token_holdings.sql"

echo "📄 Executing 05_gamification_xp_badge_logic.sql..."
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -f "sql/05_gamification_xp_badge_logic.sql"

echo "📄 Executing 06_notifications_and_limits.sql..."
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -f "sql/06_notifications_and_limits.sql"

echo "📄 Executing 07_property_rewards.sql..."
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -f "sql/07_property_rewards.sql"

echo "📄 Executing 08_dao_cap_table_view.sql..."
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -f "sql/08_dao_cap_table_view.sql"

echo "📄 Executing 09_dao_voting_epochs.sql..."
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -f "sql/09_dao_voting_epochs.sql"

echo "✅ Database reset completed."

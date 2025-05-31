#!/bin/bash

# Fail fast on error, unset vars, or pipeline failure
set -euo pipefail

# Ensure DATABASE_URL is set
if [ -z "${DATABASE_URL:-}" ]; then
  echo "❌ Error: DATABASE_URL environment variable is not set."
  echo "Please set it to your Supabase database connection string."
  exit 1
fi

echo "🚀 Starting Supabase database reset..."

# List of SQL files to execute
SQL_FILES=(
  "sql/temp_corrected_schema.sql"
  "sql/badge_voting_roles.sql"
  "sql/dao_token_holdings.sql"
  "sql/dao_cap_table_view.sql"
  "sql/gamification_core.sql"
  "sql/gamification_xp_badge_logic.sql"
  "sql/notifications_and_limits.sql"
  "sql/property_rewards.sql"
)

# Loop through each SQL file
for FILE in "${SQL_FILES[@]}"; do
  if [ ! -f "$FILE" ]; then
    echo "⚠️  Warning: $FILE not found, skipping."
    continue
  fi

  echo "📄 Executing $FILE..."
  psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -f "$FILE" 2>> sql/reset_errors.log
  echo "✅ Executed: $FILE"
done

echo "🎉 Database reset completed successfully."

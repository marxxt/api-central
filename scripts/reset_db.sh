#!/bin/bash

# This script resets the Supabase database by dropping and recreating all tables
# defined in temp_corrected_schema.sql.

# Ensure DATABASE_URL environment variable is set, e.g.:
# Or, if using Supabase CLI, ensure it's configured to connect to your project.


if [ -z "$DATABASE_URL" ]; then
  echo "Error: DATABASE_URL environment variable is not set."
  echo "Please set it to your Supabase database connection string."
  exit 1
fi

echo "Attempting to reset Supabase database using schema from temp_corrected_schema.sql..."

# Execute the SQL script using psql
# -X: Do not read startup file (~/.psqlrc)
# -v ON_ERROR_STOP=1: Exit immediately if an error occurs
# -f: Read commands from file
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -f temp_corrected_schema.sql

if [ $? -eq 0 ]; then
  echo "✅ Database reset successful."
else
  echo "❌ Database reset failed. Please check the error messages above."
  exit 1
fi
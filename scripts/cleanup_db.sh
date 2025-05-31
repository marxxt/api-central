#!/bin/bash

# Full Supabase database cleanup script
# Requires DATABASE_URL, SUPABASE_URL, and SUPABASE_SERVICE_ROLE_KEY to be set in your environment

if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL is not set."
    exit 1
fi

echo "🧹 Starting full cleanup of Supabase database..."

# 1. Drop all user-defined triggers
echo "🚫 Dropping all triggers..."
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 <<'EOSQL'
DO $$
DECLARE
    trig RECORD;
BEGIN
    FOR trig IN
        SELECT tgname, relname
        FROM pg_trigger t
        JOIN pg_class c ON t.tgrelid = c.oid
        JOIN pg_namespace n ON c.relnamespace = n.oid
        WHERE NOT t.tgisinternal AND n.nspname = 'public'
    LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS %I ON public.%I CASCADE;', trig.tgname, trig.relname);
    END LOOP;
END$$;
EOSQL

# 2. Drop all views
echo "🔭 Dropping all views..."
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 <<'EOSQL'
DO $$
DECLARE
    view_rec RECORD;
BEGIN
    FOR view_rec IN
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema = 'public'
    LOOP
        EXECUTE format('DROP VIEW IF EXISTS public.%I CASCADE;', view_rec.table_name);
    END LOOP;
END$$;
EOSQL

# 3. Drop all tables
echo "🗂️ Dropping all tables..."
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 <<'EOSQL'
DO $$
DECLARE
    tbl RECORD;
BEGIN
    FOR tbl IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
    LOOP
        EXECUTE format('DROP TABLE IF EXISTS public.%I CASCADE;', tbl.tablename);
    END LOOP;
END$$;
EOSQL

# 4. Drop all functions
echo "🧠 Dropping all user-defined functions..."
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 <<'EOSQL'
DO $$
DECLARE
    fn RECORD;
BEGIN
    FOR fn IN
        SELECT p.proname, pg_get_function_identity_arguments(p.oid) AS args
        FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'public'
    LOOP
        EXECUTE format('DROP FUNCTION IF EXISTS public.%I(%s) CASCADE;', fn.proname, fn.args);
    END LOOP;
END$$;
EOSQL

# 5. Drop custom types (e.g. enums)
echo "📦 Dropping custom types..."
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 <<'EOSQL'
DO $$
DECLARE
    typ RECORD;
BEGIN
    FOR typ IN
        SELECT t.typname
        FROM pg_type t
        JOIN pg_namespace n ON t.typnamespace = n.oid
        WHERE n.nspname = 'public' AND t.typtype = 'e'
    LOOP
        EXECUTE format('DROP TYPE IF EXISTS public.%I CASCADE;', typ.typname);
    END LOOP;
END$$;
EOSQL

# 6. Truncate auth.users
echo "🧽 Truncating all auth.users..."
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 <<'EOSQL'
TRUNCATE auth.users CASCADE;
EOSQL

echo "✅ Database cleanup complete."

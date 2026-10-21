#!/usr/bin/env bash
# Drops every table in the current schema of the database configured in .env.
# Usage: scripts/drop_tables.sh [--yes]
set -euo pipefail

ENV_FILE="$(dirname "$0")/../.env"

if [[ ! -f "$ENV_FILE" ]]; then
    echo "Error: $ENV_FILE not found" >&2
    exit 1
fi

# Export every variable defined in .env
set -a
# shellcheck source=/dev/null
source "$ENV_FILE"
set +a

: "${DATABASE_HOST:?DATABASE_HOST is not set}"
: "${DATABASE_USER:?DATABASE_USER is not set}"
: "${DATABASE_NAME:?DATABASE_NAME is not set}"
: "${DATABASE_PASSWORD:?DATABASE_PASSWORD is not set}"
DATABASE_PORT="${DATABASE_PORT:-5432}"

if [[ "${1:-}" != "--yes" ]]; then
    read -r -p "Drop ALL tables in '$DATABASE_NAME' on $DATABASE_HOST:$DATABASE_PORT? [y/N] " answer
    if [[ "$answer" != "y" && "$answer" != "Y" ]]; then
        echo "Aborted."
        exit 0
    fi
fi

export PGPASSWORD="$DATABASE_PASSWORD"

psql -v ON_ERROR_STOP=1 \
    -h "$DATABASE_HOST" \
    -p "$DATABASE_PORT" \
    -U "$DATABASE_USER" \
    -d "$DATABASE_NAME" <<'SQL'
DO $$
DECLARE
    r record;
BEGIN
    FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = current_schema() LOOP
        RAISE NOTICE 'Dropping table %', r.tablename;
        EXECUTE format('DROP TABLE IF EXISTS %I CASCADE', r.tablename);
    END LOOP;
END $$;
SQL

echo "All tables dropped from '$DATABASE_NAME'."

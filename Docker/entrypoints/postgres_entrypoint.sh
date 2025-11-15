#!/bin/bash
set -e

echo "Running Postgres init script..."

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"

    for db in $(echo "$POSTGRES_MULTIPLE_DATABASES" | tr ',' ' '); do
        echo "Ensuring database exists: $db"

        # Check if DB exists
        EXISTS=$(psql -U "$POSTGRES_USER" -tc "SELECT 1 FROM pg_database WHERE datname='${db}';" | xargs)

        if [ "$EXISTS" = "1" ]; then
            echo "Database $db already exists, skipping."
        else
            echo "Database $db does not exist. Creating..."
            psql -U "$POSTGRES_USER" -c "CREATE DATABASE \"$db\";"
        fi

        # Grant privileges (safe even if DB already existed)
        psql -U "$POSTGRES_USER" -c "GRANT ALL PRIVILEGES ON DATABASE \"$db\" TO \"$POSTGRES_USER\";"
    done

    echo "All databases ensured."
fi

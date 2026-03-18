#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status

echo "Running Postgres init script..."

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"

    for db in $(echo "$POSTGRES_MULTIPLE_DATABASES" | tr ',' ' '); do
        echo "Checking database: $db"

        if psql -U "$POSTGRES_USER" -lqt | cut -d \| -f 1 | grep -qw "$db"; then
            echo "Database $db already exists, skipping."
        else
            echo "Database $db does not exist. Creating..."
            createdb -U "$POSTGRES_USER" "$db"
            echo "Database $db created successfully."
        fi
        psql -U "$POSTGRES_USER" -c "GRANT ALL PRIVILEGES ON DATABASE \"$db\" TO \"$POSTGRES_USER\";"
    done

    echo "All databases ensured."
fi
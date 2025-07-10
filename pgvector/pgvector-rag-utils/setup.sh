#!/bin/bash

# PGVector RAG System Setup Script
# This script helps set up the database schema

set -e

# Default values
DB_HOST="${DB_HOST:-postgres-pgvector.pgvector.svc.cluster.local}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-vectordb}"
DB_USER="${DB_USER:-vectoruser}"

echo "PGVector RAG System Setup"
echo "========================="
echo "Database: $DB_HOST:$DB_PORT/$DB_NAME"
echo "User: $DB_USER"
echo ""

# Check if psql is available
if ! command -v psql &> /dev/null; then
    echo "Error: psql command not found. Please install PostgreSQL client."
    exit 1
fi

# Function to run SQL file
run_sql_file() {
    local file=$1
    echo "Running $file..."
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$file"
    if [ $? -eq 0 ]; then
        echo "✓ $file completed successfully"
    else
        echo "✗ Error running $file"
        exit 1
    fi
}

# Prompt for password if not set
if [ -z "$DB_PASSWORD" ]; then
    read -sp "Enter database password: " DB_PASSWORD
    echo ""
fi
export PGPASSWORD="$DB_PASSWORD"

# Check connection
echo "Testing database connection..."
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT version();" > /dev/null 2>&1; then
    echo "✓ Connected successfully"
else
    echo "✗ Failed to connect to database"
    exit 1
fi

# Check PGVector extension
echo "Checking PGVector extension..."
PGVECTOR_VERSION=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT extversion FROM pg_extension WHERE extname = 'vector';" 2>/dev/null | tr -d ' ')

if [ -z "$PGVECTOR_VERSION" ]; then
    echo "✗ PGVector extension not found"
    echo "Please ensure PGVector is installed in your PostgreSQL instance"
    exit 1
else
    echo "✓ PGVector $PGVECTOR_VERSION found"
fi

# Run SQL files
echo ""
echo "Setting up database schema..."
run_sql_file "01_schema.sql"
run_sql_file "02_indexes.sql"
run_sql_file "03_functions.sql"

echo ""
echo "Setup complete! 🎉"
echo ""
echo "Next steps:"
echo "1. Install Python dependencies: pip install -r requirements.txt"
echo "2. Copy .env.example to .env and update with your settings"
echo "3. Run the example: python example_usage.py"
echo ""
echo "For Jupyter notebooks, use demo_notebook.ipynb"

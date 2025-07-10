#!/usr/bin/env python3
"""
Pipeline Script 1: Database Setup

This script sets up the PGVector database schema and verifies the installation.
It performs the following operations:

1. Validates PGVector extension installation
2. Creates database schema (tables, indexes, functions)
3. Verifies setup completion
4. Outputs status for pipeline orchestration

The script is designed to be idempotent and can be run multiple times safely.
It's the first step in the RAG pipeline and must complete successfully before
document ingestion can begin.

Usage:
    python 01_setup_database.py

Environment Variables:
    DB_HOST: Database host (default: postgres-pgvector.pgvector.svc.cluster.local)
    DB_PORT: Database port (default: 5432)
    DB_NAME: Database name (default: vectordb)
    DB_USER: Database user (default: vectoruser)
    DB_PASSWORD: Database password (default: vectorpass)

Exit Codes:
    0: Success
    1: Database connection failed or PGVector not installed
"""

import sys
import os
import psycopg2
from pgvector.psycopg2 import register_vector
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline_scripts.pipeline_utils import get_env_vars, get_db_connection_params

logger = logging.getLogger(__name__)


def check_pgvector_extension(conn):
    """
    Check if PGVector extension is installed and get version information.
    
    Queries the PostgreSQL system catalogs to verify that the vector extension
    is installed and available. This is a prerequisite for all vector operations.
    
    Args:
        conn: Active psycopg2 database connection
    
    Returns:
        bool: True if PGVector extension is installed, False otherwise
    
    Side Effects:
        Logs the PGVector version if found, or error message if not found
    """
    cur = conn.cursor()
    cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
    result = cur.fetchone()
    cur.close()
    
    if result:
        logger.info(f"PGVector {result[0]} is installed")
        return True
    else:
        logger.error("PGVector extension not found")
        return False


def run_sql_file(conn, sql_file_path):
    """
    Execute a SQL file against the database.
    
    Reads and executes a SQL file within a transaction. If any error occurs,
    the transaction is rolled back to maintain database consistency.
    
    Args:
        conn: Active psycopg2 database connection
        sql_file_path (str): Path to the SQL file to execute
    
    Raises:
        Exception: If SQL execution fails, the exception is re-raised after rollback
    
    Side Effects:
        - Commits transaction on success
        - Rolls back transaction on failure
        - Logs execution status
    """
    with open(sql_file_path, 'r') as f:
        sql = f.read()
    
    cur = conn.cursor()
    try:
        cur.execute(sql)
        conn.commit()
        logger.info(f"Successfully executed {os.path.basename(sql_file_path)}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error executing {sql_file_path}: {e}")
        raise
    finally:
        cur.close()


def verify_setup(conn):
    """
    Verify that the database setup completed successfully.
    
    Checks for the existence of required tables and functions that should
    have been created during the setup process. This serves as a validation
    step to ensure the database is ready for document ingestion.
    
    Args:
        conn: Active psycopg2 database connection
    
    Side Effects:
        Logs the existence status of each required database object
    
    Note:
        Checks for:
        - Tables: projects, document_chunks
        - Functions: hybrid_search_rrf, dense_search
    """
    cur = conn.cursor()
    
    # Check tables
    tables = ['projects', 'document_chunks']
    for table in tables:
        cur.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = '{table}'
            );
        """)
        exists = cur.fetchone()[0]
        logger.info(f"Table '{table}' exists: {exists}")
    
    # Check functions
    functions = ['hybrid_search_rrf', 'dense_search']
    for func in functions:
        cur.execute(f"""
            SELECT EXISTS (
                SELECT FROM pg_proc 
                WHERE proname = '{func}'
            );
        """)
        exists = cur.fetchone()[0]
        logger.info(f"Function '{func}' exists: {exists}")
    
    cur.close()


def main():
    """
    Main execution function for database setup pipeline.
    
    Orchestrates the complete database setup process including:
    1. Environment variable validation
    2. Database connection establishment
    3. PGVector extension verification
    4. SQL schema file execution
    5. Setup verification
    6. Pipeline status output
    
    The function follows a fail-fast approach, exiting immediately if any
    critical step fails. On success, it outputs a status message for
    pipeline orchestration.
    
    Exit Codes:
        0: Setup completed successfully
        1: Database connection failed or PGVector not installed
    """
    logger.info("Starting database setup pipeline")
    
    # Get environment variables
    env_vars = get_env_vars()
    conn_params = get_db_connection_params(env_vars)
    
    # Connect to database
    try:
        conn = psycopg2.connect(
            host=conn_params['host'],
            port=conn_params['port'],
            database=conn_params['database'],
            user=conn_params['user'],
            password=conn_params['password']
        )
        register_vector(conn)
        logger.info("Connected to database successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)
    
    # Check PGVector
    if not check_pgvector_extension(conn):
        logger.error("PGVector extension is required but not installed")
        sys.exit(1)
    
    # Run SQL files
    sql_dir = os.path.join(os.path.dirname(__file__), '..')
    sql_files = ['01_schema.sql', '02_indexes.sql', '03_functions.sql']
    
    for sql_file in sql_files:
        sql_path = os.path.join(sql_dir, sql_file)
        if os.path.exists(sql_path):
            run_sql_file(conn, sql_path)
        else:
            logger.warning(f"SQL file not found: {sql_path}")
    
    # Verify setup
    verify_setup(conn)
    
    # Close connection
    conn.close()
    logger.info("Database setup completed successfully")
    
    # Output for next pipeline step
    print("DATABASE_SETUP_COMPLETE=true")


if __name__ == "__main__":
    main()

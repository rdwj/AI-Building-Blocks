#!/usr/bin/env python3
"""
Test script to verify PGVector RAG system setup
"""

import sys
import psycopg2
from pgvector.psycopg2 import register_vector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_connection(conn_params):
    """Test database connection"""
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        logger.info(f"✓ Connected to PostgreSQL: {version[:30]}...")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"✗ Connection failed: {e}")
        return False


def test_pgvector(conn_params):
    """Test PGVector extension"""
    try:
        conn = psycopg2.connect(**conn_params)
        register_vector(conn)
        
        cur = conn.cursor()
        cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
        version = cur.fetchone()
        
        if version:
            logger.info(f"✓ PGVector {version[0]} is installed")
        else:
            logger.error("✗ PGVector extension not found")
            return False
            
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"✗ PGVector test failed: {e}")
        return False


def test_tables(conn_params):
    """Test if tables exist"""
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
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
            
            if exists:
                logger.info(f"✓ Table '{table}' exists")
            else:
                logger.error(f"✗ Table '{table}' not found")
                return False
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"✗ Table test failed: {e}")
        return False


def test_functions(conn_params):
    """Test if functions exist"""
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        functions = ['hybrid_search_rrf', 'dense_search', 'get_project_stats']
        for func in functions:
            cur.execute(f"""
                SELECT EXISTS (
                    SELECT FROM pg_proc 
                    WHERE proname = '{func}'
                );
            """)
            exists = cur.fetchone()[0]
            
            if exists:
                logger.info(f"✓ Function '{func}' exists")
            else:
                logger.error(f"✗ Function '{func}' not found")
                return False
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"✗ Function test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("PGVector RAG System Test")
    print("========================\n")
    
    # Get connection parameters
    if len(sys.argv) > 1:
        # Allow passing connection string
        conn_params = {"dsn": sys.argv[1]}
    else:
        # Default parameters
        conn_params = {
            "host": "postgres-pgvector.pgvector.svc.cluster.local",
            "port": 5432,
            "database": "vectordb",
            "user": "vectoruser",
            "password": "vectorpass"
        }
    
    # Run tests
    tests = [
        ("Database Connection", test_connection),
        ("PGVector Extension", test_pgvector),
        ("Database Tables", test_tables),
        ("Database Functions", test_functions)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        success = test_func(conn_params)
        results.append((test_name, success))
    
    # Summary
    print("\n" + "="*40)
    print("Test Summary:")
    print("="*40)
    
    all_passed = True
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        symbol = "✓" if success else "✗"
        print(f"{symbol} {test_name}: {status}")
        if not success:
            all_passed = False
    
    print("="*40)
    
    if all_passed:
        print("\n✅ All tests passed! Your PGVector RAG system is ready.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the setup.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

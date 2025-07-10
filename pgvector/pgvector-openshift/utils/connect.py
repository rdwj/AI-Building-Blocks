import psycopg2
from pgvector.psycopg2 import register_vector

# Database connection
conn = psycopg2.connect(
    host="postgres-pgvector.pgvector.svc.cluster.local",  # Full service name
    # or just "postgres-pgvector" if Jupyter is in the same namespace
    port=5432,
    database="vectordb",
    user="vectoruser",
    password="vectorpass"
)

# Register vector type
register_vector(conn)

# Test the connection
cur = conn.cursor()
cur.execute("SELECT version();")
result = cur.fetchone()
if result:
    print("PostgreSQL version:", result[0])
else:
    print("Failed to get PostgreSQL version")

# Test PGVector
cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
result = cur.fetchone()
if result:
    print("PGVector version:", result[0])
else:
    print("PGVector extension not found")
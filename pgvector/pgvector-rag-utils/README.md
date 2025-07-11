# PGVector RAG System Utilities

A production-ready implementation of a Retrieval-Augmented Generation (RAG) system using PostgreSQL with PGVector extension. Supports hybrid search with both dense and sparse vectors.

## Features

- ✅ **Hybrid Search**: Combines dense and sparse vector search using Reciprocal Rank Fusion (RRF)
- ✅ **Multi-tenancy**: Support for multiple projects/topics with data isolation
- ✅ **Rich Metadata**: Flexible JSONB metadata storage with GIN indexing
- ✅ **TTL Support**: Automatic expiration of old documents
- ✅ **Batch Operations**: Efficient bulk document ingestion
- ✅ **Full PostgreSQL Power**: Leverages PostgreSQL's robust features

## Prerequisites

- PostgreSQL with PGVector 0.8.0
  - First deploy PostgreSQL+PGVector using the [pgvector-openshift](../pgvector-openshift/) deployment scripts.

- Python 3.8+
- OpenShift cluster (for deployment)

## Files Overview

### SQL Files
- `01_schema.sql` - Core database schema with tables and views
- `02_indexes.sql` - Performance indexes including HNSW for vector search
- `03_functions.sql` - Stored procedures for hybrid search and utilities

### Python Files
- `pgvector_rag.py` - Main Python client class for interacting with the system
- `example_usage.py` - Comprehensive examples of system usage

## Installation

1. **Set up PostgreSQL with PGVector** (already done in your OpenShift cluster)

2. **Create database schema**:
```bash
# Connect to your database
psql -h postgres-pgvector.pgvector.svc.cluster.local -U vectoruser -d vectordb

# Run SQL files in order
\i 01_schema.sql
\i 02_indexes.sql
\i 03_functions.sql
```

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

## Sparse Embedding Options

The system supports **hybrid search** using both dense and sparse embeddings for better search quality:

### 🔧 BM25/TF-IDF (Default)
- **No additional dependencies required**
- Classical sparse retrieval method
- Good baseline performance
- Automatically enabled

### 🚀 SPLADE (Recommended for Production)
- **Neural sparse embeddings** (state-of-the-art)
- Better semantic understanding than BM25
- Runs locally via FastEmbed library
- **Easy to enable:**

```bash
# 1. Install FastEmbed
pip install fastembed>=0.3.6

# 2. Set environment variable
echo "SPARSE_METHOD=splade" >> .env

# 3. Restart your application - SPLADE is now used automatically!
```

### 🔄 Switching Between Methods

```bash
# Use BM25 (default, no extra dependencies)
SPARSE_METHOD=bm25

# Use SPLADE (requires fastembed)
SPARSE_METHOD=splade
SPLADE_MODEL=prithivida/Splade_PP_en_v1  # optional, this is default
```

**No code changes needed** - just environment variables! Both methods work with the same hybrid search functions.

## Quick Start

```python
from pgvector_rag import PGVectorRAG
import numpy as np

# Connect to database
conn_params = {
    "host": "postgres-pgvector.pgvector.svc.cluster.local",
    "port": 5432,
    "database": "vectordb",
    "user": "vectoruser",
    "password": "vectorpass"
}

with PGVectorRAG(conn_params) as rag:
    # Create a project
    rag.create_project("my_project", "My RAG Project")
    
    # Add a document chunk
    chunk_id = rag.add_document_chunk(
        project_id="my_project",
        document_id="doc123",
        document_name="example.pdf",
        chunk_text="This is my document content",
        chunk_index=0,
        dense_embedding=np.random.randn(384),  # Your embedding here
        sparse_embedding={100: 0.5, 200: 0.3},  # Your sparse embedding
        metadata={"category": "example"}
    )
    
    # Search
    results = rag.dense_search(
        project_id="my_project",
        query_embedding=np.random.randn(384),
        limit=10
    )
```

## Schema Design

### Core Tables

1. **projects** - Multi-tenant project management
2. **document_chunks** - Main table storing document chunks with embeddings
3. **active_chunks** - View filtering out expired chunks

### Key Features

- **Vector Types**: 
  - `vector(384)` for dense embeddings
  - `sparsevec(30000)` for sparse embeddings
- **Indexes**: HNSW indexes for fast similarity search
- **Metadata**: JSONB field with GIN indexing for flexible filtering

## Search Methods

### Dense Search
Traditional semantic search using dense embeddings:
```python
results = rag.dense_search(
    project_id="my_project",
    query_embedding=query_vector,
    topic="technology",  # Optional filter
    metadata_filter={"type": "manual"}  # Optional
)
```

### Hybrid Search
Combines dense and sparse vectors using RRF:
```python
results = rag.hybrid_search(
    project_id="my_project",
    query_dense=dense_vector,
    query_sparse={"token_id": weight},
    limit=20,
    rrf_k=60  # RRF constant
)
```

## Performance Tips

1. **Batch Ingestion**: Use `add_document_chunks_batch()` for bulk uploads
2. **Index Tuning**: Adjust HNSW parameters (m, ef_construction) based on dataset size
3. **Filtering**: Use topic and metadata filters to reduce search space
4. **TTL**: Set appropriate TTL for automatic cleanup of old data

## Vector Dimensions

Default schema uses:
- Dense vectors: 384 dimensions (adjustable)
- Sparse vectors: 30,000 vocabulary size (adjustable)

Modify these in the schema based on your embedding models.

## Production Considerations

1. **Connection Pooling**: Use pgbouncer or similar for production
2. **Monitoring**: Track index performance and query times
3. **Backup**: Regular backups of the database
4. **Scaling**: Consider partitioning for very large datasets

## Troubleshooting

### Common Issues

1. **"Extension not found"**: Ensure PGVector is installed
2. **Slow searches**: Check if indexes are being used (`EXPLAIN ANALYZE`)
3. **Memory issues**: Tune PostgreSQL memory settings and index parameters

### Useful Queries

```sql
-- Check index usage
SELECT * FROM pg_stat_user_indexes WHERE schemaname = 'public';

-- View active chunks count
SELECT COUNT(*) FROM active_chunks;

-- Clean up expired chunks manually
SELECT cleanup_expired_chunks();
```

## License

This code is provided as-is for use with your PGVector deployment.

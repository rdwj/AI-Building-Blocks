"""
PGVector RAG System Python Client
Compatible with PGVector 0.8.0

SPARSE EMBEDDING SUPPORT:
========================

This client supports hybrid search using both dense and sparse vector embeddings.
The pipeline scripts automatically generate both embedding types:

1. **Dense Embeddings** (vector field)
   - Generated via Nomic Embed API
   - Provides semantic similarity search
   - 384-dimensional vectors (default)

2. **Sparse Embeddings** (sparsevec field)
   - **BM25/TF-IDF** (Default): Classical sparse retrieval, no additional dependencies
   - **SPLADE via FastEmbed** (Optional): Neural sparse embeddings, requires fastembed library
   - Switch via SPARSE_METHOD environment variable: "bm25" or "splade"
   - Provides lexical/keyword matching

The hybrid_search_rrf() function combines both embedding types using
Reciprocal Rank Fusion (RRF) for improved search quality.

To switch from BM25 to SPLADE:
1. Uncomment fastembed>=0.3.6 in requirements.txt
2. Run: pip install fastembed
3. Set environment variable: SPARSE_METHOD=splade
4. Restart your application - SPLADE will be used automatically

For best performance, use hybrid_search() for production queries.
"""

import psycopg2
import numpy as np
from pgvector.psycopg2 import register_vector
from datetime import datetime, timedelta
import json
import uuid
from typing import Dict, List, Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)


class PGVectorRAG:
    """
    A Python client for interacting with PGVector-based RAG system.
    Supports both dense and sparse vector embeddings with hybrid search.
    """
    
    def __init__(self, connection_params: dict):
        """
        Initialize connection to PGVector database.
        
        Args:
            connection_params: Dict with keys: host, port, database, user, password
        """
        self.conn = psycopg2.connect(**connection_params)
        register_vector(self.conn)
        logger.info("Connected to PGVector database")
        
    def create_project(self, project_id: str, name: str, description: Optional[str] = None) -> None:
        """Create a new project/tenant."""
        cur = self.conn.cursor()
        try:
            cur.execute("""
                INSERT INTO projects (id, name, description)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description
            """, (project_id, name, description))
            self.conn.commit()
            logger.info(f"Created/updated project: {project_id}")
        finally:
            cur.close()
    
    def add_document_chunk(
        self, 
        project_id: str,
        document_id: str,
        document_name: str,
        chunk_text: str,
        chunk_index: int,
        dense_embedding: Optional[np.ndarray] = None,
        sparse_embedding: Optional[Dict[int, float]] = None,
        metadata: Optional[Dict] = None,
        ttl_days: Optional[int] = None,
        page_number: Optional[int] = None,
        topic: Optional[str] = None,
        char_start: Optional[int] = None,
        char_end: Optional[int] = None
    ) -> int:
        """
        Add a document chunk with embeddings.
        
        Args:
            project_id: Project identifier
            document_id: Unique document ID (UUID string)
            document_name: Human-readable document name
            chunk_text: The actual text content
            chunk_index: Index of this chunk in the document
            dense_embedding: Dense vector embedding (numpy array)
            sparse_embedding: Sparse embedding as {token_id: weight}
            metadata: Additional metadata as dict
            ttl_days: Time-to-live in days
            page_number: Page number in source document
            topic: Topic/category for filtering
            char_start: Starting character position in document
            char_end: Ending character position in document
            
        Returns:
            The ID of the inserted chunk
        """
        cur = self.conn.cursor()
        
        # Convert embeddings to appropriate formats
        dense_list = dense_embedding.tolist() if dense_embedding is not None else None
        sparse_str = self._dict_to_sparsevec(sparse_embedding) if sparse_embedding else None
        
        # Calculate expiration
        expires_at = None
        if ttl_days:
            expires_at = datetime.now() + timedelta(days=ttl_days)
        
        try:
            cur.execute("""
                INSERT INTO document_chunks (
                    project_id, topic, document_id, document_name, chunk_text,
                    chunk_index, page_number, char_start, char_end,
                    dense_embedding, sparse_embedding,
                    metadata, expires_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (project_id, document_id, chunk_index) 
                DO UPDATE SET
                    chunk_text = EXCLUDED.chunk_text,
                    dense_embedding = EXCLUDED.dense_embedding,
                    sparse_embedding = EXCLUDED.sparse_embedding,
                    metadata = EXCLUDED.metadata,
                    page_number = EXCLUDED.page_number,
                    char_start = EXCLUDED.char_start,
                    char_end = EXCLUDED.char_end,
                    topic = EXCLUDED.topic,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (
                project_id, topic, document_id, document_name, chunk_text,
                chunk_index, page_number, char_start, char_end,
                dense_list, sparse_str,
                json.dumps(metadata or {}), expires_at
            ))
            
            chunk_id = cur.fetchone()[0]
            self.conn.commit()
            return chunk_id
            
        finally:
            cur.close()
    
    def add_document_chunks_batch(
        self,
        project_id: str,
        chunks: List[Dict]
    ) -> List[int]:
        """
        Add multiple document chunks in a single transaction.
        
        Args:
            project_id: Project identifier
            chunks: List of dicts with same fields as add_document_chunk
            
        Returns:
            List of inserted chunk IDs
        """
        chunk_ids = []
        cur = self.conn.cursor()
        
        try:
            for chunk in chunks:
                # Prepare data
                dense_list = chunk.get('dense_embedding')
                if isinstance(dense_list, np.ndarray):
                    dense_list = dense_list.tolist()
                    
                sparse_str = None
                if chunk.get('sparse_embedding'):
                    sparse_str = self._dict_to_sparsevec(chunk['sparse_embedding'])
                
                expires_at = None
                if chunk.get('ttl_days'):
                    expires_at = datetime.now() + timedelta(days=chunk['ttl_days'])
                
                cur.execute("""
                    INSERT INTO document_chunks (
                        project_id, topic, document_id, document_name, chunk_text,
                        chunk_index, page_number, char_start, char_end,
                        dense_embedding, sparse_embedding,
                        metadata, expires_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (project_id, document_id, chunk_index) 
                    DO UPDATE SET
                        chunk_text = EXCLUDED.chunk_text,
                        dense_embedding = EXCLUDED.dense_embedding,
                        sparse_embedding = EXCLUDED.sparse_embedding,
                        metadata = EXCLUDED.metadata,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                """, (
                    project_id, 
                    chunk.get('topic'),
                    chunk['document_id'],
                    chunk['document_name'],
                    chunk['chunk_text'],
                    chunk['chunk_index'],
                    chunk.get('page_number'),
                    chunk.get('char_start'),
                    chunk.get('char_end'),
                    dense_list,
                    sparse_str,
                    json.dumps(chunk.get('metadata', {})),
                    expires_at
                ))
                
                chunk_ids.append(cur.fetchone()[0])
            
            self.conn.commit()
            logger.info(f"Added {len(chunks)} chunks to project {project_id}")
            return chunk_ids
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error in batch insert: {e}")
            raise
        finally:
            cur.close()
    
    def hybrid_search(
        self,
        project_id: str,
        query_dense: np.ndarray,
        query_sparse: Dict[int, float],
        topic: Optional[str] = None,
        metadata_filter: Optional[Dict] = None,
        limit: int = 20,
        rrf_k: int = 60
    ) -> List[Dict]:
        """
        Perform hybrid search using both dense and sparse embeddings.
        
        Args:
            project_id: Project to search in
            query_dense: Dense query embedding
            query_sparse: Sparse query embedding {token_id: weight}
            topic: Filter by topic
            metadata_filter: Filter by metadata (JSONB containment)
            limit: Number of results to return
            rrf_k: RRF constant for score fusion
            
        Returns:
            List of search results with scores
        """
        cur = self.conn.cursor()
        
        sparse_str = self._dict_to_sparsevec(query_sparse)
        
        try:
            cur.execute("""
                SELECT * FROM hybrid_search_rrf(
                    %s, %s::vector, %s::sparsevec, %s, %s::jsonb, %s, %s
                )
            """, (
                project_id, 
                query_dense.tolist(), 
                sparse_str,
                topic,
                json.dumps(metadata_filter) if metadata_filter else None,
                limit,
                rrf_k
            ))
            
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
            
        finally:
            cur.close()
    
    def dense_search(
        self,
        project_id: str,
        query_embedding: np.ndarray,
        topic: Optional[str] = None,
        metadata_filter: Optional[Dict] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        Perform search using only dense embeddings.
        
        Args:
            project_id: Project to search in
            query_embedding: Query embedding vector
            topic: Filter by topic
            metadata_filter: Filter by metadata
            limit: Number of results
            
        Returns:
            List of search results ordered by similarity
        """
        cur = self.conn.cursor()
        
        try:
            cur.execute("""
                SELECT * FROM dense_search(
                    %s, %s::vector, %s, %s::jsonb, %s
                )
            """, (
                project_id,
                query_embedding.tolist(),
                topic,
                json.dumps(metadata_filter) if metadata_filter else None,
                limit
            ))
            
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
            
        finally:
            cur.close()
    
    def get_project_stats(self, project_id: str) -> Optional[Dict]:
        """Get statistics for a project."""
        cur = self.conn.cursor()
        
        try:
            cur.execute("SELECT * FROM get_project_stats(%s)", (project_id,))
            row = cur.fetchone()
            
            if row:
                return {
                    'total_chunks': row[0],
                    'total_documents': row[1],
                    'topics': row[2] or [],
                    'avg_chunk_length': row[3],
                    'storage_size_estimate': row[4]
                }
            return None
            
        finally:
            cur.close()
    
    def cleanup_expired(self) -> int:
        """Remove expired chunks. Returns number of deleted rows."""
        cur = self.conn.cursor()
        
        try:
            cur.execute("SELECT cleanup_expired_chunks()")
            cur.execute("SELECT COUNT(*) FROM document_chunks WHERE expires_at < NOW()")
            count = cur.fetchone()[0]
            self.conn.commit()
            logger.info(f"Cleaned up {count} expired chunks")
            return count
            
        finally:
            cur.close()
    
    def delete_document(self, project_id: str, document_id: str) -> int:
        """Delete all chunks for a document."""
        cur = self.conn.cursor()
        
        try:
            cur.execute("""
                DELETE FROM document_chunks 
                WHERE project_id = %s AND document_id = %s
                RETURNING id
            """, (project_id, document_id))
            
            deleted = len(cur.fetchall())
            self.conn.commit()
            logger.info(f"Deleted {deleted} chunks for document {document_id}")
            return deleted
            
        finally:
            cur.close()
    
    def _dict_to_sparsevec(self, sparse_dict: Dict[int, float]) -> str:
        """Convert {index: value} dict to pgvector sparsevec format."""
        if not sparse_dict:
            return "{}"
        
        # Sort by index for consistency
        sorted_items = sorted(sparse_dict.items())
        return "{" + ",".join(f"{k}:{v}" for k, v in sorted_items) + "}"
    
    def close(self):
        """Close database connection."""
        self.conn.close()
        logger.info("Closed database connection")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

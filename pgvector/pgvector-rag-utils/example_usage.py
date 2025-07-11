"""
Example usage of PGVector RAG system
Demonstrates document ingestion and hybrid search
"""

import numpy as np
from pgvector_rag import PGVectorRAG
import uuid
from typing import Dict, List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Example sparse embedding function (placeholder)
def get_sparse_embedding(text: str) -> Dict[int, float]:
    """
    Generate sparse embedding for text.
    In practice, use SPLADE, BM25, or similar.
    """
    # This is just an example - replace with real sparse encoder
    tokens = text.lower().split()
    sparse = {}
    for token in tokens:
        # Simple hash-based token ID (replace with real tokenizer)
        token_id = hash(token) % 30000
        sparse[abs(token_id)] = 1.0
    return sparse


# Example dense embedding function (placeholder)
def get_dense_embedding(text: str, dim: int = 384) -> np.ndarray:
    """
    Generate dense embedding for text.
    In practice, use sentence-transformers or similar.
    """
    # This is just an example - replace with real encoder
    # In production, use: model.encode(text)
    np.random.seed(hash(text) % 1000)
    return np.random.randn(dim).astype(np.float32)


def main():
    # Connection parameters
    conn_params = {
        "host": "postgres-pgvector.pgvector.svc.cluster.local",
        "port": 5432,
        "database": "vectordb",
        "user": "vectoruser",
        "password": "vectorpass"
    }
    
    # For local testing, use:
    # conn_params = {
    #     "host": "localhost",
    #     "port": 5432,
    #     "database": "vectordb",
    #     "user": "vectoruser",
    #     "password": "vectorpass"
    # }
    
    with PGVectorRAG(conn_params) as rag:
        # 1. Create a project
        project_id = "demo_project"
        rag.create_project(
            project_id=project_id,
            name="Demo Project",
            description="Example RAG project"
        )
        
        # 2. Add document chunks
        document_id = str(uuid.uuid4())
        document_name = "example_document.pdf"
        
        # Example document chunks
        chunks = [
            {
                "chunk_text": "PostgreSQL is a powerful, open source object-relational database system.",
                "chunk_index": 0,
                "page_number": 1,
                "topic": "databases"
            },
            {
                "chunk_text": "PGVector adds vector similarity search to PostgreSQL.",
                "chunk_index": 1,
                "page_number": 1,
                "topic": "databases"
            },
            {
                "chunk_text": "Hybrid search combines dense and sparse retrieval methods for better results.",
                "chunk_index": 2,
                "page_number": 2,
                "topic": "search"
            }
        ]
        
        # Process and add chunks
        for chunk in chunks:
            # Generate embeddings
            dense_emb = get_dense_embedding(chunk["chunk_text"])
            sparse_emb = get_sparse_embedding(chunk["chunk_text"])
            
            # Add to database
            chunk_id = rag.add_document_chunk(
                project_id=project_id,
                document_id=document_id,
                document_name=document_name,
                chunk_text=chunk["chunk_text"],
                chunk_index=chunk["chunk_index"],
                dense_embedding=dense_emb,
                sparse_embedding=sparse_emb,
                page_number=chunk["page_number"],
                topic=chunk["topic"],
                metadata={
                    "source": "example",
                    "version": "1.0"
                },
                ttl_days=365  # Expire after 1 year
            )
            logger.info(f"Added chunk {chunk_id}: {chunk['chunk_text'][:50]}...")
        
        # 3. Batch add example
        batch_chunks = []
        for i in range(3, 6):
            batch_chunks.append({
                "document_id": document_id,
                "document_name": document_name,
                "chunk_text": f"This is batch chunk {i} with sample content.",
                "chunk_index": i,
                "dense_embedding": get_dense_embedding(f"batch chunk {i}"),
                "sparse_embedding": get_sparse_embedding(f"batch chunk {i}"),
                "metadata": {"batch": True}
            })
        
        chunk_ids = rag.add_document_chunks_batch(project_id, batch_chunks)
        logger.info(f"Added {len(chunk_ids)} chunks in batch")
        
        # 4. Search examples
        
        # Dense-only search
        query = "database vector search"
        query_dense = get_dense_embedding(query)
        
        logger.info(f"\nSearching for: '{query}'")
        results = rag.dense_search(
            project_id=project_id,
            query_embedding=query_dense,
            limit=5
        )
        
        logger.info(f"Dense search found {len(results)} results:")
        for i, result in enumerate(results):
            logger.info(f"  {i+1}. {result['chunk_text'][:100]}... (distance: {result['distance']:.4f})")
        
        # Hybrid search
        query_sparse = get_sparse_embedding(query)
        
        hybrid_results = rag.hybrid_search(
            project_id=project_id,
            query_dense=query_dense,
            query_sparse=query_sparse,
            limit=5
        )
        
        logger.info(f"\nHybrid search found {len(hybrid_results)} results:")
        for i, result in enumerate(hybrid_results):
            logger.info(f"  {i+1}. {result['chunk_text'][:100]}... (RRF score: {result['rrf_score']:.4f})")
        
        # 5. Filtered search
        filtered_results = rag.dense_search(
            project_id=project_id,
            query_embedding=query_dense,
            topic="databases",  # Filter by topic
            metadata_filter={"source": "example"},  # Filter by metadata
            limit=3
        )
        
        logger.info(f"\nFiltered search found {len(filtered_results)} results")
        
        # 6. Get project statistics
        stats = rag.get_project_stats(project_id)
        logger.info(f"\nProject statistics:")
        if stats:
            logger.info(f"  Total chunks: {stats['total_chunks']}")
            logger.info(f"  Total documents: {stats['total_documents']}")
            logger.info(f"  Topics: {stats['topics']}")
            logger.info(f"  Average chunk length: {stats['avg_chunk_length']:.1f} chars")
            logger.info(f"  Storage estimate: {stats['storage_size_estimate']}")
        else:
            logger.info("  No project stats available")


def demo_sparse_embedding_methods():
    """
    Demonstrate switching between BM25 and SPLADE sparse embeddings.
    
    This shows how easy it is to switch between different sparse embedding methods
    using environment variables, without changing any code.
    """
    from pipeline_scripts.pipeline_utils import get_embeddings_with_sparse
    
    # Example environment variables (normally from .env file)
    env_vars = {
        "NOMIC_EMBED_URL": "your-nomic-url",
        "NOMIC_EMBED_API_KEY": "your-api-key",
        "NOMIC_EMBED_MODEL_NAME": "/mnt/models"
    }
    
    sample_texts = [
        "PostgreSQL is a powerful database system",
        "Vector search enables semantic similarity",
        "Hybrid search combines dense and sparse methods"
    ]
    
    logger.info("\n" + "="*50)
    logger.info("SPARSE EMBEDDING METHOD COMPARISON")
    logger.info("="*50)
    
    # Method 1: BM25 (default, no additional dependencies)
    logger.info("\n1. Using BM25/TF-IDF (default method):")
    env_vars['SPARSE_METHOD'] = 'bm25'  # or just omit this variable
    
    try:
        results_bm25 = get_embeddings_with_sparse(sample_texts, env_vars)
        logger.info(f"   ✓ Successfully generated {len(results_bm25)} embeddings using BM25")
        logger.info(f"   - Dense embedding shape: {results_bm25[0]['dense'].shape}")
        logger.info(f"   - Sparse embedding (BM25) tokens: {len(results_bm25[0]['sparse'])}")
        logger.info(f"   - Sample sparse vector: {dict(list(results_bm25[0]['sparse'].items())[:3])}...")
    except Exception as e:
        logger.error(f"   ✗ BM25 embedding failed: {e}")
    
    # Method 2: SPLADE (requires fastembed library)
    logger.info("\n2. Using SPLADE via FastEmbed (better quality):")
    env_vars['SPARSE_METHOD'] = 'splade'
    env_vars['SPLADE_MODEL'] = 'prithivida/Splade_PP_en_v1'  # optional, this is default
    
    try:
        results_splade = get_embeddings_with_sparse(sample_texts, env_vars)
        logger.info(f"   ✓ Successfully generated {len(results_splade)} embeddings using SPLADE")
        logger.info(f"   - Dense embedding shape: {results_splade[0]['dense'].shape}")
        logger.info(f"   - Sparse embedding (SPLADE) tokens: {len(results_splade[0]['sparse'])}")
        logger.info(f"   - Sample sparse vector: {dict(list(results_splade[0]['sparse'].items())[:3])}...")
    except ImportError:
        logger.warning("   ⚠ SPLADE requires fastembed library")
        logger.info("   To enable SPLADE:")
        logger.info("   1. Uncomment 'fastembed>=0.3.6' in requirements.txt")
        logger.info("   2. Run: pip install fastembed")
        logger.info("   3. Set SPARSE_METHOD=splade in your .env file")
    except Exception as e:
        logger.error(f"   ✗ SPLADE embedding failed: {e}")
    
    logger.info("\n" + "-"*50)
    logger.info("SWITCHING METHODS:")
    logger.info("- Set SPARSE_METHOD=bm25 for classical sparse retrieval (no extra deps)")
    logger.info("- Set SPARSE_METHOD=splade for neural sparse retrieval (requires fastembed)")
    logger.info("- Both methods work with the same hybrid search functions")
    logger.info("- You can switch between methods without changing any code!")
    logger.info("-"*50)


def example_with_real_embeddings():
    """
    Example using real embedding models.
    Requires: pip install sentence-transformers
    """
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
    except ImportError:
        print("sentence-transformers not installed. Run: pip install sentence-transformers")
        return
    
    # Load a model that supports both dense and sparse embeddings
    dense_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # For sparse embeddings, you could use:
    # - SPLADE: https://github.com/naver/splade
    # - BM25 embeddings
    # - TF-IDF vectors
    
    conn_params = {
        "host": "postgres-pgvector.pgvector.svc.cluster.local",
        "port": 5432,
        "database": "vectordb",
        "user": "vectoruser",
        "password": "vectorpass"
    }
    
    with PGVectorRAG(conn_params) as rag:
        # Example text
        text = "PGVector enables similarity search in PostgreSQL"
        
        # Generate real dense embedding
        dense_embedding = dense_model.encode(text)
        
        # Add to database
        rag.add_document_chunk(
            project_id="real_embeddings_demo",
            document_id=str(uuid.uuid4()),
            document_name="example.txt",
            chunk_text=text,
            chunk_index=0,
            dense_embedding=dense_embedding,
            # sparse_embedding would go here
        )


if __name__ == "__main__":
    main()
    
    # Uncomment to see comparison of BM25 vs SPLADE sparse embeddings
    # demo_sparse_embedding_methods()
    
    # Uncomment to run with real embeddings
    # example_with_real_embeddings()

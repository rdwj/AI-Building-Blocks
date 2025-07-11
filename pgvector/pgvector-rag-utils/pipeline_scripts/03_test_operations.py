#!/usr/bin/env python3
"""
Pipeline Script 3: Test RAG Operations

This script tests search, retrieval, and generation capabilities of the RAG system.
It performs comprehensive testing including:

1. Dense vector search performance and accuracy
2. Filtered search with metadata and topic constraints
3. End-to-end RAG generation with LLM integration
4. Performance metrics and system benchmarking
5. Comprehensive result reporting

The script is designed to validate that the RAG system is functioning correctly
after document ingestion and provides detailed performance metrics for
system optimization and monitoring.

Usage:
    python 03_test_operations.py

Environment Variables:
    PROJECT_ID: Project identifier to test (default: 'default_project')
    TEST_QUERIES: JSON array of test queries (default: basic queries)
    RESULTS_FILE: Path to save detailed results (default: '/mnt/outputs/test_results.json')
    
    Plus all database and API configuration variables from pipeline_utils

Test Categories:
    - Dense Search: Vector similarity search performance
    - Filtered Search: Metadata and topic-based filtering
    - RAG Generation: End-to-end question answering
    - Performance Metrics: System benchmarking and statistics

Exit Codes:
    0: All tests completed successfully
    1: Database connection failed
"""

import sys
import os
import json
import time
import logging
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pgvector_rag import PGVectorRAG
from pipeline_scripts.pipeline_utils import (
    get_env_vars, 
    get_db_connection_params,
    get_embeddings_with_sparse
)

logger = logging.getLogger(__name__)


def test_dense_search(rag: PGVectorRAG, project_id: str, queries: List[str], env_vars: dict) -> Dict:
    """
    Test dense vector search functionality and performance.
    
    Executes a series of test queries against the dense vector search system
    to validate functionality and measure performance characteristics.
    Provides detailed metrics for each query including response time and
    result quality indicators.
    
    Args:
        rag (PGVectorRAG): Initialized RAG client for database operations
        project_id (str): Project identifier to search within
        queries (List[str]): List of test queries to execute
        env_vars (dict): Environment variables for API configuration
    
    Returns:
        Dict: Test results containing:
            - dense_search_results: List of query results with metrics
            - Each result includes: query, num_results, elapsed_time, top_result
    
    Metrics Collected:
        - Query execution time
        - Number of results returned
        - Preview of top result for manual validation
    
    Side Effects:
        Logs progress and results for each test query
    """
    logger.info("Testing dense search...")
    results = []
    
    for query in queries:
        start_time = time.time()
        
        # Get query embedding
        embedding_result = get_embeddings_with_sparse([query], env_vars)[0]
        query_embedding = embedding_result['dense']
        
        # Perform search
        search_results = rag.dense_search(
            project_id=project_id,
            query_embedding=query_embedding,
            limit=5
        )
        
        elapsed_time = time.time() - start_time
        
        results.append({
            'query': query,
            'num_results': len(search_results),
            'elapsed_time': elapsed_time,
            'top_result': search_results[0]['chunk_text'][:200] if search_results else None
        })
        
        logger.info(f"Query: '{query}' - Found {len(search_results)} results in {elapsed_time:.3f}s")
    
    return {'dense_search_results': results}


def test_filtered_search(rag: PGVectorRAG, project_id: str, env_vars: dict) -> Dict:
    """
    Test filtered search capabilities with metadata and topic constraints.
    
    Validates that the search system can properly filter results based on
    metadata attributes and topic classifications. Tests both individual
    filter types and their performance characteristics.
    
    Args:
        rag (PGVectorRAG): Initialized RAG client for database operations
        project_id (str): Project identifier to search within
        env_vars (dict): Environment variables for API configuration
    
    Returns:
        Dict: Test results containing:
            - filtered_search_results: Results for different filter types
            - topic_filter: Results and timing for topic-based filtering
            - metadata_filter: Results and timing for metadata-based filtering
    
    Test Cases:
        - Topic filtering: Filter by document topic/category
        - Metadata filtering: Filter by document metadata (e.g., file_type)
    
    Note:
        Filter values should be adjusted based on actual data in the system.
        Current implementation tests for "test_topic" and "pdf" file type.
    """
    logger.info("Testing filtered search...")
    
    query = "test query for filtered search"
    embedding_result = get_embeddings_with_sparse([query], env_vars)[0]
    query_embedding = embedding_result['dense']
    
    # Test topic filter
    start_time = time.time()
    topic_results = rag.dense_search(
        project_id=project_id,
        query_embedding=query_embedding,
        topic="test_topic",  # Adjust based on your data
        limit=5
    )
    topic_elapsed = time.time() - start_time
    
    # Test metadata filter
    start_time = time.time()
    metadata_results = rag.dense_search(
        project_id=project_id,
        query_embedding=query_embedding,
        metadata_filter={"file_type": "pdf"},  # Adjust based on your data
        limit=5
    )
    metadata_elapsed = time.time() - start_time
    
    return {
        'filtered_search_results': {
            'topic_filter': {
                'num_results': len(topic_results),
                'elapsed_time': topic_elapsed
            },
            'metadata_filter': {
                'num_results': len(metadata_results),
                'elapsed_time': metadata_elapsed
            }
        }
    }


def test_rag_generation(rag: PGVectorRAG, project_id: str, query: str, env_vars: dict) -> Dict:
    """
    Test end-to-end RAG generation with LLM integration.
    
    Performs a complete RAG workflow including document retrieval,
    context preparation, and answer generation using the configured LLM.
    This tests the full system integration and validates that the
    RAG pipeline can produce coherent, contextually relevant answers.
    
    Args:
        rag (PGVectorRAG): Initialized RAG client for database operations
        project_id (str): Project identifier to search within
        query (str): Test query for generation
        env_vars (dict): Environment variables for API configuration
    
    Returns:
        Dict: Generation results containing:
            - rag_generation: Complete generation results or error information
            - query: The original query
            - num_sources: Number of source documents used
            - generated_answer: The LLM-generated response
            - sources: Preview of source documents used
    
    RAG Workflow:
        1. Generate query embedding
        2. Retrieve relevant document chunks
        3. Prepare context from retrieved chunks
        4. Generate answer using LLM with context
        5. Return answer with source attribution
    
    Error Handling:
        Returns error information if any step fails, including:
        - No relevant documents found
        - LLM API failures
        - Network or configuration issues
    """
    logger.info("Testing RAG generation...")
    
    # Get query embedding
    embedding_result = get_embeddings_with_sparse([query], env_vars)[0]
    query_embedding = embedding_result['dense']
    
    # Retrieve relevant chunks
    search_results = rag.dense_search(
        project_id=project_id,
        query_embedding=query_embedding,
        limit=5
    )
    
    if not search_results:
        return {'rag_generation': {'error': 'No relevant documents found'}}
    
    # Prepare context
    context = "\n\n".join([f"[{i+1}] {result['chunk_text']}" for i, result in enumerate(search_results)])
    
    # Generate response using Llama
    llm_url = env_vars.get('LLAMA_3_2_URL', '')
    if not llm_url.endswith('/v1'):
        llm_url = f"{llm_url}/v1"
    
    import requests
    
    prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {query}

Answer:"""
    
    try:
        response = requests.post(
            f"{llm_url}/completions",
            headers={
                'Authorization': f"Bearer {env_vars.get('LLAMA_3_2_API_KEY', '')}",
                'Content-Type': 'application/json'
            },
            json={
                'model': env_vars.get('LLAMA_3_2_MODEL_NAME', 'llama-3-2-3b'),
                'prompt': prompt,
                'max_tokens': 200,
                'temperature': 0.7
            }
        )
        response.raise_for_status()
        
        generation = response.json()['choices'][0]['text'].strip()
        
        return {
            'rag_generation': {
                'query': query,
                'num_sources': len(search_results),
                'generated_answer': generation,
                'sources': [{'doc': r['document_name'], 'text': r['chunk_text'][:100]} for r in search_results[:3]]
            }
        }
    except Exception as e:
        logger.error(f"Error in generation: {e}")
        return {'rag_generation': {'error': str(e)}}


def test_performance_metrics(rag: PGVectorRAG, project_id: str, env_vars: dict) -> Dict:
    """
    Test system performance and collect comprehensive metrics.
    
    Executes performance benchmarks to measure system characteristics
    including query latency, database statistics, and overall system
    health. Provides metrics useful for monitoring and optimization.
    
    Args:
        rag (PGVectorRAG): Initialized RAG client for database operations
        project_id (str): Project identifier to analyze
        env_vars (dict): Environment variables for API configuration
    
    Returns:
        Dict: Performance metrics containing:
            - performance_metrics: Comprehensive system metrics
            - total_chunks: Number of document chunks in database
            - total_documents: Number of documents in database
            - avg_chunk_length: Average length of document chunks
            - storage_size: Estimated storage usage
            - query_latencies: Query performance statistics (min, max, avg)
    
    Benchmark Tests:
        - Query latency across different query types and lengths
        - Database size and structure statistics
        - Storage utilization estimates
    
    Note:
        Latency tests use varied query complexity to provide
        representative performance characteristics.
    """
    logger.info("Testing performance metrics...")
    
    # Get project stats
    stats = rag.get_project_stats(project_id)
    
    # Test query latencies
    test_queries = [
        "simple test query",
        "complex query with multiple technical terms and requirements",
        "short query"
    ]
    
    latencies = []
    for query in test_queries:
        embedding_result = get_embeddings_with_sparse([query], env_vars)[0]
        
        start_time = time.time()
        results = rag.dense_search(
            project_id=project_id,
            query_embedding=embedding_result['dense'],
            limit=10
        )
        latency = time.time() - start_time
        latencies.append(latency)
    
    return {
        'performance_metrics': {
            'total_chunks': stats['total_chunks'] if stats else 0,
            'total_documents': stats['total_documents'] if stats else 0,
            'avg_chunk_length': stats['avg_chunk_length'] if stats else 0,
            'storage_size': stats['storage_size_estimate'] if stats else 'N/A',
            'query_latencies': {
                'min': min(latencies),
                'max': max(latencies),
                'avg': sum(latencies) / len(latencies)
            }
        }
    }


def main():
    """
    Main execution function for RAG testing pipeline.
    
    Orchestrates comprehensive testing of the RAG system including:
    1. Environment variable validation
    2. Database connection establishment
    3. Dense search testing
    4. Filtered search testing
    5. RAG generation testing
    6. Performance metrics collection
    7. Results compilation and output
    
    The function executes all test categories and compiles results into
    a comprehensive report suitable for system validation and monitoring.
    
    Environment Variables Used:
        PROJECT_ID: Project identifier to test
        TEST_QUERIES: JSON array of test queries
        RESULTS_FILE: Path to save detailed results
    
    Output:
        - Prints JSON-formatted test results to stdout
        - Saves detailed results to specified file
        - Provides comprehensive logging throughout execution
    
    Test Categories Executed:
        1. Dense Search: Vector similarity search validation
        2. Filtered Search: Metadata and topic filtering
        3. RAG Generation: End-to-end question answering
        4. Performance Metrics: System benchmarking
    
    Exit Codes:
        0: All tests completed successfully
        1: Database connection failed
    """
    logger.info("Starting RAG testing pipeline")
    
    # Get environment variables
    env_vars = get_env_vars()
    conn_params = get_db_connection_params(env_vars)
    
    # Get input parameters
    project_id = os.environ.get('PROJECT_ID', 'default_project')
    test_queries = json.loads(os.environ.get('TEST_QUERIES', '["What is PGVector?", "How does RAG work?"]'))
    
    # Initialize RAG client
    try:
        rag = PGVectorRAG(conn_params)
        logger.info("Connected to database")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)
    
    # Run tests
    test_results = {}
    
    # Test 1: Dense search
    test_results.update(test_dense_search(rag, project_id, test_queries, env_vars))
    
    # Test 2: Filtered search
    test_results.update(test_filtered_search(rag, project_id, env_vars))
    
    # Test 3: RAG generation
    if test_queries:
        test_results.update(test_rag_generation(rag, project_id, test_queries[0], env_vars))
    
    # Test 4: Performance metrics
    test_results.update(test_performance_metrics(rag, project_id, env_vars))
    
    # Close connection
    rag.close()
    
    # Output results
    logger.info("Testing complete")
    print(f"TEST_RESULTS={json.dumps(test_results, indent=2)}")
    
    # Write detailed results to file
    results_file = os.environ.get('RESULTS_FILE', '/mnt/outputs/test_results.json')
    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    logger.info(f"Detailed results written to {results_file}")


if __name__ == "__main__":
    main()

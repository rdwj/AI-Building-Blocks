#!/usr/bin/env python3
"""
Pipeline Script 2: Document Processing and Ingestion

This script processes documents using Docling and populates the vector database.
It performs the following operations:

1. Discovers and processes documents in specified directories
2. Extracts text content using Docling API for PDF/DOCX files
3. Chunks text into manageable pieces for vector storage
4. Generates dense embeddings using Nomic Embed API
5. Generates sparse embeddings using BM25/TF-IDF (with SPLADE option for future)
6. Stores document chunks with both embedding types and metadata in PGVector database
7. Provides progress reporting and statistics

The script supports multiple document formats and processes them in batches
for efficient database operations. It's designed to handle large document
collections and provides robust error handling.

Usage:
    python 02_ingest_documents.py

Environment Variables:
    PROJECT_ID: Project identifier (default: 'default_project')
    PROJECT_NAME: Human-readable project name (default: 'Default Project')
    DOCUMENTS_DIR: Directory containing documents to process (default: '/mnt/data/documents')
    
    Plus all database and API configuration variables from pipeline_utils

Supported File Types:
    - PDF files (processed via Docling)
    - DOCX files (processed via Docling)
    - TXT files (read directly)
    - MD files (read directly)

Exit Codes:
    0: Success
    1: Database connection failed
"""

import sys
import os
import json
import uuid
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pgvector_rag import PGVectorRAG
from pipeline_scripts.pipeline_utils import (
    get_env_vars, 
    get_db_connection_params,
    get_embeddings_with_sparse,
    process_document_with_docling,
    chunk_text
)

logger = logging.getLogger(__name__)


def process_documents_in_directory(directory_path: str, env_vars: dict, rag: PGVectorRAG, project_id: str):
    """
    Process all supported documents in a directory and its subdirectories.
    
    Recursively scans the specified directory for supported document types,
    processes each document to extract text content, generates embeddings,
    and stores the results in the vector database. The function handles
    different file types appropriately and provides comprehensive error handling.
    
    Args:
        directory_path (str): Path to the directory containing documents
        env_vars (dict): Environment variables for API configuration
        rag (PGVectorRAG): Initialized RAG client for database operations
        project_id (str): Project identifier for document organization
    
    Returns:
        int: Number of documents successfully processed
    
    Processing Steps:
        1. Scan directory for supported file types (.pdf, .docx, .txt, .md)
        2. For PDF/DOCX: Use Docling API for text extraction
        3. For TXT/MD: Read files directly
        4. Chunk text into manageable pieces
        5. Generate dense embeddings (Nomic API) and sparse embeddings (BM25) for each chunk
        6. Store chunks with both embedding types and metadata in database
    
    Side Effects:
        - Logs progress for each document processed
        - Stores document chunks in the database
        - Continues processing even if individual documents fail
    
    Note:
        Uses parent directory name as topic for document organization.
        Processes chunks in batches of 10 for database efficiency.
    """
    supported_extensions = ['.pdf', '.docx', '.txt', '.md']
    processed_count = 0
    
    path = Path(directory_path)
    if not path.exists():
        logger.error(f"Directory not found: {directory_path}")
        return 0
    
    for file_path in path.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            logger.info(f"Processing: {file_path}")
            
            try:
                # Process with Docling if PDF or DOCX
                if file_path.suffix.lower() in ['.pdf', '.docx']:
                    doc_result = process_document_with_docling(str(file_path), env_vars)
                    if doc_result and 'text' in doc_result:
                        text_content = doc_result['text']
                        metadata = doc_result.get('metadata', {})
                    else:
                        logger.warning(f"Docling processing failed for {file_path}")
                        continue
                else:
                    # Read text files directly
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text_content = f.read()
                    metadata = {}
                
                # Create chunks
                chunks = chunk_text(text_content)
                logger.info(f"Created {len(chunks)} chunks from {file_path.name}")
                
                # Generate document ID
                doc_id = str(uuid.uuid4())
                
                # Process chunks in batches
                batch_chunks = []
                for idx, chunk in enumerate(chunks):
                    # Get both dense and sparse embeddings
                    embedding_result = get_embeddings_with_sparse([chunk['text']], env_vars)[0]
                    
                    batch_chunks.append({
                        'document_id': doc_id,
                        'document_name': file_path.name,
                        'chunk_text': chunk['text'],
                        'chunk_index': idx,
                        'dense_embedding': embedding_result['dense'],
                        'sparse_embedding': embedding_result.get('sparse'),  # BM25 sparse embedding
                        'metadata': {
                            **metadata,
                            'file_path': str(file_path),
                            'file_type': file_path.suffix[1:],
                            'chunk_start': chunk['start_idx'],
                            'chunk_end': chunk['end_idx']
                        },
                        'topic': os.path.basename(file_path.parent)  # Use parent dir as topic
                    })
                    
                    # Insert in batches of 10
                    if len(batch_chunks) >= 10:
                        rag.add_document_chunks_batch(project_id, batch_chunks)
                        batch_chunks = []
                
                # Insert remaining chunks
                if batch_chunks:
                    rag.add_document_chunks_batch(project_id, batch_chunks)
                
                processed_count += 1
                logger.info(f"Successfully processed {file_path.name}")
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                continue
    
    return processed_count


def main():
    """
    Main execution function for document ingestion pipeline.
    
    Orchestrates the complete document ingestion process including:
    1. Environment variable validation
    2. Database connection establishment
    3. Project creation/update
    4. Document directory processing
    5. Statistics reporting
    6. Pipeline status output
    
    The function provides comprehensive error handling and progress reporting.
    On completion, it outputs structured results for pipeline orchestration.
    
    Environment Variables Used:
        PROJECT_ID: Unique identifier for the project
        PROJECT_NAME: Human-readable project name
        DOCUMENTS_DIR: Directory containing documents to process
    
    Output:
        Prints JSON-formatted results including:
        - project_id: The project identifier used
        - documents_processed: Number of documents successfully processed
        - total_chunks: Total number of chunks created
    
    Exit Codes:
        0: Ingestion completed successfully
        1: Database connection failed
    """
    logger.info("Starting document ingestion pipeline")
    
    # Get environment variables
    env_vars = get_env_vars()
    conn_params = get_db_connection_params(env_vars)
    
    # Get input parameters
    project_id = os.environ.get('PROJECT_ID', 'default_project')
    project_name = os.environ.get('PROJECT_NAME', 'Default Project')
    documents_dir = os.environ.get('DOCUMENTS_DIR', '/mnt/data/documents')
    
    logger.info(f"Project ID: {project_id}")
    logger.info(f"Documents directory: {documents_dir}")
    
    # Initialize RAG client
    try:
        rag = PGVectorRAG(conn_params)
        logger.info("Connected to database")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)
    
    # Create or update project
    rag.create_project(project_id, project_name, "Pipeline-created project")
    
    # Process documents
    processed_count = process_documents_in_directory(documents_dir, env_vars, rag, project_id)
    
    # Get project stats
    stats = rag.get_project_stats(project_id)
    
    logger.info(f"Ingestion complete:")
    logger.info(f"  Documents processed: {processed_count}")
    if stats:
        logger.info(f"  Total chunks: {stats['total_chunks']}")
        logger.info(f"  Total documents in DB: {stats['total_documents']}")
        logger.info(f"  Storage estimate: {stats['storage_size_estimate']}")
    else:
        logger.warning("  No project stats available")
    
    # Close connection
    rag.close()
    
    # Output for next pipeline step
    output = {
        'project_id': project_id,
        'documents_processed': processed_count,
        'total_chunks': stats['total_chunks'] if stats else 0
    }
    print(f"INGESTION_RESULT={json.dumps(output)}")


if __name__ == "__main__":
    main()

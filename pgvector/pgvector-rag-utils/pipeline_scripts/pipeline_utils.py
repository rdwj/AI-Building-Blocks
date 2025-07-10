"""
Shared utilities for pipeline scripts

This module provides common functionality used across all pipeline scripts including:
- Environment variable management
- Database connection handling
- Embedding generation via external APIs
- Document processing with Docling
- Text chunking utilities

The utilities are designed to work with the PGVector RAG pipeline system
and provide consistent interfaces for common operations.
"""
import os
import logging
from typing import Dict, List, Union, Optional
import requests
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_env_vars() -> Dict[str, str]:
    """
    Get required environment variables for the pipeline.
    
    Retrieves all necessary environment variables for database connection,
    API endpoints, and model configurations. Logs warnings for missing variables
    but continues execution to allow for partial configurations.
    
    Returns:
        Dict[str, str]: Dictionary of environment variables that are set.
                       Missing variables are excluded from the returned dict.
    
    Note:
        The following environment variables are expected:
        - DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD: Database connection
        - NOMIC_EMBED_URL, NOMIC_EMBED_API_KEY, NOMIC_EMBED_MODEL_NAME: Embedding API
        - LLAMA_3-2_URL, LLAMA_3-2_API_KEY, LLAMA_3-2_MODEL_NAME: LLM API
        - DOCLING_URL, DOCLING_API_KEY: Document processing API
    """
    required_vars = [
        'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD',
        'NOMIC_EMBED_URL', 'NOMIC_EMBED_API_KEY', 'NOMIC_EMBED_MODEL_NAME',
        'LLAMA_3_2_URL', 'LLAMA_3_2_API_KEY', 'LLAMA_3_2_MODEL_NAME',
        'DOCLING_URL', 'DOCLING_API_KEY'
    ]
    
    env_vars = {}
    missing = []
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            env_vars[var] = value
        else:
            missing.append(var)
    
    if missing:
        logger.warning(f"Missing environment variables: {missing}")
    
    return env_vars


def get_db_connection_params(env_vars: Dict[str, str]) -> Dict[str, Union[str, int]]:
    """
    Get database connection parameters from environment variables.
    
    Extracts database connection parameters from the provided environment variables
    and applies sensible defaults for OpenShift/Kubernetes deployments.
    
    Args:
        env_vars (Dict[str, str]): Dictionary of environment variables
    
    Returns:
        Dict[str, Union[str, int]]: Connection parameters suitable for psycopg2.connect()
                                   Contains: host, port, database, user, password
    
    Note:
        Default values are configured for OpenShift deployment:
        - host: postgres-pgvector.pgvector.svc.cluster.local
        - port: 5432
        - database: vectordb
        - user: vectoruser
        - password: vectorpass
    """
    return {
        "host": env_vars.get('DB_HOST', 'postgres-pgvector.pgvector.svc.cluster.local'),
        "port": int(env_vars.get('DB_PORT', '5432')),
        "database": env_vars.get('DB_NAME', 'vectordb'),
        "user": env_vars.get('DB_USER', 'vectoruser'),
        "password": env_vars.get('DB_PASSWORD', 'vectorpass')
    }


def get_embeddings(texts: List[str], env_vars: Dict[str, str]) -> List[np.ndarray]:
    """
    Get embeddings from Nomic Embed API for a list of texts.
    
    Processes a list of text strings and returns their vector embeddings
    using the configured Nomic Embed API. Handles API errors gracefully
    by returning zero vectors for failed requests.
    
    Args:
        texts (List[str]): List of text strings to embed
        env_vars (Dict[str, str]): Environment variables containing API configuration
    
    Returns:
        List[np.ndarray]: List of embedding vectors as numpy arrays.
                         Returns zero vectors (768-dim) for failed requests.
    
    Raises:
        KeyError: If required environment variables are missing
    
    Note:
        Requires the following environment variables:
        - NOMIC_EMBED_URL: API endpoint URL
        - NOMIC_EMBED_API_KEY: API authentication key
        - NOMIC_EMBED_MODEL_NAME: Model name to use for embeddings
    """
    url = env_vars['NOMIC_EMBED_URL']
    if not url.endswith('/v1'):
        url = f"{url}/v1"
    
    headers = {
        'Authorization': f"Bearer {env_vars['NOMIC_EMBED_API_KEY']}",
        'Content-Type': 'application/json'
    }
    
    embeddings = []
    
    for text in texts:
        payload = {
            'model': env_vars['NOMIC_EMBED_MODEL_NAME'],
            'input': text
        }
        
        try:
            response = requests.post(
                f"{url}/embeddings",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            embedding = data['data'][0]['embedding']
            embeddings.append(np.array(embedding))
            
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            # Return zero vector on error
            embeddings.append(np.zeros(768))  # Adjust dimension as needed
    
    return embeddings


def process_document_with_docling(file_path: str, env_vars: Dict[str, str]) -> Optional[Dict]:
    """
    Process a document using Docling API for text extraction and analysis.
    
    Sends a document file to the Docling API for processing and returns
    the extracted text and metadata. Handles various document formats
    including PDF, DOCX, and other supported types.
    
    Args:
        file_path (str): Path to the document file to process
        env_vars (Dict[str, str]): Environment variables containing API configuration
    
    Returns:
        Optional[Dict]: Dictionary containing processed document data with keys:
                       - 'text': Extracted text content
                       - 'metadata': Document metadata (optional)
                       Returns None if processing fails.
    
    Note:
        Requires the following environment variables:
        - DOCLING_URL: Docling API endpoint URL
        - DOCLING_API_KEY: API authentication key
        
        The API endpoint should support file upload via POST to /convert
    """
    url = env_vars['DOCLING_URL']
    if not url.endswith('/v1'):
        url = f"{url}/v1"
    
    headers = {
        'Authorization': f"Bearer {env_vars['DOCLING_API_KEY']}"
    }
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{url}/convert",
                headers=headers,
                files=files
            )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error processing document with Docling: {e}")
        return None


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
    """
    Split text into overlapping chunks for vector storage.
    
    Implements a simple word-based chunking strategy with configurable
    overlap to maintain context between chunks. Useful for preparing
    documents for vector database ingestion.
    
    Args:
        text (str): The text to be chunked
        chunk_size (int, optional): Number of words per chunk. Defaults to 500.
        overlap (int, optional): Number of words to overlap between chunks. Defaults to 50.
    
    Returns:
        List[Dict]: List of chunk dictionaries, each containing:
                   - 'text': The chunk text content
                   - 'start_idx': Starting word index in original text
                   - 'end_idx': Ending word index in original text
    
    Example:
        >>> chunks = chunk_text("This is a test document with many words.", 
        ...                    chunk_size=3, overlap=1)
        >>> len(chunks)
        4
        >>> chunks[0]['text']
        'This is a'
    """
    chunks = []
    words = text.split()
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        chunk_text = ' '.join(chunk_words)
        
        chunks.append({
            'text': chunk_text,
            'start_idx': i,
            'end_idx': min(i + chunk_size, len(words))
        })
    
    return chunks

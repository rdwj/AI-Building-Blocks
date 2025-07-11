"""
Shared utilities for pipeline scripts

This module provides common functionality used across all pipeline scripts including:
- Environment variable management
- Database connection handling
- Dense embedding generation via external APIs (Nomic)
- Sparse embedding generation (BM25/TF-IDF or SPLADE)
- Document processing with Docling
- Text chunking utilities

SPARSE EMBEDDING OPTIONS:
=========================

1. **BM25/TF-IDF (Current Default)**
   - Classical sparse retrieval method
   - Computed locally without additional dependencies
   - Good baseline performance
   - Implementation: get_sparse_embeddings_bm25()

2. **SPLADE via FastEmbed (Recommended - Local)**
   - Neural sparse retrieval (state-of-the-art)
   - Runs locally via fastembed library
   - Better semantic understanding than BM25
   - Implementation: get_sparse_embeddings_splade()
   - Models: Qdrant/bge-base-en-v1.5, prithivida/Splade_PP_en_v1
   - Enable: Uncomment fastembed in requirements.txt, set SPARSE_METHOD=splade

3. **SPLADE via API Service (Future Option)**
   - Deploy SPLADE model as API service
   - Consistent with current Nomic API architecture
   - Requires additional infrastructure

To switch from BM25 to SPLADE:
1. Uncomment fastembed>=0.3.6 in requirements.txt
2. Run: pip install -r requirements.txt
3. Set environment variable: SPARSE_METHOD=splade
4. Pipeline will automatically use local SPLADE model

To switch back to BM25:
1. Set environment variable: SPARSE_METHOD=bm25 (or remove variable)

The utilities are designed to work with the PGVector RAG pipeline system
and provide consistent interfaces for common operations.
"""
import os
import logging
import math
import re
from collections import Counter, defaultdict
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


# =============================================================================
# SPARSE EMBEDDING FUNCTIONS
# =============================================================================

# Global vocabulary for BM25 (simple implementation)
# In production, you might want to persist this or use a more sophisticated approach
_BM25_VOCABULARY = {}
_VOCABULARY_COUNTER = 0


def simple_tokenize(text: str) -> List[str]:
    """
    Simple tokenizer for BM25/TF-IDF.
    
    Converts text to lowercase, removes special characters, and splits on whitespace.
    This is a basic implementation - you might want to use more sophisticated
    tokenization (NLTK, spaCy) for production use.
    
    Args:
        text (str): Input text to tokenize
        
    Returns:
        List[str]: List of tokens
    """
    # Convert to lowercase and keep only alphanumeric + spaces
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
    # Split on whitespace and filter empty strings
    tokens = [token for token in cleaned.split() if token and len(token) > 1]
    return tokens


def get_sparse_embeddings_bm25(
    texts: List[str], 
    vocab_size: int = 30000,
    k1: float = 1.2, 
    b: float = 0.75
) -> List[Dict[int, float]]:
    """
    Generate BM25-based sparse embeddings for a list of texts.
    
    Implements BM25 scoring to create sparse vector representations.
    Each text becomes a sparse vector where:
    - Keys are vocabulary indices
    - Values are BM25 scores for those terms
    
    Args:
        texts (List[str]): List of texts to embed
        vocab_size (int): Maximum vocabulary size
        k1 (float): BM25 parameter controlling term frequency saturation
        b (float): BM25 parameter controlling length normalization
        
    Returns:
        List[Dict[int, float]]: List of sparse embeddings as {vocab_id: score}
        
    Note:
        This is a simplified BM25 implementation. For production use, consider:
        - Using a pre-built vocabulary from your corpus
        - More sophisticated tokenization
        - Handling of stop words
        - Stemming/lemmatization
    """
    global _BM25_VOCABULARY, _VOCABULARY_COUNTER
    
    # Tokenize all texts
    tokenized_texts = [simple_tokenize(text) for text in texts]
    
    # Build vocabulary if needed (simple approach)
    all_tokens = set()
    for tokens in tokenized_texts:
        all_tokens.update(tokens)
    
    # Add new tokens to vocabulary
    for token in all_tokens:
        if token not in _BM25_VOCABULARY and _VOCABULARY_COUNTER < vocab_size:
            _BM25_VOCABULARY[token] = _VOCABULARY_COUNTER
            _VOCABULARY_COUNTER += 1
    
    # Calculate document frequencies
    doc_freq = defaultdict(int)
    for tokens in tokenized_texts:
        unique_tokens = set(tokens)
        for token in unique_tokens:
            if token in _BM25_VOCABULARY:
                doc_freq[token] += 1
    
    # Calculate average document length
    doc_lengths = [len(tokens) for tokens in tokenized_texts]
    avg_doc_length = sum(doc_lengths) / len(doc_lengths) if doc_lengths else 1
    
    # Calculate BM25 scores for each document
    sparse_embeddings = []
    num_docs = len(texts)
    
    for doc_tokens, doc_length in zip(tokenized_texts, doc_lengths):
        sparse_vec = {}
        term_freq = Counter(doc_tokens)
        
        for term, tf in term_freq.items():
            if term in _BM25_VOCABULARY:
                vocab_id = _BM25_VOCABULARY[term]
                df = doc_freq[term]
                
                # BM25 formula
                idf = math.log((num_docs - df + 0.5) / (df + 0.5))
                tf_component = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_length / avg_doc_length)))
                bm25_score = idf * tf_component
                
                if bm25_score > 0:  # Only include positive scores
                    sparse_vec[vocab_id] = bm25_score
        
        sparse_embeddings.append(sparse_vec)
    
    return sparse_embeddings


def get_sparse_embeddings_splade(
    texts: List[str], 
    env_vars: Dict[str, str],
    model_name: str = "prithivida/Splade_PP_en_v1"
) -> List[Dict[int, float]]:
    """
    Generate SPLADE-based sparse embeddings using FastEmbed library.
    
    Uses the fastembed library to run SPLADE models locally without requiring
    API deployment. FastEmbed provides efficient local inference for various
    sparse embedding models.
    
    Args:
        texts (List[str]): List of texts to embed
        env_vars (Dict[str, str]): Environment variables (for future compatibility)
        model_name (str): FastEmbed model name to use
                         Options: "prithivida/Splade_PP_en_v1", "Qdrant/bge-base-en-v1.5"
        
    Returns:
        List[Dict[int, float]]: List of sparse embeddings as {vocab_id: score}
        
    Raises:
        ImportError: If fastembed is not installed
        RuntimeError: If model loading or embedding generation fails
        
    Example:
        >>> # First install: pip install fastembed
        >>> texts = ["hello world", "machine learning"]
        >>> embeddings = get_sparse_embeddings_splade(texts, {})
        >>> len(embeddings)
        2
        >>> isinstance(embeddings[0], dict)
        True
        
    Note:
        Available SPLADE models in FastEmbed:
        - "prithivida/Splade_PP_en_v1": SPLADE++ model, good performance
        - "Qdrant/bge-base-en-v1.5": BGE-based sparse model
        
        Models are downloaded automatically on first use and cached locally.
    """
    try:
        from fastembed import SparseTextEmbedding
    except ImportError:
        raise ImportError(
            "FastEmbed is required for SPLADE embeddings. Install with: pip install fastembed>=0.3.6\n"
            "Or uncomment fastembed in requirements.txt and run: pip install -r requirements.txt"
        )
    
    try:
        # Initialize the model (cached after first use)
        logger.info(f"Loading SPLADE model: {model_name}")
        model = SparseTextEmbedding(model_name=model_name)
        
        # Generate embeddings
        logger.info(f"Generating SPLADE embeddings for {len(texts)} texts")
        embeddings = list(model.embed(texts))
        
        # Convert FastEmbed format to our format
        sparse_embeddings = []
        for embedding in embeddings:
            # FastEmbed returns sparse embeddings as (indices, values)
            sparse_dict = {}
            indices = embedding.indices
            values = embedding.values
            
            for idx, val in zip(indices, values):
                if val > 0:  # Only include positive scores
                    sparse_dict[int(idx)] = float(val)
            
            sparse_embeddings.append(sparse_dict)
        
        logger.info(f"Generated {len(sparse_embeddings)} SPLADE embeddings")
        return sparse_embeddings
        
    except Exception as e:
        logger.error(f"Error generating SPLADE embeddings: {e}")
        raise RuntimeError(f"SPLADE embedding generation failed: {e}")


def get_sparse_embeddings(
    texts: List[str], 
    env_vars: Dict[str, str], 
    method: Optional[str] = None
) -> List[Dict[int, float]]:
    """
    Generate sparse embeddings using the specified method.
    
    This is the main entry point for sparse embedding generation.
    Method selection priority:
    1. method parameter (if provided)
    2. SPARSE_METHOD environment variable
    3. Default to "bm25"
    
    Args:
        texts (List[str]): List of texts to embed
        env_vars (Dict[str, str]): Environment variables for configuration
        method (Optional[str]): Sparse embedding method ("bm25" or "splade")
                               If None, uses SPARSE_METHOD env var or defaults to "bm25"
        
    Returns:
        List[Dict[int, float]]: List of sparse embeddings as {vocab_id: score}
        
    Raises:
        ValueError: If unknown method is specified
        ImportError: If SPLADE is requested but fastembed is not installed
        
    Environment Variables:
        SPARSE_METHOD: "bm25" or "splade" (default: "bm25")
        SPLADE_MODEL: Model name for SPLADE (default: "prithivida/Splade_PP_en_v1")
    """
    # Determine method to use
    if method is None:
        method = env_vars.get('SPARSE_METHOD', 'bm25').lower()
    else:
        method = method.lower()
    
    logger.info(f"Using sparse embedding method: {method}")
    
    if method == "bm25":
        return get_sparse_embeddings_bm25(texts)
    elif method == "splade":
        splade_model = env_vars.get('SPLADE_MODEL', 'prithivida/Splade_PP_en_v1')
        return get_sparse_embeddings_splade(texts, env_vars, splade_model)
    else:
        raise ValueError(
            f"Unknown sparse embedding method: {method}. "
            f"Supported methods: 'bm25', 'splade'"
        )


def get_embeddings_with_sparse(
    texts: List[str], 
    env_vars: Dict[str, str],
    include_sparse: bool = True,
    sparse_method: Optional[str] = None
) -> List[Dict[str, Union[np.ndarray, Dict[int, float]]]]:
    """
    Generate both dense and sparse embeddings for texts.
    
    Convenience function that generates both embedding types needed for hybrid search.
    Automatically detects sparse embedding method from environment variables.
    
    Args:
        texts (List[str]): List of texts to embed
        env_vars (Dict[str, str]): Environment variables for API configuration
        include_sparse (bool): Whether to generate sparse embeddings
        sparse_method (Optional[str]): Override sparse method ("bm25" or "splade")
                                      If None, uses SPARSE_METHOD env var or defaults to "bm25"
        
    Returns:
        List[Dict]: List of dictionaries containing:
                   - 'dense': numpy array of dense embedding
                   - 'sparse': dict of sparse embedding (if include_sparse=True)
                   
    Environment Variables:
        SPARSE_METHOD: "bm25" or "splade" (default: "bm25")
        SPLADE_MODEL: Model name for SPLADE (default: "prithivida/Splade_PP_en_v1")
        
    Example:
        >>> # Use BM25 (default)
        >>> results = get_embeddings_with_sparse(["hello world"], env_vars)
        >>> 
        >>> # Use SPLADE via environment variable
        >>> env_vars['SPARSE_METHOD'] = 'splade'
        >>> results = get_embeddings_with_sparse(["hello world"], env_vars)
        >>> 
        >>> # Force specific method
        >>> results = get_embeddings_with_sparse(["hello world"], env_vars, sparse_method="splade")
    """
    # Get dense embeddings
    dense_embeddings = get_embeddings(texts, env_vars)
    
    # Get sparse embeddings if requested
    sparse_embeddings = None
    if include_sparse:
        sparse_embeddings = get_sparse_embeddings(texts, env_vars, sparse_method)
    
    # Combine results
    results = []
    for i, dense_emb in enumerate(dense_embeddings):
        result = {'dense': dense_emb}
        if sparse_embeddings:
            result['sparse'] = sparse_embeddings[i]
        results.append(result)
    
    return results

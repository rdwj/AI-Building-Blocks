# PGVector RAG Notebooks

This directory contains Jupyter notebooks demonstrating various aspects of the PGVector RAG system.

## Notebooks

### 1. Test API Endpoints (`01_test_api_endpoints.ipynb`)
**Purpose**: Test and explore the LLM, embedding, and document processing APIs

**Features**:
- Test Nomic Embed API for generating embeddings
- Test Llama 3.2 API for text generation
- Explore prompt engineering techniques
- Test Docling API for document processing
- Run a mini RAG pipeline example

**Use this when**: You want to verify your API connections or experiment with prompt engineering

### 2. Ask RAG Questions (`02_ask_rag_questions.ipynb`)
**Purpose**: Interactive question-answering with your RAG system

**Features**:
- Ask questions and get answers from your document collection
- View source documents for answers
- Filter by topic or metadata
- Multi-turn conversations with context
- Batch question processing

**Use this when**: You want to query your knowledge base and get AI-generated answers

### 3. Compare Search Methods (`03_compare_search_methods.ipynb`)
**Purpose**: Understand the differences between dense vector search and hybrid search

**Features**:
- Side-by-side comparison of search results
- Performance benchmarking
- Result overlap analysis
- Visualizations of search differences
- Interactive comparison tool

**Use this when**: You want to understand when to use different search strategies

### 4. Database Statistics (`04_database_statistics.ipynb`)
**Purpose**: Analyze and visualize your PGVector database

**Features**:
- Overall database statistics
- Project and document analysis
- Topic distribution
- Temporal analysis (ingestion timeline)
- Vector coverage analysis
- Storage and performance metrics
- Export summary reports

**Use this when**: You want insights into your data or need to monitor system health

## Setup

Before running the notebooks:

1. **Install dependencies**:
```bash
pip install jupyter notebook pandas numpy matplotlib seaborn plotly scikit-learn python-dotenv
```

2. **Configure environment**:
- Copy `.env.example` to `.env` in the parent directory
- Fill in your API keys and database credentials

3. **Start Jupyter**:
```bash
jupyter notebook
```

## Tips

- Run cells in order - some notebooks build on previous cells
- Adjust queries based on your actual document content
- The comparison notebook adds test data - you may want to clean it up after
- Statistics notebook includes write operations for generating reports

## Customization

Feel free to modify these notebooks for your specific use case:
- Change embedding dimensions based on your model
- Adjust search parameters
- Add new visualization types
- Extend with additional API integrations

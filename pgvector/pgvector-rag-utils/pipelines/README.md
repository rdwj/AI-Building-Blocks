# Elyra Pipelines for PGVector RAG System

This directory contains Elyra pipeline definitions for deploying and managing the PGVector RAG system on OpenShift AI.

## Pipeline Overview

### 1. Setup Database Pipeline (`01_setup_database.pipeline`)
- Initializes the PGVector database schema
- Creates tables, indexes, and functions
- Verifies the setup

### 2. Document Ingestion Pipeline (`02_ingest_documents.pipeline`)
- Processes documents from a specified directory
- Uses Docling API for document parsing (PDF, DOCX)
- Generates embeddings using Nomic Embed API
- Stores chunks in the vector database

### 3. Test Operations Pipeline (`03_test_operations.pipeline`)
- Tests dense vector search
- Tests filtered search with metadata
- Tests RAG generation using Llama model
- Measures performance metrics
- Outputs results to JSON file

### 4. Complete Pipeline (`complete_pipeline.pipeline`)
- Runs all three pipelines in sequence
- Setup → Ingest → Test

## Prerequisites

1. **OpenShift AI with Elyra**
2. **PGVector database** deployed on OpenShift
3. **API Access** to:
   - Nomic Embed API (for embeddings)
   - Llama 3.2 API (for text generation)
   - Docling API (for document processing)

## Setup Instructions

### 1. Create Runtime Configuration

In Elyra, create a new runtime configuration:

1. Open JupyterLab with Elyra
2. Go to Settings → Runtime Images
3. Add the runtime image: `quay.io/modh/runtime-images:runtime-cuda-tensorflow-ubi9-python-3.9-2023b`
4. Go to Settings → Pipeline Runtime Configuration
5. Create new configuration named `pgvector-runtime`
6. Configure with your OpenShift details

### 2. Configure Environment Variables

Create a ConfigMap or Secret with your credentials:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: pgvector-pipeline-secrets
  namespace: your-namespace
type: Opaque
stringData:
  DB_HOST: "postgres-pgvector.pgvector.svc.cluster.local"
  DB_PORT: "5432"
  DB_NAME: "vectordb"
  DB_USER: "vectoruser"
  DB_PASSWORD: "your-password"
  NOMIC_EMBED_URL: "your-nomic-url"
  NOMIC_EMBED_API_KEY: "your-nomic-key"
  NOMIC_EMBED_MODEL_NAME: "/mnt/models"
  LLAMA_3-2_URL: "your-llama-url"
  LLAMA_3-2_API_KEY: "your-llama-key"
  LLAMA_3-2_MODEL_NAME: "llama-3-2-3b"
  DOCLING_URL: "your-docling-url"
  DOCLING_API_KEY: "your-docling-key"
```

### 3. Create PVC for Documents

Create a PersistentVolumeClaim for your documents:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: documents-pvc
  namespace: your-namespace
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### 4. Upload Documents

Upload your documents to the PVC at `/mnt/data/documents/`

## Running the Pipelines

### Option 1: Run Complete Pipeline
1. Open `complete_pipeline.pipeline` in Elyra
2. Configure runtime settings
3. Click "Run Pipeline"

### Option 2: Run Individual Pipelines
Run each pipeline separately in order:
1. `01_setup_database.pipeline`
2. `02_ingest_documents.pipeline`
3. `03_test_operations.pipeline`

## Customization

### Pipeline Parameters

You can customize the following parameters:

- **PROJECT_ID**: Project identifier for multi-tenancy
- **DOCUMENTS_DIR**: Directory containing documents to process
- **TEST_QUERIES**: JSON array of queries for testing

### Modifying Scripts

The pipeline scripts are in the `pipeline_scripts/` directory:
- `01_setup_database.py`
- `02_ingest_documents.py`
- `03_test_operations.py`
- `pipeline_utils.py` (shared utilities)

## Monitoring

### Pipeline Logs
- Check pipeline execution logs in the Elyra UI
- View pod logs in OpenShift console

### Test Results
- Test results are saved to `/mnt/outputs/test_results.json`
- Download from the pipeline outputs

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify database credentials
   - Check network connectivity
   - Ensure PGVector is running

2. **API Errors**
   - Verify API keys are correct
   - Check API endpoints include `/v1` if needed
   - Ensure APIs are accessible from cluster

3. **Document Processing Failed**
   - Check document format is supported
   - Verify Docling API is working
   - Check file permissions on PVC

### Debug Mode

To enable debug logging, add to environment variables:
```
PYTHONUNBUFFERED=1
LOG_LEVEL=DEBUG
```

## Next Steps

1. **Scale Up**: Process larger document sets
2. **Add Sparse Embeddings**: Implement SPLADE or BM25
3. **Custom Chunking**: Implement semantic chunking strategies
4. **Production Deployment**: Add monitoring and alerting

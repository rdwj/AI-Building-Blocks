# OpenShift Deployment Scripts for PostgreSQL + PGVector

This directory contains scripts to deploy and manage PostgreSQL with PGVector on OpenShift.

## Scripts

### 🚀 deploy-and-test.sh
Main deployment and testing script that:
- Creates namespace (if needed)
- Deploys PostgreSQL with PGVector
- Waits for pods to be ready
- Verifies PostgreSQL is running
- Creates and tests PGVector extension
- Runs vector operation tests
- Provides connection details

**Usage:**
```bash
# Deploy to default namespace (pgvector)
./deploy-and-test.sh

# Deploy to custom namespace
NAMESPACE=my-namespace ./deploy-and-test.sh
```

### 🧹 cleanup-deployment.sh
Removes the PostgreSQL + PGVector deployment:
- Confirms before deletion
- Deletes all resources
- Optionally removes namespace
- **WARNING**: This deletes all data!

**Usage:**
```bash
# Clean up default namespace
./cleanup-deployment.sh

# Clean up custom namespace
NAMESPACE=my-namespace ./cleanup-deployment.sh
```

### 🔍 test-connection.sh
Quick connectivity test that:
- Checks if PostgreSQL is accessible
- Verifies PGVector version
- Tests vector operations
- Shows connection details

**Usage:**
```bash
# Test default namespace
./test-connection.sh

# Test custom namespace
NAMESPACE=my-namespace ./test-connection.sh
```

## Prerequisites

1. **OpenShift CLI (oc)** installed
2. **Logged into OpenShift cluster**: `oc login`
3. **Appropriate permissions** to create resources

## Quick Start

1. Make scripts executable:
```bash
chmod +x deploy-and-test.sh
chmod +x cleanup-deployment.sh
chmod +x test-connection.sh
```

2. Deploy PostgreSQL + PGVector:
```bash
./deploy-and-test.sh
```

3. Test connection:
```bash
./test-connection.sh
```

## Related Building Blocks

- **Next Step**: [PGVector RAG Utilities](../pgvector-rag-utils/) - Python utilities and pipelines for building RAG applications
- **Repository**: Part of [AI Building Blocks](https://github.com/rdwj/AI-Building-Blocks)

## Connection Details

After successful deployment:

**From within OpenShift cluster:**
- Host: `postgres-pgvector.pgvector.svc.cluster.local`
- Port: `5432`
- Database: `vectordb`
- Username: `vectoruser`
- Password: `vectorpass`

**For local access:**
```bash
oc port-forward -n pgvector svc/postgres-pgvector 5432:5432
```

Then connect locally:
```bash
psql -h localhost -p 5432 -U vectoruser -d vectordb
```

## Customization

You can customize the deployment by setting environment variables:

```bash
NAMESPACE=custom-namespace \
DB_NAME=mydb \
DB_USER=myuser \
DB_PASSWORD=mypass \
./deploy-and-test.sh
```

## Troubleshooting

### Pod not starting
```bash
# Check pod status
oc get pods -n pgvector

# Check pod logs
oc logs -n pgvector $(oc get pod -l app=postgres-pgvector -o jsonpath='{.items[0].metadata.name}')

# Describe pod for events
oc describe pod -n pgvector $(oc get pod -l app=postgres-pgvector -o jsonpath='{.items[0].metadata.name}')
```

### PVC issues
```bash
# Check PVC status
oc get pvc -n pgvector

# Check available storage classes
oc get storageclass
```

### Permission errors
Ensure you have the necessary permissions:
```bash
oc auth can-i create deployment -n pgvector
oc auth can-i create service -n pgvector
oc auth can-i create pvc -n pgvector
```

## Next Steps

After deployment, proceed to the [PGVector RAG Utilities](../pgvector-rag-utils/) to:
1. Set up the database schema
2. Ingest documents using Elyra pipelines
3. Use the Jupyter notebooks to build RAG applications
4. Explore the Python client library

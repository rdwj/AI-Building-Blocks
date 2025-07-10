#!/bin/bash

# Quick PostgreSQL + PGVector Connection Test Script
# Use this to quickly test if the deployment is accessible

set -e

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
NAMESPACE="${NAMESPACE:-pgvector}"
SERVICE_NAME="postgres-pgvector"
DB_NAME="vectordb"
DB_USER="vectoruser"
DB_PASSWORD="vectorpass"

echo -e "${BLUE}PostgreSQL + PGVector Quick Test${NC}"
echo "================================="

# Get pod name
POD_NAME=$(oc get pod -l app=postgres-pgvector -n $NAMESPACE -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$POD_NAME" ]; then
    echo -e "${RED}[ERROR]${NC} No PostgreSQL pod found in namespace $NAMESPACE"
    exit 1
fi

echo "Pod: $POD_NAME"
echo ""

# Test 1: Basic connectivity
echo "1. Testing basic connectivity..."
if oc exec -n $NAMESPACE $POD_NAME -- psql -U $DB_USER -d $DB_NAME -c "SELECT 1;" &>/dev/null; then
    echo -e "${GREEN}✓${NC} PostgreSQL is accessible"
else
    echo -e "${RED}✗${NC} Cannot connect to PostgreSQL"
    exit 1
fi

# Test 2: PGVector version
echo ""
echo "2. Checking PGVector version..."
VERSION=$(oc exec -n $NAMESPACE $POD_NAME -- psql -U $DB_USER -d $DB_NAME -t -c "SELECT extversion FROM pg_extension WHERE extname = 'vector';" 2>/dev/null | tr -d ' ')

if [ -n "$VERSION" ]; then
    echo -e "${GREEN}✓${NC} PGVector $VERSION is installed"
else
    echo -e "${RED}✗${NC} PGVector extension not found"
fi

# Test 3: Vector operations
echo ""
echo "3. Testing vector operations..."
if oc exec -n $NAMESPACE $POD_NAME -- psql -U $DB_USER -d $DB_NAME -c "SELECT '[1,2,3]'::vector;" &>/dev/null; then
    echo -e "${GREEN}✓${NC} Vector operations are working"
else
    echo -e "${RED}✗${NC} Vector operations failed"
fi

# Test 4: Service endpoint
echo ""
echo "4. Service endpoint:"
echo "   Internal: $SERVICE_NAME.$NAMESPACE.svc.cluster.local:5432"
echo ""
echo "To connect locally, run:"
echo "   oc port-forward -n $NAMESPACE svc/$SERVICE_NAME 5432:5432"
echo ""

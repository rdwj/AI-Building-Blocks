#!/bin/bash

# PostgreSQL + PGVector Deployment and Testing Script
# This script deploys PostgreSQL with PGVector on OpenShift and verifies the setup

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-pgvector}"
DEPLOYMENT_NAME="postgres-pgvector"
SERVICE_NAME="postgres-pgvector"
PVC_NAME="postgres-pvc"
DB_NAME="vectordb"
DB_USER="vectoruser"
DB_PASSWORD="vectorpass"
YAML_FILE="../openshift/postgres-pgvector.yaml"

# Function to print colored output with timestamp
print_info() {
    echo -e "${BLUE}[INFO $(date '+%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS $(date '+%H:%M:%S')]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR $(date '+%H:%M:%S')]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING $(date '+%H:%M:%S')]${NC} $1"
}

# Function to wait for pod to be ready
wait_for_pod() {
    local label=$1
    local timeout=${2:-300}  # Default 5 minutes
    
    print_info "Waiting for pod with label $label to be ready..."
    
    local count=0
    while [ $count -lt $timeout ]; do
        local pod_status=$(oc get pods -l $label -n $NAMESPACE -o jsonpath='{.items[0].status.phase}' 2>/dev/null)
        local pod_ready=$(oc get pods -l $label -n $NAMESPACE -o jsonpath='{.items[0].status.containerStatuses[0].ready}' 2>/dev/null)
        
        if [ "$pod_status" = "Running" ] && [ "$pod_ready" = "true" ]; then
            print_success "Pod is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        count=$((count + 2))
    done
    
    print_error "Timeout waiting for pod to be ready"
    return 1
}

# Function to wait for PostgreSQL to be ready
wait_for_postgres() {
    local pod_name=$1
    local max_attempts=30
    local count=0
    
    print_info "Waiting for PostgreSQL to be ready..."
    
    while [ $count -lt $max_attempts ]; do
        if oc exec -n $NAMESPACE "$pod_name" -- pg_isready -U $DB_USER -d $DB_NAME &>/dev/null; then
            print_success "PostgreSQL is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        count=$((count + 1))
    done
    
    echo ""
    print_error "PostgreSQL did not become ready in time"
    return 1
}

# Function to run SQL command with retry
run_sql() {
    local sql=$1
    local retry_count=${2:-5}  # Default 5 retries
    local retry_delay=${3:-3}  # Default 3 seconds between retries
    
    local pod_name=$(oc get pod -l app=$DEPLOYMENT_NAME -n $NAMESPACE -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    
    if [ -z "$pod_name" ]; then
        print_error "No pod found"
        return 1
    fi
    
    local count=0
    while [ $count -lt $retry_count ]; do
        if oc exec -n $NAMESPACE "$pod_name" -- psql -U $DB_USER -d $DB_NAME -c "$sql" 2>/dev/null; then
            return 0
        fi
        
        count=$((count + 1))
        if [ $count -lt $retry_count ]; then
            echo -n "."
            sleep $retry_delay
        fi
    done
    
    return 1
}

# Main deployment and testing
main() {
    echo "=========================================="
    echo "PostgreSQL + PGVector Deployment Script"
    echo "=========================================="
    echo ""
    
    # Check if YAML file exists
    if [ ! -f "$YAML_FILE" ]; then
        print_error "YAML file not found: $YAML_FILE"
        exit 1
    fi
    
    # Check if logged into OpenShift
    if ! oc whoami &>/dev/null; then
        print_error "Not logged into OpenShift. Please run 'oc login' first."
        exit 1
    fi
    
    print_info "Current OpenShift context:"
    oc whoami
    CURRENT_PROJECT=$(oc project -q 2>/dev/null || echo "No current project")
    print_info "Current project: $CURRENT_PROJECT"
    echo ""
    
    # Create project/namespace if it doesn't exist
    if ! oc get project $NAMESPACE &>/dev/null; then
        print_info "Creating project: $NAMESPACE"
        oc new-project $NAMESPACE --display-name="PGVector Database" --description="PostgreSQL with PGVector for RAG system"
        print_success "Project created!"
    else
        print_info "Project $NAMESPACE already exists"
    fi
    
    # Switch to project
    print_info "Switching to project: $NAMESPACE"
    if ! oc project $NAMESPACE; then
        print_error "Failed to switch to project $NAMESPACE"
        exit 1
    fi
    echo ""
    
    # Apply the YAML
    print_info "Applying PostgreSQL + PGVector deployment..."
    oc apply -f $YAML_FILE
    echo ""
    
    # Wait for deployment to be ready
    print_info "Waiting for deployment to be ready..."
    oc rollout status deployment/$DEPLOYMENT_NAME -n $NAMESPACE --timeout=300s
    print_success "Deployment is ready!"
    echo ""
    
    # Wait for pod to be fully ready
    wait_for_pod "app=$DEPLOYMENT_NAME"
    echo ""
    
    # Get pod name
    POD_NAME=$(oc get pod -l app=$DEPLOYMENT_NAME -n $NAMESPACE -o jsonpath='{.items[0].metadata.name}')
    print_info "Pod name: $POD_NAME"
    echo ""
    
    # Wait for PostgreSQL to be ready
    if ! wait_for_postgres "$POD_NAME"; then
        print_error "PostgreSQL failed to start properly"
        exit 1
    fi
    echo ""
    
    # Test 1: Check PostgreSQL version
    print_info "Test 1: Checking PostgreSQL version..."
    if run_sql "SELECT version();"; then
        print_success "PostgreSQL is running!"
    else
        print_error "Failed to connect to PostgreSQL"
        exit 1
    fi
    echo ""
    
    # Test 2: Check PGVector extension
    print_info "Test 2: Checking PGVector extension..."
    PGVECTOR_VERSION=$(run_sql "SELECT extversion FROM pg_extension WHERE extname = 'vector';" | grep -E '[0-9]+\.[0-9]+\.[0-9]+' || echo "")
    
    if [ -z "$PGVECTOR_VERSION" ]; then
        print_warning "PGVector extension not created yet. Creating it now..."
        if run_sql "CREATE EXTENSION IF NOT EXISTS vector;"; then
            print_success "PGVector extension created!"
            PGVECTOR_VERSION=$(run_sql "SELECT extversion FROM pg_extension WHERE extname = 'vector';" | grep -E '[0-9]+\.[0-9]+\.[0-9]+')
            print_success "PGVector version: $PGVECTOR_VERSION"
        else
            print_error "Failed to create PGVector extension"
            exit 1
        fi
    else
        print_success "PGVector is already installed! Version: $PGVECTOR_VERSION"
    fi
    echo ""
    
    # Test 3: Create test table with vector column
    print_info "Test 3: Creating test table with vector column..."
    if run_sql "CREATE TABLE IF NOT EXISTS test_vectors (id SERIAL PRIMARY KEY, embedding vector(3));"; then
        print_success "Test table created successfully!"
    else
        print_error "Failed to create test table"
        exit 1
    fi
    echo ""
    
    # Test 4: Insert and query test vector
    print_info "Test 4: Testing vector operations..."
    if run_sql "INSERT INTO test_vectors (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');"; then
        print_success "Test vectors inserted!"
        
        # Query vectors
        print_info "Querying vectors..."
        run_sql "SELECT id, embedding FROM test_vectors;"
        
        # Test similarity search
        print_info "Testing similarity search..."
        run_sql "SELECT id, embedding <=> '[1,2,3]' as distance FROM test_vectors ORDER BY embedding <=> '[1,2,3]' LIMIT 2;"
        
        print_success "Vector operations working correctly!"
    else
        print_error "Failed to insert test vectors"
        exit 1
    fi
    echo ""
    
    # Test 5: Check service
    print_info "Test 5: Checking service..."
    SVC_EXISTS=$(oc get svc $SERVICE_NAME -n $NAMESPACE -o name 2>/dev/null || echo "")
    if [ -n "$SVC_EXISTS" ]; then
        print_success "Service exists!"
        oc get svc $SERVICE_NAME -n $NAMESPACE
    else
        print_error "Service not found"
        exit 1
    fi
    echo ""
    
    # Test 6: Check PVC
    print_info "Test 6: Checking persistent volume claim..."
    PVC_STATUS=$(oc get pvc $PVC_NAME -n $NAMESPACE -o jsonpath='{.status.phase}' 2>/dev/null || echo "")
    if [ "$PVC_STATUS" = "Bound" ]; then
        print_success "PVC is bound!"
        oc get pvc $PVC_NAME -n $NAMESPACE
    else
        print_warning "PVC status: $PVC_STATUS"
    fi
    echo ""
    
    # Clean up test table
    print_info "Cleaning up test table..."
    run_sql "DROP TABLE IF EXISTS test_vectors;"
    echo ""
    
    # Summary
    echo "=========================================="
    echo "Deployment Summary"
    echo "=========================================="
    print_success "PostgreSQL + PGVector deployed successfully!"
    echo ""
    echo "Connection Details:"
    echo "  Project: $NAMESPACE"
    echo "  Service: $SERVICE_NAME.$NAMESPACE.svc.cluster.local"
    echo "  Port: 5432"
    echo "  Database: $DB_NAME"
    echo "  Username: $DB_USER"
    echo "  Password: $DB_PASSWORD"
    echo ""
    echo "PGVector Version: $PGVECTOR_VERSION"
    echo ""
    echo "To connect from within the cluster:"
    echo "  psql -h $SERVICE_NAME.$NAMESPACE.svc.cluster.local -U $DB_USER -d $DB_NAME"
    echo ""
    echo "To port-forward for local access:"
    echo "  oc port-forward -n $NAMESPACE svc/$SERVICE_NAME 5432:5432"
    echo ""
    echo "To run the test again:"
    echo "  ./test-connection.sh"
    echo ""
}

# Run main function
main "$@"

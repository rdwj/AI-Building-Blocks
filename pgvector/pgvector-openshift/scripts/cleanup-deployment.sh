#!/bin/bash

# PostgreSQL + PGVector Cleanup Script
# This script removes the PostgreSQL with PGVector deployment from OpenShift

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-pgvector}"
YAML_FILE="./openshift/postgres-pgvector.yaml"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Main cleanup function
main() {
    echo "=========================================="
    echo "PostgreSQL + PGVector Cleanup Script"
    echo "=========================================="
    echo ""
    
    # Check if logged into OpenShift
    if ! oc whoami &>/dev/null; then
        print_error "Not logged into OpenShift. Please run 'oc login' first."
        exit 1
    fi
    
    print_info "Current OpenShift context:"
    oc whoami
    echo ""
    
    # Confirmation prompt
    print_warning "This will delete the PostgreSQL + PGVector deployment in project: $NAMESPACE"
    print_warning "This action will DELETE ALL DATA and cannot be undone!"
    echo ""
    read -p "Are you sure you want to continue? (type 'yes' to confirm): " confirmation
    
    if [ "$confirmation" != "yes" ]; then
        print_info "Cleanup cancelled."
        exit 0
    fi
    
    # Check if project exists
    if ! oc get project $NAMESPACE &>/dev/null; then
        print_warning "Project $NAMESPACE does not exist. Nothing to clean up."
        exit 0
    fi
    
    # Switch to project
    print_info "Switching to project: $NAMESPACE"
    oc project $NAMESPACE
    echo ""
    
    # Delete using the YAML file if it exists
    if [ -f "$YAML_FILE" ]; then
        print_info "Deleting resources using YAML file..."
        oc delete -f $YAML_FILE --ignore-not-found=true
    else
        print_warning "YAML file not found. Deleting resources individually..."
        
        # Delete individual resources
        print_info "Deleting deployment..."
        oc delete deployment postgres-pgvector --ignore-not-found=true
        
        print_info "Deleting service..."
        oc delete service postgres-pgvector --ignore-not-found=true
        
        print_info "Deleting PVC..."
        oc delete pvc postgres-pvc --ignore-not-found=true
        
        print_info "Deleting ConfigMap (if exists)..."
        oc delete configmap postgres-init --ignore-not-found=true
    fi
    
    echo ""
    
    # Optional: Delete the project
    read -p "Do you also want to delete the project '$NAMESPACE'? (yes/no): " delete_project
    if [ "$delete_project" = "yes" ]; then
        print_info "Deleting project: $NAMESPACE"
        oc delete project $NAMESPACE
        print_success "Project deleted!"
    else
        print_info "Project preserved."
    fi
    
    echo ""
    print_success "Cleanup completed!"
}

# Run main function
main "$@"

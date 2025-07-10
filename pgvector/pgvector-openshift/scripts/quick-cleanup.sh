#!/bin/bash

# Quick cleanup script before redeployment
# This ensures a clean state for testing

NAMESPACE="${NAMESPACE:-pgvector}"

echo "Cleaning up existing deployment in project: $NAMESPACE"

# Check if project exists
if oc get project $NAMESPACE &>/dev/null; then
    echo "Switching to project $NAMESPACE..."
    oc project $NAMESPACE
    
    echo "Deleting existing resources..."
    oc delete deployment postgres-pgvector --ignore-not-found=true
    oc delete service postgres-pgvector --ignore-not-found=true
    oc delete pvc postgres-pvc --ignore-not-found=true
    oc delete configmap postgres-init --ignore-not-found=true
    
    echo "Waiting for pods to terminate..."
    oc wait --for=delete pod -l app=postgres-pgvector --timeout=60s 2>/dev/null || true
    
    echo "Cleanup complete!"
else
    echo "Project $NAMESPACE does not exist"
fi

echo ""
echo "Ready for fresh deployment. Run ./deploy-and-test.sh"

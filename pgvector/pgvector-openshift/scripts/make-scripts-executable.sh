#!/bin/bash
# Make deployment scripts executable

echo "Making deployment scripts executable..."

chmod +x deploy-and-test.sh
chmod +x cleanup-deployment.sh
chmod +x test-connection.sh
chmod +x quick-cleanup.sh
chmod +x make-scripts-executable.sh

echo "✓ deploy-and-test.sh"
echo "✓ cleanup-deployment.sh"
echo "✓ test-connection.sh"
echo "✓ quick-cleanup.sh"
echo "✓ make-scripts-executable.sh"
echo ""
echo "Scripts are now executable!"
echo ""
echo "To deploy PostgreSQL + PGVector, run:"
echo "  ./deploy-and-test.sh"

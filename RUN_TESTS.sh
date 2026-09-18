#!/bin/bash
# E-Cell Task Portal - Complete System Test
# This script verifies the entire system works

echo ""
echo "================================================"
echo "  E-Cell Task Portal - System Test"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.10+"
    exit 1
fi

# Check if the test script exists
if [ ! -f "scripts/test-system.py" ]; then
    echo "ERROR: scripts/test-system.py not found"
    exit 1
fi

# Run the test
echo "Running comprehensive system tests..."
echo ""

python3 scripts/test-system.py
TEST_RESULT=$?

if [ $TEST_RESULT -ne 0 ]; then
    echo ""
    echo "================================================"
    echo "  TESTS FAILED"
    echo "================================================"
    exit 1
else
    echo ""
    echo "================================================"
    echo "  ALL TESTS PASSED!"
    echo "================================================"
    echo ""
    echo "Next steps:"
    echo "1. Configure .env with your credentials"
    echo "2. Run: docker-compose up"
    echo "3. Access: http://localhost:3000"
    echo ""
    exit 0
fi

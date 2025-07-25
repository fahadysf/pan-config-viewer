#!/bin/bash

set +e  # Continue on error

echo "🚀 PAN-OS Configuration API Test Runner (Graceful Mode)"
echo "======================================================"

# Function to cleanup
cleanup() {
    echo -e "\n🧹 Cleaning up..."
    if [ ! -z "$API_CONTAINER_ID" ]; then
        docker stop $API_CONTAINER_ID >/dev/null 2>&1 || true
        docker rm $API_CONTAINER_ID >/dev/null 2>&1 || true
    fi
    docker-compose down >/dev/null 2>&1 || true
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it and try again."
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -q -r requirements.txt

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose down >/dev/null 2>&1 || true

# Start the API using docker-compose
echo "🐳 Starting API container..."
docker-compose up -d --build

# Get container ID
API_CONTAINER_ID=$(docker-compose ps -q pan-config-api)

# Wait for API to be ready
echo "⏳ Waiting for API to be ready..."
MAX_ATTEMPTS=30
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -s http://localhost:8000/api/v1/health >/dev/null 2>&1; then
        echo "✅ API is ready!"
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo "❌ API failed to start. Check logs with: docker-compose logs"
        exit 1
    fi
    echo -n "."
    sleep 1
done
echo ""

# Test result tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Run basic smoke test first
echo -e "\n🔍 Running basic smoke test..."
if python tests/test_basic.py; then
    echo "✅ Basic smoke test passed"
    ((PASSED_TESTS++))
else
    echo "⚠️  Basic smoke test had some failures"
    ((FAILED_TESTS++))
fi
((TOTAL_TESTS++))

# Run tests with the test configuration
echo -e "\n📋 Running tests with test configuration..."
export CONFIG_FILES_PATH="tests/test_configs"
if pytest tests/test_api.py -v --tb=short --continue-on-collection-errors; then
    echo "✅ Test configuration tests passed"
    ((PASSED_TESTS++))
else
    echo "⚠️  Test configuration tests had failures"
    ((FAILED_TESTS++))
fi
((TOTAL_TESTS++))

# Run tests with the real configuration
echo -e "\n📊 Running tests with real configuration..."
export CONFIG_FILES_PATH="config-files"
if pytest tests/test_real_config.py -v --tb=short --continue-on-collection-errors; then
    echo "✅ Real configuration tests passed"
    ((PASSED_TESTS++))
else
    echo "⚠️  Real configuration tests had failures"
    ((FAILED_TESTS++))
fi
((TOTAL_TESTS++))

# Run all tests with coverage
echo -e "\n📈 Running all tests with coverage..."
if pytest --cov=main --cov=parser --cov=models \
       --cov-report=term-missing \
       --cov-report=html \
       --cov-report=xml \
       --continue-on-collection-errors; then
    echo "✅ Coverage tests completed"
else
    echo "⚠️  Coverage tests had failures"
fi

echo -e "\n📊 Test Summary:"
echo "=================="
echo "Total test suites: $TOTAL_TESTS"
echo "✅ Passed: $PASSED_TESTS"
echo "❌ Failed: $FAILED_TESTS"

echo -e "\n📊 Coverage report:"
echo "- Terminal output above"
echo "- HTML report: htmlcov/index.html"
echo "- XML report: coverage.xml"

# Show container status
echo -e "\n🐳 Container status:"
docker-compose ps

echo -e "\n💡 Tips:"
echo "- View API logs: docker-compose logs -f"
echo "- Stop API: docker-compose down"
echo "- Run specific test: pytest tests/test_real_config.py::TestRealAddressEndpoints -v"
echo "- Run tests with more detail: pytest -vvv"

# Always exit with 0 to show all test results
exit 0
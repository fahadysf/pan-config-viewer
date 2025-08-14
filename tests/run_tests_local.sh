#!/bin/bash

echo "🚀 Running tests locally (without Docker)"
echo "========================================"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Run tests with test config
echo -e "\n📋 Testing with sample configuration..."
pytest tests/test_api.py -v

# Run tests with real config
echo -e "\n📊 Testing with real configuration..."
pytest tests/test_real_config.py -v

# Run all tests with coverage
echo -e "\n📈 Running all tests with coverage..."
pytest --cov=main --cov=parser --cov=models \
       --cov-report=term-missing \
       --cov-report=html

echo -e "\n✅ Test run complete!"
echo "Coverage report available in htmlcov/index.html"
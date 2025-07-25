#!/bin/bash

set -e  # Exit on error

echo "🚀 PAN-OS Configuration API Test Runner (Simple)"
echo "==============================================="

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -q -r requirements.txt

echo -e "\n🔍 Running basic smoke test with Docker API..."
python tests/test_basic.py

echo -e "\n📋 Running tests without Docker (local API)..."

# Test with sample config
echo -e "\n1️⃣ Testing with sample configuration..."
export CONFIG_FILES_PATH="$(pwd)/tests/test_configs"
python -m pytest tests/test_api.py -v --tb=short -x

# Test with real config  
echo -e "\n2️⃣ Testing with real configuration..."
export CONFIG_FILES_PATH="$(pwd)/config-files"
python -m pytest tests/test_real_config.py -v --tb=short -x

echo -e "\n✅ Test run complete!"
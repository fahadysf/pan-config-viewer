# Test Architecture Documentation

## Overview

The PAN-OS Configuration API has multiple test approaches to validate functionality:

1. **Simple Validation Tests** - HTTP-based tests that work with running Docker container
2. **Basic Smoke Tests** - Comprehensive functionality tests via HTTP
3. **Unit Tests with pytest** - Detailed tests with specific test data (currently have environment issues)

## Current Test Status

### ✅ Working Tests

#### 1. Simple Validation (`test_simple_validation.py`)
- **Purpose**: Quick validation of core API functionality
- **Method**: Makes HTTP requests to running Docker container
- **Coverage**: Health check, config listing, addresses, device groups, field format
- **Usage**: `make test-validate` or `python tests/test_simple_validation.py`
- **Status**: ✅ All tests pass

#### 2. Basic Smoke Tests (`test_basic.py`)
- **Purpose**: Comprehensive smoke testing with error handling
- **Method**: HTTP requests with graceful error handling
- **Coverage**: All major endpoints with filtering and search
- **Usage**: `make test-basic` or `python tests/test_basic.py`
- **Status**: ✅ All tests pass

### ⚠️ Tests with Known Issues

#### 1. pytest Unit Tests (`test_api.py`)
- **Purpose**: Test with sample XML data (`test_panorama.xml`)
- **Issue**: Tests expect to find `test_panorama` config but Docker container only has real config
- **Root Cause**: Environment variable mismatch between pytest and Docker container

#### 2. pytest Integration Tests (`test_real_config.py`)
- **Purpose**: Test with real Panorama configuration
- **Issue**: Similar environment mismatch causing tests to fail
- **Root Cause**: Tests create their own app instance that doesn't match Docker environment

## Test Execution Methods

### 1. Docker-based Testing (Recommended)
```bash
# Start Docker container and run validation
docker-compose up -d
make test-validate
make test-basic
```

### 2. Full Test Suite
```bash
# Runs all tests including failing pytest tests
./run_tests_full.sh
```

### 3. Standard Test Runner
```bash
# Starts Docker, runs tests, then stops
./run_tests.sh
```

## Architecture Limitations

1. **Environment Isolation**: pytest tests create their own FastAPI app instance which doesn't share the same environment as the Docker container.

2. **Config Path Mismatch**: 
   - Docker container uses `/config-files` (mapped to `./config-files`)
   - pytest tests try to use `tests/test_configs` or `config-files` locally

3. **App Instance Conflict**: The FastAPI app is initialized on import, making it difficult to change configuration paths dynamically for different test scenarios.

## Recommendations

For reliable testing, use the HTTP-based tests:

1. **Quick Validation**: Use `test_simple_validation.py` for rapid smoke testing
2. **Comprehensive Testing**: Use `test_basic.py` for thorough endpoint testing
3. **Manual Testing**: Use Swagger UI at http://localhost:8000/docs

## Future Improvements

To fix the pytest tests, consider:

1. **Test Containers**: Use testcontainers-python to spin up isolated Docker containers for each test suite
2. **Environment Fixtures**: Create pytest fixtures that properly initialize the app with correct paths
3. **Mock Testing**: Mock the XML parser instead of relying on file system paths
4. **Separate Test Configs**: Run separate Docker containers for test and real configurations
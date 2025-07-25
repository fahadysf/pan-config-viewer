# Testing Guide for PAN-OS Panorama Configuration API

This guide explains how to run tests for the PAN-OS Configuration API.

## Prerequisites

1. Docker and Docker Compose installed
2. Python 3.8+ installed locally (for running tests)
3. The repository cloned to your local machine

## Test Structure

```
tests/
├── __init__.py
├── test_api.py              # Tests using sample XML configuration
├── test_real_config.py      # Tests using the actual pan-bkp-202507151414.xml
├── test_basic.py            # Basic smoke tests
└── test_configs/
    └── test_panorama.xml    # Sample test configuration
```

## Running Tests

### Method 1: Using Docker Compose (Recommended)

The easiest way to run tests is using the provided test script:

```bash
# Make the script executable
chmod +x run_tests.sh

# Run all tests (this will start the API, run tests, then stop)
./run_tests.sh

# For graceful test execution that continues even if some tests fail:
chmod +x run_tests_graceful.sh
./run_tests_graceful.sh
```

The graceful test runner will:
- Continue running all test suites even if some fail
- Provide a summary of passed/failed tests
- Always generate coverage reports
- Show detailed error messages for debugging

### Method 2: Manual Testing

#### Step 1: Start the API

```bash
# Using Docker Compose
docker-compose up -d

# Or run locally
export CONFIG_FILES_PATH="/Users/fahad/code/pan-config-viewer-simple/config-files"
python main.py
```

#### Step 2: Verify API is running

```bash
# Check health endpoint
curl http://localhost:8000/api/v1/health

# Or use the basic test
python tests/test_basic.py
```

#### Step 3: Run the tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest -v

# Run specific test file
pytest tests/test_real_config.py -v

# Run with coverage
pytest --cov=. --cov-report=html
```

### Method 3: Using pytest-docker

For automated testing with Docker:

```bash
# Install pytest-docker
pip install pytest-docker

# Run tests (will automatically start/stop containers)
pytest --docker-compose=docker-compose.yml -v
```

## Test Categories

### 1. Unit Tests with Sample Data (`test_api.py`)

Tests using a controlled sample XML file:
- Basic CRUD operations
- Filtering and search
- Error handling
- Edge cases

```bash
# Run only sample data tests
export CONFIG_FILES_PATH="tests/test_configs"
pytest tests/test_api.py -v
```

### 2. Integration Tests with Real Data (`test_real_config.py`)

Tests using your actual Panorama configuration:
- Validates real object names and values
- Checks actual counts and relationships
- Verifies XPath calculations
- Tests location tracking

```bash
# Run only real config tests
export CONFIG_FILES_PATH="config-files"
pytest tests/test_real_config.py -v
```

### 3. Smoke Tests (`test_basic.py`)

Quick validation that the API is working:
- Health check
- Basic endpoint functionality
- No complex assertions

```bash
# Run smoke tests (API must be running)
python tests/test_basic.py
```

## Testing Specific Endpoints

### Test a single endpoint class:
```bash
pytest tests/test_real_config.py::TestRealAddressEndpoints -v
```

### Test a single test method:
```bash
pytest tests/test_real_config.py::TestRealAddressEndpoints::test_get_all_addresses -v
```

## Debugging Failed Tests

### 1. Check API is running
```bash
docker ps  # Should show pan-config-viewer container
curl http://localhost:8000/api/v1/health
```

### 2. Check configuration files exist
```bash
ls -la config-files/
# Should show pan-bkp-202507151414.xml
```

### 3. Run tests with verbose output
```bash
pytest -vv --tb=short
```

### 4. Check test logs
```bash
pytest --log-cli-level=DEBUG
```

## Coverage Reports

Generate and view test coverage:

```bash
# Generate coverage report
pytest --cov=. --cov-report=html --cov-report=term-missing

# View coverage report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

## Environment Variables

The tests use these environment variables:

- `CONFIG_FILES_PATH`: Path to XML configuration files
  - Default for API: `/config-files`
  - For testing: `tests/test_configs` or `config-files`

## Common Issues

### 1. Import Errors
```bash
# Solution: Install all dependencies
pip install -r requirements.txt
```

### 2. Connection Refused
```bash
# Solution: Ensure API is running
docker-compose up -d
# Wait a few seconds for startup
sleep 5
```

### 3. Config File Not Found
```bash
# Solution: Ensure config files are in the right place
ls -la config-files/
# Should contain pan-bkp-202507151414.xml
```

### 4. Permission Errors
```bash
# Solution: Fix file permissions
chmod +r config-files/*.xml
```

## CI/CD Integration

The repository includes GitHub Actions workflow for automated testing:

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
```

## Writing New Tests

When adding new features, create corresponding tests:

1. Add test methods to appropriate test class
2. Use descriptive test names: `test_<feature>_<expected_behavior>`
3. Include docstrings explaining what is being tested
4. Assert both successful cases and error conditions

Example:
```python
def test_get_addresses_filters_by_tag(self):
    """Test that address filtering by tag returns only tagged addresses"""
    response = client.get(f"/api/v1/configs/{CONFIG_NAME}/addresses?tag=ipv6")
    assert response.status_code == 200
    addresses = response.json()
    assert all("ipv6" in addr["tag"] for addr in addresses if addr["tag"])
```

## Performance Testing

For load testing the API:

```bash
# Install locust
pip install locust

# Create locustfile.py
# Run load tests
locust -f locustfile.py --host=http://localhost:8000
```

## Security Testing

Basic security checks:

```bash
# Check for exposed secrets
grep -r "password\|secret\|key" . --exclude-dir=.git

# Check dependencies for vulnerabilities
pip install safety
safety check
```
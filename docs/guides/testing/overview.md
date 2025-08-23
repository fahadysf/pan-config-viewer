# Testing Guide

This application includes comprehensive tests for all API endpoints. The tests are designed to work with the Dockerized API.

## Prerequisites

1. Build and run the Docker container:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

2. Wait for the container to be ready:
   ```bash
   # Check container health
   docker ps | grep pan-config
   ```

## Test Structure

```
tests/
├── __init__.py
├── test_api.py                 # Pytest tests (has environment issues)
├── test_basic.py               # Basic smoke tests with HTTP requests
├── test_simple_validation.py   # Simple validation tests
├── test_docker_api.py          # Docker-specific API tests
├── test_all_endpoints.py       # Comprehensive endpoint testing
└── test_configs/
    └── test_panorama.xml       # Sample test configuration
```

## Running Tests

### Quick Test
Run a basic smoke test to verify the API is working:
```bash
python tests/test_basic.py
```

### Full Test Suite
Run the comprehensive test suite that covers all endpoints:
```bash
python tests/test_all_endpoints.py
```

### Docker API Test
Run tests specifically designed for the Docker environment:
```bash
python tests/test_docker_api.py
```

### Simple Validation
Run a simple validation script:
```bash
python tests/test_simple_validation.py
```

## Test Results

The comprehensive test suite (`test_all_endpoints.py`) tests the following endpoints:

### ✅ Working Endpoints (38 tests passing)
- **Health & Configuration**: Health check, list configs, config info
- **Addresses**: Get all, get specific, filter by name/location
- **Address Groups**: Get all, get specific
- **Services**: Get all, get specific, filter by protocol
- **Service Groups**: Get all
- **Security Profiles**: Vulnerability profiles, URL filtering profiles
- **Device Groups**: Summary, specific, filter by parent, child objects (addresses, services, rules)
- **Templates**: Get all, get specific
- **Template Stacks**: Get all, get specific
- **Log Profiles**: Get all
- **Schedules**: Get all, get specific
- **Search**: By XPath
- **Location Tracking**: XPath and parent context verification
- **Error Handling**: 404 responses for non-existent resources

### ❌ Not Implemented (11 endpoints)
These endpoints return 404 as they are not yet implemented:
- Get specific service group by name
- Get specific vulnerability/URL filtering profile by name
- Antivirus, Anti-Spyware, Wildfire, File Blocking, Data Filtering, DoS Protection profiles
- Device group NAT rules endpoint
- Get specific log profile by name

## Debugging Test Failures

If tests fail, check:

1. **Container is running**: `docker ps | grep pan-config`
2. **API is accessible**: `curl http://localhost:8000/api/v1/health`
3. **Configuration files exist**: Check that XML files are present in the config directory
4. **Logs**: `docker-compose logs pan-config-api`

## Test Architecture

The tests use HTTP requests to test the actual running API, ensuring real-world behavior. This approach:
- Tests the complete request/response cycle
- Verifies Docker container functionality
- Ensures API contract compliance
- Works consistently across environments

## Adding New Tests

To add tests for new endpoints:
1. Add test methods to `tests/test_all_endpoints.py`
2. Follow the existing pattern of making HTTP requests
3. Verify response status codes and data structure
4. Run the full test suite to ensure no regressions

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

## Quick Validation

For a quick validation that the API is working correctly:

```bash
# With Docker running
python tests/test_simple_validation.py
```

This will test:
- Health check endpoint
- Configuration listing
- Address retrieval
- Field format validation
- Device group functionality

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

### 5. Test Config Path Issues
The tests expect specific paths for configuration files:
- Test configs: `tests/test_configs/test_panorama.xml`
- Real config: `config-files/pan-bkp-202507151414.xml`

When running with Docker, the API uses `/config-files` inside the container, which is mapped to `./config-files` on the host.

### 6. Field Naming Convention
The API returns field names in kebab-case format:
- `parent-device-group` (not `parent_device_group`)
- `parent-template` (not `parent_template`)
- `parent-vsys` (not `parent_vsys`)
- `ip-netmask` (not `ip_netmask`)

Tests have been updated to expect this format.

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
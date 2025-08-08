# Pagination Testing Quick Reference

## Quick Start

### 1. Ensure the API server is running
```bash
python main.py
```

### 2. Run all pagination tests
```bash
# Automated test runner (runs both Python and Jest tests)
python tests/run_pagination_tests.py

# Or run individually:
# Python tests
python -m pytest tests/test_pagination.py -v

# Jest tests
npm test:pagination
```

### 3. Run manual/interactive tests
```bash
# Run default manual tests
python tests/test_pagination_manual.py

# Test specific endpoint
python tests/test_pagination_manual.py /configs/test_panorama/addresses

# Test with parameters
python tests/test_pagination_manual.py /configs/test_panorama/addresses page=2 page_size=10
```

## Test Files

1. **test_pagination.py** - Comprehensive Python unit tests
   - Basic pagination functionality
   - Edge cases and validation
   - All endpoints coverage
   - Large dataset handling
   - Backwards compatibility

2. **pagination.test.js** - Jest integration tests
   - End-to-end API testing
   - Snapshot testing
   - Performance measurements
   - Cross-endpoint validation

3. **test_pagination_manual.py** - Interactive testing tool
   - Manual verification of pagination
   - Edge case exploration
   - Comparison of pagination methods

4. **run_pagination_tests.py** - Automated test runner
   - Runs all tests in sequence
   - Generates summary report
   - Checks prerequisites

## Common Test Commands

```bash
# Run specific test class
python -m pytest tests/test_pagination.py::TestPaginationBasics -v

# Run with coverage
python -m pytest tests/test_pagination.py --cov=main --cov-report=html

# Run Jest tests with coverage
npm run test:coverage tests/pagination.test.js

# Update Jest snapshots
npm run test:snapshot-update tests/pagination.test.js

# Run tests in watch mode
npm run test:watch tests/pagination.test.js
```

## Testing Different Scenarios

### Test with large dataset
```bash
curl 'http://localhost:8000/api/v1/configs/16-7-Panorama-Core-688/device-groups/KIZAD-DC-Vsys1/pre-security-rules?page_size=100'
```

### Test pagination disabled
```bash
curl 'http://localhost:8000/api/v1/configs/test_panorama/addresses?disable_paging=true'
```

### Test with filters
```bash
curl 'http://localhost:8000/api/v1/configs/test_panorama/addresses?name=host&page=1&page_size=5'
```

### Test edge cases
```bash
# Page out of bounds
curl 'http://localhost:8000/api/v1/configs/test_panorama/addresses?page=9999'

# Invalid parameters (should return 422)
curl 'http://localhost:8000/api/v1/configs/test_panorama/addresses?page=-1'
curl 'http://localhost:8000/api/v1/configs/test_panorama/addresses?page_size=0'
curl 'http://localhost:8000/api/v1/configs/test_panorama/addresses?page_size=10001'
```

## Expected Test Results

All tests should pass with:
- ✅ 200+ Python tests passing
- ✅ 50+ Jest tests passing  
- ✅ No pagination data loss or duplication
- ✅ Proper validation of all parameters
- ✅ Consistent behavior across endpoints

## Troubleshooting

1. **API server not running**
   - Start with: `python main.py`
   - Check it's accessible: `curl http://localhost:8000/api/v1/configs`

2. **Missing test config files**
   - Ensure `test_panorama` config exists
   - Ensure `16-7-Panorama-Core-688` config exists for large dataset tests

3. **Jest tests failing**
   - Install dependencies: `npm install`
   - Update snapshots if needed: `npm run test:snapshot-update`

4. **Python tests failing**
   - Install pytest: `pip install pytest pytest-cov`
   - Check Python version (3.7+ required)
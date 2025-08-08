# PAN-OS Configuration Viewer Jest Tests

This directory contains comprehensive Jest tests for the PAN-OS Configuration Viewer's table filtering and pagination functionality.

## Test Files

### Core Test Suites

1. **viewer.test.js** - Main test suite covering:
   - Filter parameter building
   - Active filters display
   - DataTables integration
   - Filter operators
   - Column field mapping
   - Error handling
   - UI state management
   - Complex filter scenarios

2. **viewer-snapshots.test.js** - Snapshot tests for UI components:
   - Filter display components
   - Table cell rendering
   - Filter dropdown components
   - Loading states
   - Various badges and UI elements

3. **viewer-edge-cases.test.js** - Advanced scenarios and edge cases:
   - Extreme filter values
   - Concurrent operations
   - Numeric filter edge cases
   - Complex filter combinations
   - Memory leak prevention
   - Race condition handling
   - Browser compatibility
   - Accessibility

## Running the Tests

### Prerequisites

```bash
# Install Jest and dependencies
npm install --save-dev jest @babel/core @babel/preset-env babel-jest
npm install --save-dev jquery datatables.net
npm install --save-dev jest-environment-jsdom
npm install --save-dev jest-serializer-html
```

### Run All Viewer Tests

```bash
# Run with custom config
jest --config tests/jest.config.viewer.js

# Run with coverage
jest --config tests/jest.config.viewer.js --coverage

# Run in watch mode
jest --config tests/jest.config.viewer.js --watch
```

### Run Specific Test Files

```bash
# Run only the main test suite
jest tests/viewer.test.js

# Run only snapshot tests
jest tests/viewer-snapshots.test.js

# Run only edge case tests
jest tests/viewer-edge-cases.test.js
```

### Update Snapshots

```bash
jest tests/viewer-snapshots.test.js -u
```

## Test Coverage

The tests aim for >80% coverage of:
- Filter parameter building logic
- UI state management
- DataTables integration
- Error handling
- Edge cases and boundary conditions

## Key Testing Areas

### 1. Filter Parameter Building
- Tests all supported operators (eq, ne, contains, starts_with, etc.)
- Handles empty/null values correctly
- Supports special characters and Unicode
- Validates parameter format for API

### 2. UI Component Testing
- Filter display rendering
- Active filter management
- Clear/remove filter functionality
- Loading states and transitions

### 3. DataTables Integration
- Server-side processing parameters
- Pagination with filters
- Ajax request/response handling
- Table refresh on filter changes

### 4. Edge Cases
- Very long filter values (1000+ chars)
- Special characters and Unicode
- Rapid filter changes
- Concurrent operations
- Memory leak prevention

## Mocking Strategy

The tests use comprehensive mocking for:
- jQuery and DataTables
- Fetch API for server requests
- DOM elements and events
- Alpine.js components

## Adding New Tests

When adding new functionality:

1. Add unit tests to `viewer.test.js` for core logic
2. Add snapshot tests to `viewer-snapshots.test.js` for UI components
3. Add edge case tests to `viewer-edge-cases.test.js` for boundary conditions

Example test structure:
```javascript
describe('New Feature', () => {
    test('should handle basic case', () => {
        // Arrange
        const input = { /* test data */ };
        
        // Act
        const result = configViewer.newMethod(input);
        
        // Assert
        expect(result).toEqual(/* expected output */);
    });
});
```

## Debugging Tests

### Enable verbose output
```bash
jest --config tests/jest.config.viewer.js --verbose
```

### Debug specific test
```bash
node --inspect-brk node_modules/.bin/jest --runInBand tests/viewer.test.js
```

### Check test coverage gaps
```bash
jest --config tests/jest.config.viewer.js --coverage --coverageReporters=html
# Open coverage/index.html in browser
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Use descriptive test names
3. **Coverage**: Test both success and failure paths
4. **Maintainability**: Keep tests simple and focused
5. **Performance**: Mock external dependencies

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Viewer Tests
  run: |
    npm install
    npm test -- --config tests/jest.config.viewer.js --ci --coverage
```

## Troubleshooting

### Common Issues

1. **Module not found errors**
   - Ensure all dependencies are installed
   - Check module paths in jest.config.viewer.js

2. **Snapshot mismatches**
   - Review changes carefully before updating
   - Use `jest -u` to update snapshots

3. **Timeout errors**
   - Increase timeout for async tests
   - Check for unresolved promises

4. **DataTables initialization errors**
   - Ensure jQuery is loaded before DataTables
   - Check mock implementations

For questions or issues, please refer to the main project documentation or create an issue in the repository.
/**
 * Jest setup file for frontend tests
 * Configure test environment for browser/DOM testing
 */

// Add TextEncoder/TextDecoder polyfills for jsdom
const { TextEncoder, TextDecoder } = require('util');
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Increase timeout for tests
jest.setTimeout(30000);

// Add custom matchers if needed
expect.extend({
  toBeValidPaginatedResponse(received) {
    const pass = received && 
                 Array.isArray(received.items) &&
                 typeof received.total_items === 'number' &&
                 typeof received.page === 'number' &&
                 typeof received.page_size === 'number' &&
                 typeof received.total_pages === 'number' &&
                 typeof received.has_next === 'boolean' &&
                 typeof received.has_previous === 'boolean';
    
    if (pass) {
      return {
        message: () => `expected ${received} not to be a valid paginated response`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected ${received} to be a valid paginated response with items, total_items, page, page_size, total_pages, has_next, and has_previous`,
        pass: false,
      };
    }
  },
});

// Global test helpers for frontend tests
global.testHelpers = {
  API_BASE_URL: 'http://localhost:8000/api/v1',
  CONFIG_NAME: '16-7-Panorama-Core-688',
  
  // Mock DataTables initialization
  initDataTable(selector, config) {
    const table = {
      ajax: {
        reload: jest.fn()
      },
      draw: jest.fn(),
      page: {
        len: jest.fn()
      },
      search: jest.fn(),
      column: jest.fn().mockReturnValue({
        search: jest.fn()
      }),
      destroy: jest.fn(),
      clear: jest.fn(),
      rows: {
        add: jest.fn().mockReturnValue({
          draw: jest.fn()
        })
      }
    };
    
    return table;
  }
};

// Skip API health check for frontend tests
console.log('Frontend test environment configured');
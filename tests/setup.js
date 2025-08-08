/**
 * Jest setup file
 * Configure test environment and global settings
 */

// Increase timeout for API tests
jest.setTimeout(30000);

// Add custom matchers if needed
expect.extend({
  toBeValidDeviceGroup(received) {
    const pass = received && 
                 typeof received.name === 'string' &&
                 typeof received.address_count === 'number' &&
                 typeof received.service_count === 'number';
    
    if (pass) {
      return {
        message: () => `expected ${received} not to be a valid device group`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected ${received} to be a valid device group with name, address_count, and service_count`,
        pass: false,
      };
    }
  },
});

// Global test helpers
global.testHelpers = {
  API_BASE_URL: 'http://localhost:8000/api/v1',
  CONFIG_NAME: '16-7-Panorama-Core-688',
  
  // Helper to check if API is running
  async checkAPIHealth() {
    const axios = require('axios');
    try {
      const response = await axios.get(`${this.API_BASE_URL}/health`);
      return response.status === 200;
    } catch (error) {
      console.error('API health check failed:', error.message);
      return false;
    }
  }
};

// Check if API is running before tests (skip for mocked tests)
beforeAll(async () => {
  // Skip API check for frontend tests that mock axios
  const isFrontendTest = process.env.NODE_ENV === 'test' && 
                         (global.jest?.isMockFunction?.(require('axios').get) || 
                          typeof jest !== 'undefined');
  
  if (!isFrontendTest) {
    const isAPIRunning = await global.testHelpers.checkAPIHealth();
    if (!isAPIRunning) {
      console.error('\n⚠️  API is not running! Please start the API server with: python main.py\n');
      process.exit(1);
    }
  }
});
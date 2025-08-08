/**
 * Comprehensive Jest test suite for API pagination
 * Tests pagination functionality across all endpoints
 */

const axios = require('axios');

// Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';
const LARGE_CONFIG = '16-7-Panorama-Core-688';
const TEST_CONFIG = 'test_panorama';

// Axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  validateStatus: () => true // Don't throw on any status code
});

// Helper function to get endpoint URL
const getUrl = (path) => `/configs/${LARGE_CONFIG}${path}`;
const getTestUrl = (path) => `/configs/${TEST_CONFIG}${path}`;

describe('Pagination Basic Functionality', () => {
  test('should return paginated response with default parameters', async () => {
    const response = await api.get(getUrl('/addresses'));
    expect(response.status).toBe(200);
    
    const data = response.data;
    expect(data).toHaveProperty('items');
    expect(data).toHaveProperty('total_items');
    expect(data).toHaveProperty('page');
    expect(data).toHaveProperty('page_size');
    expect(data).toHaveProperty('total_pages');
    expect(data).toHaveProperty('has_next');
    expect(data).toHaveProperty('has_previous');
    
    // Check defaults
    expect(data.page).toBe(1);
    expect(data.page_size).toBe(500);
    expect(data.has_previous).toBe(false);
    expect(data.items.length).toBeLessThanOrEqual(500);
  });
  
  test('should respect custom page_size parameter', async () => {
    const pageSize = 25;
    const response = await api.get(getUrl('/addresses'), {
      params: { page_size: pageSize }
    });
    
    expect(response.status).toBe(200);
    expect(response.data.page_size).toBe(pageSize);
    expect(response.data.items.length).toBeLessThanOrEqual(pageSize);
  });
  
  test('should navigate through pages correctly', async () => {
    const pageSize = 10;
    
    // Get first page
    const page1 = await api.get(getUrl('/addresses'), {
      params: { page: 1, page_size: pageSize }
    });
    
    // Get second page
    const page2 = await api.get(getUrl('/addresses'), {
      params: { page: 2, page_size: pageSize }
    });
    
    expect(page1.status).toBe(200);
    expect(page2.status).toBe(200);
    
    // If there are enough items for 2 pages
    if (page1.data.total_items > pageSize) {
      expect(page1.data.has_next).toBe(true);
      expect(page2.data.has_previous).toBe(true);
      
      // Items should be different
      const page1Names = page1.data.items.map(item => item.name);
      const page2Names = page2.data.items.map(item => item.name);
      expect(page1Names).not.toEqual(page2Names);
    }
  });
  
  test('should disable pagination when disable_paging=true', async () => {
    const response = await api.get(getTestUrl('/addresses'), {
      params: { disable_paging: true }
    });
    
    expect(response.status).toBe(200);
    const data = response.data;
    
    expect(data.items.length).toBe(data.total_items);
    expect(data.page).toBe(1);
    expect(data.page_size).toBe(data.total_items);
    expect(data.total_pages).toBe(1);
    expect(data.has_next).toBe(false);
    expect(data.has_previous).toBe(false);
  });
});

describe('Pagination Edge Cases', () => {
  test('should handle page out of bounds gracefully', async () => {
    const response = await api.get(getTestUrl('/addresses'), {
      params: { page: 9999 }
    });
    
    expect(response.status).toBe(200);
    expect(response.data.items).toEqual([]);
    expect(response.data.page).toBe(9999);
  });
  
  test('should reject negative page numbers', async () => {
    const response = await api.get(getTestUrl('/addresses'), {
      params: { page: -1 }
    });
    
    expect(response.status).toBe(422);
  });
  
  test('should reject zero page number', async () => {
    const response = await api.get(getTestUrl('/addresses'), {
      params: { page: 0 }
    });
    
    expect(response.status).toBe(422);
  });
  
  test('should reject negative page_size', async () => {
    const response = await api.get(getTestUrl('/addresses'), {
      params: { page_size: -10 }
    });
    
    expect(response.status).toBe(422);
  });
  
  test('should reject zero page_size', async () => {
    const response = await api.get(getTestUrl('/addresses'), {
      params: { page_size: 0 }
    });
    
    expect(response.status).toBe(422);
  });
  
  test('should reject page_size over 10000', async () => {
    const response = await api.get(getTestUrl('/addresses'), {
      params: { page_size: 10001 }
    });
    
    expect(response.status).toBe(422);
  });
  
  test('should handle empty results with proper pagination metadata', async () => {
    const response = await api.get(getTestUrl('/addresses'), {
      params: { name: 'nonexistent_address_xyz_12345' }
    });
    
    expect(response.status).toBe(200);
    const data = response.data;
    
    expect(data.items).toEqual([]);
    expect(data.total_items).toBe(0);
    expect(data.total_pages).toBe(0);
    expect(data.has_next).toBe(false);
    expect(data.has_previous).toBe(false);
  });
});

describe('Pagination Across All Endpoints', () => {
  const endpoints = [
    // Address endpoints
    '/addresses',
    '/address-groups',
    '/shared/addresses',
    '/shared/address-groups',
    
    // Service endpoints
    '/services',
    '/service-groups',
    '/shared/services',
    '/shared/service-groups',
    
    // Security profiles
    '/antivirus-profiles',
    '/anti-spyware-profiles',
    '/vulnerability-profiles',
    '/url-filtering-profiles',
    '/file-blocking-profiles',
    '/wildfire-analysis-profiles',
    '/data-filtering-profiles',
    '/security-profile-groups',
    
    // Device management
    '/device-groups',
    '/templates',
    '/template-stacks',
    
    // Other endpoints
    '/log-settings',
    '/schedules',
    '/zone-protection-profiles'
  ];
  
  test.each(endpoints)('should support pagination on %s endpoint', async (endpoint) => {
    const response = await api.get(getUrl(endpoint), {
      params: { page: 1, page_size: 10 }
    });
    
    expect(response.status).toBe(200);
    const data = response.data;
    
    // Verify pagination structure
    expect(data).toHaveProperty('items');
    expect(data).toHaveProperty('total_items');
    expect(data).toHaveProperty('page', 1);
    expect(data).toHaveProperty('page_size', 10);
    expect(data).toHaveProperty('total_pages');
    expect(data).toHaveProperty('has_next');
    expect(data).toHaveProperty('has_previous');
    expect(data.items.length).toBeLessThanOrEqual(10);
  });
  
  test.each(endpoints)('should support disable_paging on %s endpoint', async (endpoint) => {
    const response = await api.get(getUrl(endpoint), {
      params: { disable_paging: true }
    });
    
    expect(response.status).toBe(200);
    const data = response.data;
    
    expect(data.page).toBe(1);
    expect(data.total_pages).toBe(1);
    expect(data.has_next).toBe(false);
    expect(data.has_previous).toBe(false);
    expect(data.items.length).toBe(data.total_items);
  });
});

describe('Device Group Specific Pagination', () => {
  const deviceGroups = [
    { name: 'KIZAD-DC-Vsys1', addresses: 684, services: 97, preRules: 19221 },
    { name: 'TCN-DC-Vsys1', addresses: 508, services: 95, preRules: 13791 }
  ];
  
  test.each(deviceGroups)('should paginate addresses in device group $name', async (dg) => {
    const response = await api.get(getUrl(`/device-groups/${dg.name}/addresses`), {
      params: { page_size: 50 }
    });
    
    expect(response.status).toBe(200);
    const data = response.data;
    
    expect(data.page_size).toBe(50);
    expect(data.items.length).toBeLessThanOrEqual(50);
    expect(data.total_items).toBeGreaterThan(dg.addresses * 0.9); // Allow some variance
  });
  
  test.each(deviceGroups)('should paginate services in device group $name', async (dg) => {
    const response = await api.get(getUrl(`/device-groups/${dg.name}/services`), {
      params: { page_size: 20 }
    });
    
    expect(response.status).toBe(200);
    const data = response.data;
    
    expect(data.page_size).toBe(20);
    expect(data.items.length).toBeLessThanOrEqual(20);
  });
  
  test('should paginate security rules with large datasets', async () => {
    const response = await api.get(getUrl('/device-groups/KIZAD-DC-Vsys1/pre-security-rules'), {
      params: { page_size: 100 }
    });
    
    expect(response.status).toBe(200);
    const data = response.data;
    
    expect(data.page_size).toBe(100);
    expect(data.total_items).toBeGreaterThan(19000); // Expected ~19221
    expect(data.total_pages).toBeGreaterThan(190);
  });
});

describe('Pagination with Filters', () => {
  test('should paginate filtered results by name', async () => {
    // Get total without filter
    const allResponse = await api.get(getUrl('/addresses'), {
      params: { page_size: 1 }
    });
    const totalAddresses = allResponse.data.total_items;
    
    // Get filtered results
    const filteredResponse = await api.get(getUrl('/addresses'), {
      params: { name: 'host', page_size: 10 }
    });
    
    expect(filteredResponse.status).toBe(200);
    const data = filteredResponse.data;
    
    expect(data.total_items).toBeLessThan(totalAddresses);
    expect(data.page_size).toBe(10);
    
    // Verify all items match filter
    data.items.forEach(item => {
      expect(item.name.toLowerCase()).toContain('host');
    });
  });
  
  test('should maintain filter consistency across pages', async () => {
    const filter = { name: 'tcp', page_size: 5 };
    
    // Get first page
    const page1 = await api.get(getUrl('/services'), {
      params: { ...filter, page: 1 }
    });
    
    // Get second page
    const page2 = await api.get(getUrl('/services'), {
      params: { ...filter, page: 2 }
    });
    
    expect(page1.status).toBe(200);
    expect(page2.status).toBe(200);
    
    // Total items should be consistent
    expect(page1.data.total_items).toBe(page2.data.total_items);
    expect(page1.data.total_pages).toBe(page2.data.total_pages);
    
    // All items should match filter
    [...page1.data.items, ...page2.data.items].forEach(item => {
      expect(item.name.toLowerCase()).toContain('tcp');
    });
  });
});

describe('Large Dataset Pagination Tests', () => {
  test('should handle pagination through entire large dataset', async () => {
    const endpoint = getUrl('/device-groups/KIZAD-DC-Vsys1/pre-security-rules');
    const pageSize = 500;
    const collectedItems = new Set();
    let currentPage = 1;
    let totalPages = null;
    
    // Paginate through all pages
    while (true) {
      const response = await api.get(endpoint, {
        params: { page: currentPage, page_size: pageSize }
      });
      
      expect(response.status).toBe(200);
      const data = response.data;
      
      if (totalPages === null) {
        totalPages = data.total_pages;
      }
      
      // Collect unique items
      data.items.forEach(item => {
        collectedItems.add(item.name);
      });
      
      // Check if we're on the last page
      if (!data.has_next) {
        break;
      }
      
      currentPage++;
      
      // Safety check
      if (currentPage > totalPages + 1) {
        throw new Error('Infinite pagination loop detected');
      }
    }
    
    // Verify we collected all items
    const finalResponse = await api.get(endpoint, {
      params: { page: currentPage, page_size: pageSize }
    });
    
    expect(collectedItems.size).toBe(finalResponse.data.total_items);
  }, 60000); // Increase timeout for large dataset test
  
  test('should perform consistently with different page sizes', async () => {
    const endpoint = getUrl('/addresses');
    const pageSizes = [10, 50, 100, 500, 1000];
    
    for (const pageSize of pageSizes) {
      const response = await api.get(endpoint, {
        params: { page_size: pageSize }
      });
      
      expect(response.status).toBe(200);
      const data = response.data;
      
      expect(data.page_size).toBe(pageSize);
      expect(data.items.length).toBeLessThanOrEqual(pageSize);
      
      // Verify total pages calculation
      const expectedPages = Math.ceil(data.total_items / pageSize);
      expect(data.total_pages).toBe(expectedPages);
    }
  });
});

describe('Backwards Compatibility', () => {
  test('should work without any pagination parameters', async () => {
    const response = await api.get(getTestUrl('/addresses'));
    
    expect(response.status).toBe(200);
    const data = response.data;
    
    // Should use default pagination
    expect(data).toHaveProperty('items');
    expect(data.page).toBe(1);
    expect(data.page_size).toBe(500);
  });
  
  test('should work with legacy filter parameters and new pagination', async () => {
    const response = await api.get(getTestUrl('/addresses'), {
      params: {
        name: 'test',
        page: 2,
        page_size: 10
      }
    });
    
    expect(response.status).toBe(200);
    const data = response.data;
    
    expect(data.page).toBe(2);
    expect(data.page_size).toBe(10);
    
    // Name filter should still work
    data.items.forEach(item => {
      expect(item.name.toLowerCase()).toContain('test');
    });
  });
});

describe('Pagination Snapshot Tests', () => {
  test('should match pagination response structure snapshot', async () => {
    const response = await api.get(getTestUrl('/addresses'), {
      params: { page: 1, page_size: 5 }
    });
    
    expect(response.status).toBe(200);
    
    // Create a sanitized version for snapshot
    const snapshot = {
      structure: {
        hasItems: Array.isArray(response.data.items),
        itemCount: response.data.items.length,
        hasTotalItems: typeof response.data.total_items === 'number',
        hasPage: typeof response.data.page === 'number',
        hasPageSize: typeof response.data.page_size === 'number',
        hasTotalPages: typeof response.data.total_pages === 'number',
        hasNext: typeof response.data.has_next === 'boolean',
        hasPrevious: typeof response.data.has_previous === 'boolean'
      },
      metadata: {
        page: response.data.page,
        page_size: response.data.page_size,
        itemsInPage: response.data.items.length
      }
    };
    
    expect(snapshot).toMatchSnapshot();
  });
  
  test('should match error response snapshot for invalid pagination', async () => {
    const response = await api.get(getTestUrl('/addresses'), {
      params: { page: -1 }
    });
    
    expect(response.status).toBe(422);
    
    // Snapshot of error structure
    const errorSnapshot = {
      hasDetail: response.data.hasOwnProperty('detail'),
      isValidationError: response.status === 422
    };
    
    expect(errorSnapshot).toMatchSnapshot();
  });
});

// Performance test helper
const measurePaginationPerformance = async (endpoint, pageSize) => {
  const start = Date.now();
  const response = await api.get(endpoint, {
    params: { page_size: pageSize }
  });
  const duration = Date.now() - start;
  
  return {
    status: response.status,
    duration,
    itemCount: response.data.items?.length || 0,
    totalItems: response.data.total_items || 0
  };
};

describe('Pagination Performance Tests', () => {
  test('should handle different page sizes efficiently', async () => {
    const endpoint = getUrl('/addresses');
    const results = [];
    
    for (const pageSize of [10, 100, 500, 1000]) {
      const perf = await measurePaginationPerformance(endpoint, pageSize);
      results.push({ pageSize, ...perf });
    }
    
    // Log performance results
    console.table(results);
    
    // All requests should succeed
    results.forEach(result => {
      expect(result.status).toBe(200);
    });
  });
});

// Global error handler for unhandled promise rejections
process.on('unhandledRejection', (error) => {
  console.error('Unhandled promise rejection:', error);
});

module.exports = {
  api,
  getUrl,
  getTestUrl
};
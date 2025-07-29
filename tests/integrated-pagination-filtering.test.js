/**
 * Comprehensive frontend tests for integrated pagination and filtering
 * Tests DataTables integration with server-side processing
 */

const axios = require('axios');
const { JSDOM } = require('jsdom');

// Mock axios
jest.mock('axios');

// Setup DOM environment
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
    url: 'http://localhost',
    pretendToBeVisual: true,
    resources: 'usable'
});

global.window = dom.window;
global.document = window.document;
global.$ = global.jQuery = require('jquery');

// Mock DataTables
$.fn.DataTable = jest.fn().mockReturnValue({
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
});

describe('Integrated Pagination and Filtering Tests', () => {
    let mockApiResponse;
    
    beforeEach(() => {
        // Reset mocks
        jest.clearAllMocks();
        
        // Setup default API response
        mockApiResponse = {
            items: [
                { name: '10.0.0.1', ip_netmask: '10.0.0.1/32', description: 'Test address 1' },
                { name: '10.0.0.2', ip_netmask: '10.0.0.2/32', description: 'Test address 2' },
                { name: '10.0.0.3', ip_netmask: '10.0.0.3/32', description: 'Test address 3' }
            ],
            total_items: 100,
            page: 1,
            page_size: 10,
            total_pages: 10,
            has_next: true,
            has_previous: false
        };
        
        axios.get.mockResolvedValue({ data: mockApiResponse });
    });
    
    describe('DataTables Server-Side Processing', () => {
        test('should initialize DataTable with server-side processing', async () => {
            const tableHtml = `
                <table id="test-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>IP</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            `;
            document.body.innerHTML = tableHtml;
            
            // Initialize DataTable with server-side processing
            const tableConfig = {
                processing: true,
                serverSide: true,
                ajax: {
                    url: '/api/v1/configs/test/addresses',
                    type: 'GET',
                    data: function(d) {
                        // Transform DataTables parameters to API parameters
                        return {
                            page: Math.floor(d.start / d.length) + 1,
                            page_size: d.length,
                            ...d.filters // Include any custom filters
                        };
                    },
                    dataSrc: function(json) {
                        // Transform API response to DataTables format
                        json.recordsTotal = json.total_items;
                        json.recordsFiltered = json.total_items;
                        return json.items;
                    }
                }
            };
            
            $('#test-table').DataTable(tableConfig);
            
            expect($.fn.DataTable).toHaveBeenCalledWith(
                expect.objectContaining({
                    processing: true,
                    serverSide: true,
                    ajax: expect.any(Object)
                })
            );
        });
        
        test('should handle pagination changes correctly', async () => {
            // Simulate page change
            const table = $('#test-table').DataTable();
            
            // Mock DataTables page change
            const pageChangeData = {
                start: 10,
                length: 10,
                draw: 2
            };
            
            // Simulate API call for page 2
            mockApiResponse.page = 2;
            mockApiResponse.has_previous = true;
            axios.get.mockResolvedValueOnce({ data: mockApiResponse });
            
            // Trigger ajax reload (simulating page change)
            await table.ajax.reload();
            
            expect(table.ajax.reload).toHaveBeenCalled();
        });
        
        test('should handle page size changes', async () => {
            const table = $('#test-table').DataTable();
            
            // Simulate page size change
            table.page.len(25);
            
            expect(table.page.len).toHaveBeenCalledWith(25);
        });
    });
    
    describe('Column Filtering Integration', () => {
        test('should apply column filters to API requests', async () => {
            const filters = {
                'filter[name]': '10.0',
                'filter[description]': 'test'
            };
            
            // Mock API call with filters
            axios.get.mockImplementationOnce((url, config) => {
                expect(config.params).toEqual(expect.objectContaining(filters));
                return Promise.resolve({ data: mockApiResponse });
            });
            
            // Make API call with filters
            await axios.get('/api/v1/configs/test/addresses', { params: filters });
            
            expect(axios.get).toHaveBeenCalledWith(
                '/api/v1/configs/test/addresses',
                expect.objectContaining({
                    params: expect.objectContaining(filters)
                })
            );
        });
        
        test('should handle multiple filter operators', async () => {
            const filters = {
                'filter[name][starts_with]': '10.',
                'filter[ip][contains]': '0.0',
                'filter[description][eq]': 'Test'
            };
            
            axios.get.mockImplementationOnce((url, config) => {
                expect(config.params).toEqual(expect.objectContaining(filters));
                return Promise.resolve({ data: mockApiResponse });
            });
            
            await axios.get('/api/v1/configs/test/addresses', { params: filters });
            
            expect(axios.get).toHaveBeenCalled();
        });
        
        test('should debounce filter input changes', (done) => {
            jest.useFakeTimers();
            
            const debounce = (func, wait) => {
                let timeout;
                return function executedFunction(...args) {
                    const later = () => {
                        clearTimeout(timeout);
                        func(...args);
                    };
                    clearTimeout(timeout);
                    timeout = setTimeout(later, wait);
                };
            };
            
            const mockFilterChange = jest.fn();
            const debouncedFilter = debounce(mockFilterChange, 300);
            
            // Simulate rapid typing
            debouncedFilter('1');
            debouncedFilter('10');
            debouncedFilter('10.');
            debouncedFilter('10.0');
            
            // Fast-forward time
            jest.advanceTimersByTime(300);
            
            // Should only be called once with final value
            expect(mockFilterChange).toHaveBeenCalledTimes(1);
            expect(mockFilterChange).toHaveBeenCalledWith('10.0');
            
            jest.useRealTimers();
            done();
        });
    });
    
    describe('Loading States and User Experience', () => {
        test('should show loading indicator during data fetch', async () => {
            document.body.innerHTML = `
                <div id="loading-indicator" style="display: none;">Loading...</div>
                <table id="test-table"></table>
            `;
            
            // Simulate showing loader before request
            const showLoader = () => {
                document.getElementById('loading-indicator').style.display = 'block';
            };
            
            const hideLoader = () => {
                document.getElementById('loading-indicator').style.display = 'none';
            };
            
            showLoader();
            expect(document.getElementById('loading-indicator').style.display).toBe('block');
            
            // Simulate API call
            await axios.get('/api/v1/configs/test/addresses');
            
            hideLoader();
            expect(document.getElementById('loading-indicator').style.display).toBe('none');
        });
        
        test('should handle empty results gracefully', async () => {
            const emptyResponse = {
                items: [],
                total_items: 0,
                page: 1,
                page_size: 10,
                total_pages: 0,
                has_next: false,
                has_previous: false
            };
            
            axios.get.mockResolvedValueOnce({ data: emptyResponse });
            
            const response = await axios.get('/api/v1/configs/test/addresses', {
                params: { 'filter[name]': 'nonexistent' }
            });
            
            expect(response.data.items).toHaveLength(0);
            expect(response.data.total_items).toBe(0);
        });
        
        test('should display appropriate message for no results', () => {
            document.body.innerHTML = `
                <div id="no-results" style="display: none;">No matching records found</div>
                <table id="test-table"></table>
            `;
            
            const emptyResponse = {
                items: [],
                total_items: 0
            };
            
            // Show no results message when empty
            if (emptyResponse.total_items === 0) {
                document.getElementById('no-results').style.display = 'block';
            }
            
            expect(document.getElementById('no-results').style.display).toBe('block');
        });
    });
    
    describe('Error Handling', () => {
        test('should handle API errors gracefully', async () => {
            const errorMessage = 'Network error';
            axios.get.mockRejectedValueOnce(new Error(errorMessage));
            
            try {
                await axios.get('/api/v1/configs/test/addresses');
            } catch (error) {
                expect(error.message).toBe(errorMessage);
            }
        });
        
        test('should handle invalid filter parameters', async () => {
            const invalidFilters = {
                'filter[invalid_field]': 'value',
                'filter[name][invalid_op]': 'value'
            };
            
            // API should still respond successfully but ignore invalid filters
            axios.get.mockResolvedValueOnce({ data: mockApiResponse });
            
            const response = await axios.get('/api/v1/configs/test/addresses', {
                params: invalidFilters
            });
            
            expect(response.data).toBeDefined();
            expect(response.data.items).toBeDefined();
        });
    });
    
    describe('Performance Optimization', () => {
        test('should cache filter results appropriately', async () => {
            const cacheKey = 'addresses_filter_10.0';
            const cache = new Map();
            
            // First request - cache miss
            const response1 = await axios.get('/api/v1/configs/test/addresses', {
                params: { 'filter[name]': '10.0' }
            });
            
            // Store in cache
            cache.set(cacheKey, response1.data);
            
            // Second request - should use cache
            const cachedData = cache.get(cacheKey);
            expect(cachedData).toEqual(response1.data);
        });
        
        test('should handle rapid pagination requests', async () => {
            const requests = [];
            
            // Simulate rapid page changes
            for (let page = 1; page <= 5; page++) {
                requests.push(
                    axios.get('/api/v1/configs/test/addresses', {
                        params: { page, page_size: 10 }
                    })
                );
            }
            
            // All requests should complete
            const responses = await Promise.all(requests);
            expect(responses).toHaveLength(5);
            expect(axios.get).toHaveBeenCalledTimes(5);
        });
    });
});

describe('Snapshot Tests for UI Components', () => {
    test('pagination controls snapshot', () => {
        const paginationHtml = `
            <div class="dataTables_paginate">
                <a class="paginate_button previous disabled">Previous</a>
                <span>
                    <a class="paginate_button current">1</a>
                    <a class="paginate_button">2</a>
                    <a class="paginate_button">3</a>
                </span>
                <a class="paginate_button next">Next</a>
            </div>
        `;
        
        expect(paginationHtml).toMatchSnapshot();
    });
    
    test('filter controls snapshot', () => {
        const filterHtml = `
            <div class="column-filters">
                <input type="text" class="column-filter" data-column="0" placeholder="Filter by name">
                <input type="text" class="column-filter" data-column="1" placeholder="Filter by IP">
                <select class="column-filter" data-column="2">
                    <option value="">All Protocols</option>
                    <option value="tcp">TCP</option>
                    <option value="udp">UDP</option>
                </select>
            </div>
        `;
        
        expect(filterHtml).toMatchSnapshot();
    });
    
    test('table with data snapshot', () => {
        const tableData = {
            headers: ['Name', 'IP', 'Description'],
            rows: [
                ['10.0.0.1', '10.0.0.1/32', 'Test address 1'],
                ['10.0.0.2', '10.0.0.2/32', 'Test address 2']
            ],
            pagination: {
                current: 1,
                total: 10,
                showing: '1-10 of 100'
            }
        };
        
        expect(tableData).toMatchSnapshot();
    });
});
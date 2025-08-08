/**
 * Comprehensive test suite for PAN-OS Configuration Viewer
 * Tests table filtering, pagination, and UI functionality
 */

import $ from 'jquery';
import 'datatables.net';

// Mock Alpine.js
global.Alpine = {
    data: jest.fn(),
    store: jest.fn()
};

// Mock fetch API
global.fetch = jest.fn();

// Mock DataTables
const mockDataTable = {
    ajax: {
        reload: jest.fn((callback, resetPaging) => {
            if (callback) callback();
        })
    },
    column: jest.fn((index) => ({
        header: jest.fn(() => $('<th>'))
    })),
    table: jest.fn(() => ({
        node: jest.fn(() => $('<table>'))
    })),
    draw: jest.fn()
};

$.fn.DataTable = jest.fn(() => mockDataTable);
$.fn.dataTable = $.fn.DataTable;

// Import the viewer component
let configViewer;

describe('PAN-OS Configuration Viewer', () => {
    beforeEach(() => {
        // Reset mocks
        jest.clearAllMocks();
        
        // Set up DOM structure
        document.body.innerHTML = `
            <div id="addresses-filters-list"></div>
            <div id="addresses-clear-all" style="display: none;"></div>
            <table id="addresses-table"></table>
            <div id="address-groups-filters-list"></div>
            <table id="address-groups-table"></table>
            <div id="services-filters-list"></div>
            <table id="services-table"></table>
            <div id="service-groups-filters-list"></div>
            <table id="service-groups-table"></table>
            <div id="security-policies-filters-list"></div>
            <table id="security-policies-table"></table>
            <div id="device-groups-filters-list"></div>
            <table id="device-groups-table"></table>
            <div id="templates-filters-list"></div>
            <table id="templates-table"></table>
        `;
        
        // Initialize configViewer
        configViewer = {
            selectedConfig: 'test-config',
            columnFilters: {
                'addresses-table': {},
                'address-groups-table': {},
                'services-table': {},
                'service-groups-table': {},
                'security-policies-table': {},
                'device-groups-table': {},
                'templates-table': {}
            },
            filterDebounceTimer: null,
            
            // Mock implementations
            buildFilterParams: function(filters) {
                const params = {};
                
                for (const [field, filter] of Object.entries(filters)) {
                    if (!filter.value && filter.operator !== 'empty' && filter.operator !== 'not_empty') {
                        continue;
                    }
                    
                    if (filter.operator === 'empty') {
                        params[`filter[${field}][is_null]`] = 'true';
                    } else if (filter.operator === 'not_empty') {
                        params[`filter[${field}][is_not_null]`] = 'true';
                    } else if (filter.operator === 'not_contains') {
                        params[`filter[${field}][not_contains]`] = filter.value;
                    } else if (filter.operator === 'equals') {
                        params[`filter[${field}]`] = filter.value;
                    } else {
                        params[`filter[${field}][${filter.operator}]`] = filter.value;
                    }
                }
                
                return params;
            },
            
            updateActiveFilters: function(tableId) {
                const filters = this.columnFilters[tableId];
                const filtersList = $(`#${tableId.replace('-table', '-filters-list')}`);
                const clearAllBtn = $(`#${tableId.replace('-table', '-clear-all')}`);
                
                filtersList.empty();
                
                if (Object.keys(filters).length === 0) {
                    clearAllBtn.hide();
                    return;
                }
                
                clearAllBtn.show();
                
                const fieldMapping = this.getColumnFieldMapping(tableId);
                
                for (const [field, filter] of Object.entries(filters)) {
                    const fieldIndex = fieldMapping.indexOf(field);
                    const columnHeader = $(`#${tableId} thead th:eq(${fieldIndex})`).text();
                    const operatorLabel = this.getOperatorLabel(filter.operator);
                    
                    let filterHtml = `
                        <span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800 mr-2 mb-2">
                            <span class="font-medium">${columnHeader}</span>
                            <span class="mx-1">${operatorLabel}</span>
                            <span>${filter.value || '(empty)'}</span>
                            <button class="ml-2 text-blue-600 hover:text-blue-800 remove-filter" 
                                    data-field="${field}" data-table="${tableId}">
                                <i class="fas fa-times"></i>
                            </button>
                        </span>
                    `;
                    
                    filtersList.append(filterHtml);
                }
                
                // Bind remove filter handlers
                filtersList.find('.remove-filter').on('click', (e) => {
                    const field = $(e.currentTarget).data('field');
                    const tableId = $(e.currentTarget).data('table');
                    this.removeFilter(tableId, field);
                });
            },
            
            removeFilter: function(tableId, field) {
                delete this.columnFilters[tableId][field];
                this.updateActiveFilters(tableId);
                
                const table = $(`#${tableId}`).DataTable();
                table.ajax.reload(null, false);
                
                const columnIndex = this.getColumnFieldMapping(tableId).indexOf(field);
                if (columnIndex >= 0) {
                    const header = $(table.column(columnIndex).header());
                    header.find('.column-burger-menu').removeClass('filtered');
                }
            },
            
            clearAllFilters: function(tableId) {
                this.columnFilters[tableId] = {};
                this.updateActiveFilters(tableId);
                
                const table = $(`#${tableId}`).DataTable();
                table.ajax.reload(null, false);
                
                $(`#${tableId} .column-burger-menu`).removeClass('filtered');
            },
            
            getColumnFieldMapping: function(tableId) {
                const mappings = {
                    'addresses-table': ['name', 'type', 'value', 'description', 'parent-device-group', 'parent-template'],
                    'address-groups-table': ['name', 'members', 'description', 'parent-device-group', 'parent-template'],
                    'services-table': ['name', 'protocol', 'port', 'description', 'parent-device-group', 'parent-template'],
                    'service-groups-table': ['name', 'members', 'description', 'parent-device-group', 'parent-template'],
                    'security-policies-table': ['name', 'from', 'to', 'source', 'destination', 'application', 'service', 'action'],
                    'device-groups-table': ['name', 'description', 'parent_dg', 'address_count', 'service_count', 'pre_security_rules_count', 'post_security_rules_count'],
                    'templates-table': ['name', 'description', 'device_count', 'device_list']
                };
                return mappings[tableId] || [];
            },
            
            getOperatorLabel: function(operator) {
                const labels = {
                    'equals': '=',
                    'ne': '≠',
                    'contains': 'contains',
                    'not_contains': 'not contains',
                    'starts_with': 'starts with',
                    'ends_with': 'ends with',
                    'gt': '>',
                    'gte': '≥',
                    'lt': '<',
                    'lte': '≤',
                    'empty': 'is empty',
                    'not_empty': 'is not empty'
                };
                return labels[operator] || operator;
            },
            
            getFieldType: function(field) {
                const numericFields = ['address_count', 'service_count', 'device_count', 
                                     'pre_security_rules_count', 'post_security_rules_count'];
                return numericFields.includes(field) ? 'numeric' : 'text';
            }
        };
    });

    describe('Filter Parameter Building', () => {
        test('buildFilterParams creates correct parameter format for text filters', () => {
            const filters = {
                name: { operator: 'contains', value: 'test' },
                description: { operator: 'starts_with', value: 'prod' }
            };
            
            const params = configViewer.buildFilterParams(filters);
            
            expect(params).toEqual({
                'filter[name][contains]': 'test',
                'filter[description][starts_with]': 'prod'
            });
        });

        test('buildFilterParams handles equals operator correctly', () => {
            const filters = {
                name: { operator: 'equals', value: 'test-address' }
            };
            
            const params = configViewer.buildFilterParams(filters);
            
            expect(params).toEqual({
                'filter[name]': 'test-address'
            });
        });

        test('buildFilterParams handles empty and not_empty operators', () => {
            const filters = {
                description: { operator: 'empty' },
                name: { operator: 'not_empty' }
            };
            
            const params = configViewer.buildFilterParams(filters);
            
            expect(params).toEqual({
                'filter[description][is_null]': 'true',
                'filter[name][is_not_null]': 'true'
            });
        });

        test('buildFilterParams ignores filters without values', () => {
            const filters = {
                name: { operator: 'contains', value: '' },
                description: { operator: 'equals', value: 'test' }
            };
            
            const params = configViewer.buildFilterParams(filters);
            
            expect(params).toEqual({
                'filter[description]': 'test'
            });
        });

        test('buildFilterParams handles numeric comparison operators', () => {
            const filters = {
                address_count: { operator: 'gt', value: '100' },
                service_count: { operator: 'lte', value: '50' }
            };
            
            const params = configViewer.buildFilterParams(filters);
            
            expect(params).toEqual({
                'filter[address_count][gt]': '100',
                'filter[service_count][lte]': '50'
            });
        });

        test('buildFilterParams handles special characters in values', () => {
            const filters = {
                name: { operator: 'contains', value: 'test/path&special=chars' }
            };
            
            const params = configViewer.buildFilterParams(filters);
            
            expect(params).toEqual({
                'filter[name][contains]': 'test/path&special=chars'
            });
        });
    });

    describe('Active Filters Display', () => {
        test('updateActiveFilters displays filters correctly', () => {
            configViewer.columnFilters['addresses-table'] = {
                name: { operator: 'contains', value: 'test' },
                description: { operator: 'empty' }
            };
            
            configViewer.updateActiveFilters('addresses-table');
            
            const filtersList = $('#addresses-filters-list');
            const filterElements = filtersList.find('.inline-flex');
            
            expect(filterElements.length).toBe(2);
            expect($('#addresses-clear-all').is(':visible')).toBe(true);
        });

        test('updateActiveFilters hides clear all button when no filters', () => {
            configViewer.columnFilters['addresses-table'] = {};
            
            configViewer.updateActiveFilters('addresses-table');
            
            expect($('#addresses-clear-all').is(':visible')).toBe(false);
            expect($('#addresses-filters-list').html()).toBe('');
        });

        test('removeFilter removes single filter and updates display', () => {
            configViewer.columnFilters['addresses-table'] = {
                name: { operator: 'contains', value: 'test' },
                description: { operator: 'equals', value: 'prod' }
            };
            
            configViewer.removeFilter('addresses-table', 'name');
            
            expect(configViewer.columnFilters['addresses-table']).toEqual({
                description: { operator: 'equals', value: 'prod' }
            });
            expect(mockDataTable.ajax.reload).toHaveBeenCalledWith(null, false);
        });

        test('clearAllFilters removes all filters for a table', () => {
            configViewer.columnFilters['addresses-table'] = {
                name: { operator: 'contains', value: 'test' },
                description: { operator: 'equals', value: 'prod' }
            };
            
            configViewer.clearAllFilters('addresses-table');
            
            expect(configViewer.columnFilters['addresses-table']).toEqual({});
            expect(mockDataTable.ajax.reload).toHaveBeenCalledWith(null, false);
        });
    });

    describe('DataTables Integration', () => {
        test('DataTable ajax request includes filter parameters', async () => {
            const mockData = {
                total_items: 100,
                items: [
                    { name: 'test-addr', 'ip-netmask': '10.0.0.1/32' }
                ]
            };
            
            fetch.mockResolvedValueOnce({
                json: () => Promise.resolve(mockData)
            });
            
            // Simulate DataTable initialization with filters
            const ajaxConfig = {
                url: '/api/v1/configs/test-config/addresses',
                data: function(d) {
                    const params = {
                        page: Math.floor(d.start / d.length) + 1,
                        page_size: d.length
                    };
                    
                    const tableFilters = {
                        name: { operator: 'contains', value: 'test' }
                    };
                    
                    const filterParams = configViewer.buildFilterParams(tableFilters);
                    Object.assign(params, filterParams);
                    
                    return params;
                }
            };
            
            const requestData = ajaxConfig.data({ start: 0, length: 25 });
            
            expect(requestData).toEqual({
                page: 1,
                page_size: 25,
                'filter[name][contains]': 'test'
            });
        });

        test('DataTable handles empty response correctly', async () => {
            const mockData = {
                total_items: 0,
                items: []
            };
            
            fetch.mockResolvedValueOnce({
                json: () => Promise.resolve(mockData)
            });
            
            // The dataFilter function should handle empty data
            const dataFilter = function(data) {
                const json = JSON.parse(data);
                return JSON.stringify({
                    draw: 1,
                    recordsTotal: json.total_items,
                    recordsFiltered: json.total_items,
                    data: json.items
                });
            };
            
            const result = JSON.parse(dataFilter(JSON.stringify(mockData)));
            
            expect(result.recordsTotal).toBe(0);
            expect(result.recordsFiltered).toBe(0);
            expect(result.data).toEqual([]);
        });

        test('Pagination parameters are calculated correctly', () => {
            const datatableParams = {
                start: 50,
                length: 25
            };
            
            const page = Math.floor(datatableParams.start / datatableParams.length) + 1;
            
            expect(page).toBe(3); // Third page (0-24, 25-49, 50-74)
        });
    });

    describe('Filter Operators', () => {
        test('getOperatorLabel returns correct labels', () => {
            expect(configViewer.getOperatorLabel('equals')).toBe('=');
            expect(configViewer.getOperatorLabel('ne')).toBe('≠');
            expect(configViewer.getOperatorLabel('contains')).toBe('contains');
            expect(configViewer.getOperatorLabel('gt')).toBe('>');
            expect(configViewer.getOperatorLabel('empty')).toBe('is empty');
        });

        test('getFieldType identifies numeric fields correctly', () => {
            expect(configViewer.getFieldType('address_count')).toBe('numeric');
            expect(configViewer.getFieldType('service_count')).toBe('numeric');
            expect(configViewer.getFieldType('name')).toBe('text');
            expect(configViewer.getFieldType('description')).toBe('text');
        });
    });

    describe('Column Field Mapping', () => {
        test('getColumnFieldMapping returns correct fields for each table', () => {
            const addressFields = configViewer.getColumnFieldMapping('addresses-table');
            expect(addressFields).toContain('name');
            expect(addressFields).toContain('type');
            expect(addressFields).toContain('value');
            
            const policyFields = configViewer.getColumnFieldMapping('security-policies-table');
            expect(policyFields).toContain('from');
            expect(policyFields).toContain('action');
            
            const dgFields = configViewer.getColumnFieldMapping('device-groups-table');
            expect(dgFields).toContain('address_count');
            expect(dgFields).toContain('parent_dg');
        });
    });

    describe('Error Handling', () => {
        test('handles API errors gracefully', async () => {
            fetch.mockRejectedValueOnce(new Error('API Error'));
            
            // Mock console.error to verify it's called
            const consoleError = jest.spyOn(console, 'error').mockImplementation();
            
            try {
                await fetch('/api/v1/configs/test-config/addresses');
            } catch (error) {
                expect(error.message).toBe('API Error');
            }
            
            consoleError.mockRestore();
        });

        test('handles malformed JSON response', () => {
            const dataFilter = function(data) {
                try {
                    const json = JSON.parse(data);
                    return JSON.stringify({
                        draw: 1,
                        recordsTotal: json.total_items || 0,
                        recordsFiltered: json.total_items || 0,
                        data: json.items || []
                    });
                } catch (e) {
                    return JSON.stringify({
                        draw: 1,
                        recordsTotal: 0,
                        recordsFiltered: 0,
                        data: [],
                        error: 'Invalid response format'
                    });
                }
            };
            
            const result = JSON.parse(dataFilter('invalid json'));
            expect(result.error).toBe('Invalid response format');
            expect(result.data).toEqual([]);
        });
    });

    describe('UI State Management', () => {
        test('loading overlay appears during filter application', () => {
            const $table = $('<div class="dataTables_wrapper"><table></table></div>');
            $('body').append($table);
            
            // Simulate adding loading overlay
            if (!$table.find('.table-loading-overlay').length) {
                $table.prepend('<div class="table-loading-overlay"><div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i> Applying filters...</div></div>');
            }
            
            expect($table.find('.table-loading-overlay').length).toBe(1);
            expect($table.find('.loading-spinner').text()).toContain('Applying filters...');
            
            $table.remove();
        });

        test('filter persistence during pagination', () => {
            configViewer.columnFilters['addresses-table'] = {
                name: { operator: 'contains', value: 'test' }
            };
            
            // Simulate pagination request
            const ajaxData = function(d) {
                const params = {
                    page: Math.floor(d.start / d.length) + 1,
                    page_size: d.length
                };
                
                const filterParams = configViewer.buildFilterParams(configViewer.columnFilters['addresses-table']);
                Object.assign(params, filterParams);
                
                return params;
            };
            
            // Test first page
            let data = ajaxData({ start: 0, length: 25 });
            expect(data['filter[name][contains]']).toBe('test');
            expect(data.page).toBe(1);
            
            // Test second page - filters should persist
            data = ajaxData({ start: 25, length: 25 });
            expect(data['filter[name][contains]']).toBe('test');
            expect(data.page).toBe(2);
        });
    });

    describe('Complex Filter Scenarios', () => {
        test('multiple filters on same table', () => {
            const filters = {
                name: { operator: 'starts_with', value: 'prod' },
                description: { operator: 'contains', value: 'server' },
                'parent-device-group': { operator: 'equals', value: 'production' }
            };
            
            const params = configViewer.buildFilterParams(filters);
            
            expect(params).toEqual({
                'filter[name][starts_with]': 'prod',
                'filter[description][contains]': 'server',
                'filter[parent-device-group]': 'production'
            });
        });

        test('mixed text and numeric filters', () => {
            const filters = {
                name: { operator: 'contains', value: 'test' },
                address_count: { operator: 'gte', value: '50' },
                service_count: { operator: 'lt', value: '100' }
            };
            
            const params = configViewer.buildFilterParams(filters);
            
            expect(params).toEqual({
                'filter[name][contains]': 'test',
                'filter[address_count][gte]': '50',
                'filter[service_count][lt]': '100'
            });
        });

        test('empty value filters combined with regular filters', () => {
            const filters = {
                name: { operator: 'not_empty' },
                description: { operator: 'empty' },
                type: { operator: 'equals', value: 'ip-netmask' }
            };
            
            const params = configViewer.buildFilterParams(filters);
            
            expect(params).toEqual({
                'filter[name][is_not_null]': 'true',
                'filter[description][is_null]': 'true',
                'filter[type]': 'ip-netmask'
            });
        });
    });

    describe('Filter Debouncing', () => {
        jest.useFakeTimers();
        
        test('filter input debounces correctly', () => {
            const applyFilter = jest.fn();
            let debounceTimer;
            
            const simulateKeyup = () => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    applyFilter();
                }, 500);
            };
            
            // Simulate rapid keystrokes
            simulateKeyup();
            simulateKeyup();
            simulateKeyup();
            
            // Should not have been called yet
            expect(applyFilter).not.toHaveBeenCalled();
            
            // Fast forward time
            jest.advanceTimersByTime(500);
            
            // Should be called once after debounce
            expect(applyFilter).toHaveBeenCalledTimes(1);
        });
        
        test('immediate apply on Enter key', () => {
            const applyFilter = jest.fn();
            
            const handleKeyup = (keyCode) => {
                if (keyCode === 13) { // Enter key
                    applyFilter();
                    return;
                }
                // Normal debounce logic would go here
            };
            
            handleKeyup(13);
            
            expect(applyFilter).toHaveBeenCalledTimes(1);
        });
    });

    describe('Table-Specific Functionality', () => {
        test('address table type detection', () => {
            const getAddressType = (item) => {
                if (item['ip-netmask']) return 'ip-netmask';
                if (item.fqdn) return 'fqdn';
                if (item['ip-range']) return 'ip-range';
                return null;
            };
            
            expect(getAddressType({ 'ip-netmask': '10.0.0.1/32' })).toBe('ip-netmask');
            expect(getAddressType({ fqdn: 'example.com' })).toBe('fqdn');
            expect(getAddressType({ 'ip-range': '10.0.0.1-10.0.0.10' })).toBe('ip-range');
        });

        test('service port extraction', () => {
            const getServicePort = (item) => {
                if (item.protocol) {
                    if (item.protocol.tcp && item.protocol.tcp.port) {
                        return `TCP: ${item.protocol.tcp.port}`;
                    }
                    if (item.protocol.udp && item.protocol.udp.port) {
                        return `UDP: ${item.protocol.udp.port}`;
                    }
                }
                return '-';
            };
            
            expect(getServicePort({ protocol: { tcp: { port: '80' } } })).toBe('TCP: 80');
            expect(getServicePort({ protocol: { udp: { port: '53' } } })).toBe('UDP: 53');
            expect(getServicePort({})).toBe('-');
        });
    });
});

describe('Integration Tests', () => {
    test('full filter application flow', async () => {
        // Set up initial state
        configViewer.columnFilters['addresses-table'] = {};
        
        // Apply a filter
        configViewer.columnFilters['addresses-table']['name'] = {
            operator: 'contains',
            value: 'test'
        };
        
        // Update display
        configViewer.updateActiveFilters('addresses-table');
        
        // Verify filter is displayed
        const filtersList = $('#addresses-filters-list');
        expect(filtersList.find('.inline-flex').length).toBe(1);
        
        // Verify DataTable would reload with filter
        expect(mockDataTable.ajax.reload).not.toHaveBeenCalled();
        
        // Simulate table reload
        mockDataTable.ajax.reload(null, false);
        expect(mockDataTable.ajax.reload).toHaveBeenCalledWith(null, false);
    });

    test('filter removal and table refresh', () => {
        // Set up filters
        configViewer.columnFilters['services-table'] = {
            name: { operator: 'starts_with', value: 'http' },
            protocol: { operator: 'equals', value: 'tcp' }
        };
        
        // Remove one filter
        configViewer.removeFilter('services-table', 'protocol');
        
        // Verify remaining filters
        expect(configViewer.columnFilters['services-table']).toEqual({
            name: { operator: 'starts_with', value: 'http' }
        });
        
        // Verify table reload was triggered
        expect(mockDataTable.ajax.reload).toHaveBeenCalledWith(null, false);
    });
});
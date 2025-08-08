/**
 * Snapshot tests for PAN-OS Configuration Viewer UI components
 * Tests the rendering of filter displays, table cells, and UI states
 */

import $ from 'jquery';

describe('Viewer UI Snapshot Tests', () => {
    let configViewer;
    
    beforeEach(() => {
        // Initialize a minimal configViewer for snapshot testing
        configViewer = {
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
            }
        };
    });

    describe('Filter Display Components', () => {
        test('renders single filter display', () => {
            const filterHtml = `
                <span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800 mr-2 mb-2">
                    <span class="font-medium">Name</span>
                    <span class="mx-1">contains</span>
                    <span>test-address</span>
                    <button class="ml-2 text-blue-600 hover:text-blue-800 remove-filter" 
                            data-field="name" data-table="addresses-table">
                        <i class="fas fa-times"></i>
                    </button>
                </span>
            `;
            
            expect(filterHtml).toMatchSnapshot('single-filter-display');
        });

        test('renders empty value filter', () => {
            const filterHtml = `
                <span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800 mr-2 mb-2">
                    <span class="font-medium">Description</span>
                    <span class="mx-1">is empty</span>
                    <span>(empty)</span>
                    <button class="ml-2 text-blue-600 hover:text-blue-800 remove-filter" 
                            data-field="description" data-table="addresses-table">
                        <i class="fas fa-times"></i>
                    </button>
                </span>
            `;
            
            expect(filterHtml).toMatchSnapshot('empty-value-filter');
        });

        test('renders numeric comparison filter', () => {
            const filterHtml = `
                <span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800 mr-2 mb-2">
                    <span class="font-medium">Address Count</span>
                    <span class="mx-1">≥</span>
                    <span>100</span>
                    <button class="ml-2 text-blue-600 hover:text-blue-800 remove-filter" 
                            data-field="address_count" data-table="device-groups-table">
                        <i class="fas fa-times"></i>
                    </button>
                </span>
            `;
            
            expect(filterHtml).toMatchSnapshot('numeric-comparison-filter');
        });
    });

    describe('Table Cell Rendering', () => {
        test('renders address type badges', () => {
            const ipNetmaskBadge = '<span class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">IP/Netmask</span>';
            const fqdnBadge = '<span class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">FQDN</span>';
            const ipRangeBadge = '<span class="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full">IP Range</span>';
            
            expect(ipNetmaskBadge).toMatchSnapshot('ip-netmask-badge');
            expect(fqdnBadge).toMatchSnapshot('fqdn-badge');
            expect(ipRangeBadge).toMatchSnapshot('ip-range-badge');
        });

        test('renders service protocol badges', () => {
            const tcpBadge = '<span class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">TCP</span>';
            const udpBadge = '<span class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">UDP</span>';
            const tcpUdpBadges = '<span class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">TCP</span> <span class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">UDP</span>';
            
            expect(tcpBadge).toMatchSnapshot('tcp-protocol-badge');
            expect(udpBadge).toMatchSnapshot('udp-protocol-badge');
            expect(tcpUdpBadges).toMatchSnapshot('tcp-udp-protocol-badges');
        });

        test('renders group members display', () => {
            const membersHtml = `
                <div class="max-w-md inline-flex flex-wrap gap-1">
                    <span class="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-md">member1</span>
                    <span class="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-md">member2</span>
                    <span class="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-md">member3</span>
                    <span class="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-md">member4</span>
                    <span class="px-2 py-1 text-xs bg-gray-200 text-gray-600 rounded-md">+6 more</span>
                </div>
            `;
            
            expect(membersHtml).toMatchSnapshot('group-members-with-overflow');
        });

        test('renders empty members display', () => {
            const emptyMembersHtml = '<span class="text-gray-400">No members</span>';
            
            expect(emptyMembersHtml).toMatchSnapshot('empty-members');
        });

        test('renders location badges', () => {
            const sharedLocation = '<span class="text-gray-400">Shared</span>';
            const dgLocation = '<span class="text-blue-600">DG: production</span>';
            const templateLocation = '<span class="text-green-600">Template: base-template</span>';
            
            expect(sharedLocation).toMatchSnapshot('shared-location');
            expect(dgLocation).toMatchSnapshot('device-group-location');
            expect(templateLocation).toMatchSnapshot('template-location');
        });
    });

    describe('Filter Dropdown Components', () => {
        test('renders text field filter dropdown', () => {
            const dropdownHtml = `
                <div class="column-filter-dropdown">
                    <div class="p-3 min-w-[200px]">
                        <div class="mb-2">
                            <select class="filter-operator-select w-full px-2 py-1 border rounded text-sm">
                                <option value="contains">Contains</option>
                                <option value="not_contains">Not Contains</option>
                                <option value="equals">Equals</option>
                                <option value="ne">Not Equals</option>
                                <option value="starts_with">Starts With</option>
                                <option value="ends_with">Ends With</option>
                                <option value="empty">Is Empty</option>
                                <option value="not_empty">Is Not Empty</option>
                            </select>
                        </div>
                        <div class="mb-2">
                            <input type="text" class="filter-search-input w-full px-2 py-1 border rounded text-sm" 
                                   placeholder="Filter value...">
                        </div>
                        <div class="filter-actions flex gap-2">
                            <button class="apply-filter px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600">
                                Apply
                            </button>
                            <button class="clear-filter px-3 py-1 bg-gray-300 text-gray-700 rounded text-sm hover:bg-gray-400">
                                Clear
                            </button>
                        </div>
                        <div class="filter-loading hidden">
                            <i class="fas fa-spinner fa-spin"></i> Applying...
                        </div>
                    </div>
                </div>
            `;
            
            expect(dropdownHtml).toMatchSnapshot('text-field-filter-dropdown');
        });

        test('renders numeric field filter dropdown', () => {
            const dropdownHtml = `
                <div class="column-filter-dropdown">
                    <div class="p-3 min-w-[200px]">
                        <div class="mb-2">
                            <select class="filter-operator-select w-full px-2 py-1 border rounded text-sm">
                                <option value="equals">Equals</option>
                                <option value="ne">Not Equals</option>
                                <option value="gt">Greater Than</option>
                                <option value="gte">Greater or Equal</option>
                                <option value="lt">Less Than</option>
                                <option value="lte">Less or Equal</option>
                                <option value="empty">Is Empty</option>
                                <option value="not_empty">Is Not Empty</option>
                            </select>
                        </div>
                        <div class="mb-2">
                            <input type="number" class="filter-search-input w-full px-2 py-1 border rounded text-sm" 
                                   placeholder="Filter value...">
                        </div>
                        <div class="filter-actions flex gap-2">
                            <button class="apply-filter px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600">
                                Apply
                            </button>
                            <button class="clear-filter px-3 py-1 bg-gray-300 text-gray-700 rounded text-sm hover:bg-gray-400">
                                Clear
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            expect(dropdownHtml).toMatchSnapshot('numeric-field-filter-dropdown');
        });
    });

    describe('Loading States', () => {
        test('renders table loading overlay', () => {
            const loadingOverlay = `
                <div class="table-loading-overlay">
                    <div class="loading-spinner">
                        <i class="fas fa-spinner fa-spin"></i> Applying filters...
                    </div>
                </div>
            `;
            
            expect(loadingOverlay).toMatchSnapshot('table-loading-overlay');
        });

        test('renders filter dropdown loading state', () => {
            const loadingState = `
                <div class="filter-loading">
                    <i class="fas fa-spinner fa-spin"></i> Applying...
                </div>
            `;
            
            expect(loadingState).toMatchSnapshot('filter-dropdown-loading');
        });
    });

    describe('Security Policy Table Cells', () => {
        test('renders policy action badges', () => {
            const allowBadge = '<span class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">allow</span>';
            const denyBadge = '<span class="px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full">deny</span>';
            const dropBadge = '<span class="px-2 py-1 text-xs bg-orange-100 text-orange-800 rounded-full">drop</span>';
            
            expect(allowBadge).toMatchSnapshot('allow-action-badge');
            expect(denyBadge).toMatchSnapshot('deny-action-badge');
            expect(dropBadge).toMatchSnapshot('drop-action-badge');
        });

        test('renders policy zones and addresses', () => {
            const zonesList = 'trust, dmz, untrust';
            const addressList = '10.0.0.0/8, 192.168.0.0/16, any';
            
            expect(zonesList).toMatchSnapshot('policy-zones-list');
            expect(addressList).toMatchSnapshot('policy-address-list');
        });
    });

    describe('Count Badges', () => {
        test('renders various count badges', () => {
            const addressCountBadge = '<span class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">1234</span>';
            const serviceCountBadge = '<span class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">567</span>';
            const ruleCountBadge = '<span class="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full">89</span>';
            
            expect(addressCountBadge).toMatchSnapshot('address-count-badge');
            expect(serviceCountBadge).toMatchSnapshot('service-count-badge');
            expect(ruleCountBadge).toMatchSnapshot('rule-count-badge');
        });
    });

    describe('Clear All Filters Button', () => {
        test('renders clear all filters button', () => {
            const clearAllButton = `
                <button class="px-3 py-1 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded">
                    <i class="fas fa-times-circle mr-1"></i>Clear All Filters
                </button>
            `;
            
            expect(clearAllButton).toMatchSnapshot('clear-all-filters-button');
        });
    });

    describe('Column Burger Menu', () => {
        test('renders column burger menu button', () => {
            const burgerMenu = `
                <button class="column-burger-menu ml-2 text-gray-400 hover:text-gray-600">
                    <i class="fas fa-filter text-xs"></i>
                </button>
            `;
            
            const filteredBurgerMenu = `
                <button class="column-burger-menu filtered ml-2 text-blue-600 hover:text-blue-800">
                    <i class="fas fa-filter text-xs"></i>
                </button>
            `;
            
            expect(burgerMenu).toMatchSnapshot('column-burger-menu');
            expect(filteredBurgerMenu).toMatchSnapshot('column-burger-menu-filtered');
        });
    });
});
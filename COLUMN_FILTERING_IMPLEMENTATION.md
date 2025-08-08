# Column Filtering Implementation

## Overview
This implementation integrates the backend filtering capabilities with DataTables column filters for server-side processing.

## Changes Made

### 1. Enhanced Column Filters Component
- Added `columnFilters` object to store active filters per table
- Added `filterDebounceTimer` for debouncing filter input
- Added `buildFilterRegex` method for client-side filtering fallback
- Added `getColumnFieldMapping` method to map table columns to API fields

### 2. Updated `addEnhancedColumnFilters` Method
- Now supports server-side filtering by storing filters in `columnFilters`
- Sends filter parameters to backend API in format: `filter[field][operator]=value`
- Shows loading indicators during filter operations
- Implements 500ms debouncing on filter input to reduce API calls
- Maintains visual feedback with filtered burger menu highlighting

### 3. DataTables Ajax Configuration
Updated all main tables to include column filters in API requests:
- Addresses table
- Address Groups table
- Services table
- Service Groups table
- Security Policies table

### 4. Filter Operators Supported
- `contains` - Default search behavior
- `equals` - Exact match
- `ne` (not equals) - Not equal to value
- `starts_with` - Starts with value
- `ends_with` - Ends with value
- `empty` - Field is empty
- `not_empty` - Field is not empty

### 5. CSS Enhancements
- Added loading indicator styling
- Improved dropdown appearance and animations

## Backend API Format
The implementation sends filters to the backend in the following format:
```
filter[field]=value              # For default 'contains' operator
filter[field][operator]=value    # For specific operators
```

Multiple filters are AND'ed together by the backend.

## Testing

### 1. Start the Server
```bash
python main.py
```

### 2. Open the Web Interface
Navigate to http://localhost:8000

### 3. Test Column Filtering
1. Load any table (Addresses, Services, Security Policies, etc.)
2. Click the burger menu icon (☰) next to any column header
3. Select a filter operator from the dropdown
4. Enter a search value
5. Click "Apply" or press Enter

### 4. Run Automated Tests
```bash
python test_column_filters.py
```

## Key Features

### Debouncing
- Typing in filter input fields triggers search after 500ms of inactivity
- Pressing Enter applies the filter immediately
- Reduces unnecessary API calls while typing

### Loading Indicators
- Shows "Applying filter..." message while processing
- Hides action buttons during loading to prevent multiple requests

### Visual Feedback
- Burger menu turns green when a filter is active on that column
- Clear visual distinction between filtered and unfiltered columns

### Server-Side Processing
- All filtering happens on the backend for performance with large datasets
- Maintains pagination and sorting while filtering
- Updates total count to reflect filtered results

## Limitations

1. The `not_contains` operator is not supported by the backend API - falls back to `contains` with a console warning
2. Complex filtering (OR conditions) is not currently supported
3. Date/time filtering operators are not implemented yet
4. Numeric comparison operators (gt, lt, gte, lte) are supported by backend but not exposed in UI yet

## Future Enhancements

1. Add numeric comparison operators for numeric columns
2. Add date range filtering for date columns
3. Implement saved filter presets
4. Add export filtered results functionality
5. Support for OR conditions between filters
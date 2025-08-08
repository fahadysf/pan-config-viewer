# Manual Test Plan: Integrated Pagination and Filtering

## Overview
This document provides a comprehensive manual testing plan for the integrated pagination and filtering features in the pan-config-viewer application.

## Prerequisites
1. Application running locally at http://localhost:8000
2. Large configuration file loaded (pan-bkp-202507151414.xml)
3. Browser developer tools available for monitoring network requests

## Test Scenarios

### 1. Basic Pagination Tests

#### 1.1 Default Pagination
- **Steps:**
  1. Navigate to http://localhost:8000/viewer
  2. Select "pan-bkp-202507151414" configuration
  3. Click on "Address Objects" tab
- **Expected Results:**
  - Table displays with default 10 entries per page
  - Pagination controls show at bottom
  - "Previous" button is disabled on first page
  - Total entries count is displayed

#### 1.2 Page Size Changes
- **Steps:**
  1. Change "Show entries" dropdown to 25
  2. Change to 50
  3. Change to 100
- **Expected Results:**
  - Table refreshes with new page size
  - Pagination updates accordingly
  - Data loads without errors
  - Performance remains acceptable (< 2 seconds)

#### 1.3 Page Navigation
- **Steps:**
  1. Click "Next" button
  2. Click page number "3"
  3. Click "Previous"
  4. Click "Last" page
  5. Click "First" page
- **Expected Results:**
  - Each navigation works correctly
  - URL updates with page parameter
  - No duplicate data between pages
  - Loading indicator appears during navigation

### 2. Column Filtering Tests

#### 2.1 Single Column Filter
- **Steps:**
  1. In Address Objects table, type "10.0" in Name column filter
  2. Wait for debounce (300ms)
- **Expected Results:**
  - Table updates to show only addresses containing "10.0"
  - Result count updates
  - Pagination resets to page 1
  - Clear filter button appears

#### 2.2 Multiple Column Filters
- **Steps:**
  1. Type "10.0" in Name filter
  2. Type "subnet" in Description filter
  3. Select "shared" in Location filter
- **Expected Results:**
  - All filters apply with AND logic
  - Only records matching ALL criteria show
  - Each filter can be cleared independently

#### 2.3 Filter Operators
- **Steps:**
  1. Test "equals" operator: `name[eq]=10.0.0.1`
  2. Test "starts with": `name[starts_with]=10.`
  3. Test "ends with": `name[ends_with]=.1`
  4. Test "contains": `name[contains]=0.0`
- **Expected Results:**
  - Each operator works as expected
  - Results match the operator logic

### 3. Combined Pagination and Filtering

#### 3.1 Filter then Paginate
- **Steps:**
  1. Apply filter: Name contains "10"
  2. Navigate through paginated results
  3. Change page size while filtered
- **Expected Results:**
  - Filter persists across pages
  - Page size change maintains filter
  - Total count reflects filtered results

#### 3.2 Paginate then Filter
- **Steps:**
  1. Navigate to page 3
  2. Apply filter: Protocol = "tcp"
  3. Observe behavior
- **Expected Results:**
  - Returns to page 1 after filtering
  - Shows filtered results starting from beginning

### 4. Performance Tests

#### 4.1 Large Dataset Performance
- **Steps:**
  1. Load Security Policies table (largest dataset)
  2. Set page size to 100
  3. Navigate through pages rapidly
- **Expected Results:**
  - Each page loads in < 2 seconds
  - No browser freezing
  - Memory usage remains stable

#### 4.2 Complex Filter Performance
- **Steps:**
  1. Apply multiple filters on Security Policies
  2. Filter by source, destination, and application
  3. Change filters rapidly
- **Expected Results:**
  - Filtering remains responsive
  - Debouncing prevents excessive API calls
  - Results update smoothly

### 5. Edge Cases and Error Handling

#### 5.1 Empty Results
- **Steps:**
  1. Filter with non-existent value: "xyz123nonexistent"
- **Expected Results:**
  - Shows "No matching records found"
  - Pagination controls hide or disable
  - Clear filter option remains available

#### 5.2 Special Characters
- **Steps:**
  1. Filter with special characters: "test-name", "test_name", "test.com"
  2. Filter with spaces: "test name"
- **Expected Results:**
  - All special characters handled correctly
  - No JavaScript errors
  - Results match expected data

#### 5.3 Invalid Page Numbers
- **Steps:**
  1. Manually edit URL to page=9999
  2. Enter negative page number
- **Expected Results:**
  - Shows empty results or redirects to valid page
  - No server errors
  - User-friendly message displayed

### 6. Browser Compatibility Tests

#### 6.1 Cross-Browser Testing
- **Test in:**
  - Chrome (latest)
  - Firefox (latest)
  - Safari (latest)
  - Edge (latest)
- **Expected Results:**
  - All features work consistently
  - No browser-specific issues
  - Performance comparable across browsers

### 7. User Experience Tests

#### 7.1 Loading Indicators
- **Steps:**
  1. Apply filters and observe loading states
  2. Navigate pages and observe indicators
- **Expected Results:**
  - Loading spinner appears during data fetch
  - Table shows "Processing..." message
  - UI remains responsive

#### 7.2 Filter Feedback
- **Steps:**
  1. Apply various filters
  2. Observe visual feedback
- **Expected Results:**
  - Active filters highlighted
  - Clear indication of applied filters
  - Easy way to clear filters

#### 7.3 Responsive Design
- **Steps:**
  1. Test on different screen sizes
  2. Test on mobile devices
- **Expected Results:**
  - Pagination controls adapt to screen size
  - Filters remain usable on mobile
  - Horizontal scrolling for wide tables

### 8. Data Integrity Tests

#### 8.1 Data Consistency
- **Steps:**
  1. Export full dataset (disable pagination)
  2. Navigate through all pages manually
  3. Compare total items collected
- **Expected Results:**
  - No missing records
  - No duplicate records
  - Counts match exactly

#### 8.2 Sort Order Preservation
- **Steps:**
  1. Apply sorting on a column
  2. Navigate through pages
  3. Apply filter
- **Expected Results:**
  - Sort order maintained across pages
  - Sort order maintained after filtering

### 9. API Integration Tests

#### 9.1 Network Request Monitoring
- **Steps:**
  1. Open browser DevTools Network tab
  2. Perform various operations
  3. Monitor API calls
- **Expected Results:**
  - Correct parameters sent to API
  - No redundant API calls
  - Proper error handling for failed requests

#### 9.2 URL Parameter Persistence
- **Steps:**
  1. Apply filters and pagination
  2. Copy URL
  3. Open in new tab
- **Expected Results:**
  - Same view restored from URL
  - All filters and page preserved

## Performance Benchmarks

### Expected Response Times:
- Initial page load: < 3 seconds
- Page navigation: < 1 second
- Filter application: < 1.5 seconds
- Page size change: < 2 seconds

### Dataset Size Expectations:
- Address Objects: ~5000+ items
- Security Policies: ~1000+ items
- Services: ~500+ items
- All should handle smoothly

## Regression Test Checklist

- [ ] Legacy filter parameters still work
- [ ] All table tabs function correctly
- [ ] Export functionality works with filters
- [ ] Burger menu actions work on filtered data
- [ ] No JavaScript console errors
- [ ] No memory leaks after extended use
- [ ] All endpoints return proper pagination structure

## Bug Reporting Template

When reporting issues, include:
1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Browser and version
5. Configuration file used
6. Console errors (if any)
7. Network request details
8. Screenshots

## Notes for Testers

1. Always test with both small (test_panorama.xml) and large (pan-bkp-202507151414.xml) configurations
2. Pay attention to performance degradation over time
3. Test filter combinations that might not make logical sense
4. Verify counts at each step
5. Check for race conditions with rapid actions
6. Monitor browser memory usage for leaks
"""
Comprehensive test suite for integrated pagination and filtering functionality.

Tests cover:
1. Pagination works correctly on all tables
2. Column filters work with server-side data
3. Filtering + pagination work together correctly
4. Performance with large datasets
5. Edge cases: empty results, invalid filters, etc.
6. User experience: debouncing, loading indicators, etc.
7. All operators work correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import time
from typing import Dict, List, Any
from fastapi.testclient import TestClient
import json


class TestIntegratedPaginationFiltering:
    """Test suite for integrated pagination and filtering functionality"""
    
    # Test data expectations for real config
    EXPECTED_MIN_COUNTS = {
        "addresses": 100,
        "address-groups": 50,
        "services": 50,
        "service-groups": 20,
        "device-groups": 5,
        "security-policies": 50
    }
    
    def test_pagination_basic_functionality(self, real_client: TestClient):
        """Test basic pagination functionality across all endpoints"""
        endpoints = [
            "/api/v1/configs/pan-bkp-202507151414/addresses",
            "/api/v1/configs/pan-bkp-202507151414/address-groups",
            "/api/v1/configs/pan-bkp-202507151414/services",
            "/api/v1/configs/pan-bkp-202507151414/service-groups",
            "/api/v1/configs/pan-bkp-202507151414/device-groups",
            "/api/v1/configs/pan-bkp-202507151414/security-policies"
        ]
        
        for endpoint in endpoints:
            # Test default pagination
            response = real_client.get(endpoint)
            assert response.status_code == 200
            data = response.json()
            
            # Check pagination structure
            assert "items" in data
            assert "total_items" in data
            assert "page" in data
            assert "page_size" in data
            assert "total_pages" in data
            assert "has_next" in data
            assert "has_previous" in data
            
            # Verify default values
            assert data["page"] == 1
            assert data["page_size"] == 500
            assert data["has_previous"] is False
            
            # Test page 2 if available
            if data["has_next"]:
                response2 = real_client.get(f"{endpoint}?page=2")
                assert response2.status_code == 200
                data2 = response2.json()
                assert data2["page"] == 2
                assert data2["has_previous"] is True
                assert len(data2["items"]) > 0
    
    def test_pagination_page_sizes(self, real_client: TestClient):
        """Test different page sizes"""
        endpoint = "/api/v1/configs/pan-bkp-202507151414/addresses"
        
        # Test various page sizes
        page_sizes = [10, 50, 100, 500, 1000]
        
        for page_size in page_sizes:
            response = real_client.get(f"{endpoint}?page_size={page_size}")
            assert response.status_code == 200
            data = response.json()
            
            assert data["page_size"] == page_size
            assert len(data["items"]) <= page_size
            
            # Calculate expected total pages
            expected_pages = (data["total_items"] + page_size - 1) // page_size
            assert data["total_pages"] == expected_pages
    
    def test_pagination_disable_paging(self, real_client: TestClient):
        """Test disable_paging parameter"""
        endpoint = "/api/v1/configs/pan-bkp-202507151414/services"
        
        # Get all items with paging disabled
        response = real_client.get(f"{endpoint}?disable_paging=true")
        assert response.status_code == 200
        data = response.json()
        
        # Should return all items
        assert data["page"] == 1
        assert data["page_size"] == len(data["items"])
        assert data["total_pages"] == 1
        assert data["has_next"] is False
        assert data["has_previous"] is False
        assert data["total_items"] == len(data["items"])
    
    def test_filtering_basic_functionality(self, real_client: TestClient):
        """Test basic filtering functionality"""
        # Test address filtering by name
        response = real_client.get(
            "/api/v1/configs/pan-bkp-202507151414/addresses?filter[name]=10.0"
        )
        assert response.status_code == 200
        data = response.json()
        
        # All items should contain "10.0" in the name
        for item in data["items"]:
            assert "10.0" in item["name"].lower()
        
        # Test service filtering by protocol
        response = real_client.get(
            "/api/v1/configs/pan-bkp-202507151414/services?filter[protocol]=tcp"
        )
        assert response.status_code == 200
        data = response.json()
        
        # All items should be TCP services
        for item in data["items"]:
            assert item["protocol"]["tcp"] is not None
            assert item["protocol"]["udp"] is None
    
    def test_filtering_operators(self, real_client: TestClient):
        """Test all filtering operators"""
        # Test equals operator
        response = real_client.get(
            "/api/v1/configs/pan-bkp-202507151414/addresses?filter[name][eq]=10.0.0.1"
        )
        assert response.status_code == 200
        data = response.json()
        if data["total_items"] > 0:
            assert all(item["name"] == "10.0.0.1" for item in data["items"])
        
        # Test starts_with operator
        response = real_client.get(
            "/api/v1/configs/pan-bkp-202507151414/addresses?filter[name][starts_with]=10."
        )
        assert response.status_code == 200
        data = response.json()
        if data["total_items"] > 0:
            assert all(item["name"].startswith("10.") for item in data["items"])
        
        # Test ends_with operator
        response = real_client.get(
            "/api/v1/configs/pan-bkp-202507151414/addresses?filter[name][ends_with]=.1"
        )
        assert response.status_code == 200
        data = response.json()
        if data["total_items"] > 0:
            assert all(item["name"].endswith(".1") for item in data["items"])
        
        # Test contains operator (default)
        response = real_client.get(
            "/api/v1/configs/pan-bkp-202507151414/addresses?filter[name][contains]=0.0"
        )
        assert response.status_code == 200
        data = response.json()
        if data["total_items"] > 0:
            assert all("0.0" in item["name"] for item in data["items"])
    
    def test_filtering_with_pagination(self, real_client: TestClient):
        """Test filtering combined with pagination"""
        # Get filtered results with pagination
        base_url = "/api/v1/configs/pan-bkp-202507151414/addresses"
        filter_param = "filter[name]=10"
        page_size = 10
        
        # Get first page
        response1 = real_client.get(f"{base_url}?{filter_param}&page=1&page_size={page_size}")
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Store first page items
        first_page_items = data1["items"]
        
        # If there's a second page, get it
        if data1["has_next"]:
            response2 = real_client.get(f"{base_url}?{filter_param}&page=2&page_size={page_size}")
            assert response2.status_code == 200
            data2 = response2.json()
            
            # Ensure no duplicate items between pages
            first_page_names = {item["name"] for item in first_page_items}
            second_page_names = {item["name"] for item in data2["items"]}
            assert len(first_page_names & second_page_names) == 0
            
            # All items should still match the filter
            for item in data2["items"]:
                assert "10" in item["name"]
    
    def test_multiple_filters(self, real_client: TestClient):
        """Test multiple filters applied together (AND logic)"""
        # Test security policies with multiple filters
        response = real_client.get(
            "/api/v1/configs/pan-bkp-202507151414/security-policies?"
            "filter[action]=allow&filter[disabled]=false"
        )
        assert response.status_code == 200
        data = response.json()
        
        # All items should match both filters
        for item in data["items"]:
            assert item["action"] == "allow"
            assert item.get("disabled", False) is False
    
    def test_edge_cases(self, real_client: TestClient):
        """Test edge cases and error handling"""
        # Test empty results
        response = real_client.get(
            "/api/v1/configs/pan-bkp-202507151414/addresses?"
            "filter[name]=this_should_not_exist_xyz123"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_items"] == 0
        assert len(data["items"]) == 0
        assert data["total_pages"] == 0
        assert data["has_next"] is False
        assert data["has_previous"] is False
        
        # Test invalid page number
        response = real_client.get(
            "/api/v1/configs/pan-bkp-202507151414/addresses?page=99999"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 0
        
        # Test invalid filter operator (should return 400)
        response = real_client.get(
            "/api/v1/configs/pan-bkp-202507151414/addresses?"
            "filter[name][invalid_op]=test"
        )
        assert response.status_code == 400  # Should return error for invalid operator
        
        # Test page_size limits
        response = real_client.get(
            "/api/v1/configs/pan-bkp-202507151414/addresses?page_size=10001"
        )
        assert response.status_code == 422  # Should enforce max page size
    
    def test_performance_large_datasets(self, real_client: TestClient):
        """Test performance with large datasets"""
        # Test response time for large dataset without filters
        start_time = time.time()
        response = real_client.get(
            "/api/v1/configs/pan-bkp-202507151414/addresses?page_size=100"
        )
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # Response should be reasonably fast (under 2 seconds)
        assert response_time < 2.0, f"Response took {response_time:.2f} seconds"
        
        # Test with filtering on large dataset
        start_time = time.time()
        response = real_client.get(
            "/api/v1/configs/pan-bkp-202507151414/addresses?"
            "filter[name]=10&page_size=100"
        )
        end_time = time.time()
        
        assert response.status_code == 200
        filter_response_time = end_time - start_time
        
        # Filtered response should also be fast
        assert filter_response_time < 2.0, f"Filtered response took {filter_response_time:.2f} seconds"
    
    def test_all_endpoint_filters(self, real_client: TestClient):
        """Test that all documented filters work for each endpoint"""
        # Test address filters
        address_filters = [
            "filter[name]=test",
            "filter[ip]=10.0.0.1",
            "filter[description]=test",
            "filter[location]=shared"
        ]
        
        for filter_param in address_filters:
            response = real_client.get(
                f"/api/v1/configs/pan-bkp-202507151414/addresses?{filter_param}"
            )
            assert response.status_code == 200
        
        # Test service filters
        service_filters = [
            "filter[name]=http",
            "filter[protocol]=tcp",
            "filter[port]=80",
            "filter[description]=test"
        ]
        
        for filter_param in service_filters:
            response = real_client.get(
                f"/api/v1/configs/pan-bkp-202507151414/services?{filter_param}"
            )
            assert response.status_code == 200
        
        # Test security policy filters
        policy_filters = [
            "filter[name]=test",
            "filter[source]=any",
            "filter[destination]=any",
            "filter[action]=allow",
            "filter[disabled]=false"
        ]
        
        for filter_param in policy_filters:
            response = real_client.get(
                f"/api/v1/configs/pan-bkp-202507151414/security-policies?{filter_param}"
            )
            assert response.status_code == 200
    
    def test_data_consistency(self, real_client: TestClient):
        """Test data consistency across paginated results"""
        endpoint = "/api/v1/configs/pan-bkp-202507151414/addresses"
        
        # Get total count with pagination
        response = real_client.get(f"{endpoint}?page_size=50")
        assert response.status_code == 200
        total_with_pagination = response.json()["total_items"]
        
        # Get all items without pagination
        response = real_client.get(f"{endpoint}?disable_paging=true")
        assert response.status_code == 200
        all_items = response.json()["items"]
        total_without_pagination = len(all_items)
        
        # Totals should match
        assert total_with_pagination == total_without_pagination
        
        # Collect all items across pages
        collected_items = []
        page = 1
        while True:
            response = real_client.get(f"{endpoint}?page={page}&page_size=50")
            assert response.status_code == 200
            data = response.json()
            
            collected_items.extend(data["items"])
            
            if not data["has_next"]:
                break
            page += 1
        
        # Should have collected all items
        assert len(collected_items) == total_without_pagination
        
        # Check that collected items match unpaginated items
        # Sort both lists by name for comparison (since order might differ)
        collected_sorted = sorted(collected_items, key=lambda x: x["name"])
        all_sorted = sorted(all_items, key=lambda x: x["name"])
        
        # Compare the sorted lists (allows duplicates in source data)
        for i, (collected, original) in enumerate(zip(collected_sorted, all_sorted)):
            assert collected["name"] == original["name"], f"Mismatch at index {i}"
    
    def test_special_characters_in_filters(self, real_client: TestClient):
        """Test handling of special characters in filter values"""
        # Test with special characters that might need encoding
        special_values = [
            "test-name",
            "test_name",
            "test.name",
            "test/name",
            "test name",  # space
            "test%20name",  # URL encoded space
        ]
        
        for value in special_values:
            # URL encode the value properly
            import urllib.parse
            encoded_value = urllib.parse.quote(value)
            
            response = real_client.get(
                f"/api/v1/configs/pan-bkp-202507151414/addresses?"
                f"filter[name]={encoded_value}"
            )
            assert response.status_code == 200
    
    def test_list_field_filters(self, real_client: TestClient):
        """Test filtering on list fields (tags, members, etc.)"""
        # Test filtering by tag (list field)
        response = real_client.get(
            "/api/v1/configs/pan-bkp-202507151414/addresses?filter[tag]=production"
        )
        assert response.status_code == 200
        data = response.json()
        
        # Test IN operator for lists
        response = real_client.get(
            "/api/v1/configs/pan-bkp-202507151414/security-policies?"
            "filter[source][in]=any"
        )
        assert response.status_code == 200
        data = response.json()
        
        if data["total_items"] > 0:
            # Check that 'any' is in the source list
            for item in data["items"]:
                assert "any" in item.get("source", [])
    
    def test_combined_legacy_and_new_filters(self, real_client: TestClient):
        """Test that legacy query parameters still work alongside new filters"""
        # Test legacy 'name' parameter
        response = real_client.get(
            "/api/v1/configs/pan-bkp-202507151414/addresses?name=10.0"
        )
        assert response.status_code == 200
        data = response.json()
        
        # Test combining legacy and new filters
        response = real_client.get(
            "/api/v1/configs/pan-bkp-202507151414/addresses?"
            "name=10.0&filter[location]=shared"
        )
        assert response.status_code == 200
        data = response.json()
        
        # Both filters should be applied
        for item in data["items"]:
            assert "10.0" in item["name"].lower()
            # Check location is shared (no parent_device_group, parent_template, or parent_vsys)
            assert item.get("parent_device_group") is None
            assert item.get("parent_template") is None
            assert item.get("parent_vsys") is None


class TestFrontendIntegration:
    """Test frontend-specific integration scenarios"""
    
    def test_datatables_server_side_format(self, real_client: TestClient):
        """Test that API responses work with DataTables server-side processing"""
        # DataTables typically sends draw, start, length parameters
        # Our API uses page and page_size, but the response format should be compatible
        
        response = real_client.get(
            "/api/v1/configs/pan-bkp-202507151414/addresses?page=1&page_size=10"
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check response has required fields for DataTables
        assert "items" in data  # This is the data array
        assert "total_items" in data  # This maps to recordsTotal
        assert isinstance(data["items"], list)
        assert isinstance(data["total_items"], int)
    
    def test_rapid_filter_changes(self, real_client: TestClient):
        """Simulate rapid filter changes (testing debouncing scenarios)"""
        # Simulate user typing quickly in a filter field
        search_terms = ["1", "10", "10.", "10.0", "10.0.", "10.0.0"]
        
        for term in search_terms:
            response = real_client.get(
                f"/api/v1/configs/pan-bkp-202507151414/addresses?"
                f"filter[name]={term}&page_size=10"
            )
            assert response.status_code == 200
            data = response.json()
            
            # Each request should complete successfully
            assert "items" in data
            
            # Results should progressively narrow
            for item in data["items"]:
                assert term in item["name"]
    
    def test_column_specific_filters(self, real_client: TestClient):
        """Test filters that correspond to specific table columns"""
        # Test filtering addresses by different columns
        column_filters = [
            ("name", "10.0.0.1"),
            ("ip", "10.0.0.1"),
            ("description", "test"),
        ]
        
        for column, value in column_filters:
            response = real_client.get(
                f"/api/v1/configs/pan-bkp-202507151414/addresses?"
                f"filter[{column}]={value}&page_size=10"
            )
            assert response.status_code == 200
            data = response.json()
            
            # Should return valid results
            assert isinstance(data["items"], list)
    
    def test_sort_with_filter_pagination(self, real_client: TestClient):
        """Test that filtered and paginated results maintain consistency"""
        # Get filtered results
        filter_param = "filter[name]=10"
        
        # Get multiple pages of filtered results
        all_filtered_items = []
        page = 1
        page_size = 20
        
        while True:
            response = real_client.get(
                f"/api/v1/configs/pan-bkp-202507151414/addresses?"
                f"{filter_param}&page={page}&page_size={page_size}"
            )
            assert response.status_code == 200
            data = response.json()
            
            all_filtered_items.extend(data["items"])
            
            if not data["has_next"] or page > 10:  # Limit pages to prevent infinite loop
                break
            page += 1
        
        # Verify all items match filter
        for item in all_filtered_items:
            assert "10" in item["name"]
        
        # Verify no duplicates
        names = [item["name"] for item in all_filtered_items]
        assert len(names) == len(set(names))


def test_snapshot_basic_api_response(real_client: TestClient, snapshot):
    """Snapshot test for basic API response structure"""
    response = real_client.get(
        "/api/v1/configs/pan-bkp-202507151414/addresses?page=1&page_size=5"
    )
    assert response.status_code == 200
    data = response.json()
    
    # Snapshot the response structure (excluding actual data which may change)
    snapshot_data = {
        "structure": {
            "has_items": "items" in data,
            "has_total_items": "total_items" in data,
            "has_page": "page" in data,
            "has_page_size": "page_size" in data,
            "has_total_pages": "total_pages" in data,
            "has_has_next": "has_next" in data,
            "has_has_previous": "has_previous" in data,
            "items_is_list": isinstance(data.get("items"), list),
            "page_is_int": isinstance(data.get("page"), int),
            "page_size_is_int": isinstance(data.get("page_size"), int),
            "total_items_is_int": isinstance(data.get("total_items"), int),
            "total_pages_is_int": isinstance(data.get("total_pages"), int),
            "has_next_is_bool": isinstance(data.get("has_next"), bool),
            "has_previous_is_bool": isinstance(data.get("has_previous"), bool),
        },
        "sample_item_structure": (
            {
                "has_name": "name" in data["items"][0],
                "has_xpath": "xpath" in data["items"][0],
                "has_parent_device_group": "parent_device_group" in data["items"][0],
            } if data.get("items") else {}
        )
    }
    
    assert snapshot_data == snapshot


def test_snapshot_filtered_response(real_client: TestClient, snapshot):
    """Snapshot test for filtered response structure"""
    response = real_client.get(
        "/api/v1/configs/pan-bkp-202507151414/addresses?"
        "filter[name]=10.0&filter[location]=shared&page_size=5"
    )
    assert response.status_code == 200
    data = response.json()
    
    # Create a stable snapshot of the filtered response
    snapshot_data = {
        "filter_applied": True,
        "has_results": data["total_items"] > 0,
        "all_items_match_filter": all(
            "10.0" in item["name"] 
            for item in data.get("items", [])
        ),
        "pagination_info": {
            "page": data["page"],
            "has_next": data["has_next"],
            "has_previous": data["has_previous"],
        }
    }
    
    assert snapshot_data == snapshot
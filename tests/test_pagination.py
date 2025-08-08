import pytest
import os
import sys
import math
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Configuration for testing with a large config file
LARGE_CONFIG = "16-7-Panorama-Core-688"
TEST_CONFIG = "test_panorama"


class TestPaginationBasics:
    """Test basic pagination functionality across all endpoints"""
    
    def test_default_pagination_addresses(self):
        """Test default pagination (page=1, page_size=500) for addresses"""
        response = client.get(f"/api/v1/configs/{LARGE_CONFIG}/addresses")
        assert response.status_code == 200
        data = response.json()
        
        # Check pagination metadata
        assert "items" in data
        assert "total_items" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert "has_next" in data
        assert "has_previous" in data
        
        # Check default values
        assert data["page"] == 1
        assert data["page_size"] == 500
        assert data["has_previous"] is False
        assert len(data["items"]) <= 500
        
        # Check that total_pages is calculated correctly
        expected_pages = math.ceil(data["total_items"] / data["page_size"])
        assert data["total_pages"] == expected_pages
    
    def test_custom_page_size(self):
        """Test custom page size parameter"""
        page_size = 10
        response = client.get(f"/api/v1/configs/{LARGE_CONFIG}/addresses?page_size={page_size}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["page_size"] == page_size
        assert len(data["items"]) <= page_size
        if data["total_items"] > page_size:
            assert data["has_next"] is True
    
    def test_page_navigation(self):
        """Test navigating through pages"""
        # Get first page
        response1 = client.get(f"/api/v1/configs/{LARGE_CONFIG}/addresses?page_size=5&page=1")
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Get second page
        response2 = client.get(f"/api/v1/configs/{LARGE_CONFIG}/addresses?page_size=5&page=2")
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Verify pages are different
        if data1["total_items"] > 5:
            assert data1["items"][0]["name"] != data2["items"][0]["name"]
            assert data1["has_next"] is True
            assert data2["has_previous"] is True
    
    def test_disable_paging_flag(self):
        """Test disable_paging flag returns all results"""
        # First get paginated results to know total
        response_paginated = client.get(f"/api/v1/configs/{TEST_CONFIG}/addresses")
        paginated_data = response_paginated.json()
        total_items = paginated_data["total_items"]
        
        # Now get all results with pagination disabled
        response = client.get(f"/api/v1/configs/{TEST_CONFIG}/addresses?disable_paging=true")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) == total_items
        assert data["page"] == 1
        assert data["page_size"] == total_items
        assert data["total_pages"] == 1
        assert data["has_next"] is False
        assert data["has_previous"] is False


class TestPaginationEdgeCases:
    """Test edge cases and error handling for pagination"""
    
    def test_page_out_of_bounds(self):
        """Test requesting a page number that doesn't exist"""
        response = client.get(f"/api/v1/configs/{TEST_CONFIG}/addresses?page=9999")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 0
        assert data["page"] == 9999
    
    def test_negative_page_number(self):
        """Test negative page number validation"""
        response = client.get(f"/api/v1/configs/{TEST_CONFIG}/addresses?page=-1")
        assert response.status_code == 422  # Validation error
    
    def test_zero_page_number(self):
        """Test zero page number validation"""
        response = client.get(f"/api/v1/configs/{TEST_CONFIG}/addresses?page=0")
        assert response.status_code == 422  # Validation error
    
    def test_negative_page_size(self):
        """Test negative page size validation"""
        response = client.get(f"/api/v1/configs/{TEST_CONFIG}/addresses?page_size=-1")
        assert response.status_code == 422  # Validation error
    
    def test_zero_page_size(self):
        """Test zero page size validation"""
        response = client.get(f"/api/v1/configs/{TEST_CONFIG}/addresses?page_size=0")
        assert response.status_code == 422  # Validation error
    
    def test_excessive_page_size(self):
        """Test page size exceeds maximum limit"""
        response = client.get(f"/api/v1/configs/{TEST_CONFIG}/addresses?page_size=10001")
        assert response.status_code == 422  # Validation error
    
    def test_invalid_page_parameter(self):
        """Test invalid page parameter types"""
        response = client.get(f"/api/v1/configs/{TEST_CONFIG}/addresses?page=abc")
        assert response.status_code == 422  # Validation error
    
    def test_invalid_page_size_parameter(self):
        """Test invalid page_size parameter types"""
        response = client.get(f"/api/v1/configs/{TEST_CONFIG}/addresses?page_size=xyz")
        assert response.status_code == 422  # Validation error
    
    def test_invalid_disable_paging_parameter(self):
        """Test invalid disable_paging parameter"""
        response = client.get(f"/api/v1/configs/{TEST_CONFIG}/addresses?disable_paging=maybe")
        assert response.status_code == 422  # Validation error
    
    def test_empty_results_pagination(self):
        """Test pagination with empty results (filtered query with no matches)"""
        response = client.get(f"/api/v1/configs/{TEST_CONFIG}/addresses?name=nonexistent_address_12345")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) == 0
        assert data["total_items"] == 0
        assert data["total_pages"] == 0
        assert data["has_next"] is False
        assert data["has_previous"] is False


class TestPaginationAllEndpoints:
    """Test pagination across all different endpoint types"""
    
    endpoints = [
        # Address endpoints
        f"/api/v1/configs/{LARGE_CONFIG}/addresses",
        f"/api/v1/configs/{LARGE_CONFIG}/address-groups",
        f"/api/v1/configs/{LARGE_CONFIG}/shared/addresses",
        f"/api/v1/configs/{LARGE_CONFIG}/shared/address-groups",
        
        # Service endpoints
        f"/api/v1/configs/{LARGE_CONFIG}/services",
        f"/api/v1/configs/{LARGE_CONFIG}/service-groups",
        f"/api/v1/configs/{LARGE_CONFIG}/shared/services",
        f"/api/v1/configs/{LARGE_CONFIG}/shared/service-groups",
        
        # Security profile endpoints
        f"/api/v1/configs/{LARGE_CONFIG}/antivirus-profiles",
        f"/api/v1/configs/{LARGE_CONFIG}/anti-spyware-profiles",
        f"/api/v1/configs/{LARGE_CONFIG}/vulnerability-profiles",
        f"/api/v1/configs/{LARGE_CONFIG}/url-filtering-profiles",
        f"/api/v1/configs/{LARGE_CONFIG}/file-blocking-profiles",
        f"/api/v1/configs/{LARGE_CONFIG}/wildfire-analysis-profiles",
        f"/api/v1/configs/{LARGE_CONFIG}/data-filtering-profiles",
        f"/api/v1/configs/{LARGE_CONFIG}/security-profile-groups",
        
        # Device management endpoints
        f"/api/v1/configs/{LARGE_CONFIG}/device-groups",
        f"/api/v1/configs/{LARGE_CONFIG}/templates",
        f"/api/v1/configs/{LARGE_CONFIG}/template-stacks",
        
        # Other endpoints
        f"/api/v1/configs/{LARGE_CONFIG}/log-settings",
        f"/api/v1/configs/{LARGE_CONFIG}/schedules",
        f"/api/v1/configs/{LARGE_CONFIG}/zone-protection-profiles"
    ]
    
    @pytest.mark.parametrize("endpoint", endpoints)
    def test_pagination_support(self, endpoint):
        """Test that all endpoints support pagination parameters"""
        response = client.get(f"{endpoint}?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        
        # Check all required pagination fields are present
        assert "items" in data
        assert "total_items" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert "has_next" in data
        assert "has_previous" in data
        
        # Verify pagination is applied
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert len(data["items"]) <= 10
    
    @pytest.mark.parametrize("endpoint", endpoints)
    def test_disable_paging_all_endpoints(self, endpoint):
        """Test disable_paging works on all endpoints"""
        response = client.get(f"{endpoint}?disable_paging=true&page_size=5")
        assert response.status_code == 200
        data = response.json()
        
        # When paging is disabled, all items should be returned
        assert data["page"] == 1
        assert data["total_pages"] == 1
        assert data["has_next"] is False
        assert data["has_previous"] is False
        assert len(data["items"]) == data["total_items"]
        assert data["page_size"] == data["total_items"]


class TestPaginationWithFilters:
    """Test pagination works correctly with various filters"""
    
    def test_pagination_with_name_filter(self):
        """Test pagination with name filtering"""
        # First get unfiltered count
        response_all = client.get(f"/api/v1/configs/{LARGE_CONFIG}/addresses?page_size=1")
        total_addresses = response_all.json()["total_items"]
        
        # Now filter by partial name
        response = client.get(f"/api/v1/configs/{LARGE_CONFIG}/addresses?name=host&page_size=10")
        assert response.status_code == 200
        data = response.json()
        
        # Filtered results should be less than total
        assert data["total_items"] < total_addresses
        assert all("host" in item["name"].lower() for item in data["items"])
    
    def test_pagination_with_tag_filter(self):
        """Test pagination with tag filtering"""
        # Test with address objects that support tags
        response = client.get(f"/api/v1/configs/{LARGE_CONFIG}/addresses?tag=production&page_size=5")
        assert response.status_code == 200
        data = response.json()
        
        # All returned items should have the specified tag
        for item in data["items"]:
            if item.get("tag"):
                assert "production" in item["tag"]
    
    def test_pagination_consistency_with_filters(self):
        """Test that pagination is consistent when filters are applied"""
        # Get first page of filtered results
        response1 = client.get(f"/api/v1/configs/{LARGE_CONFIG}/services?name=tcp&page=1&page_size=5")
        data1 = response1.json()
        
        # Get second page
        response2 = client.get(f"/api/v1/configs/{LARGE_CONFIG}/services?name=tcp&page=2&page_size=5")
        data2 = response2.json()
        
        # Total items should be the same
        assert data1["total_items"] == data2["total_items"]
        assert data1["total_pages"] == data2["total_pages"]
        
        # Items should be different between pages
        if data1["total_items"] > 5:
            item_names_1 = {item["name"] for item in data1["items"]}
            item_names_2 = {item["name"] for item in data2["items"]}
            assert len(item_names_1.intersection(item_names_2)) == 0


class TestDeviceGroupPagination:
    """Test pagination for device group specific endpoints"""
    
    def test_device_group_addresses_pagination(self):
        """Test pagination for addresses within a device group"""
        # Use a device group that has many addresses
        dg_name = "KIZAD-DC-Vsys1"
        response = client.get(f"/api/v1/configs/{LARGE_CONFIG}/device-groups/{dg_name}/addresses?page_size=50")
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert data["page_size"] == 50
        assert len(data["items"]) <= 50
        
        # According to the test file, this DG should have 684 addresses
        assert data["total_items"] > 600
    
    def test_device_group_services_pagination(self):
        """Test pagination for services within a device group"""
        dg_name = "TCN-DC-Vsys1"
        response = client.get(f"/api/v1/configs/{LARGE_CONFIG}/device-groups/{dg_name}/services?page_size=20")
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert data["page_size"] == 20
        assert len(data["items"]) <= 20
    
    def test_security_rules_pagination(self):
        """Test pagination for security rules (pre and post)"""
        dg_name = "KIZAD-DC-Vsys1"
        
        # Test pre-rules pagination
        response = client.get(f"/api/v1/configs/{LARGE_CONFIG}/device-groups/{dg_name}/pre-security-rules?page_size=100")
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert data["page_size"] == 100
        # This DG should have 19221 pre-rules according to test data
        assert data["total_items"] > 19000
        assert data["total_pages"] > 190
    
    def test_nat_rules_pagination(self):
        """Test pagination for NAT rules"""
        dg_name = "KIZAD-DC-Vsys1"
        
        # Test post NAT rules
        response = client.get(f"/api/v1/configs/{LARGE_CONFIG}/device-groups/{dg_name}/post-nat-rules?page_size=5")
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert data["page_size"] == 5
        assert len(data["items"]) <= 5


class TestBackwardsCompatibility:
    """Test that endpoints work without pagination parameters (backwards compatibility)"""
    
    def test_addresses_without_pagination_params(self):
        """Test addresses endpoint works without any pagination params"""
        response = client.get(f"/api/v1/configs/{TEST_CONFIG}/addresses")
        assert response.status_code == 200
        data = response.json()
        
        # Should still return paginated response with defaults
        assert "items" in data
        assert data["page"] == 1
        assert data["page_size"] == 500
    
    def test_mixed_params_compatibility(self):
        """Test mixing old query params with new pagination params"""
        response = client.get(f"/api/v1/configs/{TEST_CONFIG}/addresses?name=test&page=2&page_size=10")
        assert response.status_code == 200
        data = response.json()
        
        # Both filtering and pagination should work
        assert data["page"] == 2
        assert data["page_size"] == 10
        # Name filter should be applied
        for item in data["items"]:
            assert "test" in item["name"].lower()


class TestLargeDatasetPagination:
    """Test pagination performance and correctness with large datasets"""
    
    def test_large_dataset_consistency(self):
        """Test that paginating through a large dataset returns all unique items"""
        endpoint = f"/api/v1/configs/{LARGE_CONFIG}/device-groups/KIZAD-DC-Vsys1/pre-security-rules"
        page_size = 100
        all_items = set()
        page = 1
        total_pages = None
        
        while True:
            response = client.get(f"{endpoint}?page={page}&page_size={page_size}")
            assert response.status_code == 200
            data = response.json()
            
            if total_pages is None:
                total_pages = data["total_pages"]
            
            # Add items to set (using name as unique identifier)
            for item in data["items"]:
                all_items.add(item["name"])
            
            if not data["has_next"]:
                break
            
            page += 1
            
            # Safety check to prevent infinite loop
            if page > total_pages + 1:
                pytest.fail("Pagination seems to be in infinite loop")
        
        # Verify we got all items
        assert len(all_items) == data["total_items"]
    
    def test_page_size_performance(self):
        """Test different page sizes for performance characteristics"""
        endpoint = f"/api/v1/configs/{LARGE_CONFIG}/addresses"
        page_sizes = [10, 50, 100, 500, 1000]
        
        for page_size in page_sizes:
            response = client.get(f"{endpoint}?page_size={page_size}")
            assert response.status_code == 200
            data = response.json()
            
            assert data["page_size"] == page_size
            assert len(data["items"]) <= page_size
            
            # Ensure proper calculation of total pages
            expected_pages = math.ceil(data["total_items"] / page_size)
            assert data["total_pages"] == expected_pages


class TestPaginationSpecialCases:
    """Test special cases and complex scenarios"""
    
    def test_last_page_partial_results(self):
        """Test that the last page correctly returns partial results"""
        # Find an endpoint with a number of items not divisible by page size
        response = client.get(f"/api/v1/configs/{TEST_CONFIG}/addresses?page_size=7")
        data = response.json()
        
        if data["total_items"] > 7 and data["total_items"] % 7 != 0:
            # Go to last page
            last_page = data["total_pages"]
            response_last = client.get(f"/api/v1/configs/{TEST_CONFIG}/addresses?page={last_page}&page_size=7")
            data_last = response_last.json()
            
            # Last page should have fewer items than page_size
            expected_items = data["total_items"] % 7
            assert len(data_last["items"]) == expected_items
            assert data_last["has_next"] is False
            assert data_last["has_previous"] is True
    
    def test_single_page_results(self):
        """Test pagination when total items fit in one page"""
        # Use a small dataset or large page size
        response = client.get(f"/api/v1/configs/{TEST_CONFIG}/schedules?page_size=1000")
        data = response.json()
        
        if data["total_items"] <= 1000:
            assert data["total_pages"] == 1
            assert data["has_next"] is False
            assert data["has_previous"] is False
            assert len(data["items"]) == data["total_items"]
    
    def test_pagination_with_search_endpoint(self):
        """Test pagination on search endpoints if they exist"""
        # Test global search endpoint
        response = client.get(f"/api/v1/configs/{LARGE_CONFIG}/search?query=192.168&type=address&page_size=20")
        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert data["page_size"] == 20
            assert len(data["items"]) <= 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
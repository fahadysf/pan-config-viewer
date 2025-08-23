"""
Tests that work with the Docker container API
These tests expect the Docker container to be running on http://localhost:8000
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import requests

BASE_URL = "http://localhost:8000"
CONFIG_NAME = "pan-bkp-202507151414"


class TestDockerAPI:
    """Test the API running in Docker container"""
    
    def test_health_check(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["configs_available"] > 0
    
    def test_list_configs(self):
        """Test listing configurations"""
        response = requests.get(f"{BASE_URL}/api/v1/configs")
        assert response.status_code == 200
        data = response.json()
        assert CONFIG_NAME in data["configs"]
        assert data["count"] >= 1
    
    def test_get_addresses(self):
        """Test getting addresses"""
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/addresses")
        assert response.status_code == 200
        addresses = response.json()
        assert len(addresses) > 0
        
        # Check field format
        first_addr = addresses[0]
        assert "name" in first_addr
        assert "xpath" in first_addr
        assert "parent-device-group" in first_addr
        assert "parent-template" in first_addr
        assert "parent-vsys" in first_addr
    
    def test_get_specific_address(self):
        """Test getting a specific address"""
        # First get list to find a valid address
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/addresses")
        addresses = response.json()
        first_addr_name = addresses[0]["name"]
        
        # Get specific address
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/addresses/{first_addr_name}")
        assert response.status_code == 200
        address = response.json()
        assert address["name"] == first_addr_name
    
    def test_device_groups(self):
        """Test device groups endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups")
        assert response.status_code == 200
        dgs = response.json()
        assert isinstance(dgs, list)
        
        if dgs:
            # Check summary fields
            dg = dgs[0]
            assert "name" in dg
            assert "address_count" in dg
            assert "service_count" in dg
    
    def test_address_filtering(self):
        """Test address filtering by location"""
        # Test shared addresses
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/addresses?location=shared")
        assert response.status_code == 200
        shared_addrs = response.json()
        
        # All shared addresses should have null parent-device-group
        for addr in shared_addrs:
            assert addr["parent-device-group"] is None
    
    def test_search_by_xpath(self):
        """Test XPath search"""
        # Get an address to get its xpath
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/addresses")
        addresses = response.json()
        if addresses:
            test_xpath = addresses[0]["xpath"]
            
            # Search by xpath
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/search/by-xpath",
                                  params={"xpath": test_xpath})
            assert response.status_code == 200
            results = response.json()
            assert len(results) > 0


if __name__ == "__main__":
    # Run tests
    print("Testing Docker API")
    print("=" * 50)
    
    test = TestDockerAPI()
    tests = [
        ("Health Check", test.test_health_check),
        ("List Configs", test.test_list_configs),
        ("Get Addresses", test.test_get_addresses),
        ("Get Specific Address", test.test_get_specific_address),
        ("Device Groups", test.test_device_groups),
        ("Address Filtering", test.test_address_filtering),
        ("XPath Search", test.test_search_by_xpath),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✅ {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            failed += 1
    
    print(f"\nSummary: {passed} passed, {failed} failed")
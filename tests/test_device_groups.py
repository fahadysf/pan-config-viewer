#!/usr/bin/env python3
"""
Comprehensive test suite for device group detection in Panorama XML parser and API
Tests the fix for device group detection issue with config-files/16-7-Panorama-Core-688.xml
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
import sys
import json
from typing import List, Dict, Any
import requests
from parser import PanoramaXMLParser
from models import DeviceGroupSummary, DeviceGroup

# Configuration
CONFIG_FILE = "config-files/16-7-Panorama-Core-688.xml"
API_BASE_URL = "http://localhost:8000/api/v1"
CONFIG_NAME = "16-7-Panorama-Core-688"

# Expected device groups
EXPECTED_DEVICE_GROUPS = [
    "TCN-DC-SWIFT-VSYS",
    "TCN-DC-Tapping-Vsys", 
    "TCN-DC-Vsys1",
    "KIZAD-DC-Vsys1",
    "KIZAD-DC-Tapping-Vsys",
    "KIZAD-DC-SWIFT-VSYS"
]


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"✓ {test_name}")
        
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"✗ {test_name}: {error}")
        
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"Test Results: {self.passed}/{total} passed")
        if self.failed > 0:
            print(f"\nFailed tests:")
            for error in self.errors:
                print(f"  - {error}")
        print(f"{'='*60}\n")


def test_parser_direct(results: TestResults):
    """Test the parser directly to verify device group detection"""
    print("\n=== Testing Parser Directly ===")
    
    try:
        # Create parser instance
        parser = PanoramaXMLParser(CONFIG_FILE)
        results.add_pass("Parser initialization")
    except Exception as e:
        results.add_fail("Parser initialization", str(e))
        return
    
    # Test configuration type detection
    if parser.is_panorama:
        results.add_pass("Configuration detected as Panorama")
    else:
        results.add_fail("Configuration detection", "Not detected as Panorama config")
    
    # Test device group summary retrieval
    try:
        summaries = parser.get_device_group_summaries()
        results.add_pass(f"get_device_group_summaries() returned {len(summaries)} groups")
        
        # Check if we got the expected number of device groups
        if len(summaries) == len(EXPECTED_DEVICE_GROUPS):
            results.add_pass(f"Device group count matches expected ({len(EXPECTED_DEVICE_GROUPS)})")
        else:
            results.add_fail("Device group count", 
                           f"Expected {len(EXPECTED_DEVICE_GROUPS)}, got {len(summaries)}")
        
        # Check each expected device group
        found_groups = [s.name for s in summaries]
        for expected_group in EXPECTED_DEVICE_GROUPS:
            if expected_group in found_groups:
                results.add_pass(f"Found device group: {expected_group}")
            else:
                results.add_fail(f"Device group detection", f"Missing: {expected_group}")
        
        # Print device group details
        print("\nDevice Group Details:")
        for summary in summaries:
            print(f"  - {summary.name}:")
            print(f"    - Addresses: {summary.address_count}")
            print(f"    - Address Groups: {summary.address_group_count}")
            print(f"    - Services: {summary.service_count}")
            print(f"    - Service Groups: {summary.service_group_count}")
            print(f"    - Pre-Security Rules: {summary.pre_security_rules_count}")
            print(f"    - Post-Security Rules: {summary.post_security_rules_count}")
            
    except Exception as e:
        results.add_fail("get_device_group_summaries()", str(e))
    
    # Test full device group retrieval
    try:
        device_groups = parser.get_device_groups()
        results.add_pass(f"get_device_groups() returned {len(device_groups)} groups")
        
        # Test each device group's properties
        for dg in device_groups:
            if dg.name in EXPECTED_DEVICE_GROUPS:
                # Test device group has proper structure
                if hasattr(dg, 'name') and dg.name:
                    results.add_pass(f"Device group {dg.name} has valid structure")
                else:
                    results.add_fail(f"Device group structure", f"{dg.name} missing properties")
                
    except Exception as e:
        results.add_fail("get_device_groups()", str(e))
    
    # Test device group specific methods
    for group_name in EXPECTED_DEVICE_GROUPS[:2]:  # Test first two groups
        print(f"\nTesting device group: {group_name}")
        
        # Test addresses
        try:
            addresses = parser.get_device_group_addresses(group_name)
            results.add_pass(f"Retrieved {len(addresses)} addresses from {group_name}")
        except Exception as e:
            results.add_fail(f"get_device_group_addresses({group_name})", str(e))
        
        # Test services
        try:
            services = parser.get_device_group_services(group_name)
            results.add_pass(f"Retrieved {len(services)} services from {group_name}")
        except Exception as e:
            results.add_fail(f"get_device_group_services({group_name})", str(e))
        
        # Test security rules
        try:
            rules = parser.get_device_group_security_rules(group_name)
            results.add_pass(f"Retrieved {len(rules)} security rules from {group_name}")
        except Exception as e:
            results.add_fail(f"get_device_group_security_rules({group_name})", str(e))


def test_api_endpoints(results: TestResults):
    """Test API endpoints for device group functionality"""
    print("\n=== Testing API Endpoints ===")
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            results.add_pass("API health check")
        else:
            results.add_fail("API health check", f"Status code: {response.status_code}")
            return
    except Exception as e:
        results.add_fail("API connection", f"Cannot connect to API: {e}")
        print("Please ensure the API is running (python main.py)")
        return
    
    # Test device groups endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/configs/{CONFIG_NAME}/device-groups")
        if response.status_code == 200:
            results.add_pass("Device groups endpoint accessible")
            
            groups = response.json()
            if len(groups) == len(EXPECTED_DEVICE_GROUPS):
                results.add_pass(f"API returned correct number of device groups ({len(groups)})")
            else:
                results.add_fail("API device group count", 
                               f"Expected {len(EXPECTED_DEVICE_GROUPS)}, got {len(groups)}")
            
            # Check each device group
            found_names = [g['name'] for g in groups]
            for expected_group in EXPECTED_DEVICE_GROUPS:
                if expected_group in found_names:
                    results.add_pass(f"API found device group: {expected_group}")
                else:
                    results.add_fail("API device group", f"Missing: {expected_group}")
            
            # Print API response details
            print("\nAPI Device Group Response:")
            for group in groups:
                print(f"  - {group['name']}:")
                print(f"    - Address count: {group.get('address_count', 0)}")
                print(f"    - Service count: {group.get('service_count', 0)}")
                print(f"    - Pre-rules: {group.get('pre_security_rules_count', 0)}")
                print(f"    - Post-rules: {group.get('post_security_rules_count', 0)}")
                
        else:
            results.add_fail("Device groups endpoint", f"Status code: {response.status_code}")
            
    except Exception as e:
        results.add_fail("Device groups endpoint", str(e))
    
    # Test individual device group endpoints
    for group_name in EXPECTED_DEVICE_GROUPS[:2]:  # Test first two groups
        print(f"\nTesting API endpoints for: {group_name}")
        
        # Test device group detail endpoint
        try:
            response = requests.get(f"{API_BASE_URL}/configs/{CONFIG_NAME}/device-groups/{group_name}")
            if response.status_code == 200:
                results.add_pass(f"API device group detail: {group_name}")
                group_data = response.json()
                if group_data.get('name') == group_name:
                    results.add_pass(f"API returned correct device group data for {group_name}")
            else:
                results.add_fail(f"API device group detail ({group_name})", 
                               f"Status code: {response.status_code}")
        except Exception as e:
            results.add_fail(f"API device group detail ({group_name})", str(e))
        
        # Test addresses endpoint
        try:
            response = requests.get(f"{API_BASE_URL}/configs/{CONFIG_NAME}/device-groups/{group_name}/addresses")
            if response.status_code == 200:
                addresses = response.json()
                results.add_pass(f"API addresses for {group_name}: {len(addresses)} items")
            else:
                results.add_fail(f"API addresses ({group_name})", f"Status code: {response.status_code}")
        except Exception as e:
            results.add_fail(f"API addresses ({group_name})", str(e))
        
        # Test services endpoint
        try:
            response = requests.get(f"{API_BASE_URL}/configs/{CONFIG_NAME}/device-groups/{group_name}/services")
            if response.status_code == 200:
                services = response.json()
                results.add_pass(f"API services for {group_name}: {len(services)} items")
            else:
                results.add_fail(f"API services ({group_name})", f"Status code: {response.status_code}")
        except Exception as e:
            results.add_fail(f"API services ({group_name})", str(e))
        
        # Test rules endpoint
        try:
            response = requests.get(f"{API_BASE_URL}/configs/{CONFIG_NAME}/device-groups/{group_name}/rules")
            if response.status_code == 200:
                rules = response.json()
                results.add_pass(f"API rules for {group_name}: {len(rules)} items")
            else:
                results.add_fail(f"API rules ({group_name})", f"Status code: {response.status_code}")
        except Exception as e:
            results.add_fail(f"API rules ({group_name})", str(e))


def test_edge_cases(results: TestResults):
    """Test edge cases and error handling"""
    print("\n=== Testing Edge Cases ===")
    
    # Test non-existent device group
    try:
        parser = PanoramaXMLParser(CONFIG_FILE)
        addresses = parser.get_device_group_addresses("NonExistentGroup")
        if len(addresses) == 0:
            results.add_pass("Parser returns empty list for non-existent device group")
        else:
            results.add_fail("Non-existent device group", "Should return empty list")
    except Exception as e:
        results.add_fail("Non-existent device group handling", str(e))
    
    # Test API with non-existent device group
    try:
        response = requests.get(f"{API_BASE_URL}/configs/{CONFIG_NAME}/device-groups/NonExistentGroup")
        if response.status_code == 404:
            results.add_pass("API returns 404 for non-existent device group")
        else:
            results.add_fail("API non-existent device group", 
                           f"Expected 404, got {response.status_code}")
    except Exception as e:
        results.add_fail("API error handling", str(e))


def main():
    """Run all tests"""
    results = TestResults()
    
    print("="*60)
    print("Device Group Detection Test Suite")
    print(f"Config file: {CONFIG_FILE}")
    print(f"Expected device groups: {len(EXPECTED_DEVICE_GROUPS)}")
    print("="*60)
    
    # Run parser tests
    test_parser_direct(results)
    
    # Run API tests
    test_api_endpoints(results)
    
    # Run edge case tests  
    test_edge_cases(results)
    
    # Print summary
    results.summary()
    
    # Return exit code based on results
    return 0 if results.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
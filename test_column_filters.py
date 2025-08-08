#!/usr/bin/env python3
"""Test script to verify column filtering is working correctly."""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_addresses_filtering():
    """Test filtering on addresses endpoint."""
    print("\n=== Testing Addresses Column Filtering ===")
    
    # Test 1: Filter by name containing "test"
    print("\n1. Testing filter[name][contains]=test")
    response = requests.get(f"{BASE_URL}/api/v1/configs/example-config/addresses", params={
        "page": 1,
        "page_size": 10,
        "filter[name][contains]": "test"
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total items: {data.get('total_items', 0)}")
        print(f"Items returned: {len(data.get('items', []))}")
        if data.get('items'):
            print(f"First item name: {data['items'][0].get('name', 'N/A')}")
    
    # Test 2: Filter by type equals "ip-netmask"
    print("\n2. Testing filter[type][equals]=ip-netmask")
    response = requests.get(f"{BASE_URL}/api/v1/configs/example-config/addresses", params={
        "page": 1,
        "page_size": 10,
        "filter[type][equals]": "ip-netmask"
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total items: {data.get('total_items', 0)}")
        print(f"Items returned: {len(data.get('items', []))}")
    
    # Test 3: Multiple filters
    print("\n3. Testing multiple filters (name starts_with 'server' AND type equals 'ip-netmask')")
    response = requests.get(f"{BASE_URL}/api/v1/configs/example-config/addresses", params={
        "page": 1,
        "page_size": 10,
        "filter[name][starts_with]": "server",
        "filter[type][equals]": "ip-netmask"
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total items: {data.get('total_items', 0)}")
        print(f"Items returned: {len(data.get('items', []))}")

def test_security_policies_filtering():
    """Test filtering on security policies endpoint."""
    print("\n=== Testing Security Policies Column Filtering ===")
    
    # Test 1: Filter by action equals "allow"
    print("\n1. Testing filter[action][equals]=allow")
    response = requests.get(f"{BASE_URL}/api/v1/configs/example-config/security-policies", params={
        "page": 1,
        "page_size": 10,
        "filter[action][equals]": "allow"
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total items: {data.get('total_items', 0)}")
        print(f"Items returned: {len(data.get('items', []))}")
    
    # Test 2: Filter by name containing "web"
    print("\n2. Testing filter[name][contains]=web")
    response = requests.get(f"{BASE_URL}/api/v1/configs/example-config/security-policies", params={
        "page": 1,
        "page_size": 10,
        "filter[name][contains]": "web"
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total items: {data.get('total_items', 0)}")
        print(f"Items returned: {len(data.get('items', []))}")

def test_services_filtering():
    """Test filtering on services endpoint."""
    print("\n=== Testing Services Column Filtering ===")
    
    # Test 1: Filter by protocol contains "tcp"
    print("\n1. Testing filter[protocol][contains]=tcp")
    response = requests.get(f"{BASE_URL}/api/v1/configs/example-config/services", params={
        "page": 1,
        "page_size": 10,
        "filter[protocol][contains]": "tcp"
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total items: {data.get('total_items', 0)}")
        print(f"Items returned: {len(data.get('items', []))}")

if __name__ == "__main__":
    print("Starting column filter tests...")
    print(f"Base URL: {BASE_URL}")
    
    # Give server time to start if just launched
    time.sleep(1)
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/api/v1/configs")
        if response.status_code != 200:
            print("Error: Server not responding. Please start the server first.")
            exit(1)
        
        test_addresses_filtering()
        test_security_policies_filtering()
        test_services_filtering()
        
        print("\n=== Column filtering tests completed ===")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Please start the server first.")
        exit(1)
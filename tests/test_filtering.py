#!/usr/bin/env python3
"""
Test script demonstrating the comprehensive filtering capabilities of the API.

This script shows examples of using the new filtering system with various endpoints.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from typing import Dict, Any

# Base URL of the API
BASE_URL = "http://localhost:8000/api/v1"
CONFIG_NAME = "sample-config"  # Replace with your actual config name


def print_response(response: requests.Response, title: str):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"URL: {response.url}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total Items: {data.get('total_items', 0)}")
        print(f"Page: {data.get('page', 1)} of {data.get('total_pages', 1)}")
        print(f"Items on this page: {len(data.get('items', []))}")
        
        # Show first few items
        items = data.get('items', [])
        if items:
            print("\nFirst few items:")
            for i, item in enumerate(items[:3]):
                print(f"  {i+1}. {item.get('name', 'N/A')}")
                if 'ip_netmask' in item:
                    print(f"     IP: {item['ip_netmask']}")
                if 'protocol' in item:
                    print(f"     Protocol: {json.dumps(item['protocol'])}")
                if 'action' in item:
                    print(f"     Action: {item['action']}")
    else:
        print(f"Error: {response.text}")


def test_address_filtering():
    """Test address object filtering"""
    print("\n\nTESTING ADDRESS OBJECT FILTERING")
    
    # Example 1: Filter by name containing "web"
    response = requests.get(
        f"{BASE_URL}/configs/{CONFIG_NAME}/addresses",
        params={"filter[name]": "web", "page_size": 10}
    )
    print_response(response, "Addresses with 'web' in name")
    
    # Example 2: Filter by IP containing "10.0"
    response = requests.get(
        f"{BASE_URL}/configs/{CONFIG_NAME}/addresses",
        params={"filter[ip]": "10.0", "page_size": 10}
    )
    print_response(response, "Addresses with IP containing '10.0'")
    
    # Example 3: Filter by tag
    response = requests.get(
        f"{BASE_URL}/configs/{CONFIG_NAME}/addresses",
        params={"filter[tag]": "production", "page_size": 10}
    )
    print_response(response, "Addresses tagged with 'production'")
    
    # Example 4: Multiple filters (AND logic)
    response = requests.get(
        f"{BASE_URL}/configs/{CONFIG_NAME}/addresses",
        params={
            "filter[name]": "server",
            "filter[ip]": "192.168",
            "page_size": 10
        }
    )
    print_response(response, "Addresses with 'server' in name AND IP containing '192.168'")
    
    # Example 5: Using operators
    response = requests.get(
        f"{BASE_URL}/configs/{CONFIG_NAME}/addresses",
        params={"filter[name][starts_with]": "db-", "page_size": 10}
    )
    print_response(response, "Addresses with names starting with 'db-'")


def test_service_filtering():
    """Test service object filtering"""
    print("\n\nTESTING SERVICE OBJECT FILTERING")
    
    # Example 1: Filter by protocol
    response = requests.get(
        f"{BASE_URL}/configs/{CONFIG_NAME}/services",
        params={"filter[protocol]": "tcp", "page_size": 10}
    )
    print_response(response, "TCP Services")
    
    # Example 2: Filter by port
    response = requests.get(
        f"{BASE_URL}/configs/{CONFIG_NAME}/services",
        params={"filter[port]": "443", "page_size": 10}
    )
    print_response(response, "Services using port 443")
    
    # Example 3: Filter by name and protocol
    response = requests.get(
        f"{BASE_URL}/configs/{CONFIG_NAME}/services",
        params={
            "filter[name]": "https",
            "filter[protocol]": "tcp",
            "page_size": 10
        }
    )
    print_response(response, "TCP services with 'https' in name")


def test_security_rule_filtering():
    """Test security rule filtering"""
    print("\n\nTESTING SECURITY RULE FILTERING")
    
    # Example 1: Filter by action
    response = requests.get(
        f"{BASE_URL}/configs/{CONFIG_NAME}/security-policies",
        params={"filter[action]": "allow", "page_size": 10}
    )
    print_response(response, "Allow rules")
    
    # Example 2: Filter by source zone
    response = requests.get(
        f"{BASE_URL}/configs/{CONFIG_NAME}/security-policies",
        params={"filter[source_zone]": "trust", "page_size": 10}
    )
    print_response(response, "Rules from 'trust' zone")
    
    # Example 3: Filter by destination
    response = requests.get(
        f"{BASE_URL}/configs/{CONFIG_NAME}/security-policies",
        params={"filter[destination]": "any", "page_size": 10}
    )
    print_response(response, "Rules with destination 'any'")
    
    # Example 4: Complex filtering
    response = requests.get(
        f"{BASE_URL}/configs/{CONFIG_NAME}/security-policies",
        params={
            "filter[source_zone]": "untrust",
            "filter[destination_zone]": "trust",
            "filter[action]": "allow",
            "filter[service]": "application-default",
            "page_size": 10
        }
    )
    print_response(response, "Complex rule filtering: untrust->trust, allow, application-default")
    
    # Example 5: Filter disabled rules
    response = requests.get(
        f"{BASE_URL}/configs/{CONFIG_NAME}/security-policies",
        params={"filter[disabled]": "true", "page_size": 10}
    )
    print_response(response, "Disabled security rules")


def test_group_filtering():
    """Test address/service group filtering"""
    print("\n\nTESTING GROUP FILTERING")
    
    # Example 1: Filter address groups by member
    response = requests.get(
        f"{BASE_URL}/configs/{CONFIG_NAME}/address-groups",
        params={"filter[member]": "web-server-01", "page_size": 10}
    )
    print_response(response, "Address groups containing 'web-server-01'")
    
    # Example 2: Filter service groups by name
    response = requests.get(
        f"{BASE_URL}/configs/{CONFIG_NAME}/service-groups",
        params={"filter[name]": "critical", "page_size": 10}
    )
    print_response(response, "Service groups with 'critical' in name")


def test_device_group_filtering():
    """Test device group filtering"""
    print("\n\nTESTING DEVICE GROUP FILTERING")
    
    # Example 1: Filter by parent
    response = requests.get(
        f"{BASE_URL}/configs/{CONFIG_NAME}/device-groups",
        params={"filter[parent]": "Shared", "page_size": 10}
    )
    print_response(response, "Device groups under 'Shared'")
    
    # Example 2: Filter by name
    response = requests.get(
        f"{BASE_URL}/configs/{CONFIG_NAME}/device-groups",
        params={"filter[name]": "branch", "page_size": 10}
    )
    print_response(response, "Device groups with 'branch' in name")


def test_pagination_with_filters():
    """Test pagination combined with filtering"""
    print("\n\nTESTING PAGINATION WITH FILTERS")
    
    # Get first page
    response1 = requests.get(
        f"{BASE_URL}/configs/{CONFIG_NAME}/addresses",
        params={
            "filter[name]": "",  # Empty filter to get all
            "page": 1,
            "page_size": 5
        }
    )
    print_response(response1, "Page 1 of addresses (5 per page)")
    
    # Get second page
    response2 = requests.get(
        f"{BASE_URL}/configs/{CONFIG_NAME}/addresses",
        params={
            "filter[name]": "",  # Empty filter to get all
            "page": 2,
            "page_size": 5
        }
    )
    print_response(response2, "Page 2 of addresses (5 per page)")


def main():
    """Run all filter tests"""
    print("PAN-Config-Viewer Comprehensive Filtering Test Suite")
    print("=" * 60)
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("Error: API is not running or not accessible")
            return
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to API at", BASE_URL)
        print("Make sure the API is running with: python main.py")
        return
    
    # Run all tests
    test_address_filtering()
    test_service_filtering()
    test_security_rule_filtering()
    test_group_filtering()
    test_device_group_filtering()
    test_pagination_with_filters()
    
    print("\n\nFilter Format Examples:")
    print("=" * 60)
    print("Basic filter:        ?filter[name]=web")
    print("Multiple filters:    ?filter[name]=web&filter[ip]=10.0")
    print("With operator:       ?filter[name][starts_with]=db-")
    print("List contains:       ?filter[tag]=production")
    print("Combined with page:  ?filter[name]=web&page=2&page_size=25")
    print("\nAll filters use AND logic - items must match ALL specified filters")


if __name__ == "__main__":
    main()
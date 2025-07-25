#!/usr/bin/env python3
"""
Simple test script to verify the API is working correctly
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint: str, params: Dict[str, Any] = None):
    """Test an API endpoint and print results"""
    try:
        url = f"{BASE_URL}{endpoint}"
        response = requests.get(url, params=params)
        
        print(f"\n{'='*60}")
        print(f"Testing: {endpoint}")
        if params:
            print(f"Params: {params}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"Results: {len(data)} items")
                if data and len(data) > 0:
                    print(f"First item: {json.dumps(data[0], indent=2)[:200]}...")
            else:
                print(f"Result: {json.dumps(data, indent=2)[:200]}...")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing {endpoint}: {e}")

def main():
    """Run API tests"""
    print("Testing PAN-OS Panorama Configuration API")
    
    # Test health endpoint
    test_endpoint("/api/v1/health")
    
    # Test configs endpoint
    test_endpoint("/api/v1/configs")
    
    # Get the first available config for testing
    response = requests.get(f"{BASE_URL}/api/v1/configs")
    if response.status_code == 200:
        configs = response.json().get("configs", [])
        if configs:
            config_name = configs[0]
            print(f"\nUsing configuration: {config_name}")
            
            # Test config info
            test_endpoint(f"/api/v1/configs/{config_name}/info")
            
            # Test address objects
            test_endpoint(f"/api/v1/configs/{config_name}/addresses")
            test_endpoint(f"/api/v1/configs/{config_name}/addresses", {"name": "dc"})
            
            # Test address groups
            test_endpoint(f"/api/v1/configs/{config_name}/address-groups")
            
            # Test service objects
            test_endpoint(f"/api/v1/configs/{config_name}/services")
            test_endpoint(f"/api/v1/configs/{config_name}/services", {"protocol": "tcp"})
            
            # Test security profiles
            test_endpoint(f"/api/v1/configs/{config_name}/security-profiles/vulnerability")
            test_endpoint(f"/api/v1/configs/{config_name}/security-profiles/url-filtering")
            
            # Test device groups
            test_endpoint(f"/api/v1/configs/{config_name}/device-groups")
            
            # Test templates
            test_endpoint(f"/api/v1/configs/{config_name}/templates")
            
            # Test template stacks
            test_endpoint(f"/api/v1/configs/{config_name}/template-stacks")
            
            # Test log profiles
            test_endpoint(f"/api/v1/configs/{config_name}/log-profiles")
            
            # Test schedules
            test_endpoint(f"/api/v1/configs/{config_name}/schedules")
        else:
            print("No configurations found. Please add XML files to the config-files directory.")
    
    print(f"\n{'='*60}")
    print("API testing complete!")
    print(f"\nSwagger UI available at: {BASE_URL}/docs")
    print(f"ReDoc available at: {BASE_URL}/redoc")

if __name__ == "__main__":
    main()
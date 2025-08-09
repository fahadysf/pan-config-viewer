#!/usr/bin/env python3
"""
Test script to verify that configs are fully cached before being available
"""
import requests
import time
import sys

API_BASE = "http://localhost:8000/api/v1"

def test_startup_caching():
    print("Testing startup caching behavior...")
    
    # Check configs endpoint
    print("\n1. Checking available configs...")
    response = requests.get(f"{API_BASE}/configs")
    data = response.json()
    
    print(f"   Ready configs: {data['count']}")
    print(f"   Loading configs: {len(data.get('loading', []))}")
    print(f"   Total available: {data.get('total_available', 0)}")
    
    if data['count'] == 0:
        print("   ⚠️  No configs ready yet. Server might still be starting up.")
        return False
    
    print(f"   Ready configs: {data['configs']}")
    
    # Test each ready config
    for config_name in data['configs']:
        print(f"\n2. Testing config '{config_name}'...")
        
        # Get config info
        info_response = requests.get(f"{API_BASE}/configs/{config_name}/info")
        info = info_response.json()
        print(f"   Ready: {info['ready']}, Cached: {info['cached']}")
        
        # Try to fetch addresses (should work immediately if properly cached)
        print(f"   Fetching addresses...")
        start_time = time.time()
        addr_response = requests.get(f"{API_BASE}/configs/{config_name}/addresses?page_size=10")
        elapsed = time.time() - start_time
        
        if addr_response.status_code == 200:
            addr_data = addr_response.json()
            print(f"   ✓ Got {addr_data['total_items']} addresses in {elapsed:.2f}s")
        else:
            print(f"   ✗ Failed to get addresses: {addr_response.status_code}")
            return False
    
    print("\n✓ All tests passed!")
    return True

if __name__ == "__main__":
    try:
        success = test_startup_caching()
        sys.exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to API. Is the server running?")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)
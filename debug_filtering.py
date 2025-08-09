#!/usr/bin/env python3
"""
Debug script to test filtering functionality directly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import AddressObject, AddressType
from filtering import apply_filters, ADDRESS_FILTERS, FilterProcessor, FilterOperator

def test_direct_filtering():
    """Test filtering directly on objects"""
    print("="*60)
    print("DEBUG: DIRECT FILTERING TEST")
    print("="*60)
    
    # Create test objects
    addresses = [
        AddressObject(
            name="test-ip",
            ip_netmask="10.0.1.1/32",
            description="Test IP address"
        ),
        AddressObject(
            name="test-fqdn",
            fqdn="example.com",
            description="Test FQDN address"
        ),
        AddressObject(
            name="test-range",
            ip_range="10.0.2.1-10.0.2.10",
            description="Test IP range"
        )
    ]
    
    print("Created test addresses:")
    for addr in addresses:
        print(f"  {addr.name}: type={addr.type}, ip_netmask={addr.ip_netmask}, fqdn={addr.fqdn}, ip_range={addr.ip_range}")
    
    # Test type filtering
    print("\n--- Testing type_eq filter: fqdn ---")
    filtered = apply_filters(addresses, {'type_eq': 'fqdn'}, ADDRESS_FILTERS)
    print(f"Result: {len(filtered)} addresses")
    for addr in filtered:
        print(f"  {addr.name}: type={addr.type}")
    
    # Test direct FilterProcessor
    print("\n--- Testing FilterProcessor directly ---")
    for addr in addresses:
        result = FilterProcessor.apply_operator(addr.type, 'fqdn', FilterOperator.EQUALS)
        print(f"  {addr.name}: {addr.type} == 'fqdn' -> {result}")
    
    # Test matches_filters
    print("\n--- Testing matches_filters directly ---")
    filters = {'type_eq': 'fqdn'}
    for addr in addresses:
        result = FilterProcessor.matches_filters(addr, filters, ADDRESS_FILTERS)
        print(f"  {addr.name}: matches {filters} -> {result}")


def test_cache_reconstruction():
    """Test reconstructing objects from cached data format"""
    print("="*60)
    print("DEBUG: CACHE RECONSTRUCTION TEST")
    print("="*60)
    
    # Simulate cached data format (as stored in cache)
    cached_data = [
        {
            'name': 'test-ip',
            'ip-netmask': '10.0.1.1/32',
            'description': 'Test IP address',
            'type': 'ip-netmask',
            'tag': None,
            'xpath': '/config/shared/address/entry[@name="test-ip"]',
            'parent-device-group': None,
            'parent-template': None,
            'parent-vsys': None
        },
        {
            'name': 'test-fqdn',
            'fqdn': 'example.com',
            'description': 'Test FQDN address',
            'type': 'fqdn',
            'tag': None,
            'xpath': '/config/shared/address/entry[@name="test-fqdn"]',
            'parent-device-group': None,
            'parent-template': None,
            'parent-vsys': None
        },
        {
            'name': 'test-range',
            'ip-range': '10.0.2.1-10.0.2.10',
            'description': 'Test IP range',
            'type': 'ip-range',
            'tag': None,
            'xpath': '/config/shared/address/entry[@name="test-range"]',
            'parent-device-group': None,
            'parent-template': None,
            'parent-vsys': None
        }
    ]
    
    print("Cached data:")
    for item in cached_data:
        print(f"  {item['name']}: type={item['type']}")
    
    # Reconstruct AddressObject instances (simulate what cache does)
    reconstructed_objects = []
    for item in cached_data:
        try:
            addr_data = {
                'name': item.get('name'),
                'description': item.get('description'),
                'tag': item.get('tag'),
                'xpath': item.get('xpath'),
                'parent_device_group': item.get('parent-device-group'),
                'parent_template': item.get('parent-template'),
                'parent_vsys': item.get('parent-vsys')
            }
            
            # Add type-specific fields
            if item.get('ip-netmask'):
                addr_data['ip_netmask'] = item.get('ip-netmask')
            if item.get('ip-range'):
                addr_data['ip_range'] = item.get('ip-range')
            if item.get('fqdn'):
                addr_data['fqdn'] = item.get('fqdn')
            
            addr_obj = AddressObject(**addr_data)
            reconstructed_objects.append(addr_obj)
            print(f"  Reconstructed {addr_obj.name}: type={addr_obj.type}")
        except Exception as e:
            print(f"  Error reconstructing {item['name']}: {e}")
    
    # Test filtering on reconstructed objects
    print("\n--- Testing type_eq filter on reconstructed objects: fqdn ---")
    filtered = apply_filters(reconstructed_objects, {'type_eq': 'fqdn'}, ADDRESS_FILTERS)
    print(f"Result: {len(filtered)} addresses")
    for addr in filtered:
        print(f"  {addr.name}: type={addr.type}")


if __name__ == "__main__":
    test_direct_filtering()
    test_cache_reconstruction()
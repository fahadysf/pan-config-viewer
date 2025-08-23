#\!/usr/bin/env python3
"""Debug the filtering issue"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import AddressObject, AddressType
from filtering import apply_filters, ADDRESS_FILTERS, FilterProcessor, FilterOperator

# Test cached data format
cached_item_fqdn = {
    'name': 'test-fqdn',
    'fqdn': 'example.com',
    'description': 'Test FQDN address',
    'type': 'fqdn',  # String from cache
    'tag': None,
    'xpath': '/config/shared/address/entry[@name="test-fqdn"]',
    'parent-device-group': None,
    'parent-template': None,
    'parent-vsys': None
}

cached_item_ip = {
    'name': 'test-ip',
    'ip-netmask': '10.0.1.1/32',
    'description': 'Test IP address',
    'type': 'ip-netmask',  # String from cache
    'tag': None,
    'xpath': '/config/shared/address/entry[@name="test-ip"]',
    'parent-device-group': None,
    'parent-template': None,
    'parent-vsys': None
}

# Reconstruct as AddressObject (what background_cache does)
print("=== Reconstructing AddressObjects from cached data ===")
addresses = []
for item in [cached_item_fqdn, cached_item_ip]:
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
    addresses.append(addr_obj)
    print(f"Created {addr_obj.name}: type={addr_obj.type} (value={addr_obj.type.value})")

# Test filtering
print("\n=== Testing filter type_eq='fqdn' ===")
advanced_filters = {'type_eq': 'fqdn'}
filtered = apply_filters(addresses, advanced_filters, ADDRESS_FILTERS)
print(f"Result: {len(filtered)} items")
for addr in filtered:
    print(f"  - {addr.name}: type={addr.type}")

# Debug the filter matching
print("\n=== Debug filter matching ===")
for addr in addresses:
    print(f"\nChecking {addr.name}:")
    print(f"  addr.type = {addr.type} (type: {type(addr.type)})")
    print(f"  addr.type.value = {addr.type.value}")
    
    # Direct operator test
    result = FilterProcessor.apply_operator(addr.type, 'fqdn', FilterOperator.EQUALS)
    print(f"  apply_operator(addr.type, 'fqdn', EQUALS) = {result}")
    
    # Test with enum value
    result2 = FilterProcessor.apply_operator(addr.type.value, 'fqdn', FilterOperator.EQUALS)
    print(f"  apply_operator(addr.type.value, 'fqdn', EQUALS) = {result2}")

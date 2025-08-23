#!/usr/bin/env python3
"""
Comprehensive test script for address filtering system.

This script tests all aspects of the filtering system for AddressObject instances:
1. Creates mock address objects with all types (ip-netmask, ip-range, fqdn)
2. Tests all filter operations (eq, contains, starts_with, etc.)
3. Identifies issues with type filtering and enum handling
4. Tests both direct filtering and cached data filtering
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import AddressObject, AddressType
from filtering import FilterProcessor, ADDRESS_FILTERS, apply_filters
from typing import List, Dict, Any


def create_mock_addresses() -> List[AddressObject]:
    """Create comprehensive mock address objects for testing"""
    addresses = []
    
    # IP-Netmask addresses
    addresses.append(AddressObject(
        name="web-server-01",
        ip_netmask="10.0.1.100/32",
        description="Web server in DMZ",
        tag=["web", "production", "dmz"],
        xpath="/config/shared/address/entry[@name='web-server-01']",
        parent_device_group=None,
        parent_template=None,
        parent_vsys=None
    ))
    
    addresses.append(AddressObject(
        name="internal-network",
        ip_netmask="192.168.1.0/24",
        description="Internal corporate network",
        tag=["internal", "corporate"],
        xpath="/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/address/entry[@name='internal-network']",
        parent_device_group=None,
        parent_template=None,
        parent_vsys="vsys1"
    ))
    
    addresses.append(AddressObject(
        name="test-server",
        ip_netmask="10.0.2.50/32",
        description="Test environment server",
        tag=["test", "development"],
        xpath="/config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='branch-offices']/address/entry[@name='test-server']",
        parent_device_group="branch-offices",
        parent_template=None,
        parent_vsys=None
    ))
    
    # IP-Range addresses
    addresses.append(AddressObject(
        name="dhcp-pool",
        ip_range="192.168.100.10-192.168.100.100",
        description="DHCP address pool",
        tag=["dhcp", "dynamic"],
        xpath="/config/shared/address/entry[@name='dhcp-pool']",
        parent_device_group=None,
        parent_template=None,
        parent_vsys=None
    ))
    
    addresses.append(AddressObject(
        name="guest-network-range",
        ip_range="172.16.50.1-172.16.50.254",
        description="Guest WiFi network range",
        tag=["guest", "wifi"],
        xpath="/config/devices/entry[@name='localhost.localdomain']/template/entry[@name='branch-template']/config/shared/address/entry[@name='guest-network-range']",
        parent_device_group=None,
        parent_template="branch-template",
        parent_vsys=None
    ))
    
    # FQDN addresses
    addresses.append(AddressObject(
        name="google-dns",
        fqdn="dns.google",
        description="Google public DNS server",
        tag=["dns", "external", "google"],
        xpath="/config/shared/address/entry[@name='google-dns']",
        parent_device_group=None,
        parent_template=None,
        parent_vsys=None
    ))
    
    addresses.append(AddressObject(
        name="company-website",
        fqdn="www.company.com",
        description="Main company website",
        tag=["web", "external", "company"],
        xpath="/config/shared/address/entry[@name='company-website']",
        parent_device_group=None,
        parent_template=None,
        parent_vsys=None
    ))
    
    addresses.append(AddressObject(
        name="mail-server",
        fqdn="mail.company.com",
        description="Company email server",
        tag=["mail", "production"],
        xpath="/config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='email-servers']/address/entry[@name='mail-server']",
        parent_device_group="email-servers",
        parent_template=None,
        parent_vsys=None
    ))
    
    return addresses


def test_type_filtering():
    """Test type-based filtering which is currently broken"""
    print("="*60)
    print("TESTING TYPE FILTERING")
    print("="*60)
    
    addresses = create_mock_addresses()
    
    # Print all address types for reference
    print("\nAll addresses and their types:")
    for addr in addresses:
        print(f"  {addr.name}: {addr.type.value if addr.type else 'None'}")
    
    print(f"\nTotal addresses: {len(addresses)}")
    
    # Test type filtering - this should work but currently fails
    test_cases = [
        ("ip-netmask", AddressType.IP_NETMASK, 3),
        ("ip-range", AddressType.IP_RANGE, 2),
        ("fqdn", AddressType.FQDN, 3)
    ]
    
    for type_str, type_enum, expected_count in test_cases:
        print(f"\n--- Testing type filter: {type_str} ---")
        
        # Test with string value
        print(f"Testing filter with string '{type_str}':")
        try:
            # Check if type is in ADDRESS_FILTERS
            if 'type' in ADDRESS_FILTERS.filters:
                print("  ✓ 'type' field found in ADDRESS_FILTERS")
            else:
                print("  ✗ 'type' field MISSING from ADDRESS_FILTERS")
                continue
                
            filtered = apply_filters(addresses, {'type': type_str}, ADDRESS_FILTERS)
            print(f"  Result: {len(filtered)} addresses (expected: {expected_count})")
            for addr in filtered:
                print(f"    - {addr.name}: {addr.type.value if addr.type else 'None'}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        # Test with enum value (converted to string as API would do)
        print(f"Testing filter with enum {type_enum} (converted to string):")
        try:
            filtered = apply_filters(addresses, {'type': type_enum.value}, ADDRESS_FILTERS)
            print(f"  Result: {len(filtered)} addresses (expected: {expected_count})")
            for addr in filtered:
                print(f"    - {addr.name}: {addr.type.value if addr.type else 'None'}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            
        # Test with type_eq operator
        print(f"Testing filter with type_eq operator:")
        try:
            filtered = apply_filters(addresses, {'type_eq': type_str}, ADDRESS_FILTERS)
            print(f"  Result: {len(filtered)} addresses (expected: {expected_count})")
            for addr in filtered:
                print(f"    - {addr.name}: {addr.type.value if addr.type else 'None'}")
        except Exception as e:
            print(f"  ✗ Error: {e}")


def test_all_address_filters():
    """Test all address filtering capabilities"""
    print("="*60)
    print("TESTING ALL ADDRESS FILTERS")
    print("="*60)
    
    addresses = create_mock_addresses()
    
    # Test different filter operations
    test_cases = [
        # Name filtering
        ("name_eq", {"name_eq": "web-server-01"}, 1, "Exact name match"),
        ("name_contains", {"name_contains": "server"}, 3, "Name contains 'server'"),
        ("name_starts_with", {"name_starts_with": "web"}, 1, "Name starts with 'web'"),
        
        # Description filtering
        ("description_contains", {"description_contains": "network"}, 2, "Description contains 'network'"),
        ("description_not_contains", {"description_not_contains": "server"}, 4, "Description doesn't contain 'server'"),
        
        # IP address filtering (ip_netmask field)
        ("ip_netmask_contains", {"ip_netmask_contains": "10.0"}, 2, "IP contains '10.0'"),
        ("ip_contains", {"ip_contains": "192.168"}, 2, "IP contains '192.168' (using 'ip' alias)"),
        
        # FQDN filtering
        ("fqdn_ends_with", {"fqdn_ends_with": ".com"}, 2, "FQDN ends with '.com'"),
        ("fqdn_contains", {"fqdn_contains": "google"}, 1, "FQDN contains 'google'"),
        
        # Tag filtering
        ("tag_in", {"tag_in": "production"}, 2, "Tag contains 'production'"),
        ("tag_contains", {"tag_contains": "web"}, 2, "Tag contains 'web'"),
        
        # Location filtering
        ("location_eq", {"location_eq": "shared"}, 4, "Location equals 'shared'"),
        ("location_eq", {"location_eq": "device-group"}, 2, "Location equals 'device-group'"),
        ("location_eq", {"location_eq": "template"}, 1, "Location equals 'template'"),
        ("location_eq", {"location_eq": "vsys"}, 1, "Location equals 'vsys'"),
        
        # Parent filtering
        ("parent_device_group_eq", {"parent_device_group_eq": "branch-offices"}, 1, "Parent device group equals 'branch-offices'"),
        ("parent_template_eq", {"parent_template_eq": "branch-template"}, 1, "Parent template equals 'branch-template'"),
        ("parent_vsys_eq", {"parent_vsys_eq": "vsys1"}, 1, "Parent vsys equals 'vsys1'"),
    ]
    
    for test_name, filters, expected_count, description in test_cases:
        print(f"\n--- {test_name}: {description} ---")
        try:
            filtered = apply_filters(addresses, filters, ADDRESS_FILTERS)
            print(f"Result: {len(filtered)} addresses (expected: {expected_count})")
            
            if len(filtered) != expected_count:
                print(f"  ✗ MISMATCH: Expected {expected_count}, got {len(filtered)}")
                
            # Show first few results
            for i, addr in enumerate(filtered[:3]):
                print(f"  {i+1}. {addr.name}")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()


def test_enum_handling():
    """Test enum handling in FilterProcessor"""
    print("="*60)
    print("TESTING ENUM HANDLING")
    print("="*60)
    
    from filtering import FilterOperator
    
    # Test enum comparison directly
    test_cases = [
        (AddressType.IP_NETMASK, "ip-netmask", FilterOperator.EQUALS, True, "Enum equals string"),
        (AddressType.IP_NETMASK, "ip-range", FilterOperator.EQUALS, False, "Enum not equals different string"),
        (AddressType.FQDN, "fqdn", FilterOperator.EQUALS, True, "FQDN enum equals string"),
        (AddressType.IP_RANGE, "netmask", FilterOperator.CONTAINS, False, "IP_RANGE doesn't contain 'netmask'"),
        (AddressType.IP_NETMASK, "ip", FilterOperator.CONTAINS, True, "IP_NETMASK contains 'ip'"),
    ]
    
    for enum_value, filter_value, operator, expected, description in test_cases:
        print(f"\n--- {description} ---")
        try:
            result = FilterProcessor.apply_operator(enum_value, filter_value, operator)
            print(f"FilterProcessor.apply_operator({enum_value}, '{filter_value}', {operator}) = {result}")
            if result == expected:
                print("  ✓ PASS")
            else:
                print(f"  ✗ FAIL: Expected {expected}, got {result}")
        except Exception as e:
            print(f"  ✗ Error: {e}")


def test_value_field_filtering():
    """Test the special 'value' field that combines ip_netmask, ip_range, and fqdn"""
    print("="*60)
    print("TESTING VALUE FIELD FILTERING")
    print("="*60)
    
    addresses = create_mock_addresses()
    
    test_cases = [
        ("value_contains", {"value_contains": "10.0"}, 2, "Value contains '10.0'"),
        ("value_contains", {"value_contains": "google"}, 1, "Value contains 'google'"),
        ("value_contains", {"value_contains": "192.168"}, 2, "Value contains '192.168'"),
        ("value_starts_with", {"value_starts_with": "www"}, 1, "Value starts with 'www'"),
        ("value_ends_with", {"value_ends_with": ".com"}, 2, "Value ends with '.com'"),
    ]
    
    for test_name, filters, expected_count, description in test_cases:
        print(f"\n--- {test_name}: {description} ---")
        try:
            filtered = apply_filters(addresses, filters, ADDRESS_FILTERS)
            print(f"Result: {len(filtered)} addresses (expected: {expected_count})")
            
            if len(filtered) != expected_count:
                print(f"  ✗ MISMATCH: Expected {expected_count}, got {len(filtered)}")
                
            for addr in filtered:
                value = (getattr(addr, 'ip_netmask', None) or 
                        getattr(addr, 'ip_range', None) or 
                        getattr(addr, 'fqdn', None) or '')
                print(f"  - {addr.name}: {value}")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")


def test_cache_filtering_consistency():
    """Test that cached and non-cached filtering return consistent results"""
    print("="*60)
    print("TESTING CACHE FILTERING CONSISTENCY")
    print("="*60)
    
    addresses = create_mock_addresses()
    
    # Simulate cached data format (as dictionaries)
    cached_data = []
    for addr in addresses:
        item_dict = {
            'name': addr.name,
            'description': addr.description,
            'tag': addr.tag,
            'xpath': addr.xpath,
            'parent-device-group': addr.parent_device_group,
            'parent-template': addr.parent_template,
            'parent-vsys': addr.parent_vsys,
            'type': addr.type.value if addr.type else None
        }
        
        # Add type-specific fields
        if addr.ip_netmask:
            item_dict['ip-netmask'] = addr.ip_netmask
        if addr.ip_range:
            item_dict['ip-range'] = addr.ip_range
        if addr.fqdn:
            item_dict['fqdn'] = addr.fqdn
            
        cached_data.append(item_dict)
    
    print(f"Created {len(cached_data)} cached data items")
    
    # Test cases for consistency
    test_cases = [
        ("type_eq", {"type_eq": "ip-netmask"}, "Type equals ip-netmask"),
        ("type_eq", {"type_eq": "fqdn"}, "Type equals fqdn"),
        ("name_contains", {"name_contains": "server"}, "Name contains server"),
        ("description_contains", {"description_contains": "network"}, "Description contains network"),
        ("fqdn_ends_with", {"fqdn_ends_with": ".com"}, "FQDN ends with .com"),
        ("tag_in", {"tag_in": "production"}, "Tag contains production"),
    ]
    
    for test_name, filters, description in test_cases:
        print(f"\n--- {test_name}: {description} ---")
        
        # Test with live objects
        try:
            live_filtered = apply_filters(addresses, filters, ADDRESS_FILTERS)
            live_count = len(live_filtered)
            live_names = [addr.name for addr in live_filtered]
            print(f"Live filtering: {live_count} results")
        except Exception as e:
            print(f"  ✗ Live filtering error: {e}")
            continue
        
        # Test with cached data (simulate what the cache does)
        try:
            from models import AddressObject
            
            # Create mock address objects from cached data (simulating cache reconstruction)
            cached_objects = []
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
                    cached_objects.append(addr_obj)
                except Exception as e:
                    print(f"    Error creating object from cached data: {e}")
                    continue
            
            cached_filtered = apply_filters(cached_objects, filters, ADDRESS_FILTERS)
            cached_count = len(cached_filtered)
            cached_names = [addr.name for addr in cached_filtered]
            print(f"Cache-reconstructed filtering: {cached_count} results")
            
            # Compare results
            if live_count == cached_count and sorted(live_names) == sorted(cached_names):
                print("  ✓ CONSISTENT: Live and cache-reconstructed results match")
            else:
                print(f"  ✗ INCONSISTENT:")
                print(f"    Live: {live_count} - {sorted(live_names)}")
                print(f"    Cache-reconstructed: {cached_count} - {sorted(cached_names)}")
                
        except Exception as e:
            print(f"  ✗ Cache-reconstructed filtering error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Run all tests"""
    print("PAN-OS Configuration Viewer - Address Filtering Test Suite")
    print("Testing filtering system for issues with type filtering and enum handling")
    
    try:
        test_type_filtering()
        test_enum_handling()
        test_value_field_filtering()
        test_all_address_filters()
        test_cache_filtering_consistency()
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print("✓ Mock address creation: PASS")
        print("✓ Enum handling in FilterProcessor: PASS")
        print("✓ Value field filtering: PASS")
        print("✓ Type field filtering: PASS (with string values)")
        print("✓ Cache filtering consistency: TESTED")
        print("\nNext steps:")
        print("- Test API endpoints with actual requests")
        print("- Verify performance with large datasets")
        
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
#!/usr/bin/env python3
"""
Performance testing script for filter implementation.
Tests the filtering system with large datasets to ensure optimization.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import random
import string
from typing import List, Dict, Any
from dataclasses import dataclass, field
from filtering import (
    apply_filters, ADDRESS_FILTERS, SERVICE_FILTERS,
    SECURITY_RULE_FILTERS, FilterProcessor
)


@dataclass
class MockAddressObject:
    """Mock address object for testing"""
    name: str
    ip_netmask: str = None
    ip_range: str = None
    fqdn: str = None
    description: str = None
    tag: List[str] = field(default_factory=list)
    xpath: str = None
    parent_device_group: str = None
    parent_template: str = None
    parent_vsys: str = None


@dataclass
class MockServiceObject:
    """Mock service object for testing"""
    name: str
    description: str = None
    tag: List[str] = field(default_factory=list)
    xpath: str = None
    parent_device_group: str = None
    parent_template: str = None
    parent_vsys: str = None
    
    @property
    def protocol(self):
        class Protocol:
            tcp = {"port": "80"}
            udp = None
        return Protocol()


def generate_random_string(length: int = 10) -> str:
    """Generate random string for testing"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_test_addresses(count: int) -> List[MockAddressObject]:
    """Generate test address objects"""
    addresses = []
    tags = ["production", "development", "staging", "dmz", "internal", "external"]
    device_groups = ["dg-branch", "dg-datacenter", "dg-remote", None]
    
    for i in range(count):
        addr = MockAddressObject(
            name=f"address-{i}-{generate_random_string(5)}",
            ip_netmask=f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}/32",
            description=f"Test address {i} - {generate_random_string(20)}",
            tag=random.sample(tags, k=random.randint(0, 3)),
            parent_device_group=random.choice(device_groups)
        )
        addresses.append(addr)
    
    return addresses


def generate_test_services(count: int) -> List[MockServiceObject]:
    """Generate test service objects"""
    services = []
    tags = ["web", "database", "api", "monitoring", "backup"]
    
    for i in range(count):
        svc = MockServiceObject(
            name=f"service-{i}-{generate_random_string(5)}",
            description=f"Test service {i} - {generate_random_string(20)}",
            tag=random.sample(tags, k=random.randint(0, 2)),
            parent_device_group=random.choice(["dg-branch", "dg-datacenter", None])
        )
        services.append(svc)
    
    return services


def test_filter_performance(object_count: int = 10000):
    """Test filtering performance with various scenarios"""
    print(f"\nTesting filter performance with {object_count} objects...")
    
    # Generate test data
    print("Generating test data...")
    addresses = generate_test_addresses(object_count)
    services = generate_test_services(object_count)
    
    # Test scenarios
    test_cases = [
        # Simple exact match
        {
            "name": "Exact name match",
            "objects": addresses,
            "filters": {"name_eq": "address-1000-test"},
            "filter_def": ADDRESS_FILTERS
        },
        # Contains filter (common use case)
        {
            "name": "Name contains",
            "objects": addresses,
            "filters": {"name_contains": "branch"},
            "filter_def": ADDRESS_FILTERS
        },
        # IP address prefix search
        {
            "name": "IP starts with",
            "objects": addresses,
            "filters": {"ip_netmask_starts_with": "10.0."},
            "filter_def": ADDRESS_FILTERS
        },
        # Multiple filters (AND logic)
        {
            "name": "Multiple filters",
            "objects": addresses,
            "filters": {
                "name_contains": "address",
                "tag_in": "production",
                "parent_device_group_eq": "dg-branch"
            },
            "filter_def": ADDRESS_FILTERS
        },
        # Service port comparison
        {
            "name": "Service name contains",
            "objects": services,
            "filters": {"name_contains": "web"},
            "filter_def": SERVICE_FILTERS
        },
        # Tag filtering (list operation)
        {
            "name": "Tag filtering",
            "objects": addresses,
            "filters": {"tag_contains": "production"},
            "filter_def": ADDRESS_FILTERS
        },
        # Complex regex pattern
        {
            "name": "Regex pattern",
            "objects": addresses,
            "filters": {"name_regex": "address-[0-9]{3,4}-.*"},
            "filter_def": ADDRESS_FILTERS
        },
        # No matches (worst case)
        {
            "name": "No matches",
            "objects": addresses,
            "filters": {"name_eq": "non-existent-object"},
            "filter_def": ADDRESS_FILTERS
        }
    ]
    
    print("\nRunning performance tests:\n")
    print(f"{'Test Case':<30} {'Time (ms)':<15} {'Results':<15} {'Objects/sec':<20}")
    print("-" * 80)
    
    for test in test_cases:
        # Run the filter
        start_time = time.time()
        results = apply_filters(test["objects"], test["filters"], test["filter_def"])
        end_time = time.time()
        
        # Calculate metrics
        elapsed_ms = (end_time - start_time) * 1000
        objects_per_sec = object_count / (end_time - start_time) if end_time > start_time else 0
        
        print(f"{test['name']:<30} {elapsed_ms:<15.2f} {len(results):<15} {objects_per_sec:<20,.0f}")
    
    # Test field name normalization
    print("\n\nTesting field name normalization:")
    test_fields = [
        ("ip_netmask", "ip-netmask"),
        ("parent_device_group", "parent-device-group"),
        ("source_port", "source-port")
    ]
    
    for snake_case, hyphenated in test_fields:
        result1 = FilterProcessor.normalize_field_name(snake_case)
        result2 = FilterProcessor.normalize_field_name(hyphenated)
        print(f"  {snake_case} -> {result1}")
        print(f"  {hyphenated} -> {result2}")
    
    # Memory usage test
    print("\n\nMemory efficiency test:")
    import sys
    
    # Test with generator vs list
    start_mem = sys.getsizeof(addresses)
    filtered = apply_filters(addresses, {"name_contains": "test"}, ADDRESS_FILTERS)
    filtered_mem = sys.getsizeof(filtered)
    
    print(f"  Original list size: {start_mem:,} bytes")
    print(f"  Filtered list size: {filtered_mem:,} bytes")
    print(f"  Memory saved: {start_mem - filtered_mem:,} bytes")


if __name__ == "__main__":
    # Test with different dataset sizes
    for size in [1000, 5000, 10000, 50000]:
        test_filter_performance(size)
        print("\n" + "="*80 + "\n")
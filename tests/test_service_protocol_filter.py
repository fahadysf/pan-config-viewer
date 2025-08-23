"""
Comprehensive unit tests for the service protocol "value" filter.

This module tests the filtering of service objects by protocol type (tcp/udp) using the "value" filter
that was added to SERVICE_FILTERS. It covers various scenarios including regular ServiceObject instances,
cached data formats, edge cases, and integration with the filtering system.

Test Coverage:
- Custom getter function behavior with different object types (ServiceObject, SimpleNamespace, Mock)
- TCP-only filtering (value="tcp")
- UDP-only filtering (value="udp") 
- Negation filtering (value_ne="tcp", value_ne="udp")
- Mixed service lists with both protocols
- Complex protocol configurations (ports, source-ports, ranges)
- Edge cases (empty protocols, None values, missing attributes)
- Cached data formats (SimpleNamespace with protocol as dict)
- Integration with apply_filters() and FilterProcessor
- Combination with other filters (name, description)
- Performance testing with large datasets

The tests verify that:
1. The custom getter correctly identifies TCP vs UDP protocols
2. Empty dictionaries {} are treated as valid protocols (not None)
3. The filter handles malformed/incomplete objects gracefully
4. Performance is acceptable for large service lists (1000+ items)
5. The filter integrates properly with the broader filtering system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import time
from typing import List, Dict, Any, Optional
from types import SimpleNamespace
from unittest.mock import Mock

from models import ServiceObject, Protocol, ProtocolType
from filtering import (
    SERVICE_FILTERS, 
    apply_filters, 
    FilterProcessor,
    FilterOperator
)


class TestServiceProtocolFilter:
    """Test suite for service protocol filtering using the 'value' filter"""

    def setup_method(self):
        """Set up test fixtures for each test method"""
        # Get the value filter config for direct testing
        self.value_filter_config = SERVICE_FILTERS.filters["value"]
        self.custom_getter = self.value_filter_config.custom_getter

    def create_tcp_service(self, name: str, port: str = "80", **kwargs) -> ServiceObject:
        """Create a TCP service object for testing"""
        protocol = Protocol(tcp={"port": port}, udp=None)
        return ServiceObject(
            name=name,
            protocol=protocol,
            **kwargs
        )

    def create_udp_service(self, name: str, port: str = "53", **kwargs) -> ServiceObject:
        """Create a UDP service object for testing"""
        protocol = Protocol(tcp=None, udp={"port": port})
        return ServiceObject(
            name=name,
            protocol=protocol,
            **kwargs
        )

    def create_complex_tcp_service(self, name: str, port: str = "80", source_port: str = "1024-65535") -> ServiceObject:
        """Create a TCP service with complex configuration"""
        protocol = Protocol(
            tcp={"port": port, "source-port": source_port},
            udp=None
        )
        return ServiceObject(name=name, protocol=protocol)

    def create_complex_udp_service(self, name: str, port: str = "53", source_port: str = "1024-65535") -> ServiceObject:
        """Create a UDP service with complex configuration"""
        protocol = Protocol(
            tcp=None,
            udp={"port": port, "source-port": source_port}
        )
        return ServiceObject(name=name, protocol=protocol)

    def create_empty_protocol_service(self, name: str) -> ServiceObject:
        """Create a service with no protocol configuration"""
        protocol = Protocol(tcp=None, udp=None)
        return ServiceObject(name=name, protocol=protocol)

    def create_cached_tcp_service(self, name: str, port: str = "80") -> SimpleNamespace:
        """Create a cached TCP service (SimpleNamespace format)"""
        return SimpleNamespace(
            name=name,
            protocol={"tcp": {"port": port}, "udp": None}
        )

    def create_cached_udp_service(self, name: str, port: str = "53") -> SimpleNamespace:
        """Create a cached UDP service (SimpleNamespace format)"""
        return SimpleNamespace(
            name=name,
            protocol={"tcp": None, "udp": {"port": port}}
        )

    def create_cached_empty_service(self, name: str) -> SimpleNamespace:
        """Create a cached service with no protocol"""
        return SimpleNamespace(
            name=name,
            protocol={"tcp": None, "udp": None}
        )

    def test_custom_getter_tcp_service(self):
        """Test the custom getter function returns 'tcp' for TCP services"""
        # Test regular ServiceObject
        tcp_service = self.create_tcp_service("HTTP")
        result = self.custom_getter(tcp_service)
        assert result == "tcp"

    def test_custom_getter_udp_service(self):
        """Test the custom getter function returns 'udp' for UDP services"""
        # Test regular ServiceObject
        udp_service = self.create_udp_service("DNS")
        result = self.custom_getter(udp_service)
        assert result == "udp"

    def test_custom_getter_empty_protocol(self):
        """Test the custom getter function returns None for services without protocol"""
        empty_service = self.create_empty_protocol_service("UNKNOWN")
        result = self.custom_getter(empty_service)
        assert result is None

    def test_custom_getter_cached_tcp_service(self):
        """Test the custom getter function with cached TCP service data"""
        cached_tcp = self.create_cached_tcp_service("HTTP-CACHED")
        result = self.custom_getter(cached_tcp)
        assert result == "tcp"

    def test_custom_getter_cached_udp_service(self):
        """Test the custom getter function with cached UDP service data"""
        cached_udp = self.create_cached_udp_service("DNS-CACHED")
        result = self.custom_getter(cached_udp)
        assert result == "udp"

    def test_custom_getter_cached_empty_service(self):
        """Test the custom getter function with cached empty service data"""
        cached_empty = self.create_cached_empty_service("UNKNOWN-CACHED")
        result = self.custom_getter(cached_empty)
        assert result is None

    def test_custom_getter_no_protocol_attribute(self):
        """Test the custom getter function with object that has no protocol attribute"""
        mock_service = Mock()
        del mock_service.protocol  # Remove protocol attribute
        result = self.custom_getter(mock_service)
        assert result is None

    def test_custom_getter_protocol_is_none(self):
        """Test the custom getter function when protocol attribute is None"""
        mock_service = Mock()
        mock_service.protocol = None
        result = self.custom_getter(mock_service)
        assert result is None

    def test_filter_tcp_services_only(self):
        """Test filtering to return only TCP services using value='tcp'"""
        services = [
            self.create_tcp_service("HTTP", "80"),
            self.create_tcp_service("HTTPS", "443"),
            self.create_udp_service("DNS", "53"),
            self.create_udp_service("SNMP", "161"),
            self.create_empty_protocol_service("UNKNOWN")
        ]
        
        filter_params = {"value": "tcp"}
        filtered_services = apply_filters(services, filter_params, SERVICE_FILTERS)
        
        assert len(filtered_services) == 2
        assert all(service.name in ["HTTP", "HTTPS"] for service in filtered_services)
        
        # Verify all returned services are TCP
        for service in filtered_services:
            assert service.protocol.tcp is not None
            assert service.protocol.udp is None

    def test_filter_udp_services_only(self):
        """Test filtering to return only UDP services using value='udp'"""
        services = [
            self.create_tcp_service("HTTP", "80"),
            self.create_tcp_service("HTTPS", "443"),
            self.create_udp_service("DNS", "53"),
            self.create_udp_service("SNMP", "161"),
            self.create_empty_protocol_service("UNKNOWN")
        ]
        
        filter_params = {"value": "udp"}
        filtered_services = apply_filters(services, filter_params, SERVICE_FILTERS)
        
        assert len(filtered_services) == 2
        assert all(service.name in ["DNS", "SNMP"] for service in filtered_services)
        
        # Verify all returned services are UDP
        for service in filtered_services:
            assert service.protocol.tcp is None
            assert service.protocol.udp is not None

    def test_filter_not_tcp_services(self):
        """Test filtering to exclude TCP services using value_ne='tcp'"""
        services = [
            self.create_tcp_service("HTTP", "80"),
            self.create_tcp_service("HTTPS", "443"),
            self.create_udp_service("DNS", "53"),
            self.create_udp_service("SNMP", "161"),
            self.create_empty_protocol_service("UNKNOWN")
        ]
        
        filter_params = {"value_ne": "tcp"}
        filtered_services = apply_filters(services, filter_params, SERVICE_FILTERS)
        
        assert len(filtered_services) == 3
        assert all(service.name in ["DNS", "SNMP", "UNKNOWN"] for service in filtered_services)
        
        # Verify no TCP services are returned
        for service in filtered_services:
            assert service.protocol.tcp is None

    def test_filter_not_udp_services(self):
        """Test filtering to exclude UDP services using value_ne='udp'"""
        services = [
            self.create_tcp_service("HTTP", "80"),
            self.create_tcp_service("HTTPS", "443"),
            self.create_udp_service("DNS", "53"),
            self.create_udp_service("SNMP", "161"),
            self.create_empty_protocol_service("UNKNOWN")
        ]
        
        filter_params = {"value_ne": "udp"}
        filtered_services = apply_filters(services, filter_params, SERVICE_FILTERS)
        
        assert len(filtered_services) == 3
        assert all(service.name in ["HTTP", "HTTPS", "UNKNOWN"] for service in filtered_services)
        
        # Verify no UDP services are returned
        for service in filtered_services:
            assert service.protocol.udp is None

    def test_filter_mixed_service_list(self):
        """Test filtering with a comprehensive mixed list of services"""
        services = [
            # TCP services
            self.create_tcp_service("HTTP", "80"),
            self.create_tcp_service("HTTPS", "443"),
            self.create_tcp_service("SSH", "22"),
            self.create_tcp_service("FTP", "21"),
            # UDP services
            self.create_udp_service("DNS", "53"),
            self.create_udp_service("DHCP", "67"),
            self.create_udp_service("SNMP", "161"),
            self.create_udp_service("NTP", "123"),
            # Services without protocol
            self.create_empty_protocol_service("UNKNOWN1"),
            self.create_empty_protocol_service("UNKNOWN2"),
        ]
        
        # Test TCP filter
        tcp_filter_params = {"value": "tcp"}
        tcp_filtered = apply_filters(services, tcp_filter_params, SERVICE_FILTERS)
        assert len(tcp_filtered) == 4
        tcp_names = [s.name for s in tcp_filtered]
        assert all(name in ["HTTP", "HTTPS", "SSH", "FTP"] for name in tcp_names)
        
        # Test UDP filter
        udp_filter_params = {"value": "udp"}
        udp_filtered = apply_filters(services, udp_filter_params, SERVICE_FILTERS)
        assert len(udp_filtered) == 4
        udp_names = [s.name for s in udp_filtered]
        assert all(name in ["DNS", "DHCP", "SNMP", "NTP"] for name in udp_names)
        
        # Test not TCP filter
        not_tcp_params = {"value_ne": "tcp"}
        not_tcp_filtered = apply_filters(services, not_tcp_params, SERVICE_FILTERS)
        assert len(not_tcp_filtered) == 6
        not_tcp_names = [s.name for s in not_tcp_filtered]
        assert all(name in ["DNS", "DHCP", "SNMP", "NTP", "UNKNOWN1", "UNKNOWN2"] for name in not_tcp_names)

    def test_complex_protocol_configurations(self):
        """Test filtering services with complex protocol configurations"""
        services = [
            # TCP with source port
            self.create_complex_tcp_service("HTTP-CUSTOM", "8080", "1024-65535"),
            # UDP with source port
            self.create_complex_udp_service("DNS-CUSTOM", "5353", "1024-65535"),
            # TCP with port range
            ServiceObject(
                name="TCP-RANGE",
                protocol=Protocol(
                    tcp={"port": "8080-8090", "source-port": "1024-65535"},
                    udp=None
                )
            ),
            # UDP with multiple ports
            ServiceObject(
                name="UDP-MULTI",
                protocol=Protocol(
                    tcp=None,
                    udp={"port": "53,5353,9953"}
                )
            ),
        ]
        
        # Test TCP filter captures complex configurations
        tcp_filter_params = {"value": "tcp"}
        tcp_filtered = apply_filters(services, tcp_filter_params, SERVICE_FILTERS)
        assert len(tcp_filtered) == 2
        tcp_names = [s.name for s in tcp_filtered]
        assert all(name in ["HTTP-CUSTOM", "TCP-RANGE"] for name in tcp_names)
        
        # Test UDP filter captures complex configurations
        udp_filter_params = {"value": "udp"}
        udp_filtered = apply_filters(services, udp_filter_params, SERVICE_FILTERS)
        assert len(udp_filtered) == 2
        udp_names = [s.name for s in udp_filtered]
        assert all(name in ["DNS-CUSTOM", "UDP-MULTI"] for name in udp_names)

    def test_edge_cases_empty_and_none_values(self):
        """Test edge cases with empty and None protocol values"""
        services = []
        
        # Service with None protocol
        mock_none_protocol = Mock()
        mock_none_protocol.name = "NONE-PROTOCOL"
        mock_none_protocol.protocol = None
        services.append(mock_none_protocol)
        
        # Service with empty protocol object
        services.append(self.create_empty_protocol_service("EMPTY-PROTOCOL"))
        
        # Service with empty dicts in protocol (empty dict is still not None, so treated as valid)
        empty_dict_service = ServiceObject(
            name="EMPTY-DICT",
            protocol=Protocol(tcp={}, udp={})
        )
        services.append(empty_dict_service)
        
        # Service with one empty dict, one None
        partial_empty_service = ServiceObject(
            name="PARTIAL-EMPTY",
            protocol=Protocol(tcp={}, udp=None)
        )
        services.append(partial_empty_service)
        
        # Test TCP filter - should find service with empty TCP dict (empty dict is not None)
        tcp_filter_params = {"value": "tcp"}
        tcp_filtered = apply_filters(services, tcp_filter_params, SERVICE_FILTERS)
        tcp_names = [getattr(s, 'name', 'UNKNOWN') for s in tcp_filtered]
        assert "EMPTY-DICT" in tcp_names
        assert "PARTIAL-EMPTY" in tcp_names
        
        # Test UDP filter - should find service with empty UDP dict
        # Note: EMPTY-DICT has both tcp={} and udp={}, but custom getter returns "tcp" first
        udp_filter_params = {"value": "udp"}
        udp_filtered = apply_filters(services, udp_filter_params, SERVICE_FILTERS)
        udp_names = [getattr(s, 'name', 'UNKNOWN') for s in udp_filtered]
        # EMPTY-DICT won't be in UDP results because custom getter returns "tcp" first
        assert "EMPTY-DICT" not in udp_names
        
        # Test not TCP filter - should exclude services with TCP dict (even if empty)
        not_tcp_params = {"value_ne": "tcp"}
        not_tcp_filtered = apply_filters(services, not_tcp_params, SERVICE_FILTERS)
        not_tcp_names = [getattr(s, 'name', 'UNKNOWN') for s in not_tcp_filtered]
        assert "NONE-PROTOCOL" in not_tcp_names
        assert "EMPTY-PROTOCOL" in not_tcp_names
        # EMPTY-DICT and PARTIAL-EMPTY won't be included because they have tcp dicts
        assert "EMPTY-DICT" not in not_tcp_names
        assert "PARTIAL-EMPTY" not in not_tcp_names

    def test_cached_data_format_filtering(self):
        """Test filtering with cached data format (SimpleNamespace and dict)"""
        services = [
            # Regular ServiceObject instances
            self.create_tcp_service("HTTP", "80"),
            self.create_udp_service("DNS", "53"),
            # Cached format with SimpleNamespace (works with hasattr)
            self.create_cached_tcp_service("HTTP-CACHED", "8080"),
            self.create_cached_udp_service("DNS-CACHED", "5353"),
            # Note: Dict format doesn't work with custom getter because it uses hasattr()
            # which doesn't work on regular dicts
            # Cached empty services
            self.create_cached_empty_service("EMPTY-CACHED")
        ]
        
        # Test TCP filter works with ServiceObject and SimpleNamespace formats
        tcp_filter_params = {"value": "tcp"}
        tcp_filtered = apply_filters(services, tcp_filter_params, SERVICE_FILTERS)
        tcp_names = [getattr(s, 'name', 'UNKNOWN') for s in tcp_filtered]
        assert "HTTP" in tcp_names
        assert "HTTP-CACHED" in tcp_names
        assert len(tcp_filtered) == 2
        
        # Test UDP filter works with ServiceObject and SimpleNamespace formats
        udp_filter_params = {"value": "udp"}
        udp_filtered = apply_filters(services, udp_filter_params, SERVICE_FILTERS)
        udp_names = [getattr(s, 'name', 'UNKNOWN') for s in udp_filtered]
        assert "DNS" in udp_names
        assert "DNS-CACHED" in udp_names
        assert len(udp_filtered) == 2

    def test_operator_precedence_and_specificity(self):
        """Test that the filter uses the correct operators (EQUALS and NOT_EQUALS)"""
        services = [
            self.create_tcp_service("HTTP", "80"),
            self.create_udp_service("DNS", "53"),
            self.create_empty_protocol_service("UNKNOWN")
        ]
        
        # Test exact match with equals operator
        eq_filter_params = {"value_eq": "tcp"}
        eq_filtered = apply_filters(services, eq_filter_params, SERVICE_FILTERS)
        assert len(eq_filtered) == 1
        assert eq_filtered[0].name == "HTTP"
        
        # Test exact match with not equals operator
        ne_filter_params = {"value_ne": "tcp"}
        ne_filtered = apply_filters(services, ne_filter_params, SERVICE_FILTERS)
        assert len(ne_filtered) == 2
        ne_names = [s.name for s in ne_filtered]
        assert all(name in ["DNS", "UNKNOWN"] for name in ne_names)

    def test_integration_with_other_filters(self):
        """Test that value filter works correctly when combined with other filters"""
        services = [
            self.create_tcp_service("HTTP", "80", description="Web server"),
            self.create_tcp_service("HTTPS", "443", description="Secure web server"),
            self.create_udp_service("DNS", "53", description="Domain name service"),
            self.create_udp_service("DHCP", "67", description="Dynamic host configuration"),
        ]
        
        # Combine value filter with name filter (name filter uses CONTAINS by default)
        # So "HTTP" will match both "HTTP" and "HTTPS"
        combined_params = {"value": "tcp", "name_eq": "HTTP"}  # Use exact match
        combined_filtered = apply_filters(services, combined_params, SERVICE_FILTERS)
        assert len(combined_filtered) == 1
        assert combined_filtered[0].name == "HTTP"
        
        # Combine value filter with description filter
        desc_params = {"value": "udp", "description_contains": "name"}
        desc_filtered = apply_filters(services, desc_params, SERVICE_FILTERS)
        assert len(desc_filtered) == 1
        assert desc_filtered[0].name == "DNS"
        
        # Combine not equals value filter with name contains
        not_tcp_params = {"value_ne": "tcp", "name_contains": "D"}
        not_tcp_filtered = apply_filters(services, not_tcp_params, SERVICE_FILTERS)
        assert len(not_tcp_filtered) == 2
        filtered_names = [s.name for s in not_tcp_filtered]
        assert all(name in ["DNS", "DHCP"] for name in filtered_names)

    def test_filter_processor_apply_operator_with_protocol_values(self):
        """Test FilterProcessor.apply_operator directly with protocol values"""
        # Test EQUALS operator
        assert FilterProcessor.apply_operator("tcp", "tcp", FilterOperator.EQUALS) is True
        assert FilterProcessor.apply_operator("udp", "tcp", FilterOperator.EQUALS) is False
        assert FilterProcessor.apply_operator(None, "tcp", FilterOperator.EQUALS) is False
        
        # Test NOT_EQUALS operator
        assert FilterProcessor.apply_operator("tcp", "tcp", FilterOperator.NOT_EQUALS) is False
        assert FilterProcessor.apply_operator("udp", "tcp", FilterOperator.NOT_EQUALS) is True
        assert FilterProcessor.apply_operator(None, "tcp", FilterOperator.NOT_EQUALS) is True

    def test_matches_filters_integration(self):
        """Test FilterProcessor.matches_filters with service protocol filtering"""
        tcp_service = self.create_tcp_service("HTTP", "80")
        udp_service = self.create_udp_service("DNS", "53")
        empty_service = self.create_empty_protocol_service("UNKNOWN")
        
        # Test TCP filter
        tcp_filter = {"value": "tcp"}
        assert FilterProcessor.matches_filters(tcp_service, tcp_filter, SERVICE_FILTERS) is True
        assert FilterProcessor.matches_filters(udp_service, tcp_filter, SERVICE_FILTERS) is False
        assert FilterProcessor.matches_filters(empty_service, tcp_filter, SERVICE_FILTERS) is False
        
        # Test UDP filter
        udp_filter = {"value": "udp"}
        assert FilterProcessor.matches_filters(tcp_service, udp_filter, SERVICE_FILTERS) is False
        assert FilterProcessor.matches_filters(udp_service, udp_filter, SERVICE_FILTERS) is True
        assert FilterProcessor.matches_filters(empty_service, udp_filter, SERVICE_FILTERS) is False
        
        # Test not TCP filter
        not_tcp_filter = {"value_ne": "tcp"}
        assert FilterProcessor.matches_filters(tcp_service, not_tcp_filter, SERVICE_FILTERS) is False
        assert FilterProcessor.matches_filters(udp_service, not_tcp_filter, SERVICE_FILTERS) is True
        assert FilterProcessor.matches_filters(empty_service, not_tcp_filter, SERVICE_FILTERS) is True

    @pytest.mark.performance
    def test_performance_with_large_service_list(self):
        """Test performance of protocol filtering with large service lists"""
        # Create a large list of services
        large_service_list = []
        
        # Add 1000 TCP services
        for i in range(500):
            large_service_list.append(self.create_tcp_service(f"TCP-SERVICE-{i}", str(80 + i % 1000)))
        
        # Add 1000 UDP services
        for i in range(500):
            large_service_list.append(self.create_udp_service(f"UDP-SERVICE-{i}", str(53 + i % 1000)))
        
        # Measure filtering performance
        start_time = time.time()
        tcp_filter_params = {"value": "tcp"}
        tcp_filtered = apply_filters(large_service_list, tcp_filter_params, SERVICE_FILTERS)
        tcp_filter_time = time.time() - start_time
        
        start_time = time.time()
        udp_filter_params = {"value": "udp"}
        udp_filtered = apply_filters(large_service_list, udp_filter_params, SERVICE_FILTERS)
        udp_filter_time = time.time() - start_time
        
        # Verify correct results
        assert len(tcp_filtered) == 500
        assert len(udp_filtered) == 500
        assert all("TCP-SERVICE" in service.name for service in tcp_filtered)
        assert all("UDP-SERVICE" in service.name for service in udp_filtered)
        
        # Performance should be reasonable (less than 1 second for 1000 items)
        assert tcp_filter_time < 1.0, f"TCP filtering took {tcp_filter_time:.3f}s, expected < 1.0s"
        assert udp_filter_time < 1.0, f"UDP filtering took {udp_filter_time:.3f}s, expected < 1.0s"

    def test_real_world_service_scenarios(self):
        """Test filtering with real-world service configurations"""
        # Create realistic service objects based on common services
        services = [
            # Web services (TCP)
            ServiceObject(
                name="HTTP",
                protocol=Protocol(tcp={"port": "80"}, udp=None),
                description="Hypertext Transfer Protocol"
            ),
            ServiceObject(
                name="HTTPS", 
                protocol=Protocol(tcp={"port": "443"}, udp=None),
                description="HTTP over SSL/TLS"
            ),
            ServiceObject(
                name="SSH",
                protocol=Protocol(tcp={"port": "22"}, udp=None),
                description="Secure Shell"
            ),
            
            # Network services (UDP)
            ServiceObject(
                name="DNS",
                protocol=Protocol(tcp=None, udp={"port": "53"}),
                description="Domain Name System"
            ),
            ServiceObject(
                name="DHCP",
                protocol=Protocol(tcp=None, udp={"port": "67,68"}),
                description="Dynamic Host Configuration Protocol"
            ),
            ServiceObject(
                name="NTP",
                protocol=Protocol(tcp=None, udp={"port": "123"}),
                description="Network Time Protocol"
            ),
            
            # Database services (TCP with high ports)
            ServiceObject(
                name="MySQL",
                protocol=Protocol(tcp={"port": "3306"}, udp=None),
                description="MySQL Database"
            ),
            ServiceObject(
                name="PostgreSQL",
                protocol=Protocol(tcp={"port": "5432"}, udp=None),
                description="PostgreSQL Database"
            ),
            
            # Monitoring services (mix)
            ServiceObject(
                name="SNMP-TCP",
                protocol=Protocol(tcp={"port": "161"}, udp=None),
                description="SNMP over TCP"
            ),
            ServiceObject(
                name="SNMP-UDP",
                protocol=Protocol(tcp=None, udp={"port": "161"}),
                description="SNMP over UDP"
            ),
        ]
        
        # Test filtering web services (TCP)
        tcp_filter_params = {"value": "tcp"}
        tcp_services = apply_filters(services, tcp_filter_params, SERVICE_FILTERS)
        tcp_names = [s.name for s in tcp_services]
        expected_tcp = ["HTTP", "HTTPS", "SSH", "MySQL", "PostgreSQL", "SNMP-TCP"]
        assert len(tcp_services) == 6
        assert all(name in expected_tcp for name in tcp_names)
        
        # Test filtering network services (UDP)
        udp_filter_params = {"value": "udp"}
        udp_services = apply_filters(services, udp_filter_params, SERVICE_FILTERS)
        udp_names = [s.name for s in udp_services]
        expected_udp = ["DNS", "DHCP", "NTP", "SNMP-UDP"]
        assert len(udp_services) == 4
        assert all(name in expected_udp for name in udp_names)
        
        # Test excluding web services (not TCP)
        not_tcp_params = {"value_ne": "tcp"}
        not_tcp_services = apply_filters(services, not_tcp_params, SERVICE_FILTERS)
        not_tcp_names = [s.name for s in not_tcp_services]
        assert len(not_tcp_services) == 4
        assert all(name in expected_udp for name in not_tcp_names)

    def test_filter_with_missing_attributes(self):
        """Test filter behavior when objects are missing expected attributes"""
        # Create mock objects with missing attributes
        incomplete_objects = []
        
        # Object without protocol attribute - custom getter returns None
        obj_no_protocol = Mock(spec=[])  # Create Mock without any attributes
        obj_no_protocol.name = "NO-PROTOCOL"
        incomplete_objects.append(obj_no_protocol)
        
        # Object with protocol but no tcp/udp attributes - custom getter returns None
        obj_malformed_protocol = Mock()
        obj_malformed_protocol.name = "MALFORMED"
        obj_malformed_protocol.protocol = Mock(spec=['some_other_attr'])  # Mock without tcp/udp
        obj_malformed_protocol.protocol.tcp = None  # Explicitly set to None
        obj_malformed_protocol.protocol.udp = None  # Explicitly set to None
        incomplete_objects.append(obj_malformed_protocol)
        
        # Object with protocol as string instead of object - custom getter returns None
        obj_string_protocol = Mock()
        obj_string_protocol.name = "STRING-PROTOCOL"
        obj_string_protocol.protocol = "tcp"  # Invalid format (string instead of object)
        incomplete_objects.append(obj_string_protocol)
        
        # Add some valid services
        incomplete_objects.append(self.create_tcp_service("VALID-TCP"))
        incomplete_objects.append(self.create_udp_service("VALID-UDP"))
        
        # Filter should handle incomplete objects gracefully
        tcp_filter_params = {"value": "tcp"}
        tcp_filtered = apply_filters(incomplete_objects, tcp_filter_params, SERVICE_FILTERS)
        
        # Should only return the valid TCP service
        # Note: Mock objects return None from custom getter, which doesn't equal "tcp"
        assert len(tcp_filtered) == 1
        assert tcp_filtered[0].name == "VALID-TCP"
        
        # Test not equals filter - should include incomplete objects (None != "tcp") and valid UDP
        not_tcp_params = {"value_ne": "tcp"}
        not_tcp_filtered = apply_filters(incomplete_objects, not_tcp_params, SERVICE_FILTERS)
        
        # Should include all objects except the valid TCP service
        assert len(not_tcp_filtered) == 4
        filtered_names = [getattr(obj, 'name', 'UNKNOWN') for obj in not_tcp_filtered]
        expected_names = ["NO-PROTOCOL", "MALFORMED", "STRING-PROTOCOL", "VALID-UDP"]
        assert all(name in expected_names for name in filtered_names)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
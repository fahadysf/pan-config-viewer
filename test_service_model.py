"""
Unit tests for ServiceObject model type computation.

Tests cover:
- Type computation from protocol configuration
- Validation logic for TCP services
- Validation logic for UDP services  
- Edge cases (both protocols, neither protocol)
- Type field persistence and serialization
- Model validation behavior
"""

import pytest
import sys
import os
from typing import Dict, Any
from pydantic import ValidationError

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import ServiceObject, Protocol, ProtocolType


class TestServiceObjectTypeComputation:
    """Test ServiceObject type field computation and validation"""

    def test_tcp_service_type_computation(self):
        """Test that TCP services get type=tcp"""
        # Create TCP service
        tcp_protocol = Protocol(tcp={"port": "80"})
        service = ServiceObject(
            name="web-service",
            protocol=tcp_protocol,
            description="Web server"
        )
        
        # Type should be automatically set to TCP
        assert service.type == ProtocolType.TCP
        assert service.type.value == "tcp"

    def test_udp_service_type_computation(self):
        """Test that UDP services get type=udp"""
        # Create UDP service
        udp_protocol = Protocol(udp={"port": "53"})
        service = ServiceObject(
            name="dns-service",
            protocol=udp_protocol,
            description="DNS server"
        )
        
        # Type should be automatically set to UDP
        assert service.type == ProtocolType.UDP
        assert service.type.value == "udp"

    def test_tcp_service_with_multiple_ports(self):
        """Test TCP service with complex port configuration"""
        tcp_protocol = Protocol(tcp={
            "port": "8080-8090",
            "source-port": "1024-65535"
        })
        service = ServiceObject(
            name="app-service",
            protocol=tcp_protocol
        )
        
        assert service.type == ProtocolType.TCP
        assert service.protocol.tcp["port"] == "8080-8090"
        assert service.protocol.tcp["source-port"] == "1024-65535"

    def test_udp_service_with_multiple_ports(self):
        """Test UDP service with complex port configuration"""
        udp_protocol = Protocol(udp={
            "port": "5000,5001,5002",
            "override": {"timeout": 30}
        })
        service = ServiceObject(
            name="multicast-service",
            protocol=udp_protocol
        )
        
        assert service.type == ProtocolType.UDP
        assert service.protocol.udp["port"] == "5000,5001,5002"

    def test_service_with_both_protocols(self):
        """Test service with both TCP and UDP protocols (edge case)"""
        # In real PAN configurations, this shouldn't happen, but test the behavior
        both_protocol = Protocol(
            tcp={"port": "80"},
            udp={"port": "80"}
        )
        service = ServiceObject(
            name="dual-protocol-service",
            protocol=both_protocol
        )
        
        # TCP takes precedence in validation logic
        assert service.type == ProtocolType.TCP

    def test_service_with_neither_protocol(self):
        """Test service with neither TCP nor UDP protocols"""
        empty_protocol = Protocol()
        service = ServiceObject(
            name="empty-service",
            protocol=empty_protocol
        )
        
        # Type should remain None when no protocol is specified
        assert service.type is None

    def test_explicitly_set_type_overridden_by_validation(self):
        """Test that explicitly set type is overridden by validation"""
        tcp_protocol = Protocol(tcp={"port": "443"})
        
        # Try to create service with wrong type
        service = ServiceObject(
            name="https-service",
            protocol=tcp_protocol,
            type=ProtocolType.UDP  # Wrong type
        )
        
        # Validation should override the wrong type
        assert service.type == ProtocolType.TCP

    def test_type_field_in_model_dump(self):
        """Test that type field is included in model serialization"""
        tcp_protocol = Protocol(tcp={"port": "22"})
        service = ServiceObject(
            name="ssh-service",
            protocol=tcp_protocol,
            description="SSH service"
        )
        
        # Get model dump
        service_dict = service.model_dump()
        
        # Type should be serialized
        assert "type" in service_dict
        assert service_dict["type"] == "tcp"

    def test_type_field_with_aliases(self):
        """Test type field with field aliases"""
        udp_protocol = Protocol(udp={"port": "161"})
        service = ServiceObject(
            name="snmp-service",
            protocol=udp_protocol,
            parent_device_group="test-dg"
        )
        
        # Test with by_alias=True
        service_dict = service.model_dump(by_alias=True)
        assert service_dict["type"] == "udp"
        assert service_dict["parent-device-group"] == "test-dg"

    def test_service_creation_from_dict(self):
        """Test creating service from dictionary data"""
        service_data = {
            "name": "mysql-service",
            "protocol": {
                "tcp": {"port": "3306"}
            },
            "description": "MySQL database",
            "tag": ["database", "mysql"]
        }
        
        service = ServiceObject(**service_data)
        
        assert service.name == "mysql-service"
        assert service.type == ProtocolType.TCP
        assert service.protocol.tcp["port"] == "3306"
        assert service.description == "MySQL database"
        assert service.tag == ["database", "mysql"]

    def test_service_update_protocol_updates_type(self):
        """Test that updating protocol updates type accordingly"""
        # Start with TCP service
        tcp_protocol = Protocol(tcp={"port": "80"})
        service = ServiceObject(
            name="web-service",
            protocol=tcp_protocol
        )
        assert service.type == ProtocolType.TCP
        
        # Update to UDP protocol
        service.protocol = Protocol(udp={"port": "80"})
        
        # Re-validate to trigger type update
        service = ServiceObject(**service.model_dump())
        assert service.type == ProtocolType.UDP

    def test_type_enum_values(self):
        """Test ProtocolType enum values"""
        assert ProtocolType.TCP.value == "tcp"
        assert ProtocolType.UDP.value == "udp"
        
        # Test string comparison
        assert ProtocolType.TCP == "tcp"
        assert ProtocolType.UDP == "udp"

    def test_service_with_complex_tcp_config(self):
        """Test service with complex TCP configuration"""
        complex_tcp = Protocol(tcp={
            "port": "443",
            "override": {
                "yes": {
                    "timeout": 30,
                    "halfclose-timeout": 5,
                    "timewait-timeout": 15
                }
            }
        })
        
        service = ServiceObject(
            name="custom-https",
            protocol=complex_tcp,
            description="Custom HTTPS with timeouts"
        )
        
        assert service.type == ProtocolType.TCP
        assert service.protocol.tcp["port"] == "443"
        assert "override" in service.protocol.tcp

    def test_service_with_complex_udp_config(self):
        """Test service with complex UDP configuration"""
        complex_udp = Protocol(udp={
            "port": "1194",
            "override": {
                "yes": {
                    "timeout": 60
                }
            }
        })
        
        service = ServiceObject(
            name="openvpn",
            protocol=complex_udp,
            description="OpenVPN service"
        )
        
        assert service.type == ProtocolType.UDP
        assert service.protocol.udp["port"] == "1194"

    def test_service_with_empty_protocol_dict(self):
        """Test service with empty protocol dictionaries"""
        # TCP with empty dict
        empty_tcp = Protocol(tcp={})
        service = ServiceObject(name="empty-tcp", protocol=empty_tcp)
        assert service.type == ProtocolType.TCP
        
        # UDP with empty dict
        empty_udp = Protocol(udp={})
        service = ServiceObject(name="empty-udp", protocol=empty_udp)
        assert service.type == ProtocolType.UDP

    def test_protocol_validation_with_none_values(self):
        """Test protocol validation with None values"""
        protocol_with_none = Protocol(tcp=None, udp={"port": "123"})
        service = ServiceObject(name="test-service", protocol=protocol_with_none)
        
        assert service.type == ProtocolType.UDP
        assert service.protocol.tcp is None
        assert service.protocol.udp is not None

    def test_service_type_consistency_after_multiple_validations(self):
        """Test type consistency after multiple model validations"""
        tcp_protocol = Protocol(tcp={"port": "8080"})
        service = ServiceObject(
            name="test-app",
            protocol=tcp_protocol
        )
        
        # Multiple serialization/deserialization cycles
        for _ in range(3):
            service_dict = service.model_dump()
            service = ServiceObject(**service_dict)
            assert service.type == ProtocolType.TCP

    def test_service_validation_edge_cases(self):
        """Test various edge cases in service validation"""
        
        # Test with minimal data
        minimal_service = ServiceObject(
            name="minimal",
            protocol=Protocol(tcp={"port": "80"})
        )
        assert minimal_service.type == ProtocolType.TCP
        
        # Test with maximal data
        maximal_service = ServiceObject(
            name="maximal-service",
            protocol=Protocol(tcp={
                "port": "443", 
                "source-port": "1024-65535",
                "override": {"timeout": 30}
            }),
            description="Full-featured HTTPS service",
            tag=["web", "secure", "https"],
            xpath="/config/shared/service/entry[@name='maximal-service']",
            parent_device_group="production",
            parent_template="web-template",
            parent_vsys="vsys1"
        )
        assert maximal_service.type == ProtocolType.TCP
        assert maximal_service.description == "Full-featured HTTPS service"
        assert len(maximal_service.tag) == 3

    def test_type_field_json_serialization(self):
        """Test JSON serialization includes type field correctly"""
        import json
        
        service = ServiceObject(
            name="json-test",
            protocol=Protocol(udp={"port": "514"})
        )
        
        # Serialize to JSON
        json_str = service.model_dump_json()
        parsed = json.loads(json_str)
        
        assert "type" in parsed
        assert parsed["type"] == "udp"
        assert parsed["name"] == "json-test"

    def test_model_validator_execution_order(self):
        """Test that model validator runs after field assignment"""
        # This tests the @model_validator(mode='after') behavior
        service_data = {
            "name": "validator-test",
            "protocol": {"tcp": {"port": "9090"}},
            "type": "udp"  # Wrong type, should be overridden
        }
        
        service = ServiceObject(**service_data)
        
        # Validator should have run and corrected the type
        assert service.type == ProtocolType.TCP

    def test_type_field_inheritance_from_config_location(self):
        """Test that type field works alongside ConfigLocation inheritance"""
        service = ServiceObject(
            name="inherited-service",
            protocol=Protocol(tcp={"port": "25"}),
            xpath="/config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='test']/service/entry[@name='inherited-service']",
            parent_device_group="test-dg"
        )
        
        assert service.type == ProtocolType.TCP
        assert service.xpath is not None
        assert service.parent_device_group == "test-dg"

    def test_protocol_type_enum_in_filtering_context(self):
        """Test ProtocolType enum behavior in filtering scenarios"""
        # Test enum comparison with strings
        assert ProtocolType.TCP == "tcp"
        assert ProtocolType.UDP == "udp"
        assert ProtocolType.TCP != "udp"
        
        # Test enum in collections
        types = [ProtocolType.TCP, ProtocolType.UDP]
        assert "tcp" in types
        assert "udp" in types
        assert "icmp" not in types
"""Test model validation logic"""
import pytest
from models import AddressObject, AddressType


class TestAddressObject:
    """Test AddressObject model validation"""
    
    def test_ip_netmask_address(self):
        """Test that ip-netmask address sets correct type and nulls other fields"""
        address = AddressObject(
            name="test-server",
            ip_netmask="10.1.1.100/32",
            description="Test server"
        )
        
        assert address.type == AddressType.IP_NETMASK
        assert address.ip_netmask == "10.1.1.100/32"
        assert address.ip_range is None
        assert address.fqdn is None
    
    def test_ip_range_address(self):
        """Test that ip-range address sets correct type and nulls other fields"""
        address = AddressObject(
            name="test-range",
            ip_range="10.1.1.1-10.1.1.100",
            description="Test range"
        )
        
        assert address.type == AddressType.IP_RANGE
        assert address.ip_range == "10.1.1.1-10.1.1.100"
        assert address.ip_netmask is None
        assert address.fqdn is None
    
    def test_fqdn_address(self):
        """Test that FQDN address sets correct type and nulls other fields"""
        address = AddressObject(
            name="test-fqdn",
            fqdn="example.com",
            description="Test FQDN"
        )
        
        assert address.type == AddressType.FQDN
        assert address.fqdn == "example.com"
        assert address.ip_netmask is None
        assert address.ip_range is None
    
    def test_multiple_values_prioritize_ip_netmask(self):
        """Test that when multiple values are provided, ip-netmask takes precedence"""
        address = AddressObject(
            name="test-multi",
            ip_netmask="10.1.1.100/32",
            ip_range="10.1.1.1-10.1.1.100",
            fqdn="example.com"
        )
        
        # ip-netmask should take precedence
        assert address.type == AddressType.IP_NETMASK
        assert address.ip_netmask == "10.1.1.100/32"
        assert address.ip_range is None
        assert address.fqdn is None
    
    def test_multiple_values_prioritize_ip_range(self):
        """Test that when ip-range and fqdn are provided (no ip-netmask), ip-range takes precedence"""
        address = AddressObject(
            name="test-multi",
            ip_range="10.1.1.1-10.1.1.100",
            fqdn="example.com"
        )
        
        # ip-range should take precedence over fqdn
        assert address.type == AddressType.IP_RANGE
        assert address.ip_range == "10.1.1.1-10.1.1.100"
        assert address.ip_netmask is None
        assert address.fqdn is None
    
    def test_type_field_consistency(self):
        """Test that type field is correctly set based on populated value"""
        # Test with ip-netmask
        addr1 = AddressObject(name="addr1", ip_netmask="192.168.1.0/24")
        assert addr1.type == AddressType.IP_NETMASK
        
        # Test with ip-range
        addr2 = AddressObject(name="addr2", ip_range="192.168.1.1-192.168.1.254")
        assert addr2.type == AddressType.IP_RANGE
        
        # Test with fqdn
        addr3 = AddressObject(name="addr3", fqdn="www.example.com")
        assert addr3.type == AddressType.FQDN
    
    def test_no_address_value_provided(self):
        """Test that address with only name and no value fields works"""
        address = AddressObject(
            name="empty-address",
            description="No address value"
        )
        
        assert address.type is None
        assert address.ip_netmask is None
        assert address.ip_range is None
        assert address.fqdn is None
    
    def test_with_tags_and_location(self):
        """Test address with tags and location information"""
        address = AddressObject(
            name="tagged-server",
            ip_netmask="10.1.1.100/32",
            description="Tagged server",
            tag=["production", "web"],
            parent_device_group="test-dg",
            xpath="/config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='test-dg']/address/entry[@name='tagged-server']"
        )
        
        assert address.type == AddressType.IP_NETMASK
        assert address.ip_netmask == "10.1.1.100/32"
        assert address.ip_range is None
        assert address.fqdn is None
        assert address.tag == ["production", "web"]
        assert address.parent_device_group == "test-dg"
    
    def test_type_explicitly_set(self):
        """Test that explicitly setting type without value maintains consistency"""
        address = AddressObject(
            name="explicit-type",
            type=AddressType.IP_NETMASK
        )
        
        assert address.type == AddressType.IP_NETMASK
        assert address.ip_netmask is None
        assert address.ip_range is None
        assert address.fqdn is None
    
    def test_serialization(self):
        """Test that model serializes correctly with type field"""
        address = AddressObject(
            name="test-serialize",
            ip_netmask="10.1.1.100/32"
        )
        
        data = address.model_dump(by_alias=True)
        assert data["type"] == "ip-netmask"
        assert data["ip-netmask"] == "10.1.1.100/32"
        assert data["ip-range"] is None
        assert data["fqdn"] is None
    
    def test_deserialization(self):
        """Test that model deserializes correctly with type field"""
        data = {
            "name": "test-deserialize",
            "ip-netmask": "10.1.1.100/32",
            "description": "Test"
        }
        
        address = AddressObject(**data)
        assert address.type == AddressType.IP_NETMASK
        assert address.ip_netmask == "10.1.1.100/32"
        assert address.ip_range is None
        assert address.fqdn is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
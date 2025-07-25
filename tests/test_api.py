import pytest
import os
import sys
import shutil
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# We need to delay the import until the environment is set by pytest
from fastapi.testclient import TestClient

# Import app - tests will run with Docker API
from main import app
client = TestClient(app)


class TestConfigurationEndpoints:
    """Test configuration management endpoints"""
    
    def test_list_configs(self):
        """Test listing available configurations"""
        response = client.get("/api/v1/configs")
        assert response.status_code == 200
        data = response.json()
        assert "configs" in data
        assert "test_panorama" in data["configs"]
        assert data["count"] > 0
    
    def test_get_config_info(self):
        """Test getting configuration info"""
        response = client.get("/api/v1/configs/test_panorama/info")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test_panorama"
        assert "size" in data
        assert "modified" in data
    
    def test_get_config_info_not_found(self):
        """Test getting info for non-existent config"""
        response = client.get("/api/v1/configs/nonexistent/info")
        assert response.status_code == 404


class TestAddressEndpoints:
    """Test address object endpoints"""
    
    def test_get_all_addresses(self):
        """Test getting all addresses"""
        response = client.get("/api/v1/configs/test_panorama/addresses")
        assert response.status_code == 200
        addresses = response.json()
        assert isinstance(addresses, list)
        assert len(addresses) >= 3  # Should have shared and device group addresses
        
        # Check for expected addresses
        names = [addr["name"] for addr in addresses]
        assert "test-server" in names
        assert "web-server" in names
        assert "dg-server" in names
    
    def test_get_addresses_with_filter(self):
        """Test getting addresses with name filter"""
        response = client.get("/api/v1/configs/test_panorama/addresses?name=server")
        assert response.status_code == 200
        addresses = response.json()
        assert all("server" in addr["name"].lower() for addr in addresses)
    
    def test_get_addresses_by_location(self):
        """Test getting addresses filtered by location"""
        # Test shared addresses only
        response = client.get("/api/v1/configs/test_panorama/addresses?location=shared")
        assert response.status_code == 200
        addresses = response.json()
        assert all(addr["parent-device-group"] is None for addr in addresses)
        
        # Test device-group addresses only
        response = client.get("/api/v1/configs/test_panorama/addresses?location=device-group")
        assert response.status_code == 200
        addresses = response.json()
        assert all(addr["parent-device-group"] is not None for addr in addresses)
    
    def test_get_specific_address(self):
        """Test getting a specific address"""
        response = client.get("/api/v1/configs/test_panorama/addresses/test-server")
        assert response.status_code == 200
        address = response.json()
        assert address["name"] == "test-server"
        assert address["ip-netmask"] == "10.1.1.100"
        assert address["description"] == "Test server"
        assert "xpath" in address
        assert address["xpath"] is not None
    
    def test_get_address_not_found(self):
        """Test getting non-existent address"""
        response = client.get("/api/v1/configs/test_panorama/addresses/nonexistent")
        assert response.status_code == 404


class TestAddressGroupEndpoints:
    """Test address group endpoints"""
    
    def test_get_address_groups(self):
        """Test getting address groups"""
        response = client.get("/api/v1/configs/test_panorama/address-groups")
        assert response.status_code == 200
        groups = response.json()
        assert isinstance(groups, list)
        assert len(groups) > 0
        
        # Check specific group
        test_group = next((g for g in groups if g["name"] == "test-servers"), None)
        assert test_group is not None
        assert "test-server" in test_group["static"]
        assert "web-server" in test_group["static"]
    
    def test_get_specific_address_group(self):
        """Test getting a specific address group"""
        response = client.get("/api/v1/configs/test_panorama/address-groups/test-servers")
        assert response.status_code == 200
        group = response.json()
        assert group["name"] == "test-servers"
        assert group["description"] == "Test server group"


class TestServiceEndpoints:
    """Test service object endpoints"""
    
    def test_get_services(self):
        """Test getting services"""
        response = client.get("/api/v1/configs/test_panorama/services")
        assert response.status_code == 200
        services = response.json()
        assert isinstance(services, list)
        assert len(services) >= 2
        
        # Check for expected services
        names = [svc["name"] for svc in services]
        assert "tcp-8080" in names
        assert "udp-5000" in names
    
    def test_get_services_by_protocol(self):
        """Test getting services filtered by protocol"""
        response = client.get("/api/v1/configs/test_panorama/services?protocol=tcp")
        assert response.status_code == 200
        services = response.json()
        assert all("tcp" in svc["protocol"] for svc in services)
    
    def test_get_specific_service(self):
        """Test getting a specific service"""
        response = client.get("/api/v1/configs/test_panorama/services/tcp-8080")
        assert response.status_code == 200
        service = response.json()
        assert service["name"] == "tcp-8080"
        assert service["protocol"]["tcp"]["port"] == "8080"
        assert service["description"] == "Test TCP service"


class TestServiceGroupEndpoints:
    """Test service group endpoints"""
    
    def test_get_service_groups(self):
        """Test getting service groups"""
        response = client.get("/api/v1/configs/test_panorama/service-groups")
        assert response.status_code == 200
        groups = response.json()
        assert isinstance(groups, list)
        assert len(groups) > 0


class TestSecurityProfileEndpoints:
    """Test security profile endpoints"""
    
    def test_get_vulnerability_profiles(self):
        """Test getting vulnerability profiles"""
        response = client.get("/api/v1/configs/test_panorama/security-profiles/vulnerability")
        assert response.status_code == 200
        profiles = response.json()
        assert isinstance(profiles, list)
        assert len(profiles) > 0
        
        # Check specific profile
        test_profile = next((p for p in profiles if p["name"] == "test-vuln-profile"), None)
        assert test_profile is not None
        assert len(test_profile["rules"]) > 0
    
    def test_get_url_filtering_profiles(self):
        """Test getting URL filtering profiles"""
        response = client.get("/api/v1/configs/test_panorama/security-profiles/url-filtering")
        assert response.status_code == 200
        profiles = response.json()
        assert isinstance(profiles, list)
        assert len(profiles) > 0
        
        # Check specific profile
        test_profile = next((p for p in profiles if p["name"] == "test-url-profile"), None)
        assert test_profile is not None
        assert test_profile["description"] == "Test URL filtering profile"


class TestDeviceGroupEndpoints:
    """Test device group endpoints"""
    
    def test_get_device_groups_summary(self):
        """Test getting device groups summary"""
        response = client.get("/api/v1/configs/test_panorama/device-groups")
        assert response.status_code == 200
        groups = response.json()
        assert isinstance(groups, list)
        assert len(groups) >= 2  # test-dg and child-dg
        
        # Check summary fields
        test_dg = next((g for g in groups if g["name"] == "test-dg"), None)
        assert test_dg is not None
        assert test_dg["devices_count"] == 2
        assert test_dg["address_count"] == 1
        assert test_dg["service_count"] == 1
        assert test_dg["pre_security_rules_count"] == 1
        assert test_dg["post_security_rules_count"] == 1
        assert test_dg["pre_nat_rules_count"] == 1
        assert "xpath" in test_dg
    
    def test_get_device_group_with_parent_filter(self):
        """Test getting device groups filtered by parent"""
        response = client.get("/api/v1/configs/test_panorama/device-groups?parent=test-dg")
        assert response.status_code == 200
        groups = response.json()
        assert len(groups) == 1
        assert groups[0]["name"] == "child-dg"
        assert groups[0]["parent_dg"] == "test-dg"
    
    def test_get_specific_device_group(self):
        """Test getting a specific device group"""
        response = client.get("/api/v1/configs/test_panorama/device-groups/test-dg")
        assert response.status_code == 200
        group = response.json()
        assert group["name"] == "test-dg"
        assert group["description"] == "Test device group"
    
    def test_get_device_group_addresses(self):
        """Test getting addresses for a device group"""
        response = client.get("/api/v1/configs/test_panorama/device-groups/test-dg/addresses")
        assert response.status_code == 200
        addresses = response.json()
        assert isinstance(addresses, list)
        assert len(addresses) == 1
        assert addresses[0]["name"] == "dg-server"
        assert addresses[0]["parent-device-group"] == "test-dg"
    
    def test_get_device_group_address_groups(self):
        """Test getting address groups for a device group"""
        response = client.get("/api/v1/configs/test_panorama/device-groups/test-dg/address-groups")
        assert response.status_code == 200
        groups = response.json()
        assert isinstance(groups, list)
        assert len(groups) == 1
        assert groups[0]["name"] == "dg-servers"
    
    def test_get_device_group_services(self):
        """Test getting services for a device group"""
        response = client.get("/api/v1/configs/test_panorama/device-groups/test-dg/services")
        assert response.status_code == 200
        services = response.json()
        assert isinstance(services, list)
        assert len(services) == 1
        assert services[0]["name"] == "tcp-9090"
    
    def test_get_device_group_service_groups(self):
        """Test getting service groups for a device group"""
        response = client.get("/api/v1/configs/test_panorama/device-groups/test-dg/service-groups")
        assert response.status_code == 200
        groups = response.json()
        assert isinstance(groups, list)
        assert len(groups) == 1
        assert groups[0]["name"] == "dg-services"
    
    def test_get_device_group_rules(self):
        """Test getting security rules for a device group"""
        # Test all rules
        response = client.get("/api/v1/configs/test_panorama/device-groups/test-dg/rules")
        assert response.status_code == 200
        rules = response.json()
        assert len(rules) == 2  # 1 pre + 1 post
        
        # Test pre rules only
        response = client.get("/api/v1/configs/test_panorama/device-groups/test-dg/rules?rulebase=pre")
        assert response.status_code == 200
        rules = response.json()
        assert len(rules) == 1
        assert rules[0]["name"] == "pre-rule-1"
        
        # Test post rules only
        response = client.get("/api/v1/configs/test_panorama/device-groups/test-dg/rules?rulebase=post")
        assert response.status_code == 200
        rules = response.json()
        assert len(rules) == 1
        assert rules[0]["name"] == "post-rule-1"
    
    def test_get_device_group_not_found(self):
        """Test accessing non-existent device group"""
        response = client.get("/api/v1/configs/test_panorama/device-groups/nonexistent/addresses")
        assert response.status_code == 200
        assert response.json() == []


class TestTemplateEndpoints:
    """Test template endpoints"""
    
    def test_get_templates(self):
        """Test getting templates"""
        response = client.get("/api/v1/configs/test_panorama/templates")
        assert response.status_code == 200
        templates = response.json()
        assert isinstance(templates, list)
        assert len(templates) == 1
        assert templates[0]["name"] == "test-template"
    
    def test_get_specific_template(self):
        """Test getting a specific template"""
        response = client.get("/api/v1/configs/test_panorama/templates/test-template")
        assert response.status_code == 200
        template = response.json()
        assert template["name"] == "test-template"
        assert template["description"] == "Test template"
        assert template["settings"]["default-vsys"] == "vsys1"


class TestTemplateStackEndpoints:
    """Test template stack endpoints"""
    
    def test_get_template_stacks(self):
        """Test getting template stacks"""
        response = client.get("/api/v1/configs/test_panorama/template-stacks")
        assert response.status_code == 200
        stacks = response.json()
        assert isinstance(stacks, list)
        assert len(stacks) == 1
        assert stacks[0]["name"] == "test-stack"
        assert "test-template" in stacks[0]["templates"]
    
    def test_get_specific_template_stack(self):
        """Test getting a specific template stack"""
        response = client.get("/api/v1/configs/test_panorama/template-stacks/test-stack")
        assert response.status_code == 200
        stack = response.json()
        assert stack["name"] == "test-stack"
        assert len(stack["devices"]) == 1


class TestLoggingEndpoints:
    """Test logging and schedule endpoints"""
    
    def test_get_log_profiles(self):
        """Test getting log profiles"""
        response = client.get("/api/v1/configs/test_panorama/log-profiles")
        assert response.status_code == 200
        profiles = response.json()
        assert isinstance(profiles, list)
        assert len(profiles) == 1
        assert profiles[0]["name"] == "test-log-profile"
    
    def test_get_schedules(self):
        """Test getting schedules"""
        response = client.get("/api/v1/configs/test_panorama/schedules")
        assert response.status_code == 200
        schedules = response.json()
        assert isinstance(schedules, list)
        assert len(schedules) == 1
        assert schedules[0]["name"] == "test-schedule"


class TestSearchEndpoints:
    """Test search endpoints"""
    
    def test_search_by_xpath(self):
        """Test searching by XPath"""
        # Get an address to get its xpath
        response = client.get("/api/v1/configs/test_panorama/addresses/test-server")
        assert response.status_code == 200
        address = response.json()
        xpath = address["xpath"]
        
        # Search by xpath
        response = client.get(f"/api/v1/configs/test_panorama/search/by-xpath?xpath={xpath}")
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0]["type"] == "address"
        assert results[0]["object"]["name"] == "test-server"
    
    def test_search_by_xpath_not_found(self):
        """Test searching with non-existent XPath"""
        response = client.get("/api/v1/configs/test_panorama/search/by-xpath?xpath=/nonexistent/path")
        assert response.status_code == 404


class TestSystemEndpoints:
    """Test system endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["configs_available"] > 0
        assert "test_panorama" in data["available_configs"]


class TestLocationTracking:
    """Test xpath and parent context tracking"""
    
    def test_shared_object_location(self):
        """Test that shared objects have correct location info"""
        response = client.get("/api/v1/configs/test_panorama/addresses/test-server")
        assert response.status_code == 200
        address = response.json()
        
        assert address["xpath"] is not None
        assert "/shared/address/entry[@name='test-server']" in address["xpath"]
        assert address["parent-device-group"] is None
        assert address["parent-template"] is None
        assert address["parent-vsys"] is None
    
    def test_device_group_object_location(self):
        """Test that device group objects have correct location info"""
        response = client.get("/api/v1/configs/test_panorama/device-groups/test-dg/addresses")
        assert response.status_code == 200
        addresses = response.json()
        
        dg_address = addresses[0]
        assert dg_address["parent-device-group"] == "test-dg"
        assert "/device-group/entry[@name='test-dg']" in dg_address["xpath"]
        assert dg_address["parent-template"] is None
        assert dg_address["parent-vsys"] is None
    
    def test_template_object_location(self):
        """Test that template objects have correct location info"""
        response = client.get("/api/v1/configs/test_panorama/addresses?location=template")
        assert response.status_code == 200
        addresses = response.json()
        
        # Find template address
        template_addresses = [a for a in addresses if a["name"] == "template-server"]
        assert len(template_addresses) == 1
        
        template_addr = template_addresses[0]
        assert template_addr["parent-template"] == "test-template"
        assert template_addr["parent-vsys"] == "vsys1"
        assert "/template/entry[@name='test-template']" in template_addr["xpath"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
Unit tests for API endpoints using the real Panorama configuration file.
Tests assert against actual expected outputs from the pan-bkp-202507151414.xml file.
"""

import pytest
import os
import sys
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# We need to delay the import until the environment is set by pytest
from fastapi.testclient import TestClient

# Set config path if not already set
if "CONFIG_FILES_PATH" not in os.environ:
    os.environ["CONFIG_FILES_PATH"] = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config-files"
    )

# Import app after environment is set
from main import app
client = TestClient(app)

# Configuration file name without extension
CONFIG_NAME = "pan-bkp-202507151414"


class TestRealConfigurationEndpoints:
    """Test configuration management endpoints with real config"""
    
    def test_list_configs(self):
        """Test listing available configurations"""
        response = client.get("/api/v1/configs")
        assert response.status_code == 200
        data = response.json()
        
        # Assert expected structure and content
        assert "configs" in data
        assert CONFIG_NAME in data["configs"]
        assert data["count"] >= 1
        # Path will vary based on environment, just check it ends correctly
        assert data["path"].endswith("config-files")
    
    def test_get_config_info(self):
        """Test getting configuration info for real config"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/info")
        assert response.status_code == 200
        data = response.json()
        
        # Assert expected fields exist
        assert data["name"] == CONFIG_NAME
        assert data["size"] > 1000000  # File is over 1MB
        assert "modified" in data
        assert data["loaded"] in [True, False]
        assert data["path"].endswith(f"{CONFIG_NAME}.xml")


class TestRealAddressEndpoints:
    """Test address endpoints with real configuration data"""
    
    def test_get_all_addresses(self):
        """Test getting all addresses from real config"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/addresses")
        assert response.status_code == 200
        addresses = response.json()
        
        # Assert we have addresses
        assert isinstance(addresses, list)
        assert len(addresses) > 0
        
        # Check for known addresses from the file
        address_names = [addr["name"] for addr in addresses]
        assert "dca.l.f9.je" in address_names
        assert "dc2.l.f9.je" in address_names
        assert "dc.l.f9.je" in address_names
        assert "caddy-ipv6" in address_names
        assert "gns3-vm.fy.loc" in address_names
        
        # Check specific address structure
        dca_addr = next(a for a in addresses if a["name"] == "dca.l.f9.je")
        assert dca_addr["fqdn"] == "dca.l.f9.je"
        assert "ipv6" in dca_addr["tag"]
        assert dca_addr["xpath"] is not None
        assert "/shared/address/entry[@name='dca.l.f9.je']" in dca_addr["xpath"]
        
        # Check IPv6 address
        caddy_addr = next(a for a in addresses if a["name"] == "caddy-ipv6")
        assert caddy_addr["ip-netmask"] == "fd52:16a2:30e:b503::1000:1111"
        assert "ipv6" in caddy_addr["tag"]
    
    def test_get_addresses_with_tag_filter(self):
        """Test filtering addresses by tag"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/addresses?tag=ipv6")
        assert response.status_code == 200
        addresses = response.json()
        
        # All returned addresses should have ipv6 tag
        assert all("ipv6" in addr["tag"] for addr in addresses if addr["tag"])
        assert len(addresses) >= 4  # At least the known IPv6 addresses
    
    def test_get_specific_address(self):
        """Test getting a specific address by name"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/addresses/gns3-vm.fy.loc")
        assert response.status_code == 200
        address = response.json()
        
        assert address["name"] == "gns3-vm.fy.loc"
        assert address["fqdn"] == "gns3-vm.fy.loc"
        assert address["ip-netmask"] is None
        assert address["xpath"] is not None
        assert address["parent-device-group"] is None  # Shared address


class TestRealAddressGroupEndpoints:
    """Test address group endpoints with real data"""
    
    def test_get_address_groups(self):
        """Test getting address groups from real config"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/address-groups")
        assert response.status_code == 200
        groups = response.json()
        
        assert isinstance(groups, list)
        assert len(groups) > 0
        
        # Check for known address groups
        group_names = [g["name"] for g in groups]
        assert "dag-quarantined-ips" in group_names
        
        # Check dynamic address group
        dag_group = next(g for g in groups if g["name"] == "dag-quarantined-ips")
        assert dag_group["dynamic"] is not None
        assert "'User-Quarantine'" in dag_group["dynamic"]["filter"]
    
    def test_get_specific_address_group(self):
        """Test getting a specific address group"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/address-groups/dag-quarantined-ips")
        assert response.status_code == 200
        group = response.json()
        
        assert group["name"] == "dag-quarantined-ips"
        assert group["description"] == "The tag User-Quarantine is being used for identification of users belonging to this DAG."
        assert group["dynamic"]["filter"] == "'User-Quarantine'"


class TestRealServiceEndpoints:
    """Test service endpoints with real data"""
    
    def test_get_services(self):
        """Test getting services from real config"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/services")
        assert response.status_code == 200
        services = response.json()
        
        assert isinstance(services, list)
        assert len(services) > 0
        
        # Check for known services
        service_names = [s["name"] for s in services]
        assert "all-tcp" in service_names
        assert "all-udp" in service_names
        assert "tcp-9443" in service_names
        assert "udp-12224" in service_names
        
        # Check specific service
        tcp_9443 = next(s for s in services if s["name"] == "tcp-9443")
        assert tcp_9443["protocol"]["tcp"]["port"] == "9443"
        assert tcp_9443["protocol"]["tcp"]["override"] is True
    
    def test_get_services_by_protocol(self):
        """Test filtering services by protocol"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/services?protocol=udp")
        assert response.status_code == 200
        services = response.json()
        
        # All services should have UDP protocol
        assert all("udp" in s["protocol"] for s in services)
        
        # Check known UDP services
        service_names = [s["name"] for s in services]
        assert "all-udp" in service_names
        assert "udp-12224" in service_names
        assert "udp-12004" in service_names


class TestRealSecurityProfileEndpoints:
    """Test security profile endpoints with real data"""
    
    def test_get_vulnerability_profiles(self):
        """Test getting vulnerability profiles"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/security-profiles/vulnerability")
        assert response.status_code == 200
        profiles = response.json()
        
        assert isinstance(profiles, list)
        assert len(profiles) > 0
        
        # Check for known profiles
        profile_names = [p["name"] for p in profiles]
        assert "fy-custom-VS-profile-dev2" in profile_names
        
        # Check specific profile
        fy_profile = next(p for p in profiles if p["name"] == "fy-custom-VS-profile-dev2")
        assert len(fy_profile["rules"]) > 0
        
        # Check rule structure
        rule_names = [r["name"] for r in fy_profile["rules"]]
        assert "simple-server-critical" in rule_names
        assert "simple-client-critical" in rule_names
        
        # Check specific rule
        server_critical = next(r for r in fy_profile["rules"] if r["name"] == "simple-server-critical")
        assert server_critical["action"] == "default"
        assert "critical" in server_critical["severity"]
        assert server_critical["host"] == "server"
        assert server_critical["packet_capture"] == "single-packet"
    
    def test_get_url_filtering_profiles(self):
        """Test getting URL filtering profiles"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/security-profiles/url-filtering")
        assert response.status_code == 200
        profiles = response.json()
        
        assert isinstance(profiles, list)
        # URL filtering profiles might be empty in this config
        # but the endpoint should still work


class TestRealDeviceGroupEndpoints:
    """Test device group endpoints with real data"""
    
    def test_get_device_groups_summary(self):
        """Test getting device groups summary"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/device-groups")
        assert response.status_code == 200
        groups = response.json()
        
        assert isinstance(groups, list)
        assert len(groups) > 0
        
        # Check for known device groups
        group_names = [g["name"] for g in groups]
        assert "fy-home-net-fw-dg" in group_names
        assert "fy-lab-parent-dg" in group_names
        
        # Check parent-child relationship
        fw_dg = next(g for g in groups if g["name"] == "fy-home-net-fw-dg")
        assert fw_dg["parent_dg"] == "fy-lab-parent-dg"
        
        # Check counts (summary fields)
        assert "devices_count" in fw_dg
        assert "address_count" in fw_dg
        assert "pre_security_rules_count" in fw_dg
        assert "post_security_rules_count" in fw_dg
    
    def test_get_device_group_addresses(self):
        """Test getting addresses for a specific device group"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/device-groups/fy-home-net-fw-dg/addresses")
        assert response.status_code == 200
        addresses = response.json()
        
        # Check if device group has addresses
        assert isinstance(addresses, list)
        # This device group might not have addresses, which is fine
    
    def test_get_device_group_rules(self):
        """Test getting security rules for device group"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/device-groups/fy-lab-parent-dg/rules")
        assert response.status_code == 200
        rules = response.json()
        
        assert isinstance(rules, list)
        if len(rules) > 0:
            # Check rule structure
            rule = rules[0]
            assert "name" in rule
            assert "from_" in rule
            assert "to" in rule
            assert "source" in rule
            assert "destination" in rule
            assert "action" in rule
            assert "xpath" in rule
            assert rule["parent-device-group"] == "fy-lab-parent-dg"


class TestRealTemplateEndpoints:
    """Test template endpoints with real data"""
    
    def test_get_templates(self):
        """Test getting templates"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/templates")
        assert response.status_code == 200
        templates = response.json()
        
        assert isinstance(templates, list)
        assert len(templates) > 0
        
        # Check for known templates
        template_names = [t["name"] for t in templates]
        assert "fy-home-net-template" in template_names
        assert "fy-home-net-fw-template" in template_names
        
        # Check template structure
        fw_template = next(t for t in templates if t["name"] == "fy-home-net-fw-template")
        assert fw_template["settings"]["default-vsys"] == "vsys1"
        assert fw_template["xpath"] is not None
    
    def test_get_specific_template(self):
        """Test getting a specific template"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/templates/fy-home-net-template")
        assert response.status_code == 200
        template = response.json()
        
        assert template["name"] == "fy-home-net-template"
        assert template["settings"]["default-vsys"] == "vsys1"


class TestRealTemplateStackEndpoints:
    """Test template stack endpoints with real data"""
    
    def test_get_template_stacks(self):
        """Test getting template stacks"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/template-stacks")
        assert response.status_code == 200
        stacks = response.json()
        
        assert isinstance(stacks, list)
        assert len(stacks) > 0
        
        # Check for known template stacks
        stack_names = [s["name"] for s in stacks]
        assert "fy_home_tmpl_stack" in stack_names
        
        # Check stack structure
        home_stack = next(s for s in stacks if s["name"] == "fy_home_tmpl_stack")
        assert "fy-home-net-fw-template" in home_stack["templates"]
        assert "fy-home-net-template" in home_stack["templates"]
        assert len(home_stack["devices"]) > 0


class TestRealLoggingEndpoints:
    """Test logging and schedule endpoints with real data"""
    
    def test_get_log_profiles(self):
        """Test getting log profiles"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/log-profiles")
        assert response.status_code == 200
        profiles = response.json()
        
        assert isinstance(profiles, list)
        assert len(profiles) > 0
        
        # Check for known log profiles
        profile_names = [p["name"] for p in profiles]
        assert "log-fwr-pro" in profile_names
    
    def test_get_schedules(self):
        """Test getting schedules"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/schedules")
        assert response.status_code == 200
        schedules = response.json()
        
        assert isinstance(schedules, list)
        assert len(schedules) > 0
        
        # Check for known schedules
        schedule_names = [s["name"] for s in schedules]
        assert "test-schedule" in schedule_names
        
        # Check schedule structure
        test_schedule = next(s for s in schedules if s["name"] == "test-schedule")
        assert test_schedule["schedule_type"]["recurring"]["daily"] is not None
        assert "00:00-23:45" in test_schedule["schedule_type"]["recurring"]["daily"]


class TestRealSearchEndpoints:
    """Test search functionality with real data"""
    
    def test_search_by_xpath_address(self):
        """Test searching for an address by xpath"""
        # First get an address to get its xpath
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/addresses/dc.l.f9.je")
        assert response.status_code == 200
        address = response.json()
        xpath = address["xpath"]
        
        # Now search by that xpath
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/search/by-xpath?xpath={xpath}")
        assert response.status_code == 200
        results = response.json()
        
        assert len(results) == 1
        assert results[0]["type"] == "address"
        assert results[0]["object"]["name"] == "dc.l.f9.je"
    
    def test_search_by_xpath_device_group(self):
        """Test searching for a device group by xpath"""
        # Get device group to get its xpath
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/device-groups/fy-home-net-fw-dg")
        assert response.status_code == 200
        dg = response.json()
        xpath = dg["xpath"]
        
        # Search by xpath
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/search/by-xpath?xpath={xpath}")
        assert response.status_code == 200
        results = response.json()
        
        assert len(results) == 1
        assert results[0]["type"] == "device-group"
        assert results[0]["object"]["name"] == "fy-home-net-fw-dg"


class TestRealLocationTracking:
    """Test xpath and parent context with real data"""
    
    def test_shared_objects_have_no_parent_context(self):
        """Test that shared objects don't have parent device group/template/vsys"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/addresses?location=shared")
        assert response.status_code == 200
        addresses = response.json()
        
        # All shared addresses should have no parent context
        for addr in addresses:
            assert addr["parent-device-group"] is None
            assert addr["parent-template"] is None
            assert addr["parent-vsys"] is None
            assert "/shared/address/" in addr["xpath"]
    
    def test_device_group_objects_have_correct_parent(self):
        """Test that device group objects have correct parent-device-group"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/device-groups/fy-home-net-fw-dg/addresses")
        assert response.status_code == 200
        addresses = response.json()
        
        # All addresses from this device group should have it as parent
        for addr in addresses:
            assert addr["parent-device-group"] == "fy-home-net-fw-dg"
            assert "/device-group/entry[@name='fy-home-net-fw-dg']" in addr["xpath"]
    
    def test_address_location_filtering(self):
        """Test filtering addresses by location type"""
        # Get all addresses
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/addresses")
        assert response.status_code == 200
        all_addresses = response.json()
        total_count = len(all_addresses)
        
        # Get shared only
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/addresses?location=shared")
        assert response.status_code == 200
        shared_addresses = response.json()
        
        # Get device-group only
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/addresses?location=device-group")
        assert response.status_code == 200
        dg_addresses = response.json()
        
        # Get template only
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/addresses?location=template")
        assert response.status_code == 200
        template_addresses = response.json()
        
        # Verify filtering worked
        assert all(a["parent-device-group"] is None for a in shared_addresses)
        assert all(a["parent-device-group"] is not None for a in dg_addresses)
        assert all(a["parent-template"] is not None for a in template_addresses)
        
        # The sum might not equal total due to overlaps, but each should be less than total
        assert len(shared_addresses) <= total_count
        assert len(dg_addresses) <= total_count
        assert len(template_addresses) <= total_count


class TestRealSystemEndpoints:
    """Test system endpoints"""
    
    def test_health_check(self):
        """Test health endpoint returns expected data"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["config_path"] == "/Users/fahad/code/pan-config-viewer-simple/config-files"
        assert data["configs_available"] >= 1
        assert CONFIG_NAME in data["available_configs"]
        assert data["configs_loaded"] >= 0  # May or may not be loaded yet


class TestEdgeCasesAndErrors:
    """Test error handling and edge cases"""
    
    def test_nonexistent_config(self):
        """Test accessing non-existent configuration"""
        response = client.get("/api/v1/configs/nonexistent/addresses")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_nonexistent_address(self):
        """Test getting non-existent address"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/addresses/does-not-exist")
        assert response.status_code == 404
    
    def test_nonexistent_device_group(self):
        """Test accessing non-existent device group"""
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/device-groups/fake-dg")
        assert response.status_code == 404
    
    def test_empty_device_group_objects(self):
        """Test device group with no objects returns empty list"""
        # Find a device group with no addresses
        response = client.get(f"/api/v1/configs/{CONFIG_NAME}/device-groups/fy-lab-parent-dg/addresses")
        assert response.status_code == 200
        # Should return empty list, not error
        assert isinstance(response.json(), list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
#!/usr/bin/env python3
"""
Comprehensive test suite for all API endpoints
This test suite uses HTTP requests to test the API running in Docker container
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import sys
import traceback
from typing import Dict, Any, List, Tuple

BASE_URL = "http://localhost:8000"
CONFIG_NAME = "pan-bkp-202507151414"


class APITester:
    """Test all API endpoints"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def test(self, name: str, func):
        """Run a test and track results"""
        try:
            func()
            self.passed += 1
            self.results.append((name, True, None))
            print(f"✅ {name}")
        except Exception as e:
            self.failed += 1
            self.results.append((name, False, str(e)))
            print(f"❌ {name}: {e}")
            if "--verbose" in sys.argv:
                traceback.print_exc()
    
    def assert_response(self, response, expected_status=200):
        """Assert response status and return JSON data"""
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}: {response.text}"
        if response.status_code == 200:
            return response.json()
        return None
    
    def run_all_tests(self):
        """Run all endpoint tests"""
        print("Testing All API Endpoints")
        print("=" * 50)
        
        # Health and Configuration Tests
        self.test("Health Check", self.test_health_check)
        self.test("List Configs", self.test_list_configs)
        self.test("Config Info", self.test_config_info)
        
        # Address Tests
        self.test("Get All Addresses", self.test_get_all_addresses)
        self.test("Get Specific Address", self.test_get_specific_address)
        self.test("Filter Addresses by Name", self.test_filter_addresses_by_name)
        self.test("Filter Addresses by Location", self.test_filter_addresses_by_location)
        
        # Address Group Tests
        self.test("Get Address Groups", self.test_get_address_groups)
        self.test("Get Specific Address Group", self.test_get_specific_address_group)
        
        # Service Tests
        self.test("Get Services", self.test_get_services)
        self.test("Get Specific Service", self.test_get_specific_service)
        self.test("Filter Services by Protocol", self.test_filter_services_by_protocol)
        
        # Service Group Tests
        self.test("Get Service Groups", self.test_get_service_groups)
        self.test("Get Specific Service Group", self.test_get_specific_service_group)
        
        # Security Profile Tests
        self.test("Get Vulnerability Profiles", self.test_get_vulnerability_profiles)
        self.test("Get Specific Vulnerability Profile", self.test_get_specific_vulnerability_profile)
        self.test("Get URL Filtering Profiles", self.test_get_url_filtering_profiles)
        self.test("Get Specific URL Filtering Profile", self.test_get_specific_url_filtering_profile)
        self.test("Get Antivirus Profiles", self.test_get_antivirus_profiles)
        self.test("Get Anti-Spyware Profiles", self.test_get_anti_spyware_profiles)
        self.test("Get Wildfire Profiles", self.test_get_wildfire_profiles)
        self.test("Get File Blocking Profiles", self.test_get_file_blocking_profiles)
        self.test("Get Data Filtering Profiles", self.test_get_data_filtering_profiles)
        self.test("Get DoS Protection Profiles", self.test_get_dos_protection_profiles)
        
        # Device Group Tests
        self.test("Get Device Groups Summary", self.test_get_device_groups_summary)
        self.test("Get Specific Device Group", self.test_get_specific_device_group)
        self.test("Filter Device Groups by Parent", self.test_filter_device_groups_by_parent)
        self.test("Get Device Group Addresses", self.test_get_device_group_addresses)
        self.test("Get Device Group Address Groups", self.test_get_device_group_address_groups)
        self.test("Get Device Group Services", self.test_get_device_group_services)
        self.test("Get Device Group Service Groups", self.test_get_device_group_service_groups)
        self.test("Get Device Group Rules", self.test_get_device_group_rules)
        self.test("Get Device Group Pre Rules", self.test_get_device_group_pre_rules)
        self.test("Get Device Group Post Rules", self.test_get_device_group_post_rules)
        self.test("Get Device Group NAT Rules", self.test_get_device_group_nat_rules)
        
        # Template Tests
        self.test("Get Templates", self.test_get_templates)
        self.test("Get Specific Template", self.test_get_specific_template)
        
        # Template Stack Tests
        self.test("Get Template Stacks", self.test_get_template_stacks)
        self.test("Get Specific Template Stack", self.test_get_specific_template_stack)
        
        # Log Profile Tests
        self.test("Get Log Profiles", self.test_get_log_profiles)
        self.test("Get Specific Log Profile", self.test_get_specific_log_profile)
        
        # Schedule Tests
        self.test("Get Schedules", self.test_get_schedules)
        self.test("Get Specific Schedule", self.test_get_specific_schedule)
        
        # Search Tests
        self.test("Search by XPath", self.test_search_by_xpath)
        self.test("Search Invalid XPath", self.test_search_invalid_xpath)
        
        # Location Tracking Tests
        self.test("Verify XPath in Objects", self.test_verify_xpath_in_objects)
        self.test("Verify Parent Context", self.test_verify_parent_context)
        
        # Error Handling Tests
        self.test("404 for Non-existent Config", self.test_404_nonexistent_config)
        self.test("404 for Non-existent Object", self.test_404_nonexistent_object)
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print(f"Test Summary: {self.passed} passed, {self.failed} failed")
        
        if self.failed > 0:
            print("\nFailed Tests:")
            for name, passed, error in self.results:
                if not passed:
                    print(f"  - {name}: {error}")
    
    # Health and Configuration Tests
    def test_health_check(self):
        response = requests.get(f"{BASE_URL}/api/v1/health")
        data = self.assert_response(response)
        assert data["status"] == "healthy"
        assert data["configs_available"] > 0
    
    def test_list_configs(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs")
        data = self.assert_response(response)
        assert CONFIG_NAME in data["configs"]
        assert data["count"] >= 1
    
    def test_config_info(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/info")
        data = self.assert_response(response)
        assert data["name"] == CONFIG_NAME
        assert "size" in data
        assert "modified" in data
    
    # Address Tests
    def test_get_all_addresses(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/addresses")
        addresses = self.assert_response(response)
        assert len(addresses) > 0
        
        # Verify fields
        addr = addresses[0]
        assert "name" in addr
        assert "xpath" in addr
        assert "parent-device-group" in addr
        assert "parent-template" in addr
        assert "parent-vsys" in addr
    
    def test_get_specific_address(self):
        # First get an address name
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/addresses")
        addresses = self.assert_response(response)
        addr_name = addresses[0]["name"]
        
        # Get specific address
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/addresses/{addr_name}")
        addr = self.assert_response(response)
        assert addr["name"] == addr_name
        assert addr["xpath"] is not None
    
    def test_filter_addresses_by_name(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/addresses?name=server")
        addresses = self.assert_response(response)
        # May be empty if no addresses contain "server"
        for addr in addresses:
            assert "server" in addr["name"].lower()
    
    def test_filter_addresses_by_location(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/addresses?location=shared")
        addresses = self.assert_response(response)
        for addr in addresses:
            assert addr["parent-device-group"] is None
    
    # Address Group Tests
    def test_get_address_groups(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/address-groups")
        groups = self.assert_response(response)
        assert isinstance(groups, list)
    
    def test_get_specific_address_group(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/address-groups")
        groups = self.assert_response(response)
        if groups:
            group_name = groups[0]["name"]
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/address-groups/{group_name}")
            group = self.assert_response(response)
            assert group["name"] == group_name
    
    # Service Tests
    def test_get_services(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/services")
        services = self.assert_response(response)
        assert isinstance(services, list)
    
    def test_get_specific_service(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/services")
        services = self.assert_response(response)
        if services:
            svc_name = services[0]["name"]
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/services/{svc_name}")
            svc = self.assert_response(response)
            assert svc["name"] == svc_name
    
    def test_filter_services_by_protocol(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/services?protocol=tcp")
        services = self.assert_response(response)
        for svc in services:
            assert "tcp" in svc["protocol"]
    
    # Service Group Tests
    def test_get_service_groups(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/service-groups")
        groups = self.assert_response(response)
        assert isinstance(groups, list)
    
    def test_get_specific_service_group(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/service-groups")
        groups = self.assert_response(response)
        if groups:
            group_name = groups[0]["name"]
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/service-groups/{group_name}")
            group = self.assert_response(response)
            assert group["name"] == group_name
    
    # Security Profile Tests
    def test_get_vulnerability_profiles(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/security-profiles/vulnerability")
        profiles = self.assert_response(response)
        assert isinstance(profiles, list)
    
    def test_get_specific_vulnerability_profile(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/security-profiles/vulnerability")
        profiles = self.assert_response(response)
        if profiles:
            profile_name = profiles[0]["name"]
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/security-profiles/vulnerability/{profile_name}")
            profile = self.assert_response(response)
            assert profile["name"] == profile_name
    
    def test_get_url_filtering_profiles(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/security-profiles/url-filtering")
        profiles = self.assert_response(response)
        assert isinstance(profiles, list)
    
    def test_get_specific_url_filtering_profile(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/security-profiles/url-filtering")
        profiles = self.assert_response(response)
        if profiles:
            profile_name = profiles[0]["name"]
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/security-profiles/url-filtering/{profile_name}")
            profile = self.assert_response(response)
            assert profile["name"] == profile_name
    
    def test_get_antivirus_profiles(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/security-profiles/antivirus")
        profiles = self.assert_response(response)
        assert isinstance(profiles, list)
    
    def test_get_anti_spyware_profiles(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/security-profiles/anti-spyware")
        profiles = self.assert_response(response)
        assert isinstance(profiles, list)
    
    def test_get_wildfire_profiles(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/security-profiles/wildfire")
        profiles = self.assert_response(response)
        assert isinstance(profiles, list)
    
    def test_get_file_blocking_profiles(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/security-profiles/file-blocking")
        profiles = self.assert_response(response)
        assert isinstance(profiles, list)
    
    def test_get_data_filtering_profiles(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/security-profiles/data-filtering")
        profiles = self.assert_response(response)
        assert isinstance(profiles, list)
    
    def test_get_dos_protection_profiles(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/security-profiles/dos-protection")
        profiles = self.assert_response(response)
        assert isinstance(profiles, list)
    
    # Device Group Tests
    def test_get_device_groups_summary(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups")
        groups = self.assert_response(response)
        assert isinstance(groups, list)
        if groups:
            dg = groups[0]
            assert "name" in dg
            assert "address_count" in dg
            assert "service_count" in dg
            assert "xpath" in dg
    
    def test_get_specific_device_group(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups")
        groups = self.assert_response(response)
        if groups:
            dg_name = groups[0]["name"]
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups/{dg_name}")
            dg = self.assert_response(response)
            assert dg["name"] == dg_name
    
    def test_filter_device_groups_by_parent(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups?parent=shared")
        groups = self.assert_response(response)
        # This tests the filter parameter works without error
    
    def test_get_device_group_addresses(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups")
        groups = self.assert_response(response)
        if groups:
            dg_name = groups[0]["name"]
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups/{dg_name}/addresses")
            addresses = self.assert_response(response)
            assert isinstance(addresses, list)
    
    def test_get_device_group_address_groups(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups")
        groups = self.assert_response(response)
        if groups:
            dg_name = groups[0]["name"]
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups/{dg_name}/address-groups")
            addr_groups = self.assert_response(response)
            assert isinstance(addr_groups, list)
    
    def test_get_device_group_services(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups")
        groups = self.assert_response(response)
        if groups:
            dg_name = groups[0]["name"]
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups/{dg_name}/services")
            services = self.assert_response(response)
            assert isinstance(services, list)
    
    def test_get_device_group_service_groups(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups")
        groups = self.assert_response(response)
        if groups:
            dg_name = groups[0]["name"]
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups/{dg_name}/service-groups")
            svc_groups = self.assert_response(response)
            assert isinstance(svc_groups, list)
    
    def test_get_device_group_rules(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups")
        groups = self.assert_response(response)
        if groups:
            dg_name = groups[0]["name"]
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups/{dg_name}/rules")
            rules = self.assert_response(response)
            assert isinstance(rules, list)
    
    def test_get_device_group_pre_rules(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups")
        groups = self.assert_response(response)
        if groups:
            dg_name = groups[0]["name"]
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups/{dg_name}/rules?rulebase=pre")
            rules = self.assert_response(response)
            assert isinstance(rules, list)
    
    def test_get_device_group_post_rules(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups")
        groups = self.assert_response(response)
        if groups:
            dg_name = groups[0]["name"]
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups/{dg_name}/rules?rulebase=post")
            rules = self.assert_response(response)
            assert isinstance(rules, list)
    
    def test_get_device_group_nat_rules(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups")
        groups = self.assert_response(response)
        if groups:
            dg_name = groups[0]["name"]
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups/{dg_name}/nat-rules")
            rules = self.assert_response(response)
            assert isinstance(rules, list)
    
    # Template Tests
    def test_get_templates(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/templates")
        templates = self.assert_response(response)
        assert isinstance(templates, list)
    
    def test_get_specific_template(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/templates")
        templates = self.assert_response(response)
        if templates:
            template_name = templates[0]["name"]
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/templates/{template_name}")
            template = self.assert_response(response)
            assert template["name"] == template_name
    
    # Template Stack Tests
    def test_get_template_stacks(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/template-stacks")
        stacks = self.assert_response(response)
        assert isinstance(stacks, list)
    
    def test_get_specific_template_stack(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/template-stacks")
        stacks = self.assert_response(response)
        if stacks:
            stack_name = stacks[0]["name"]
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/template-stacks/{stack_name}")
            stack = self.assert_response(response)
            assert stack["name"] == stack_name
    
    # Log Profile Tests
    def test_get_log_profiles(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/log-profiles")
        profiles = self.assert_response(response)
        assert isinstance(profiles, list)
    
    def test_get_specific_log_profile(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/log-profiles")
        profiles = self.assert_response(response)
        if profiles:
            profile_name = profiles[0]["name"]
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/log-profiles/{profile_name}")
            profile = self.assert_response(response)
            assert profile["name"] == profile_name
    
    # Schedule Tests
    def test_get_schedules(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/schedules")
        schedules = self.assert_response(response)
        assert isinstance(schedules, list)
    
    def test_get_specific_schedule(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/schedules")
        schedules = self.assert_response(response)
        if schedules:
            schedule_name = schedules[0]["name"]
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/schedules/{schedule_name}")
            schedule = self.assert_response(response)
            assert schedule["name"] == schedule_name
    
    # Search Tests
    def test_search_by_xpath(self):
        # Get an address with xpath
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/addresses")
        addresses = self.assert_response(response)
        if addresses:
            test_xpath = addresses[0]["xpath"]
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/search/by-xpath",
                                  params={"xpath": test_xpath})
            results = self.assert_response(response)
            assert len(results) > 0
    
    def test_search_invalid_xpath(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/search/by-xpath",
                              params={"xpath": "/invalid/xpath"})
        self.assert_response(response, expected_status=404)
    
    # Location Tracking Tests
    def test_verify_xpath_in_objects(self):
        # Test that all objects have xpath
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/addresses")
        addresses = self.assert_response(response)
        for addr in addresses[:5]:  # Check first 5
            assert addr["xpath"] is not None
            assert addr["xpath"].startswith("/")
    
    def test_verify_parent_context(self):
        # Test shared objects have no parent
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/addresses?location=shared")
        addresses = self.assert_response(response)
        for addr in addresses[:5]:  # Check first 5
            assert addr["parent-device-group"] is None
            assert addr["parent-template"] is None
    
    # Error Handling Tests
    def test_404_nonexistent_config(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/nonexistent/addresses")
        self.assert_response(response, expected_status=404)
    
    def test_404_nonexistent_object(self):
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/addresses/nonexistent-address-12345")
        self.assert_response(response, expected_status=404)


if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
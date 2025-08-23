#!/usr/bin/env python3
"""
Comprehensive test suite for device group detection functionality.
Tests various edge cases and validates proper parsing of device groups.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import os
from lxml import etree
from parser import PanoramaXMLParser
from models import DeviceGroup, DeviceGroupSummary


class TestDeviceGroupDetection:
    """Test suite for device group detection functionality."""
    
    @pytest.fixture
    def real_config_file(self):
        """Fixture for the real configuration file."""
        return "config-files/16-7-Panorama-Core-688.xml"
    
    @pytest.fixture
    def parser_with_real_config(self, real_config_file):
        """Fixture to create parser with real config file."""
        return PanoramaXMLParser(real_config_file)
    
    def test_config_type_detection(self, parser_with_real_config):
        """Test that the config is properly identified as Panorama."""
        assert parser_with_real_config.is_panorama is True
        assert parser_with_real_config.is_firewall is False
    
    def test_device_group_summaries_count(self, parser_with_real_config):
        """Test that all device groups are found in summaries."""
        summaries = parser_with_real_config.get_device_group_summaries()
        assert len(summaries) == 6
        
        # Verify specific device groups are present
        dg_names = [s.name for s in summaries]
        assert "TCN-DC-SWIFT-VSYS" in dg_names
        assert "TCN-DC-Tapping-Vsys" in dg_names
        assert "TCN-DC-Vsys1" in dg_names
        assert "KIZAD-DC-Vsys1" in dg_names
        assert "KIZAD-DC-Tapping-Vsys" in dg_names
        assert "KIZAD-DC-SWIFT-VSYS" in dg_names
    
    def test_device_group_summary_details(self, parser_with_real_config):
        """Test device group summary details are correctly parsed."""
        summaries = parser_with_real_config.get_device_group_summaries()
        
        # Find specific device group
        tcn_swift = next((s for s in summaries if s.name == "TCN-DC-SWIFT-VSYS"), None)
        assert tcn_swift is not None
        assert tcn_swift.description == "C119323"
        assert tcn_swift.devices_count == 2
        
        # Test device group with addresses
        tcn_vsys1 = next((s for s in summaries if s.name == "TCN-DC-Vsys1"), None)
        assert tcn_vsys1 is not None
        assert tcn_vsys1.address_count == 508
        assert tcn_vsys1.devices_count == 2
        
        # Test KIZAD device group
        kizad_vsys1 = next((s for s in summaries if s.name == "KIZAD-DC-Vsys1"), None)
        assert kizad_vsys1 is not None
        assert kizad_vsys1.address_count == 684
        assert kizad_vsys1.devices_count == 2
    
    def test_device_groups_full_details(self, parser_with_real_config):
        """Test full device group details are correctly parsed."""
        device_groups = parser_with_real_config.get_device_groups()
        assert len(device_groups) == 6
        
        # Test specific device group
        tcn_swift = next((dg for dg in device_groups if dg.name == "TCN-DC-SWIFT-VSYS"), None)
        assert tcn_swift is not None
        assert tcn_swift.description == "C119323"
        assert len(tcn_swift.devices) == 2
        
        # Verify device names
        device_names = [d["name"] for d in tcn_swift.devices]
        assert "010701000929" in device_names
        assert "010701000928" in device_names
    
    def test_device_group_xpath_location(self, parser_with_real_config):
        """Test that xpath location information is correctly added."""
        summaries = parser_with_real_config.get_device_group_summaries()
        
        # All device groups should have xpath
        for summary in summaries:
            assert hasattr(summary, 'xpath')
            assert summary.xpath is not None
            assert summary.xpath.startswith("/config/devices/entry")
    
    def test_device_group_specific_addresses(self, parser_with_real_config):
        """Test retrieving addresses for specific device groups."""
        # Test TCN-DC-Vsys1 which has 508 addresses
        addresses = parser_with_real_config.get_device_group_addresses("TCN-DC-Vsys1")
        assert len(addresses) == 508
        
        # Test KIZAD-DC-Vsys1 which has 684 addresses
        addresses = parser_with_real_config.get_device_group_addresses("KIZAD-DC-Vsys1")
        assert len(addresses) == 684
        
        # Test device group with few addresses
        addresses = parser_with_real_config.get_device_group_addresses("KIZAD-DC-SWIFT-VSYS")
        assert len(addresses) == 3
    
    def test_device_group_security_rules(self, parser_with_real_config):
        """Test retrieving security rules for device groups."""
        # Test pre-rulebase rules
        pre_rules = parser_with_real_config.get_device_group_security_rules("TCN-DC-SWIFT-VSYS", "pre")
        assert isinstance(pre_rules, list)
        
        # Test post-rulebase rules
        post_rules = parser_with_real_config.get_device_group_security_rules("TCN-DC-SWIFT-VSYS", "post")
        assert isinstance(post_rules, list)
        
        # Test all rules
        all_rules = parser_with_real_config.get_device_group_security_rules("TCN-DC-SWIFT-VSYS", "all")
        assert isinstance(all_rules, list)
        assert len(all_rules) == len(pre_rules) + len(post_rules)
    
    def test_nonexistent_device_group(self, parser_with_real_config):
        """Test behavior with non-existent device group."""
        addresses = parser_with_real_config.get_device_group_addresses("NonExistentDG")
        assert addresses == []
        
        rules = parser_with_real_config.get_device_group_security_rules("NonExistentDG")
        assert rules == []
    
    def test_device_group_services(self, parser_with_real_config):
        """Test retrieving services for device groups."""
        # Test TCN-DC-Vsys1 services
        services = parser_with_real_config.get_device_group_services("TCN-DC-Vsys1")
        assert isinstance(services, list)
        
        # Test KIZAD-DC-Vsys1 services
        services = parser_with_real_config.get_device_group_services("KIZAD-DC-Vsys1")
        assert isinstance(services, list)
    
    def test_edge_case_empty_device_group(self):
        """Test handling of device groups with no entries."""
        xml_content = """<?xml version="1.0"?>
        <config version="11.1.0">
            <devices>
                <entry name="localhost.localdomain">
                    <device-group>
                        <!-- Empty device-group element -->
                    </device-group>
                </entry>
            </devices>
        </config>"""
        
        # Create temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            parser = PanoramaXMLParser(temp_file)
            summaries = parser.get_device_group_summaries()
            assert summaries == []
            
            groups = parser.get_device_groups()
            assert groups == []
        finally:
            os.unlink(temp_file)
    
    def test_edge_case_no_devices_entry(self):
        """Test handling when devices/entry is missing."""
        xml_content = """<?xml version="1.0"?>
        <config version="11.1.0">
            <devices>
                <!-- No entry element -->
            </devices>
        </config>"""
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            parser = PanoramaXMLParser(temp_file)
            summaries = parser.get_device_group_summaries()
            assert summaries == []
            
            groups = parser.get_device_groups()
            assert groups == []
        finally:
            os.unlink(temp_file)
    
    def test_device_group_with_all_features(self):
        """Test device group with all possible features."""
        xml_content = """<?xml version="1.0"?>
        <config version="11.1.0">
            <devices>
                <entry name="localhost.localdomain">
                    <device-group>
                        <entry name="TestDG">
                            <description>Test Device Group</description>
                            <parent-dg>ParentDG</parent-dg>
                            <devices>
                                <entry name="device1">
                                    <vsys>
                                        <entry name="vsys1"/>
                                    </vsys>
                                </entry>
                                <entry name="device2"/>
                            </devices>
                            <address>
                                <entry name="addr1">
                                    <ip-netmask>10.0.0.1</ip-netmask>
                                </entry>
                            </address>
                            <address-group>
                                <entry name="addrgrp1">
                                    <static>
                                        <member>addr1</member>
                                    </static>
                                </entry>
                            </address-group>
                            <service>
                                <entry name="svc1">
                                    <protocol>
                                        <tcp>
                                            <port>80</port>
                                        </tcp>
                                    </protocol>
                                </entry>
                            </service>
                            <service-group>
                                <entry name="svcgrp1">
                                    <members>
                                        <member>svc1</member>
                                    </members>
                                </entry>
                            </service-group>
                            <pre-rulebase>
                                <security>
                                    <rules>
                                        <entry name="rule1">
                                            <from>
                                                <member>any</member>
                                            </from>
                                            <to>
                                                <member>any</member>
                                            </to>
                                            <source>
                                                <member>any</member>
                                            </source>
                                            <destination>
                                                <member>any</member>
                                            </destination>
                                            <service>
                                                <member>any</member>
                                            </service>
                                            <application>
                                                <member>any</member>
                                            </application>
                                            <action>allow</action>
                                        </entry>
                                    </rules>
                                </security>
                                <nat>
                                    <rules>
                                        <entry name="natrule1">
                                            <from>
                                                <member>any</member>
                                            </from>
                                            <to>
                                                <member>any</member>
                                            </to>
                                        </entry>
                                    </rules>
                                </nat>
                            </pre-rulebase>
                            <post-rulebase>
                                <security>
                                    <rules>
                                        <entry name="rule2">
                                            <action>deny</action>
                                        </entry>
                                    </rules>
                                </security>
                            </post-rulebase>
                        </entry>
                    </device-group>
                </entry>
            </devices>
        </config>"""
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            parser = PanoramaXMLParser(temp_file)
            
            # Test summaries
            summaries = parser.get_device_group_summaries()
            assert len(summaries) == 1
            summary = summaries[0]
            assert summary.name == "TestDG"
            assert summary.description == "Test Device Group"
            assert summary.parent_dg == "ParentDG"
            assert summary.devices_count == 2
            assert summary.address_count == 1
            assert summary.address_group_count == 1
            assert summary.service_count == 1
            assert summary.service_group_count == 1
            assert summary.pre_security_rules_count == 1
            assert summary.post_security_rules_count == 1
            assert summary.pre_nat_rules_count == 1
            assert summary.post_nat_rules_count == 0
            
            # Test full device group
            groups = parser.get_device_groups()
            assert len(groups) == 1
            group = groups[0]
            assert group.name == "TestDG"
            assert group.parent_dg == "ParentDG"
            assert len(group.devices) == 2
            assert group.pre_rules is not None
            assert "security" in group.pre_rules
            assert len(group.pre_rules["security"]) == 1
            
        finally:
            os.unlink(temp_file)


class TestDeviceGroupDataValidation:
    """Test data validation for device group parsing."""
    
    @pytest.fixture
    def parser_with_real_config(self):
        """Fixture to create parser with real config file."""
        return PanoramaXMLParser("config-files/16-7-Panorama-Core-688.xml")
    
    def test_device_group_summary_data_integrity(self, parser_with_real_config):
        """Test data integrity of device group summaries."""
        summaries = parser_with_real_config.get_device_group_summaries()
        
        # Expected device groups based on the test output
        expected_device_groups = {
            "TCN-DC-SWIFT-VSYS": {"devices": 2, "description": "C119323"},
            "TCN-DC-Tapping-Vsys": {"devices": 2, "description": "TCN DR CORE TAPPING VSYS"},
            "TCN-DC-Vsys1": {"devices": 2, "addresses": 508},
            "KIZAD-DC-Vsys1": {"devices": 2, "addresses": 684},
            "KIZAD-DC-Tapping-Vsys": {"devices": 2},
            "KIZAD-DC-SWIFT-VSYS": {"devices": 2, "addresses": 3}
        }
        
        # Verify all expected device groups are found
        found_names = {s.name for s in summaries}
        expected_names = set(expected_device_groups.keys())
        assert found_names == expected_names, f"Expected {expected_names}, found {found_names}"
        
        # Verify specific details
        for summary in summaries:
            expected = expected_device_groups[summary.name]
            assert summary.devices_count == expected.get("devices", 0)
            if "description" in expected:
                assert summary.description == expected["description"]
            if "addresses" in expected:
                assert summary.address_count == expected["addresses"]
    
    def test_device_group_hierarchy_validation(self, parser_with_real_config):
        """Test device group hierarchy and relationships."""
        device_groups = parser_with_real_config.get_device_groups()
        
        # All device groups should be at the same level (no parent_dg in this config)
        for group in device_groups:
            assert group.parent_dg is None
            
        # All device groups should have exactly 2 devices
        for group in device_groups:
            assert len(group.devices) == 2
            
        # Device names should match expected patterns
        all_device_names = set()
        for group in device_groups:
            for device in group.devices:
                all_device_names.add(device["name"])
        
        # These are the known device IDs in the config
        expected_devices = {"010701000929", "010701000928", "010701000930", "010701000659"}
        assert all_device_names == expected_devices


if __name__ == "__main__":
    # Run specific tests for debugging
    pytest.main([__file__, "-v", "-s"])
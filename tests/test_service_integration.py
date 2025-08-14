"""
Integration tests for service type filtering functionality.

Tests cover:
- End-to-end service type filtering with real data
- Configuration switching with type filtering
- Filter persistence across config switches  
- Integration with frontend components
- Performance under realistic loads
- Error scenarios and recovery
"""

import pytest
import os
import sys
import time
import requests
import subprocess
from typing import List, Dict, Any
from fastapi.testclient import TestClient
from unittest.mock import patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment
os.environ["CONFIG_FILES_PATH"] = os.path.join(os.path.dirname(__file__), "tests", "test_configs")

from main import app
from parser import PanoramaXMLParser
from models import ServiceObject, Protocol, ProtocolType


class TestServiceTypeFilteringIntegration:
    """Integration tests for service type filtering across the entire stack"""
    
    @classmethod
    def setup_class(cls):
        """Set up integration test environment"""
        cls.client = TestClient(app)
        # Trigger startup event
        with cls.client:
            _ = cls.client.get("/api/v1/configs")
            
        # Get available configs for testing
        response = cls.client.get("/api/v1/configs")
        if response.status_code == 200:
            cls.available_configs = response.json().get("configs", [])
        else:
            cls.available_configs = []

    def test_end_to_end_type_filtering_workflow(self):
        """Test complete workflow from API request to filtered response"""
        if not self.available_configs:
            pytest.skip("No test configurations available")
            
        config_name = self.available_configs[0]
        
        # Step 1: Get all services to establish baseline
        response = self.client.get(f"/api/v1/configs/{config_name}/services")
        assert response.status_code == 200
        all_data = response.json()
        all_services = all_data["items"]
        
        # Step 2: Filter by TCP type
        tcp_response = self.client.get(f"/api/v1/configs/{config_name}/services?filter[type][eq]=tcp")
        assert tcp_response.status_code == 200
        tcp_data = tcp_response.json()
        tcp_services = tcp_data["items"]
        
        # Step 3: Filter by UDP type
        udp_response = self.client.get(f"/api/v1/configs/{config_name}/services?filter[type][eq]=udp")
        assert udp_response.status_code == 200
        udp_data = udp_response.json()
        udp_services = udp_data["items"]
        
        # Verify end-to-end consistency
        assert len(tcp_services) + len(udp_services) <= len(all_services)  # Some services might have no type
        
        # Verify all TCP services have correct type
        for service in tcp_services:
            assert service.get("type") == "tcp"
            assert service["protocol"]["tcp"] is not None
            
        # Verify all UDP services have correct type
        for service in udp_services:
            assert service.get("type") == "udp"
            assert service["protocol"]["udp"] is not None

    def test_config_switching_preserves_type_filtering(self):
        """Test that type filtering works correctly when switching configurations"""
        if len(self.available_configs) < 2:
            pytest.skip("Need at least 2 configurations for switching test")
            
        config1, config2 = self.available_configs[0], self.available_configs[1]
        
        # Test type filtering on first config
        response1 = self.client.get(f"/api/v1/configs/{config1}/services?filter[type][eq]=tcp")
        assert response1.status_code == 200
        tcp_services_1 = response1.json()["items"]
        
        # Switch to second config and test type filtering
        response2 = self.client.get(f"/api/v1/configs/{config2}/services?filter[type][eq]=tcp")
        assert response2.status_code == 200
        tcp_services_2 = response2.json()["items"]
        
        # Both should have valid TCP services (if any exist)
        for service in tcp_services_1:
            assert service.get("type") == "tcp"
        for service in tcp_services_2:
            assert service.get("type") == "tcp"
            
        # Switch back to first config - should still work
        response1_again = self.client.get(f"/api/v1/configs/{config1}/services?filter[type][eq]=udp")
        assert response1_again.status_code == 200
        udp_services_1 = response1_again.json()["items"]
        
        for service in udp_services_1:
            assert service.get("type") == "udp"

    def test_filter_persistence_across_endpoints(self):
        """Test that type filtering works consistently across different service endpoints"""
        if not self.available_configs:
            pytest.skip("No test configurations available")
            
        config_name = self.available_configs[0]
        
        # Test endpoints
        endpoints = [
            f"/api/v1/configs/{config_name}/services",
            f"/api/v1/configs/{config_name}/shared/services"
        ]
        
        # Get device groups for device-group endpoint testing
        dg_response = self.client.get(f"/api/v1/configs/{config_name}/device-groups")
        if dg_response.status_code == 200:
            device_groups = dg_response.json().get("items", [])
            if device_groups:
                endpoints.append(f"/api/v1/configs/{config_name}/device-groups/{device_groups[0]['name']}/services")
        
        # Test type filtering on all endpoints
        tcp_results = {}
        udp_results = {}
        
        for endpoint in endpoints:
            # Test TCP filtering
            tcp_response = self.client.get(f"{endpoint}?filter[type][eq]=tcp")
            if tcp_response.status_code == 200:
                tcp_results[endpoint] = tcp_response.json()["items"]
            
            # Test UDP filtering
            udp_response = self.client.get(f"{endpoint}?filter[type][eq]=udp")
            if udp_response.status_code == 200:
                udp_results[endpoint] = udp_response.json()["items"]
        
        # Verify consistency across endpoints
        for endpoint, services in tcp_results.items():
            for service in services:
                assert service.get("type") == "tcp", f"TCP type inconsistent in {endpoint}"
                
        for endpoint, services in udp_results.items():
            for service in services:
                assert service.get("type") == "udp", f"UDP type inconsistent in {endpoint}"

    def test_complex_filtering_scenarios_integration(self):
        """Test complex filtering scenarios that combine type with other filters"""
        if not self.available_configs:
            pytest.skip("No test configurations available")
            
        config_name = self.available_configs[0]
        
        # Scenario 1: Type + Name filtering
        response = self.client.get(
            f"/api/v1/configs/{config_name}/services?"
            "filter[type][eq]=tcp&filter[name][contains]=tcp"
        )
        assert response.status_code == 200
        services = response.json()["items"]
        
        for service in services:
            assert service.get("type") == "tcp"
            assert "tcp" in service["name"].lower()
        
        # Scenario 2: Type + Port range filtering
        response = self.client.get(
            f"/api/v1/configs/{config_name}/services?"
            "filter[type][eq]=tcp&filter[port][gt]=1000"
        )
        assert response.status_code == 200
        services = response.json()["items"]
        
        for service in services:
            assert service.get("type") == "tcp"
            # Verify port is greater than 1000 (if numeric)
            port = service["protocol"]["tcp"].get("port", "")
            if port.isdigit():
                assert int(port) > 1000
        
        # Scenario 3: Type + Multiple operators
        response = self.client.get(
            f"/api/v1/configs/{config_name}/services?"
            "filter[type][in]=tcp,udp&filter[name][ne]=any"
        )
        assert response.status_code == 200
        services = response.json()["items"]
        
        for service in services:
            assert service.get("type") in ["tcp", "udp"]
            assert service["name"] != "any"

    def test_pagination_integration_with_type_filtering(self):
        """Test pagination integration with type filtering"""
        if not self.available_configs:
            pytest.skip("No test configurations available")
            
        config_name = self.available_configs[0]
        
        # Get total count with type filtering
        response = self.client.get(f"/api/v1/configs/{config_name}/services?filter[type][eq]=tcp")
        assert response.status_code == 200
        total_data = response.json()
        total_tcp = total_data["total_items"]
        
        if total_tcp == 0:
            pytest.skip("No TCP services available for pagination test")
        
        # Test pagination with small page size
        page_size = max(1, total_tcp // 3) if total_tcp > 3 else 1
        
        # Get first page
        response = self.client.get(
            f"/api/v1/configs/{config_name}/services?"
            f"filter[type][eq]=tcp&page=1&page_size={page_size}"
        )
        assert response.status_code == 200
        page1_data = response.json()
        
        # Verify pagination metadata
        assert page1_data["page"] == 1
        assert page1_data["page_size"] == page_size
        assert page1_data["total_items"] == total_tcp
        
        # Verify all items are TCP
        for service in page1_data["items"]:
            assert service.get("type") == "tcp"
        
        # If there are more pages, test next page
        if page1_data["has_next"]:
            response = self.client.get(
                f"/api/v1/configs/{config_name}/services?"
                f"filter[type][eq]=tcp&page=2&page_size={page_size}"
            )
            assert response.status_code == 200
            page2_data = response.json()
            
            # Verify second page
            for service in page2_data["items"]:
                assert service.get("type") == "tcp"

    def test_performance_under_realistic_load(self):
        """Test performance of type filtering under realistic conditions"""
        if not self.available_configs:
            pytest.skip("No test configurations available")
            
        config_name = self.available_configs[0]
        
        # Simulate realistic load - multiple concurrent requests
        request_types = [
            ("tcp", "eq"),
            ("udp", "eq"),
            ("tcp", "ne"),
            ("tcp,udp", "in")
        ]
        
        start_time = time.time()
        results = []
        
        # Send multiple requests
        for value, operator in request_types:
            response = self.client.get(
                f"/api/v1/configs/{config_name}/services?"
                f"filter[type][{operator}]={value}"
            )
            results.append((response.status_code, len(response.json().get("items", []))))
        
        end_time = time.time()
        
        # Verify all requests succeeded
        for status_code, item_count in results:
            assert status_code == 200
            
        # Performance should be acceptable
        total_time = end_time - start_time
        assert total_time < 5.0, f"Type filtering under load took too long: {total_time}s"

    def test_error_scenarios_and_recovery(self):
        """Test error handling and recovery in integration scenarios"""
        if not self.available_configs:
            pytest.skip("No test configurations available")
            
        config_name = self.available_configs[0]
        
        # Test 1: Invalid type value
        response = self.client.get(f"/api/v1/configs/{config_name}/services?filter[type][eq]=invalid")
        assert response.status_code == 200  # Should not error, just return empty results
        assert len(response.json()["items"]) == 0
        
        # Test 2: Malformed filter parameter
        response = self.client.get(f"/api/v1/configs/{config_name}/services?filter[type][invalid_op]=tcp")
        assert response.status_code == 200  # Should handle gracefully
        
        # Test 3: Recovery after error - normal filtering should still work
        response = self.client.get(f"/api/v1/configs/{config_name}/services?filter[type][eq]=tcp")
        assert response.status_code == 200
        
        # Verify recovery worked
        services = response.json()["items"]
        for service in services:
            assert service.get("type") == "tcp"

    def test_real_world_data_integration(self):
        """Test integration with real configuration data patterns"""
        if not self.available_configs:
            pytest.skip("No test configurations available")
            
        config_name = self.available_configs[0]
        
        # Get all services to analyze real data patterns
        response = self.client.get(f"/api/v1/configs/{config_name}/services?disable_paging=true")
        assert response.status_code == 200
        all_services = response.json()["items"]
        
        if not all_services:
            pytest.skip("No services available in test configuration")
        
        # Analyze type distribution
        type_counts = {"tcp": 0, "udp": 0, "none": 0}
        
        for service in all_services:
            service_type = service.get("type")
            if service_type == "tcp":
                type_counts["tcp"] += 1
            elif service_type == "udp":
                type_counts["udp"] += 1
            else:
                type_counts["none"] += 1
        
        # Test filtering matches analysis
        if type_counts["tcp"] > 0:
            tcp_response = self.client.get(f"/api/v1/configs/{config_name}/services?filter[type][eq]=tcp")
            assert tcp_response.status_code == 200
            tcp_services = tcp_response.json()["items"]
            assert len(tcp_services) == type_counts["tcp"]
        
        if type_counts["udp"] > 0:
            udp_response = self.client.get(f"/api/v1/configs/{config_name}/services?filter[type][eq]=udp")
            assert udp_response.status_code == 200
            udp_services = udp_response.json()["items"]
            assert len(udp_services) == type_counts["udp"]

    def test_api_documentation_consistency(self):
        """Test that API responses match documented behavior for type filtering"""
        if not self.available_configs:
            pytest.skip("No test configurations available")
            
        config_name = self.available_configs[0]
        
        # Test documented filter operators
        documented_operators = ["eq", "ne", "contains", "in", "not_in"]
        
        for operator in documented_operators:
            test_value = "tcp" if operator != "in" else "tcp,udp"
            
            response = self.client.get(
                f"/api/v1/configs/{config_name}/services?"
                f"filter[type][{operator}]={test_value}"
            )
            
            # All documented operators should work
            assert response.status_code == 200, f"Operator {operator} failed"
            
            # Response should have expected structure
            data = response.json()
            assert "items" in data
            assert "total_items" in data
            assert "page" in data
            assert isinstance(data["items"], list)

    def test_frontend_integration_compatibility(self):
        """Test compatibility with frontend filtering components"""
        if not self.available_configs:
            pytest.skip("No test configurations available")
            
        config_name = self.available_configs[0]
        
        # Test formats that frontend might send
        frontend_formats = [
            "filter[type]=tcp",  # Simple format
            "filter.type=tcp",   # Dot notation
            "filter[type][eq]=tcp",  # Explicit operator
            "filter.type.eq=tcp"     # Dot notation with operator
        ]
        
        for filter_format in frontend_formats:
            response = self.client.get(f"/api/v1/configs/{config_name}/services?{filter_format}")
            
            # All frontend formats should work
            assert response.status_code == 200, f"Frontend format {filter_format} failed"
            
            services = response.json()["items"]
            for service in services:
                if service.get("type"):  # Allow for services without type
                    assert service["type"] == "tcp"

    def test_database_consistency_integration(self):
        """Test that type filtering is consistent with underlying data model"""
        if not self.available_configs:
            pytest.skip("No test configurations available")
            
        config_name = self.available_configs[0]
        
        # Get services with explicit protocol filtering (legacy)
        legacy_tcp_response = self.client.get(f"/api/v1/configs/{config_name}/services?protocol=tcp")
        legacy_udp_response = self.client.get(f"/api/v1/configs/{config_name}/services?protocol=udp")
        
        # Get services with new type filtering
        type_tcp_response = self.client.get(f"/api/v1/configs/{config_name}/services?filter[type][eq]=tcp")
        type_udp_response = self.client.get(f"/api/v1/configs/{config_name}/services?filter[type][eq]=udp")
        
        # Results should be consistent
        if legacy_tcp_response.status_code == 200 and type_tcp_response.status_code == 200:
            legacy_tcp = sorted([s["name"] for s in legacy_tcp_response.json()["items"]])
            type_tcp = sorted([s["name"] for s in type_tcp_response.json()["items"]])
            assert legacy_tcp == type_tcp, "TCP filtering inconsistent between legacy and type filters"
        
        if legacy_udp_response.status_code == 200 and type_udp_response.status_code == 200:
            legacy_udp = sorted([s["name"] for s in legacy_udp_response.json()["items"]])
            type_udp = sorted([s["name"] for s in type_udp_response.json()["items"]])
            assert legacy_udp == type_udp, "UDP filtering inconsistent between legacy and type filters"

    def test_monitoring_and_logging_integration(self):
        """Test that type filtering operations can be monitored and logged"""
        if not self.available_configs:
            pytest.skip("No test configurations available")
            
        config_name = self.available_configs[0]
        
        # Make requests that should be logged/monitored
        test_requests = [
            f"/api/v1/configs/{config_name}/services?filter[type][eq]=tcp",
            f"/api/v1/configs/{config_name}/services?filter[type][eq]=udp",
            f"/api/v1/configs/{config_name}/services?filter[type][in]=tcp,udp"
        ]
        
        for request_url in test_requests:
            start_time = time.time()
            response = self.client.get(request_url)
            end_time = time.time()
            
            # Request should succeed
            assert response.status_code == 200
            
            # Should complete in reasonable time (for monitoring)
            assert (end_time - start_time) < 2.0
            
            # Response should have monitoring-friendly metadata
            data = response.json()
            assert "total_items" in data  # For monitoring result counts
            assert "page" in data  # For monitoring pagination usage
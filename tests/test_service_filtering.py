"""
Comprehensive tests for service type filtering functionality.

Tests cover:
- API endpoint filtering by service type (TCP/UDP)
- Various filter operators (eq, ne, contains, in, not_in)
- Bracket and dot notation support
- Combined filters with other service properties
- Pagination with type filtering
- Error handling for invalid type values
- Case sensitivity handling
"""

import pytest
import os
import sys
from typing import List, Dict, Any
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment
os.environ["CONFIG_FILES_PATH"] = os.path.join(os.path.dirname(__file__), "tests", "test_configs")

from main import app
from models import ServiceObject, Protocol, ProtocolType


class TestServiceTypeFiltering:
    """Test service type filtering via API endpoints"""
    
    @classmethod
    def setup_class(cls):
        """Set up test client"""
        cls.client = TestClient(app)
        # Trigger startup event
        with cls.client:
            _ = cls.client.get("/api/v1/configs")

    def test_filter_services_by_type_tcp_eq(self):
        """Test filtering services by type=tcp using equals operator"""
        # Test bracket notation
        response = self.client.get("/api/v1/configs/test_panorama/services?filter[type][eq]=tcp")
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        services = data["items"]
        assert len(services) > 0
        
        # All services should be TCP type
        for service in services:
            assert service.get("type") == "tcp"
            assert service["protocol"]["tcp"] is not None
            assert service["protocol"]["udp"] is None
        
        # Verify specific services
        tcp_service_names = [s["name"] for s in services]
        assert "tcp-8080" in tcp_service_names

    def test_filter_services_by_type_tcp_dot_notation(self):
        """Test filtering services by type=tcp using dot notation"""
        response = self.client.get("/api/v1/configs/test_panorama/services?filter.type.eq=tcp")
        assert response.status_code == 200
        data = response.json()
        
        services = data["items"]
        assert len(services) > 0
        
        # All services should be TCP type
        for service in services:
            assert service.get("type") == "tcp"
            assert service["protocol"]["tcp"] is not None

    def test_filter_services_by_type_udp_eq(self):
        """Test filtering services by type=udp using equals operator"""
        response = self.client.get("/api/v1/configs/test_panorama/services?filter[type][eq]=udp")
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        services = data["items"]
        assert len(services) > 0
        
        # All services should be UDP type
        for service in services:
            assert service.get("type") == "udp"
            assert service["protocol"]["udp"] is not None
            assert service["protocol"]["tcp"] is None
        
        # Verify specific services
        udp_service_names = [s["name"] for s in services]
        assert "udp-5000" in udp_service_names

    def test_filter_services_by_type_ne(self):
        """Test filtering services with type not equals operator"""
        # Get all services first
        all_response = self.client.get("/api/v1/configs/test_panorama/services")
        all_services = all_response.json()["items"]
        
        # Filter out TCP services
        response = self.client.get("/api/v1/configs/test_panorama/services?filter[type][ne]=tcp")
        assert response.status_code == 200
        data = response.json()
        
        services = data["items"]
        # Should only have UDP services
        for service in services:
            assert service.get("type") != "tcp"
            if service.get("type"):  # If type is set, it should be udp
                assert service.get("type") == "udp"

    def test_filter_services_by_type_contains(self):
        """Test filtering services with type contains operator"""
        # Should find both TCP and UDP services containing 'p'
        response = self.client.get("/api/v1/configs/test_panorama/services?filter[type][contains]=p")
        assert response.status_code == 200
        data = response.json()
        
        services = data["items"]
        assert len(services) > 0
        
        # All services should have 'p' in their type (tcp or udp)
        for service in services:
            service_type = service.get("type", "")
            assert "p" in service_type.lower()

    def test_filter_services_by_type_in(self):
        """Test filtering services with type in operator"""
        # Test with single value
        response = self.client.get("/api/v1/configs/test_panorama/services?filter[type][in]=tcp")
        assert response.status_code == 200
        data = response.json()
        
        services = data["items"]
        assert len(services) > 0
        
        for service in services:
            assert service.get("type") == "tcp"
        
        # Test with multiple values
        response = self.client.get("/api/v1/configs/test_panorama/services?filter[type][in]=tcp,udp")
        assert response.status_code == 200
        data = response.json()
        
        services = data["items"]
        assert len(services) > 0
        
        for service in services:
            assert service.get("type") in ["tcp", "udp"]

    def test_filter_services_by_type_not_in(self):
        """Test filtering services with type not_in operator"""
        response = self.client.get("/api/v1/configs/test_panorama/services?filter[type][not_in]=tcp")
        assert response.status_code == 200
        data = response.json()
        
        services = data["items"]
        
        # Should only have non-TCP services
        for service in services:
            assert service.get("type") != "tcp"

    def test_type_field_included_in_response(self):
        """Test that type field is always included in API responses"""
        response = self.client.get("/api/v1/configs/test_panorama/services")
        assert response.status_code == 200
        data = response.json()
        
        services = data["items"]
        assert len(services) > 0
        
        for service in services:
            # Type field should always be present
            assert "type" in service
            # Type should be either tcp, udp, or None
            service_type = service.get("type")
            assert service_type in ["tcp", "udp", None]

    def test_combined_filters_name_and_type(self):
        """Test combined filtering by name and type"""
        response = self.client.get(
            "/api/v1/configs/test_panorama/services?"
            "filter[name][contains]=tcp&filter[type][eq]=tcp"
        )
        assert response.status_code == 200
        data = response.json()
        
        services = data["items"]
        assert len(services) > 0
        
        for service in services:
            assert "tcp" in service["name"].lower()
            assert service.get("type") == "tcp"
            assert service["protocol"]["tcp"] is not None

    def test_combined_filters_port_and_type(self):
        """Test combined filtering by port and type"""
        response = self.client.get(
            "/api/v1/configs/test_panorama/services?"
            "filter[port][eq]=8080&filter[type][eq]=tcp"
        )
        assert response.status_code == 200
        data = response.json()
        
        services = data["items"]
        
        for service in services:
            assert service.get("type") == "tcp"
            assert service["protocol"]["tcp"]["port"] == "8080"

    def test_pagination_with_type_filtering(self):
        """Test pagination works correctly with type filtering"""
        # Test with small page size to verify pagination
        response = self.client.get(
            "/api/v1/configs/test_panorama/services?"
            "filter[type][eq]=tcp&page=1&page_size=1"
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should have pagination metadata
        assert "total_items" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert "has_next" in data
        assert "has_previous" in data
        
        # Check items
        services = data["items"]
        assert len(services) <= 1  # Should respect page_size
        
        if services:
            assert services[0].get("type") == "tcp"

    def test_pagination_disable_with_type_filtering(self):
        """Test disabling pagination with type filtering"""
        response = self.client.get(
            "/api/v1/configs/test_panorama/services?"
            "filter[type][eq]=tcp&disable_paging=true"
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should have all TCP services without pagination
        assert data["page"] == 1
        assert data["total_pages"] == 1
        assert data["has_next"] is False
        assert data["has_previous"] is False
        
        services = data["items"]
        for service in services:
            assert service.get("type") == "tcp"

    def test_invalid_type_values(self):
        """Test behavior with invalid type filter values"""
        # Test invalid protocol type
        response = self.client.get("/api/v1/configs/test_panorama/services?filter[type][eq]=icmp")
        assert response.status_code == 200
        data = response.json()
        
        # Should return empty results since icmp is not a valid service type
        services = data["items"]
        assert len(services) == 0

    def test_case_sensitivity_type_filtering(self):
        """Test case sensitivity in type filtering"""
        # Test uppercase TCP
        response = self.client.get("/api/v1/configs/test_panorama/services?filter[type][eq]=TCP")
        assert response.status_code == 200
        data = response.json()
        
        # Should return empty since filtering is case sensitive and we store lowercase
        services = data["items"]
        assert len(services) == 0
        
        # Test correct lowercase
        response = self.client.get("/api/v1/configs/test_panorama/services?filter[type][eq]=tcp")
        assert response.status_code == 200
        data = response.json()
        
        services = data["items"]
        assert len(services) > 0
        
        for service in services:
            assert service.get("type") == "tcp"

    def test_empty_type_filtering(self):
        """Test filtering with empty type value"""
        response = self.client.get("/api/v1/configs/test_panorama/services?filter[type][eq]=")
        assert response.status_code == 200
        data = response.json()
        
        # Should handle empty string gracefully
        services = data["items"]
        # Results depend on whether there are services with None/empty type
        assert isinstance(services, list)

    def test_device_group_services_type_filtering(self):
        """Test type filtering works for device group services"""
        response = self.client.get(
            "/api/v1/configs/test_panorama/device-groups/test-dg/services?"
            "filter[type][eq]=tcp"
        )
        assert response.status_code == 200
        data = response.json()
        
        services = data["items"]
        
        for service in services:
            assert service.get("type") == "tcp"
            assert service["protocol"]["tcp"] is not None
            # Should have device group location info
            assert service.get("parent-device-group") == "test-dg"

    def test_shared_services_type_filtering(self):
        """Test type filtering works for shared services"""
        response = self.client.get(
            "/api/v1/configs/test_panorama/shared/services?"
            "filter[type][eq]=udp"
        )
        assert response.status_code == 200
        data = response.json()
        
        services = data["items"]
        
        for service in services:
            assert service.get("type") == "udp"
            assert service["protocol"]["udp"] is not None
            # Shared services should not have device group
            assert service.get("parent-device-group") is None

    def test_legacy_protocol_filter_compatibility(self):
        """Test that legacy protocol filter still works alongside type filter"""
        # Test legacy protocol parameter
        response = self.client.get("/api/v1/configs/test_panorama/services?protocol=tcp")
        assert response.status_code == 200
        legacy_data = response.json()
        
        # Test new type filter
        response = self.client.get("/api/v1/configs/test_panorama/services?filter[type][eq]=tcp")
        assert response.status_code == 200
        type_data = response.json()
        
        # Results should be the same
        legacy_services = sorted(legacy_data["items"], key=lambda x: x["name"])
        type_services = sorted(type_data["items"], key=lambda x: x["name"])
        
        assert len(legacy_services) == len(type_services)
        
        for legacy_svc, type_svc in zip(legacy_services, type_services):
            assert legacy_svc["name"] == type_svc["name"]
            assert legacy_svc.get("type") == type_svc.get("type")

    def test_type_filter_with_description_and_tags(self):
        """Test type filtering combined with description and tag filters"""
        response = self.client.get(
            "/api/v1/configs/test_panorama/services?"
            "filter[type][eq]=tcp&"
            "filter[description][contains]=test&"
            "filter[tag][contains]=service"
        )
        assert response.status_code == 200
        data = response.json()
        
        services = data["items"]
        
        for service in services:
            assert service.get("type") == "tcp"
            if service.get("description"):
                assert "test" in service["description"].lower()
            # Note: tag filtering depends on test data having appropriate tags

    def test_all_filter_operators_with_type(self):
        """Test all supported operators work with type field"""
        operators_to_test = [
            ("eq", "tcp"),
            ("ne", "tcp"), 
            ("contains", "c"),
            ("in", "tcp,udp"),
            ("not_in", "tcp")
        ]
        
        for operator, value in operators_to_test:
            response = self.client.get(
                f"/api/v1/configs/test_panorama/services?filter[type][{operator}]={value}"
            )
            assert response.status_code == 200, f"Failed for operator {operator}"
            data = response.json()
            
            # Should return valid response structure
            assert "items" in data
            assert "total_items" in data
            assert isinstance(data["items"], list)

    def test_type_field_consistency_across_endpoints(self):
        """Test that type field is consistent across different service endpoints"""
        endpoints = [
            "/api/v1/configs/test_panorama/services",
            "/api/v1/configs/test_panorama/shared/services",
            "/api/v1/configs/test_panorama/device-groups/test-dg/services"
        ]
        
        all_services = []
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            assert response.status_code == 200
            data = response.json()
            services = data["items"]
            
            for service in services:
                # Type field should always be present
                assert "type" in service
                # Type should match protocol configuration
                if service["protocol"].get("tcp"):
                    assert service.get("type") == "tcp"
                elif service["protocol"].get("udp"):
                    assert service.get("type") == "udp"
                
                all_services.append(service)
        
        assert len(all_services) > 0

    def test_error_handling_invalid_config(self):
        """Test error handling when config doesn't exist"""
        response = self.client.get(
            "/api/v1/configs/nonexistent/services?filter[type][eq]=tcp"
        )
        assert response.status_code == 404

    def test_type_filtering_performance_with_large_result_set(self):
        """Test type filtering performance characteristics"""
        import time
        
        start_time = time.time()
        response = self.client.get("/api/v1/configs/test_panorama/services?filter[type][eq]=tcp")
        end_time = time.time()
        
        assert response.status_code == 200
        # Should complete within reasonable time (adjust threshold as needed)
        execution_time = end_time - start_time
        assert execution_time < 2.0, f"Type filtering took too long: {execution_time}s"

    def test_multiple_type_filters_precedence(self):
        """Test behavior when multiple type filters are specified"""
        # This tests how the system handles conflicting type filters
        response = self.client.get(
            "/api/v1/configs/test_panorama/services?"
            "filter[type][eq]=tcp&filter[type][ne]=tcp"
        )
        assert response.status_code == 200
        data = response.json()
        
        # With conflicting filters, should return empty results (AND logic)
        services = data["items"]
        assert len(services) == 0
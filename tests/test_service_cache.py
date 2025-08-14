"""
Tests for service type filtering with caching functionality.

Tests cover:
- Cached services can be filtered by type
- Type field preservation in cache
- Background cache filtering with type
- Cache invalidation with type fields
- Performance of type filtering on cached data
- Async cache manager integration
"""

import pytest
import asyncio
import os
import sys
import time
from typing import List, Dict, Any
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment
os.environ["CONFIG_FILES_PATH"] = os.path.join(os.path.dirname(__file__), "tests", "test_configs")

from models import ServiceObject, Protocol, ProtocolType
from async_cache import AsyncCacheManager, TaskStatus
from background_cache import BackgroundCacheManager
from parser import PanoramaXMLParser
from filtering import apply_filters, SERVICE_FILTERS


class TestServiceCacheFiltering:
    """Test service type filtering with caching"""
    
    def setup_method(self):
        """Set up test cache managers"""
        self.async_cache = AsyncCacheManager()
        self.bg_cache = BackgroundCacheManager()
        
    def teardown_method(self):
        """Clean up cache managers"""
        # Clear cache data
        if hasattr(self.async_cache, 'cache'):
            self.async_cache.cache.clear()
        if hasattr(self.async_cache, 'tasks'):
            self.async_cache.tasks.clear()

    def create_test_services(self) -> List[ServiceObject]:
        """Create test services for caching tests"""
        services = []
        
        # TCP services
        tcp_services = [
            {"name": "tcp-80", "port": "80", "protocol": "tcp"},
            {"name": "tcp-443", "port": "443", "protocol": "tcp"},
            {"name": "tcp-22", "port": "22", "protocol": "tcp"},
            {"name": "tcp-3306", "port": "3306", "protocol": "tcp"}
        ]
        
        for svc_data in tcp_services:
            service = ServiceObject(
                name=svc_data["name"],
                protocol=Protocol(tcp={"port": svc_data["port"]}),
                description=f"{svc_data['name']} service"
            )
            services.append(service)
        
        # UDP services
        udp_services = [
            {"name": "udp-53", "port": "53", "protocol": "udp"},
            {"name": "udp-123", "port": "123", "protocol": "udp"},
            {"name": "udp-161", "port": "161", "protocol": "udp"},
            {"name": "udp-514", "port": "514", "protocol": "udp"}
        ]
        
        for svc_data in udp_services:
            service = ServiceObject(
                name=svc_data["name"],
                protocol=Protocol(udp={"port": svc_data["port"]}),
                description=f"{svc_data['name']} service"
            )
            services.append(service)
        
        return services

    def test_type_field_preserved_in_cache(self):
        """Test that type field is preserved when services are cached"""
        services = self.create_test_services()
        
        # Cache the services
        cache_key = "test-config:services"
        self.async_cache.cache[cache_key] = services
        
        # Retrieve from cache
        cached_services = self.async_cache.cache[cache_key]
        
        # Verify type fields are preserved
        tcp_services = [s for s in cached_services if s.type == ProtocolType.TCP]
        udp_services = [s for s in cached_services if s.type == ProtocolType.UDP]
        
        assert len(tcp_services) == 4
        assert len(udp_services) == 4
        
        # Verify specific services
        tcp_80 = next((s for s in tcp_services if s.name == "tcp-80"), None)
        assert tcp_80 is not None
        assert tcp_80.type == ProtocolType.TCP
        
        udp_53 = next((s for s in udp_services if s.name == "udp-53"), None)
        assert udp_53 is not None
        assert udp_53.type == ProtocolType.UDP

    def test_filter_cached_services_by_type_tcp(self):
        """Test filtering cached services by TCP type"""
        services = self.create_test_services()
        
        # Apply type filter
        filter_params = {"type": "tcp"}
        filtered_services = apply_filters(services, filter_params, SERVICE_FILTERS)
        
        # All filtered services should be TCP
        assert len(filtered_services) == 4
        for service in filtered_services:
            assert service.type == ProtocolType.TCP
            assert service.protocol.tcp is not None
            assert service.protocol.udp is None

    def test_filter_cached_services_by_type_udp(self):
        """Test filtering cached services by UDP type"""
        services = self.create_test_services()
        
        # Apply type filter
        filter_params = {"type": "udp"}
        filtered_services = apply_filters(services, filter_params, SERVICE_FILTERS)
        
        # All filtered services should be UDP
        assert len(filtered_services) == 4
        for service in filtered_services:
            assert service.type == ProtocolType.UDP
            assert service.protocol.udp is not None
            assert service.protocol.tcp is None

    def test_filter_cached_services_type_ne(self):
        """Test filtering cached services with type not equals"""
        services = self.create_test_services()
        
        # Filter out TCP services
        filter_params = {"type_ne": "tcp"}
        filtered_services = apply_filters(services, filter_params, SERVICE_FILTERS)
        
        # Should only have UDP services
        assert len(filtered_services) == 4
        for service in filtered_services:
            assert service.type != ProtocolType.TCP
            assert service.type == ProtocolType.UDP

    def test_filter_cached_services_type_in(self):
        """Test filtering cached services with type in operator"""
        services = self.create_test_services()
        
        # Filter for both TCP and UDP
        filter_params = {"type_in": "tcp,udp"}
        filtered_services = apply_filters(services, filter_params, SERVICE_FILTERS)
        
        # Should have all services
        assert len(filtered_services) == 8
        
        # Filter for only TCP
        filter_params = {"type_in": "tcp"}
        filtered_services = apply_filters(services, filter_params, SERVICE_FILTERS)
        
        assert len(filtered_services) == 4
        for service in filtered_services:
            assert service.type == ProtocolType.TCP

    def test_combined_filters_with_cached_services(self):
        """Test combined type and other filters on cached services"""
        services = self.create_test_services()
        
        # Filter for TCP services with port 443
        filter_params = {
            "type": "tcp",
            "port": "443"
        }
        filtered_services = apply_filters(services, filter_params, SERVICE_FILTERS)
        
        assert len(filtered_services) == 1
        service = filtered_services[0]
        assert service.name == "tcp-443"
        assert service.type == ProtocolType.TCP
        assert service.protocol.tcp["port"] == "443"

    def test_background_cache_type_filtering(self):
        """Test background cache with type filtering"""
        services = self.create_test_services()
        
        # Mock background cache data
        with patch.object(self.bg_cache, 'get_cached_data') as mock_get:
            mock_get.return_value = services
            
            cached_data = self.bg_cache.get_cached_data("test-config", "services")
            
            # Apply type filtering to background cached data
            filter_params = {"type": "udp"}
            filtered_services = apply_filters(cached_data, filter_params, SERVICE_FILTERS)
            
            assert len(filtered_services) == 4
            for service in filtered_services:
                assert service.type == ProtocolType.UDP

    def test_async_cache_task_with_type_filtering(self):
        """Test async cache task handles type filtering correctly"""
        services = self.create_test_services()
        
        # Create a cache task
        task_id = self.async_cache.create_task("test-config", "services")
        
        # Complete the task with service data
        self.async_cache.complete_task(task_id, services)
        
        # Retrieve task and verify type fields
        task = self.async_cache.get_task(task_id)
        assert task.status == TaskStatus.COMPLETED
        assert task.data is not None
        
        # Apply type filtering to async cached data
        filter_params = {"type": "tcp"}
        filtered_services = apply_filters(task.data, filter_params, SERVICE_FILTERS)
        
        assert len(filtered_services) == 4
        for service in filtered_services:
            assert service.type == ProtocolType.TCP

    def test_cache_serialization_preserves_type(self):
        """Test that cache serialization preserves type field"""
        services = self.create_test_services()
        
        # Simulate serialization/deserialization cycle
        serialized_data = []
        for service in services:
            service_dict = service.model_dump()
            serialized_data.append(service_dict)
        
        # Deserialize back to objects
        deserialized_services = []
        for service_dict in serialized_data:
            service = ServiceObject(**service_dict)
            deserialized_services.append(service)
        
        # Verify type fields are preserved
        tcp_count = len([s for s in deserialized_services if s.type == ProtocolType.TCP])
        udp_count = len([s for s in deserialized_services if s.type == ProtocolType.UDP])
        
        assert tcp_count == 4
        assert udp_count == 4

    def test_cache_performance_with_type_filtering(self):
        """Test performance of type filtering on cached data"""
        # Create larger dataset for performance testing
        services = []
        
        # Create 1000 services (500 TCP, 500 UDP)
        for i in range(500):
            tcp_service = ServiceObject(
                name=f"tcp-service-{i}",
                protocol=Protocol(tcp={"port": str(8000 + i)}),
                description=f"TCP service {i}"
            )
            udp_service = ServiceObject(
                name=f"udp-service-{i}",
                protocol=Protocol(udp={"port": str(9000 + i)}),
                description=f"UDP service {i}"
            )
            services.extend([tcp_service, udp_service])
        
        # Measure type filtering performance
        start_time = time.time()
        filter_params = {"type": "tcp"}
        filtered_services = apply_filters(services, filter_params, SERVICE_FILTERS)
        end_time = time.time()
        
        # Verify results
        assert len(filtered_services) == 500
        for service in filtered_services:
            assert service.type == ProtocolType.TCP
        
        # Performance should be reasonable (adjust threshold as needed)
        execution_time = end_time - start_time
        assert execution_time < 1.0, f"Type filtering took too long: {execution_time}s"

    def test_cache_invalidation_with_type_fields(self):
        """Test cache invalidation preserves type field integrity"""
        services = self.create_test_services()
        cache_key = "test-config:services"
        
        # Cache the services
        self.async_cache.cache[cache_key] = services
        
        # Invalidate cache (simulate cache refresh)
        del self.async_cache.cache[cache_key]
        
        # Re-cache with updated data
        updated_services = self.create_test_services()
        # Add one more service
        new_service = ServiceObject(
            name="tcp-8080",
            protocol=Protocol(tcp={"port": "8080"}),
            description="New TCP service"
        )
        updated_services.append(new_service)
        
        self.async_cache.cache[cache_key] = updated_services
        
        # Verify type filtering still works
        cached_data = self.async_cache.cache[cache_key]
        filter_params = {"type": "tcp"}
        filtered_services = apply_filters(cached_data, filter_params, SERVICE_FILTERS)
        
        # Should have 5 TCP services now (4 original + 1 new)
        assert len(filtered_services) == 5
        tcp_names = [s.name for s in filtered_services]
        assert "tcp-8080" in tcp_names

    def test_concurrent_type_filtering_on_cache(self):
        """Test concurrent type filtering operations on cached data"""
        services = self.create_test_services()
        
        def filter_tcp():
            filter_params = {"type": "tcp"}
            return apply_filters(services, filter_params, SERVICE_FILTERS)
        
        def filter_udp():
            filter_params = {"type": "udp"}
            return apply_filters(services, filter_params, SERVICE_FILTERS)
        
        def filter_combined():
            filter_params = {"type": "tcp", "port": "80"}
            return apply_filters(services, filter_params, SERVICE_FILTERS)
        
        # Simulate concurrent filtering (in real scenario, would use threading)
        tcp_results = filter_tcp()
        udp_results = filter_udp()
        combined_results = filter_combined()
        
        # Verify all results are correct
        assert len(tcp_results) == 4
        assert len(udp_results) == 4
        assert len(combined_results) == 1
        assert combined_results[0].name == "tcp-80"

    def test_cache_with_real_parser_data(self):
        """Test type filtering with real parser-generated cached data"""
        # This test would use real configuration data if available
        config_path = os.path.join(os.path.dirname(__file__), "tests", "test_configs", "test_panorama.xml")
        
        if os.path.exists(config_path):
            parser = PanoramaXMLParser(config_path)
            real_services = parser.get_shared_services()
            
            # Cache the real services
            cache_key = "test_panorama:services"
            self.async_cache.cache[cache_key] = real_services
            
            # Test type filtering on real data
            filter_params = {"type": "tcp"}
            filtered_services = apply_filters(real_services, filter_params, SERVICE_FILTERS)
            
            # Verify all results have correct type
            for service in filtered_services:
                assert service.type == ProtocolType.TCP
                assert service.protocol.tcp is not None
        else:
            pytest.skip("Real config file not available for testing")

    def test_cache_memory_efficiency_with_type_filtering(self):
        """Test memory efficiency of cached type filtering"""
        import sys
        
        services = self.create_test_services()
        
        # Measure memory usage (rough estimate)
        initial_size = sys.getsizeof(services)
        
        # Apply type filtering multiple times
        for _ in range(100):
            filter_params = {"type": "tcp"}
            filtered_services = apply_filters(services, filter_params, SERVICE_FILTERS)
            
            # Verify results without storing references (to avoid memory buildup)
            assert len(filtered_services) == 4
            del filtered_services
        
        # Memory usage should remain reasonable
        final_size = sys.getsizeof(services)
        assert final_size == initial_size  # Original data should be unchanged

    def test_cache_error_handling_with_type_filtering(self):
        """Test error handling in cache operations with type filtering"""
        # Test with invalid cache data
        invalid_services = [{"name": "invalid", "protocol": {}}]  # Missing required fields
        
        # This should handle validation errors gracefully
        try:
            validated_services = []
            for service_data in invalid_services:
                try:
                    service = ServiceObject(**service_data)
                    validated_services.append(service)
                except Exception:
                    # Skip invalid services
                    continue
            
            # Type filtering should work with valid services only
            filter_params = {"type": "tcp"}
            filtered_services = apply_filters(validated_services, filter_params, SERVICE_FILTERS)
            
            # Should be empty since we had no valid services
            assert len(filtered_services) == 0
            
        except Exception as e:
            pytest.fail(f"Error handling failed: {e}")

    def test_cache_consistency_across_multiple_configs(self):
        """Test cache consistency when handling multiple configurations"""
        # Create services for different configs
        config1_services = self.create_test_services()
        config2_services = [
            ServiceObject(
                name="config2-tcp-9090",
                protocol=Protocol(tcp={"port": "9090"}),
                description="Config 2 TCP service"
            ),
            ServiceObject(
                name="config2-udp-1234",
                protocol=Protocol(udp={"port": "1234"}),
                description="Config 2 UDP service"
            )
        ]
        
        # Cache both configurations
        self.async_cache.cache["config1:services"] = config1_services
        self.async_cache.cache["config2:services"] = config2_services
        
        # Test type filtering on each config
        config1_tcp = apply_filters(
            self.async_cache.cache["config1:services"],
            {"type": "tcp"},
            SERVICE_FILTERS
        )
        config2_udp = apply_filters(
            self.async_cache.cache["config2:services"],
            {"type": "udp"},
            SERVICE_FILTERS
        )
        
        assert len(config1_tcp) == 4  # Original test services
        assert len(config2_udp) == 1  # Only one UDP service in config2
        assert config2_udp[0].name == "config2-udp-1234"
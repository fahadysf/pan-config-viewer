"""
Performance tests for integrated pagination and filtering.
Tests system performance with large datasets and complex operations.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import time
import statistics
from typing import List, Dict, Tuple
from fastapi.testclient import TestClient
import concurrent.futures
import psutil
import os


class TestPerformanceIntegrated:
    """Performance test suite for pagination and filtering"""
    
    # Performance thresholds (in seconds)
    THRESHOLDS = {
        "simple_request": 0.5,      # Simple paginated request
        "filtered_request": 1.0,    # Filtered request
        "complex_filter": 1.5,      # Multiple filters
        "large_page": 2.0,          # Large page size (1000 items)
        "concurrent_requests": 3.0   # Multiple simultaneous requests
    }
    
    def measure_response_time(self, client: TestClient, url: str, params: Dict = None) -> float:
        """Measure response time for a request"""
        start_time = time.time()
        response = client.get(url, params=params)
        end_time = time.time()
        
        assert response.status_code == 200
        return end_time - start_time
    
    def test_baseline_performance(self, real_client: TestClient):
        """Establish baseline performance metrics"""
        endpoints = [
            "/api/v1/configs/pan-bkp-202507151414/addresses",
            "/api/v1/configs/pan-bkp-202507151414/services",
            "/api/v1/configs/pan-bkp-202507151414/security-policies"
        ]
        
        print("\n=== Baseline Performance Metrics ===")
        for endpoint in endpoints:
            times = []
            
            # Make multiple requests to get average
            for _ in range(5):
                response_time = self.measure_response_time(
                    real_client, 
                    endpoint,
                    {"page_size": 100}
                )
                times.append(response_time)
            
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"\n{endpoint}:")
            print(f"  Average: {avg_time:.3f}s")
            print(f"  Min: {min_time:.3f}s")
            print(f"  Max: {max_time:.3f}s")
            
            # Check against threshold
            assert avg_time < self.THRESHOLDS["simple_request"], \
                f"Baseline performance for {endpoint} exceeded threshold"
    
    def test_pagination_performance_scaling(self, real_client: TestClient):
        """Test how performance scales with different page sizes"""
        endpoint = "/api/v1/configs/pan-bkp-202507151414/addresses"
        page_sizes = [10, 50, 100, 500, 1000]
        
        print("\n=== Pagination Scaling Performance ===")
        for page_size in page_sizes:
            times = []
            
            for page in range(1, 4):  # Test first 3 pages
                response_time = self.measure_response_time(
                    real_client,
                    endpoint,
                    {"page": page, "page_size": page_size}
                )
                times.append(response_time)
            
            avg_time = statistics.mean(times)
            print(f"Page size {page_size}: {avg_time:.3f}s average")
            
            # Larger pages should still meet threshold
            if page_size <= 100:
                assert avg_time < self.THRESHOLDS["simple_request"]
            else:
                assert avg_time < self.THRESHOLDS["large_page"]
    
    def test_filter_performance(self, real_client: TestClient):
        """Test performance impact of different filter types"""
        endpoint = "/api/v1/configs/pan-bkp-202507151414/addresses"
        
        filter_tests = [
            ("Simple contains", {"filter[name]": "10.0"}),
            ("Exact match", {"filter[name][eq]": "10.0.0.1"}),
            ("Starts with", {"filter[name][starts_with]": "10."}),
            ("Multiple filters", {
                "filter[name]": "10",
                "filter[description]": "test",
                "filter[location]": "shared"
            })
        ]
        
        print("\n=== Filter Performance ===")
        for test_name, params in filter_tests:
            times = []
            
            for _ in range(5):
                response_time = self.measure_response_time(
                    real_client,
                    endpoint,
                    {**params, "page_size": 100}
                )
                times.append(response_time)
            
            avg_time = statistics.mean(times)
            print(f"{test_name}: {avg_time:.3f}s average")
            
            # Check appropriate threshold
            if len(params) > 2:
                assert avg_time < self.THRESHOLDS["complex_filter"]
            else:
                assert avg_time < self.THRESHOLDS["filtered_request"]
    
    def test_concurrent_request_performance(self, real_client: TestClient):
        """Test performance under concurrent load"""
        endpoint = "/api/v1/configs/pan-bkp-202507151414/addresses"
        
        def make_request(page: int) -> Tuple[int, float]:
            response_time = self.measure_response_time(
                real_client,
                endpoint,
                {"page": page, "page_size": 50}
            )
            return page, response_time
        
        print("\n=== Concurrent Request Performance ===")
        
        # Test different concurrency levels
        for num_concurrent in [5, 10, 20]:
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
                start_time = time.time()
                
                # Submit concurrent requests
                futures = [
                    executor.submit(make_request, i % 10 + 1)
                    for i in range(num_concurrent)
                ]
                
                # Collect results
                response_times = []
                for future in concurrent.futures.as_completed(futures):
                    page, response_time = future.result()
                    response_times.append(response_time)
                
                total_time = time.time() - start_time
                avg_response_time = statistics.mean(response_times)
                
                print(f"\nConcurrency {num_concurrent}:")
                print(f"  Total time: {total_time:.3f}s")
                print(f"  Avg response: {avg_response_time:.3f}s")
                print(f"  Throughput: {num_concurrent/total_time:.1f} req/s")
                
                # Each request should still be reasonably fast
                assert avg_response_time < self.THRESHOLDS["concurrent_requests"]
    
    def test_memory_efficiency(self, real_client: TestClient):
        """Test memory usage doesn't grow excessively"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print("\n=== Memory Efficiency Test ===")
        print(f"Initial memory: {initial_memory:.1f} MB")
        
        # Make many requests with different filters
        endpoint = "/api/v1/configs/pan-bkp-202507151414/addresses"
        
        for i in range(50):
            # Vary the requests
            params = {
                "page": (i % 10) + 1,
                "page_size": 100,
                "filter[name]": f"10.{i % 256}"
            }
            
            response = real_client.get(endpoint, params=params)
            assert response.status_code == 200
        
        # Check memory after requests
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        print(f"Final memory: {final_memory:.1f} MB")
        print(f"Memory growth: {memory_growth:.1f} MB")
        
        # Memory growth should be reasonable (< 100MB)
        assert memory_growth < 100, f"Excessive memory growth: {memory_growth:.1f} MB"
    
    def test_filter_complexity_impact(self, real_client: TestClient):
        """Test how filter complexity affects performance"""
        endpoint = "/api/v1/configs/pan-bkp-202507151414/security-policies"
        
        complexity_tests = [
            ("No filters", {}),
            ("Single filter", {"filter[action]": "allow"}),
            ("Two filters", {
                "filter[action]": "allow",
                "filter[disabled]": "false"
            }),
            ("Complex filters", {
                "filter[action]": "allow",
                "filter[source][contains]": "any",
                "filter[destination][contains]": "any",
                "filter[service][contains]": "any"
            }),
            ("Many filters", {
                "filter[name]": "test",
                "filter[action]": "allow",
                "filter[source][contains]": "10",
                "filter[destination][contains]": "10",
                "filter[service][contains]": "tcp",
                "filter[application][contains]": "web",
                "filter[disabled]": "false"
            })
        ]
        
        print("\n=== Filter Complexity Impact ===")
        for test_name, filters in complexity_tests:
            times = []
            
            for _ in range(3):
                response_time = self.measure_response_time(
                    real_client,
                    endpoint,
                    {**filters, "page_size": 50}
                )
                times.append(response_time)
            
            avg_time = statistics.mean(times)
            print(f"{test_name}: {avg_time:.3f}s")
            
            # Even complex filters should be reasonably fast
            assert avg_time < self.THRESHOLDS["complex_filter"]
    
    def test_pagination_edge_cases_performance(self, real_client: TestClient):
        """Test performance of edge cases"""
        endpoint = "/api/v1/configs/pan-bkp-202507151414/addresses"
        
        print("\n=== Edge Case Performance ===")
        
        # Test 1: Very large page number
        response_time = self.measure_response_time(
            real_client,
            endpoint,
            {"page": 9999, "page_size": 100}
        )
        print(f"Large page number: {response_time:.3f}s")
        assert response_time < self.THRESHOLDS["simple_request"]
        
        # Test 2: Maximum page size
        response_time = self.measure_response_time(
            real_client,
            endpoint,
            {"page": 1, "page_size": 10000}
        )
        print(f"Maximum page size: {response_time:.3f}s")
        assert response_time < self.THRESHOLDS["large_page"] * 2  # Allow more time
        
        # Test 3: Filter with no results
        response_time = self.measure_response_time(
            real_client,
            endpoint,
            {"filter[name]": "xyz_nonexistent_123"}
        )
        print(f"No results filter: {response_time:.3f}s")
        assert response_time < self.THRESHOLDS["filtered_request"]
    
    def test_rapid_filter_changes(self, real_client: TestClient):
        """Simulate rapid filter changes (user typing)"""
        endpoint = "/api/v1/configs/pan-bkp-202507151414/addresses"
        
        # Simulate user typing "10.0.0.1"
        search_progression = ["1", "10", "10.", "10.0", "10.0.", "10.0.0", "10.0.0.", "10.0.0.1"]
        
        print("\n=== Rapid Filter Changes ===")
        times = []
        
        for search_term in search_progression:
            response_time = self.measure_response_time(
                real_client,
                endpoint,
                {"filter[name]": search_term, "page_size": 50}
            )
            times.append(response_time)
            print(f"Filter '{search_term}': {response_time:.3f}s")
        
        avg_time = statistics.mean(times)
        print(f"\nAverage response time: {avg_time:.3f}s")
        
        # All rapid changes should be handled quickly
        assert all(t < self.THRESHOLDS["filtered_request"] for t in times)
    
    def test_cache_effectiveness(self, real_client: TestClient):
        """Test if repeated requests benefit from caching"""
        endpoint = "/api/v1/configs/pan-bkp-202507151414/addresses"
        params = {"page": 1, "page_size": 100, "filter[name]": "10.0"}
        
        print("\n=== Cache Effectiveness ===")
        
        # First request (cold)
        cold_time = self.measure_response_time(real_client, endpoint, params)
        print(f"Cold request: {cold_time:.3f}s")
        
        # Subsequent requests (potentially cached)
        warm_times = []
        for i in range(5):
            warm_time = self.measure_response_time(real_client, endpoint, params)
            warm_times.append(warm_time)
        
        avg_warm_time = statistics.mean(warm_times)
        print(f"Warm requests average: {avg_warm_time:.3f}s")
        
        # Warm requests should be at least as fast (allowing for variance)
        assert avg_warm_time <= cold_time * 1.1  # Allow 10% variance


def test_generate_performance_report(real_client: TestClient):
    """Generate a comprehensive performance report"""
    report = []
    report.append("# Performance Test Report\n")
    report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Run all performance tests and collect results
    test_suite = TestPerformanceIntegrated()
    
    tests = [
        ("Baseline Performance", test_suite.test_baseline_performance),
        ("Pagination Scaling", test_suite.test_pagination_performance_scaling),
        ("Filter Performance", test_suite.test_filter_performance),
        ("Concurrent Requests", test_suite.test_concurrent_request_performance),
        ("Memory Efficiency", test_suite.test_memory_efficiency),
        ("Filter Complexity", test_suite.test_filter_complexity_impact),
        ("Edge Cases", test_suite.test_pagination_edge_cases_performance),
        ("Rapid Filter Changes", test_suite.test_rapid_filter_changes),
        ("Cache Effectiveness", test_suite.test_cache_effectiveness)
    ]
    
    report.append("\n## Test Results\n")
    
    for test_name, test_func in tests:
        report.append(f"\n### {test_name}\n")
        try:
            # Capture print output
            import io
            import sys
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            test_func(real_client)
            
            sys.stdout = sys.__stdout__
            output = captured_output.getvalue()
            
            report.append("✅ PASSED\n")
            report.append("```\n")
            report.append(output)
            report.append("```\n")
        except Exception as e:
            sys.stdout = sys.__stdout__
            report.append("❌ FAILED\n")
            report.append(f"Error: {str(e)}\n")
    
    # Write report
    with open("performance_test_report.md", "w") as f:
        f.writelines(report)
    
    print("\nPerformance report generated: performance_test_report.md")
#!/usr/bin/env python3
"""
Manual pagination testing script for interactive verification
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import sys
from typing import Dict, Any


class PaginationTester:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_endpoint(self, endpoint: str, params: Dict[str, Any] = None):
        """Test a single endpoint with given parameters"""
        url = f"{self.base_url}{endpoint}"
        print(f"\nTesting: {url}")
        if params:
            print(f"Parameters: {params}")
        
        try:
            response = self.session.get(url, params=params)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Total Items: {data.get('total_items', 'N/A')}")
                print(f"Page: {data.get('page', 'N/A')} / {data.get('total_pages', 'N/A')}")
                print(f"Page Size: {data.get('page_size', 'N/A')}")
                print(f"Items in Page: {len(data.get('items', []))}")
                print(f"Has Next: {data.get('has_next', 'N/A')}")
                print(f"Has Previous: {data.get('has_previous', 'N/A')}")
                
                if data.get('items'):
                    print(f"\nFirst item: {data['items'][0].get('name', 'N/A')}")
                    if len(data['items']) > 1:
                        print(f"Last item: {data['items'][-1].get('name', 'N/A')}")
            else:
                print(f"Error Response: {response.text}")
                
            return response
            
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def test_pagination_sequence(self, endpoint: str, page_size: int = 10):
        """Test paginating through an entire dataset"""
        print(f"\n{'='*60}")
        print(f"Testing pagination sequence for: {endpoint}")
        print(f"Page size: {page_size}")
        print(f"{'='*60}")
        
        all_items = []
        page = 1
        
        while True:
            response = self.test_endpoint(endpoint, {'page': page, 'page_size': page_size})
            
            if not response or response.status_code != 200:
                break
                
            data = response.json()
            items = data.get('items', [])
            all_items.extend(items)
            
            if not data.get('has_next'):
                break
                
            page += 1
            
            # Safety check
            if page > 1000:
                print("\nSafety limit reached (1000 pages)")
                break
        
        print(f"\nTotal items collected: {len(all_items)}")
        print(f"Total pages traversed: {page}")
        
        # Check for duplicates
        unique_names = set(item.get('name', '') for item in all_items)
        if len(unique_names) != len(all_items):
            print(f"\u26a0️  Warning: Found duplicates! Unique: {len(unique_names)}, Total: {len(all_items)}")
        else:
            print("\u2705 No duplicates found")
        
        return all_items
    
    def run_edge_case_tests(self, config_name: str = "test_panorama"):
        """Run various edge case tests"""
        print(f"\n{'#'*60}")
        print("# EDGE CASE TESTS")
        print(f"{'#'*60}")
        
        test_cases = [
            {
                'name': 'Default pagination',
                'endpoint': f'/configs/{config_name}/addresses',
                'params': None
            },
            {
                'name': 'Small page size',
                'endpoint': f'/configs/{config_name}/addresses',
                'params': {'page_size': 5}
            },
            {
                'name': 'Large page size',
                'endpoint': f'/configs/{config_name}/addresses',
                'params': {'page_size': 1000}
            },
            {
                'name': 'Page out of bounds',
                'endpoint': f'/configs/{config_name}/addresses',
                'params': {'page': 9999}
            },
            {
                'name': 'Disable paging',
                'endpoint': f'/configs/{config_name}/addresses',
                'params': {'disable_paging': 'true'}
            },
            {
                'name': 'With name filter',
                'endpoint': f'/configs/{config_name}/addresses',
                'params': {'name': 'host', 'page_size': 10}
            },
            {
                'name': 'Empty results',
                'endpoint': f'/configs/{config_name}/addresses',
                'params': {'name': 'nonexistent_xyz_123'}
            },
            {
                'name': 'Invalid page (negative)',
                'endpoint': f'/configs/{config_name}/addresses',
                'params': {'page': -1}
            },
            {
                'name': 'Invalid page size (zero)',
                'endpoint': f'/configs/{config_name}/addresses',
                'params': {'page_size': 0}
            },
            {
                'name': 'Invalid page size (too large)',
                'endpoint': f'/configs/{config_name}/addresses',
                'params': {'page_size': 10001}
            }
        ]
        
        for test_case in test_cases:
            print(f"\n\n{'*'*40}")
            print(f"Test: {test_case['name']}")
            print(f"{'*'*40}")
            self.test_endpoint(test_case['endpoint'], test_case['params'])
    
    def compare_pagination_methods(self, endpoint: str):
        """Compare paginated vs non-paginated results"""
        print(f"\n{'#'*60}")
        print(f"# COMPARING PAGINATION METHODS")
        print(f"# Endpoint: {endpoint}")
        print(f"{'#'*60}")
        
        # Get all items with pagination disabled
        print("\nGetting all items (disable_paging=true)...")
        response_all = self.test_endpoint(endpoint, {'disable_paging': 'true'})
        
        if response_all and response_all.status_code == 200:
            all_items = response_all.json().get('items', [])
            print(f"Total items: {len(all_items)}")
            
            # Get items by paginating
            print("\nGetting items through pagination...")
            paginated_items = self.test_pagination_sequence(endpoint, page_size=100)
            
            # Compare results
            print("\n" + "="*40)
            print("COMPARISON RESULTS:")
            print(f"Items from disable_paging: {len(all_items)}")
            print(f"Items from pagination: {len(paginated_items)}")
            
            if len(all_items) == len(paginated_items):
                print("\u2705 Item counts match!")
                
                # Check if items are the same
                all_names = set(item.get('name', '') for item in all_items)
                paginated_names = set(item.get('name', '') for item in paginated_items)
                
                if all_names == paginated_names:
                    print("\u2705 All items match!")
                else:
                    print("\u274c Items don't match!")
                    missing = all_names - paginated_names
                    extra = paginated_names - all_names
                    if missing:
                        print(f"Missing from paginated: {missing}")
                    if extra:
                        print(f"Extra in paginated: {extra}")
            else:
                print("\u274c Item counts don't match!")


def main():
    tester = PaginationTester()
    
    if len(sys.argv) > 1:
        # Test specific endpoint
        endpoint = sys.argv[1]
        print(f"Testing specific endpoint: {endpoint}")
        
        if len(sys.argv) > 2:
            # With specific parameters
            params = {}
            for param in sys.argv[2:]:
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
            tester.test_endpoint(endpoint, params)
        else:
            # Test pagination sequence
            tester.test_pagination_sequence(endpoint)
    else:
        # Run default tests
        print("Running default test suite...")
        
        # Check if API is running
        try:
            response = requests.get("http://localhost:8000/api/v1/configs")
            if response.status_code != 200:
                print("\u274c API server is not running!")
                print("Please start the server with: python main.py")
                sys.exit(1)
        except:
            print("\u274c Cannot connect to API server!")
            print("Please start the server with: python main.py")
            sys.exit(1)
        
        # Run edge case tests
        tester.run_edge_case_tests()
        
        # Compare pagination methods
        tester.compare_pagination_methods("/configs/test_panorama/addresses")
        
        # Test large dataset
        print("\n\nTesting large dataset...")
        tester.test_endpoint(
            "/configs/16-7-Panorama-Core-688/device-groups/KIZAD-DC-Vsys1/pre-security-rules",
            {'page_size': 100}
        )


if __name__ == "__main__":
    main()
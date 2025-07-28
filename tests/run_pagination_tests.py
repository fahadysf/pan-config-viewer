#!/usr/bin/env python3
"""
Helper script to run pagination tests and generate a summary report
"""

import subprocess
import sys
import json
import time
from datetime import datetime


def run_command(cmd, description):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True
        )
        duration = time.time() - start_time
        
        print(f"\nCompleted in {duration:.2f} seconds")
        print(f"Exit code: {result.returncode}")
        
        if result.stdout:
            print("\nOutput:")
            print(result.stdout)
        
        if result.stderr:
            print("\nErrors:")
            print(result.stderr)
            
        return {
            'success': result.returncode == 0,
            'duration': duration,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except Exception as e:
        print(f"\nError running command: {e}")
        return {
            'success': False,
            'duration': time.time() - start_time,
            'error': str(e)
        }


def main():
    print(f"""
Pagination Test Suite Runner
Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
    
    results = {}
    
    # Check if the API server is running
    print("Checking API server status...")
    api_check = run_command(
        "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/v1/configs",
        "API Server Check"
    )
    
    if api_check['stdout'].strip() != '200':
        print("\n\u274c ERROR: API server is not running on http://localhost:8000")
        print("Please start the server with: python main.py")
        sys.exit(1)
    else:
        print("\n\u2705 API server is running")
    
    # Run Python pagination tests
    print("\n" + "#" * 60)
    print("# PYTHON PAGINATION TESTS")
    print("#" * 60)
    
    results['python_tests'] = run_command(
        "python -m pytest tests/test_pagination.py -v --tb=short",
        "Python Pagination Tests"
    )
    
    # Run Python tests with coverage
    results['python_coverage'] = run_command(
        "python -m pytest tests/test_pagination.py --cov=main --cov-report=term-missing --cov-report=html",
        "Python Tests with Coverage"
    )
    
    # Run Jest pagination tests
    print("\n" + "#" * 60)
    print("# JEST PAGINATION TESTS")
    print("#" * 60)
    
    results['jest_tests'] = run_command(
        "npm test pagination.test.js",
        "Jest Pagination Tests"
    )
    
    # Generate summary report
    print("\n" + "#" * 60)
    print("# TEST SUMMARY")
    print("#" * 60)
    
    all_passed = True
    for test_name, result in results.items():
        status = "\u2705 PASSED" if result['success'] else "\u274c FAILED"
        print(f"\n{test_name}: {status}")
        if not result['success']:
            all_passed = False
    
    if all_passed:
        print("\n\u2705 All pagination tests passed successfully!")
    else:
        print("\n\u274c Some tests failed. Please check the output above.")
    
    # Additional checks
    print("\n" + "#" * 60)
    print("# ADDITIONAL CHECKS")
    print("#" * 60)
    
    # Check for large config file
    print("\nChecking for large config file...")
    config_check = run_command(
        "curl -s http://localhost:8000/api/v1/configs/16-7-Panorama-Core-688/info",
        "Large Config File Check"
    )
    
    try:
        config_info = json.loads(config_check['stdout'])
        print(f"\u2705 Large config file found: {config_info.get('name')}")
        print(f"   Size: {config_info.get('size', 'Unknown')} bytes")
    except:
        print("\u26a0️  Warning: Could not verify large config file")
    
    # Sample pagination request
    print("\nTesting sample pagination request...")
    sample_test = run_command(
        "curl -s 'http://localhost:8000/api/v1/configs/test_panorama/addresses?page=1&page_size=5' | python -m json.tool | head -20",
        "Sample Pagination Request"
    )
    
    print(f"\n\nTest run completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
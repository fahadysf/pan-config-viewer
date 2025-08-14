#!/usr/bin/env python3
"""
Generate a comprehensive test report for device group detection
"""

import os
import sys
import json
import datetime
from typing import Dict, List, Any
import subprocess
import requests
from parser import PanoramaXMLParser

CONFIG_FILE = "config-files/16-7-Panorama-Core-688.xml"
API_BASE_URL = "http://localhost:8000/api/v1"
CONFIG_NAME = "16-7-Panorama-Core-688"

EXPECTED_DEVICE_GROUPS = [
    "TCN-DC-SWIFT-VSYS",
    "TCN-DC-Tapping-Vsys", 
    "TCN-DC-Vsys1",
    "KIZAD-DC-Vsys1",
    "KIZAD-DC-Tapping-Vsys",
    "KIZAD-DC-SWIFT-VSYS"
]


def generate_html_report(test_results: Dict[str, Any]) -> str:
    """Generate HTML test report"""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Device Group Detection Test Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1, h2, h3 {{
            color: #333;
        }}
        .summary {{
            background-color: #f0f8ff;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .pass {{
            color: #28a745;
            font-weight: bold;
        }}
        .fail {{
            color: #dc3545;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        .device-group-card {{
            border: 1px solid #ddd;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            background-color: #fafafa;
        }}
        .metric {{
            display: inline-block;
            margin: 0 20px 10px 0;
        }}
        .metric-label {{
            font-weight: bold;
            color: #666;
        }}
        .metric-value {{
            font-size: 1.2em;
            color: #333;
        }}
        .test-section {{
            margin: 30px 0;
        }}
        .code {{
            background-color: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Device Group Detection Test Report</h1>
        <p>Generated: {test_results['timestamp']}</p>
        
        <div class="summary">
            <h2>Test Summary</h2>
            <div class="metric">
                <span class="metric-label">Total Tests:</span>
                <span class="metric-value">{test_results['total_tests']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Passed:</span>
                <span class="metric-value pass">{test_results['passed_tests']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Failed:</span>
                <span class="metric-value fail">{test_results['failed_tests']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Success Rate:</span>
                <span class="metric-value">{test_results['success_rate']:.1f}%</span>
            </div>
        </div>
        
        <div class="test-section">
            <h2>Configuration Details</h2>
            <table>
                <tr>
                    <th>Property</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Config File</td>
                    <td class="code">{test_results['config_file']}</td>
                </tr>
                <tr>
                    <td>API Base URL</td>
                    <td class="code">{test_results['api_base_url']}</td>
                </tr>
                <tr>
                    <td>Expected Device Groups</td>
                    <td>{test_results['expected_count']}</td>
                </tr>
                <tr>
                    <td>Found Device Groups</td>
                    <td class="{'pass' if test_results['found_count'] == test_results['expected_count'] else 'fail'}">{test_results['found_count']}</td>
                </tr>
            </table>
        </div>
        
        <div class="test-section">
            <h2>Device Groups Detected</h2>
            {generate_device_group_cards(test_results['device_groups'])}
        </div>
        
        <div class="test-section">
            <h2>Test Results by Category</h2>
            {generate_test_results_table(test_results['test_categories'])}
        </div>
        
        <div class="test-section">
            <h2>API Endpoint Tests</h2>
            {generate_api_tests_table(test_results['api_tests'])}
        </div>
        
        {generate_failed_tests_section(test_results.get('failed_tests_details', []))}
    </div>
</body>
</html>
    """
    return html


def generate_device_group_cards(device_groups: List[Dict]) -> str:
    """Generate HTML cards for device groups"""
    cards = ""
    for dg in device_groups:
        cards += f"""
        <div class="device-group-card">
            <h3>{dg['name']}</h3>
            <div class="metric">
                <span class="metric-label">Addresses:</span>
                <span class="metric-value">{dg['addresses']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Services:</span>
                <span class="metric-value">{dg['services']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Pre-Rules:</span>
                <span class="metric-value">{dg['pre_rules']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Post-Rules:</span>
                <span class="metric-value">{dg['post_rules']}</span>
            </div>
        </div>
        """
    return cards


def generate_test_results_table(categories: Dict[str, Dict]) -> str:
    """Generate test results table by category"""
    rows = ""
    for category, results in categories.items():
        status = "pass" if results['failed'] == 0 else "fail"
        rows += f"""
        <tr>
            <td>{category}</td>
            <td>{results['total']}</td>
            <td class="pass">{results['passed']}</td>
            <td class="fail">{results['failed']}</td>
            <td class="{status}">{results['success_rate']:.1f}%</td>
        </tr>
        """
    
    return f"""
    <table>
        <tr>
            <th>Category</th>
            <th>Total Tests</th>
            <th>Passed</th>
            <th>Failed</th>
            <th>Success Rate</th>
        </tr>
        {rows}
    </table>
    """


def generate_api_tests_table(api_tests: List[Dict]) -> str:
    """Generate API endpoint test results table"""
    rows = ""
    for test in api_tests:
        status_class = "pass" if test['status'] == "PASS" else "fail"
        rows += f"""
        <tr>
            <td>{test['endpoint']}</td>
            <td>{test['method']}</td>
            <td class="{status_class}">{test['status']}</td>
            <td>{test['response_time_ms']}ms</td>
            <td>{test['response_code']}</td>
        </tr>
        """
    
    return f"""
    <table>
        <tr>
            <th>Endpoint</th>
            <th>Method</th>
            <th>Status</th>
            <th>Response Time</th>
            <th>HTTP Code</th>
        </tr>
        {rows}
    </table>
    """


def generate_failed_tests_section(failed_tests: List[Dict]) -> str:
    """Generate section for failed tests if any"""
    if not failed_tests:
        return ""
    
    rows = ""
    for test in failed_tests:
        rows += f"""
        <tr>
            <td>{test['test_name']}</td>
            <td>{test['category']}</td>
            <td>{test['error']}</td>
        </tr>
        """
    
    return f"""
    <div class="test-section">
        <h2>Failed Tests Details</h2>
        <table>
            <tr>
                <th>Test Name</th>
                <th>Category</th>
                <th>Error</th>
            </tr>
            {rows}
        </table>
    </div>
    """


def run_comprehensive_tests() -> Dict[str, Any]:
    """Run comprehensive tests and collect results"""
    results = {
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'config_file': CONFIG_FILE,
        'api_base_url': API_BASE_URL,
        'expected_count': len(EXPECTED_DEVICE_GROUPS),
        'found_count': 0,
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'success_rate': 0.0,
        'device_groups': [],
        'test_categories': {},
        'api_tests': [],
        'failed_tests_details': []
    }
    
    # Test categories
    categories = {
        'Parser Tests': {'total': 0, 'passed': 0, 'failed': 0},
        'API Tests': {'total': 0, 'passed': 0, 'failed': 0},
        'Data Integrity': {'total': 0, 'passed': 0, 'failed': 0},
        'Edge Cases': {'total': 0, 'passed': 0, 'failed': 0}
    }
    
    # Run parser tests
    print("Running parser tests...")
    try:
        parser = PanoramaXMLParser(CONFIG_FILE)
        summaries = parser.get_device_group_summaries()
        results['found_count'] = len(summaries)
        
        for summary in summaries:
            results['device_groups'].append({
                'name': summary.name,
                'addresses': summary.address_count,
                'services': summary.service_count,
                'pre_rules': summary.pre_security_rules_count,
                'post_rules': summary.post_security_rules_count
            })
        
        categories['Parser Tests']['total'] += 1
        categories['Parser Tests']['passed'] += 1
    except Exception as e:
        categories['Parser Tests']['total'] += 1
        categories['Parser Tests']['failed'] += 1
        results['failed_tests_details'].append({
            'test_name': 'Parser Initialization',
            'category': 'Parser Tests',
            'error': str(e)
        })
    
    # Run API tests
    print("Running API tests...")
    api_endpoints = [
        f"/configs/{CONFIG_NAME}/device-groups",
        f"/configs/{CONFIG_NAME}/device-groups/TCN-DC-SWIFT-VSYS",
        f"/configs/{CONFIG_NAME}/device-groups/TCN-DC-SWIFT-VSYS/addresses",
        f"/configs/{CONFIG_NAME}/device-groups/TCN-DC-SWIFT-VSYS/services",
        f"/configs/{CONFIG_NAME}/device-groups/TCN-DC-SWIFT-VSYS/rules"
    ]
    
    for endpoint in api_endpoints:
        start_time = datetime.datetime.now()
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}")
            response_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
            
            test_result = {
                'endpoint': endpoint,
                'method': 'GET',
                'status': 'PASS' if response.status_code == 200 else 'FAIL',
                'response_time_ms': int(response_time),
                'response_code': response.status_code
            }
            
            results['api_tests'].append(test_result)
            categories['API Tests']['total'] += 1
            if response.status_code == 200:
                categories['API Tests']['passed'] += 1
            else:
                categories['API Tests']['failed'] += 1
                
        except Exception as e:
            categories['API Tests']['total'] += 1
            categories['API Tests']['failed'] += 1
            results['api_tests'].append({
                'endpoint': endpoint,
                'method': 'GET',
                'status': 'FAIL',
                'response_time_ms': 0,
                'response_code': 'ERROR'
            })
    
    # Calculate totals and success rates
    for category, data in categories.items():
        data['success_rate'] = (data['passed'] / data['total'] * 100) if data['total'] > 0 else 0
        results['total_tests'] += data['total']
        results['passed_tests'] += data['passed']
        results['failed_tests'] += data['failed']
    
    results['test_categories'] = categories
    results['success_rate'] = (results['passed_tests'] / results['total_tests'] * 100) if results['total_tests'] > 0 else 0
    
    return results


def main():
    """Generate comprehensive test report"""
    print("Generating comprehensive test report...")
    
    # Run tests
    test_results = run_comprehensive_tests()
    
    # Generate HTML report
    html_report = generate_html_report(test_results)
    
    # Save report
    report_file = "device_group_test_report.html"
    with open(report_file, 'w') as f:
        f.write(html_report)
    
    print(f"\nTest report generated: {report_file}")
    print(f"Total tests: {test_results['total_tests']}")
    print(f"Passed: {test_results['passed_tests']}")
    print(f"Failed: {test_results['failed_tests']}")
    print(f"Success rate: {test_results['success_rate']:.1f}%")
    
    # Return exit code based on results
    return 0 if test_results['failed_tests'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
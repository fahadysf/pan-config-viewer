#!/usr/bin/env python3
"""
Run all integrated pagination and filtering tests and generate a comprehensive report.
"""

import subprocess
import sys
import time
import json
from datetime import datetime
import os


def run_command(cmd, description):
    """Run a command and capture output"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    end_time = time.time()
    
    duration = end_time - start_time
    
    return {
        "description": description,
        "command": cmd,
        "duration": duration,
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "success": result.returncode == 0
    }


def main():
    """Run all integrated tests and generate report"""
    print("Starting Integrated Pagination and Filtering Tests")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Ensure we're in the right directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    results = []
    
    # 1. Run Python integration tests
    results.append(run_command(
        "python -m pytest tests/test_integrated_pagination_filtering.py -v --tb=short",
        "Python Integration Tests"
    ))
    
    # 2. Run performance tests
    results.append(run_command(
        "python -m pytest tests/test_performance_integrated.py -v -s",
        "Performance Tests"
    ))
    
    # 3. Run JavaScript/Jest tests
    results.append(run_command(
        "npm test -- tests/integrated-pagination-filtering.test.js",
        "JavaScript Frontend Tests"
    ))
    
    # 4. Run existing pagination tests to ensure no regression
    results.append(run_command(
        "python -m pytest tests/test_pagination.py -v",
        "Existing Pagination Tests (Regression)"
    ))
    
    # 5. Run filtering tests
    results.append(run_command(
        "python -m pytest test_filtering.py -v",
        "Filtering Tests"
    ))
    
    # Generate comprehensive report
    generate_report(results)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["success"])
    failed_tests = total_tests - passed_tests
    
    print(f"Total test suites: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    
    if failed_tests > 0:
        print("\nFailed tests:")
        for result in results:
            if not result["success"]:
                print(f"  - {result['description']}")
        sys.exit(1)
    else:
        print("\nAll tests passed! ✅")
        sys.exit(0)


def generate_report(results):
    """Generate a detailed HTML report"""
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Integrated Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
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
        h1 {{
            color: #333;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #666;
            margin-top: 30px;
        }}
        .test-suite {{
            margin-bottom: 30px;
            border: 1px solid #ddd;
            border-radius: 4px;
            overflow: hidden;
        }}
        .test-header {{
            padding: 15px;
            background-color: #f8f8f8;
            border-bottom: 1px solid #ddd;
            cursor: pointer;
        }}
        .test-header.success {{
            background-color: #d4edda;
            border-color: #c3e6cb;
        }}
        .test-header.failure {{
            background-color: #f8d7da;
            border-color: #f5c6cb;
        }}
        .test-content {{
            padding: 15px;
            display: none;
        }}
        .test-content.show {{
            display: block;
        }}
        pre {{
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 12px;
        }}
        .summary {{
            background-color: #e9ecef;
            padding: 20px;
            border-radius: 4px;
            margin-bottom: 30px;
        }}
        .summary-stat {{
            display: inline-block;
            margin-right: 30px;
            font-size: 18px;
        }}
        .success-text {{
            color: #28a745;
            font-weight: bold;
        }}
        .failure-text {{
            color: #dc3545;
            font-weight: bold;
        }}
        .duration {{
            color: #6c757d;
            font-size: 14px;
        }}
        .toggle-all {{
            margin-bottom: 20px;
        }}
        button {{
            background-color: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
        }}
        button:hover {{
            background-color: #0056b3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Integrated Pagination and Filtering Test Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="summary">
            <h2>Summary</h2>
            <div class="summary-stat">
                Total Tests: <strong>{len(results)}</strong>
            </div>
            <div class="summary-stat">
                <span class="success-text">Passed: {sum(1 for r in results if r['success'])}</span>
            </div>
            <div class="summary-stat">
                <span class="failure-text">Failed: {sum(1 for r in results if not r['success'])}</span>
            </div>
            <div class="summary-stat">
                Total Duration: <strong>{sum(r['duration'] for r in results):.2f}s</strong>
            </div>
        </div>
        
        <div class="toggle-all">
            <button onclick="toggleAll()">Toggle All Details</button>
        </div>
        
        <h2>Test Results</h2>
"""
    
    for i, result in enumerate(results):
        status_class = "success" if result["success"] else "failure"
        status_text = "✅ PASSED" if result["success"] else "❌ FAILED"
        
        html_content += f"""
        <div class="test-suite">
            <div class="test-header {status_class}" onclick="toggleContent({i})">
                <strong>{result['description']}</strong>
                <span style="float: right;">
                    {status_text} <span class="duration">({result['duration']:.2f}s)</span>
                </span>
            </div>
            <div class="test-content" id="content-{i}">
                <h3>Command</h3>
                <pre>{result['command']}</pre>
                
                <h3>Standard Output</h3>
                <pre>{result['stdout'] or '(empty)'}</pre>
                
                {"<h3>Error Output</h3><pre>" + result['stderr'] + "</pre>" if result['stderr'] else ""}
            </div>
        </div>
"""
    
    html_content += """
    </div>
    
    <script>
        function toggleContent(id) {
            const content = document.getElementById('content-' + id);
            content.classList.toggle('show');
        }
        
        function toggleAll() {
            const contents = document.querySelectorAll('.test-content');
            const allShown = Array.from(contents).every(c => c.classList.contains('show'));
            
            contents.forEach(content => {
                if (allShown) {
                    content.classList.remove('show');
                } else {
                    content.classList.add('show');
                }
            });
        }
    </script>
</body>
</html>
"""
    
    # Write HTML report
    with open("integrated_test_report.html", "w") as f:
        f.write(html_content)
    
    print(f"\nDetailed HTML report generated: integrated_test_report.html")
    
    # Also create a JSON report for programmatic access
    json_report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tests": len(results),
            "passed": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "total_duration": sum(r["duration"] for r in results)
        },
        "results": results
    }
    
    with open("integrated_test_report.json", "w") as f:
        json.dump(json_report, f, indent=2)
    
    print(f"JSON report generated: integrated_test_report.json")


if __name__ == "__main__":
    main()
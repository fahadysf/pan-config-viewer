#!/usr/bin/env python3
"""
Debug script to understand test environment issues
"""
import os
import sys
import glob
import json
from datetime import datetime

def debug_environment():
    """Debug the test environment setup"""
    debug_info = {
        "timestamp": datetime.now().isoformat(),
        "python_path": sys.path,
        "current_dir": os.getcwd(),
        "env_vars": {
            "CONFIG_FILES_PATH": os.environ.get("CONFIG_FILES_PATH", "NOT SET"),
            "PYTHONPATH": os.environ.get("PYTHONPATH", "NOT SET"),
        },
        "test_configs": {},
        "real_configs": {},
        "docker_status": {}
    }
    
    # Check test configs directory
    test_config_dir = os.path.join(os.path.dirname(__file__), "tests", "test_configs")
    debug_info["test_configs"]["path"] = test_config_dir
    debug_info["test_configs"]["exists"] = os.path.exists(test_config_dir)
    if os.path.exists(test_config_dir):
        debug_info["test_configs"]["files"] = glob.glob(os.path.join(test_config_dir, "*.xml"))
    
    # Check real configs directory
    real_config_dir = os.path.join(os.path.dirname(__file__), "config-files")
    debug_info["real_configs"]["path"] = real_config_dir
    debug_info["real_configs"]["exists"] = os.path.exists(real_config_dir)
    if os.path.exists(real_config_dir):
        debug_info["real_configs"]["files"] = glob.glob(os.path.join(real_config_dir, "*.xml"))
    
    # Test importing the app with different configs
    debug_info["import_tests"] = {}
    
    # Test 1: Import with test config
    try:
        os.environ["CONFIG_FILES_PATH"] = test_config_dir
        if 'main' in sys.modules:
            del sys.modules['main']
        import main
        debug_info["import_tests"]["test_config"] = {
            "success": True,
            "available_configs": main.available_configs,
            "config_path": main.CONFIG_FILES_PATH
        }
    except Exception as e:
        debug_info["import_tests"]["test_config"] = {
            "success": False,
            "error": str(e)
        }
    
    # Test 2: Import with real config
    try:
        os.environ["CONFIG_FILES_PATH"] = real_config_dir
        if 'main' in sys.modules:
            del sys.modules['main']
        import main
        debug_info["import_tests"]["real_config"] = {
            "success": True,
            "available_configs": main.available_configs,
            "config_path": main.CONFIG_FILES_PATH
        }
    except Exception as e:
        debug_info["import_tests"]["real_config"] = {
            "success": False,
            "error": str(e)
        }
    
    return debug_info

if __name__ == "__main__":
    debug_data = debug_environment()
    
    # Save to file
    with open("debug_logs/environment_debug.json", "w") as f:
        json.dump(debug_data, f, indent=2)
    
    # Print summary
    print("Debug Environment Report")
    print("=" * 50)
    print(f"Current Directory: {debug_data['current_dir']}")
    print(f"CONFIG_FILES_PATH: {debug_data['env_vars']['CONFIG_FILES_PATH']}")
    print(f"\nTest Configs:")
    print(f"  Path: {debug_data['test_configs']['path']}")
    print(f"  Exists: {debug_data['test_configs']['exists']}")
    print(f"  Files: {debug_data['test_configs'].get('files', [])}")
    print(f"\nReal Configs:")
    print(f"  Path: {debug_data['real_configs']['path']}")
    print(f"  Exists: {debug_data['real_configs']['exists']}")
    print(f"  Files: {debug_data['real_configs'].get('files', [])}")
    print(f"\nImport Tests:")
    for test_name, result in debug_data['import_tests'].items():
        print(f"  {test_name}: {'✅ Success' if result.get('success') else '❌ Failed'}")
        if result.get('success'):
            print(f"    Available configs: {result.get('available_configs')}")
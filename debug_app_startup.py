#!/usr/bin/env python3
"""
Debug app startup and configuration loading
"""
import os
import sys
import asyncio
import json
from datetime import datetime

# Set test environment
test_config_dir = os.path.join(os.path.dirname(__file__), "tests", "test_configs")
os.environ["CONFIG_FILES_PATH"] = test_config_dir

# Import app
from main import app, startup_event, available_configs, CONFIG_FILES_PATH

async def test_startup():
    """Test the startup event"""
    debug_info = {
        "timestamp": datetime.now().isoformat(),
        "CONFIG_FILES_PATH": CONFIG_FILES_PATH,
        "before_startup": {
            "available_configs": available_configs.copy() if available_configs else []
        }
    }
    
    # Manually trigger startup
    print("Triggering startup event...")
    await startup_event()
    
    debug_info["after_startup"] = {
        "available_configs": available_configs.copy() if available_configs else []
    }
    
    # Test with TestClient
    print("\nTesting with TestClient...")
    from fastapi.testclient import TestClient
    
    with TestClient(app) as client:
        # The TestClient should trigger startup events
        response = client.get("/api/v1/configs")
        debug_info["test_client_response"] = {
            "status_code": response.status_code,
            "data": response.json()
        }
    
    return debug_info

async def test_direct_import():
    """Test importing and manually running startup"""
    # Clear modules
    for module in ['main', 'parser', 'models']:
        if module in sys.modules:
            del sys.modules[module]
    
    # Set environment
    os.environ["CONFIG_FILES_PATH"] = test_config_dir
    
    # Import fresh
    import main
    
    # Check initial state
    print(f"Initial available_configs: {main.available_configs}")
    print(f"CONFIG_FILES_PATH: {main.CONFIG_FILES_PATH}")
    
    # Run startup
    await main.startup_event()
    
    print(f"After startup available_configs: {main.available_configs}")
    
    return {
        "CONFIG_FILES_PATH": main.CONFIG_FILES_PATH,
        "available_configs": main.available_configs
    }

if __name__ == "__main__":
    print("Debug App Startup")
    print("=" * 50)
    
    # Test 1: Regular startup
    debug_data = asyncio.run(test_startup())
    
    with open("debug_logs/startup_debug.json", "w") as f:
        json.dump(debug_data, f, indent=2)
    
    print(f"CONFIG_FILES_PATH: {debug_data['CONFIG_FILES_PATH']}")
    print(f"Before startup: {debug_data['before_startup']['available_configs']}")
    print(f"After startup: {debug_data['after_startup']['available_configs']}")
    print(f"TestClient response: {debug_data['test_client_response']['status_code']}")
    print(f"TestClient configs: {debug_data['test_client_response']['data']['configs']}")
    
    # Test 2: Direct import
    print("\n" + "=" * 50)
    print("Testing direct import and startup...")
    direct_result = asyncio.run(test_direct_import())
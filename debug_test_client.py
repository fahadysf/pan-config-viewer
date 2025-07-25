#!/usr/bin/env python3
"""
Debug TestClient behavior
"""
import os
import sys

# Clear environment
if "CONFIG_FILES_PATH" in os.environ:
    del os.environ["CONFIG_FILES_PATH"]

# Set test config path
test_config_path = os.path.join(os.path.dirname(__file__), "tests", "test_configs")
print(f"Setting CONFIG_FILES_PATH to: {test_config_path}")
os.environ["CONFIG_FILES_PATH"] = test_config_path

# Clear modules
for module in list(sys.modules.keys()):
    if module.startswith(('main', 'parser', 'models')):
        del sys.modules[module]

# Import and test
from fastapi.testclient import TestClient

print("\nImporting main module...")
import main

print(f"After import - CONFIG_FILES_PATH: {main.CONFIG_FILES_PATH}")
print(f"After import - available_configs: {main.available_configs}")

print("\nCreating TestClient...")
client = TestClient(main.app)

print(f"After TestClient - available_configs: {main.available_configs}")

print("\nMaking request to /api/v1/configs...")
response = client.get("/api/v1/configs")
print(f"Response status: {response.status_code}")
print(f"Response data: {response.json()}")

print(f"\nFinal available_configs: {main.available_configs}")

# Try another approach - using with statement
print("\n" + "="*50)
print("Testing with 'with' statement...")

# Clear again
for module in list(sys.modules.keys()):
    if module.startswith(('main', 'parser', 'models')):
        del sys.modules[module]

os.environ["CONFIG_FILES_PATH"] = test_config_path

from main import app
from fastapi.testclient import TestClient

with TestClient(app) as client:
    print("Inside with statement...")
    response = client.get("/api/v1/configs")
    print(f"Response: {response.json()}")
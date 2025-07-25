"""
Factory for creating test app instances with proper configuration
"""
import os
import sys
import importlib
from typing import Optional
from fastapi.testclient import TestClient


def create_test_app(config_path: str):
    """Create a fresh app instance with specific config path"""
    # Store original env
    original_env = os.environ.get("CONFIG_FILES_PATH")
    
    # Set new config path
    os.environ["CONFIG_FILES_PATH"] = config_path
    
    # Force reload of main module
    if 'main' in sys.modules:
        # Remove all related modules
        modules_to_remove = [m for m in sys.modules if m.startswith('main') or m == 'parser' or m == 'models']
        for module in modules_to_remove:
            del sys.modules[module]
    
    # Import fresh
    import main
    
    # Restore original env if needed
    if original_env:
        os.environ["CONFIG_FILES_PATH"] = original_env
    elif "CONFIG_FILES_PATH" in os.environ:
        del os.environ["CONFIG_FILES_PATH"]
    
    return main.app


def get_test_client_for_config(config_name: str) -> TestClient:
    """Get test client for specific configuration"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if config_name == "test":
        config_path = os.path.join(base_dir, "tests", "test_configs")
    elif config_name == "real":
        config_path = os.path.join(base_dir, "config-files")
    else:
        raise ValueError(f"Unknown config name: {config_name}")
    
    app = create_test_app(config_path)
    return TestClient(app)
"""
Pytest configuration and fixtures
"""
import os
import sys
import pytest
from typing import Generator

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def test_config_path():
    """Path to test configuration files"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_configs")


@pytest.fixture(scope="session") 
def real_config_path():
    """Path to real configuration files"""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config-files"
    )


@pytest.fixture
def set_test_config(test_config_path):
    """Set CONFIG_FILES_PATH to test configs"""
    original = os.environ.get("CONFIG_FILES_PATH")
    os.environ["CONFIG_FILES_PATH"] = test_config_path
    yield
    if original:
        os.environ["CONFIG_FILES_PATH"] = original
    else:
        os.environ.pop("CONFIG_FILES_PATH", None)


@pytest.fixture
def set_real_config(real_config_path):
    """Set CONFIG_FILES_PATH to real configs"""
    original = os.environ.get("CONFIG_FILES_PATH")
    os.environ["CONFIG_FILES_PATH"] = real_config_path
    yield
    if original:
        os.environ["CONFIG_FILES_PATH"] = original
    else:
        os.environ.pop("CONFIG_FILES_PATH", None)


@pytest.fixture(scope="module")
def test_client():
    """Create test client for API"""
    from fastapi.testclient import TestClient
    from main import app
    
    with TestClient(app) as client:
        yield client


# Configure pytest to find our tests
def pytest_configure(config):
    """Configure pytest"""
    import sys
    # Ensure the project root is in the path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
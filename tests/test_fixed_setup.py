"""
Fixed test setup that properly handles app initialization
"""
import os
import sys
import pytest
from typing import Generator

# Ensure parent directory is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_test_client_for_config(config_type: str):
    """Get a properly initialized test client"""
    # Clear any existing modules
    for module in ['main', 'parser', 'models']:
        if module in sys.modules:
            del sys.modules[module]
    
    # Set appropriate config path
    if config_type == "test":
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "tests", "test_configs"
        )
    else:  # real
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config-files"
        )
    
    os.environ["CONFIG_FILES_PATH"] = config_path
    
    # Import fresh app
    from fastapi.testclient import TestClient
    from main import app
    
    # Create client which will trigger startup
    return TestClient(app)


@pytest.fixture(scope="function")
def test_client():
    """Fixture for test config client"""
    return get_test_client_for_config("test")


@pytest.fixture(scope="function") 
def real_client():
    """Fixture for real config client"""
    return get_test_client_for_config("real")


def test_with_test_config(test_client):
    """Test that test config is loaded"""
    response = test_client.get("/api/v1/configs")
    assert response.status_code == 200
    data = response.json()
    assert "test_panorama" in data["configs"]
    print(f"✅ Test config loaded: {data['configs']}")


def test_with_real_config(real_client):
    """Test that real config is loaded"""
    response = real_client.get("/api/v1/configs")
    assert response.status_code == 200
    data = response.json()
    assert "pan-bkp-202507151414" in data["configs"]
    print(f"✅ Real config loaded: {data['configs']}")


def test_addresses_from_test_config(test_client):
    """Test getting addresses from test config"""
    response = test_client.get("/api/v1/configs/test_panorama/addresses")
    assert response.status_code == 200
    addresses = response.json()
    assert len(addresses) > 0
    
    # Check expected test addresses
    names = [addr["name"] for addr in addresses]
    assert "test-server" in names
    print(f"✅ Found {len(addresses)} addresses in test config")


def test_addresses_from_real_config(real_client):
    """Test getting addresses from real config"""
    response = real_client.get("/api/v1/configs/pan-bkp-202507151414/addresses")
    assert response.status_code == 200
    addresses = response.json()
    assert len(addresses) > 0
    print(f"✅ Found {len(addresses)} addresses in real config")


if __name__ == "__main__":
    # Run tests manually
    print("Testing Fixed Setup")
    print("=" * 50)
    
    test_client = get_test_client_for_config("test")
    real_client = get_test_client_for_config("real")
    
    print("\n1. Testing with test config:")
    test_with_test_config(test_client)
    test_addresses_from_test_config(test_client)
    
    print("\n2. Testing with real config:")
    test_with_real_config(real_client)
    test_addresses_from_real_config(real_client)
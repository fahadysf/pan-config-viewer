"""
Simple validation tests that work with the running Docker container
"""
import requests
import json

BASE_URL = "http://localhost:8000"
CONFIG_NAME = "pan-bkp-202507151414"

def test_api_basics():
    """Test basic API functionality"""
    print("\n🧪 Testing PAN-OS Configuration API")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    # Test 1: Health check
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        assert response.status_code == 200
        print("✅ Health check passed")
        passed += 1
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        failed += 1
    
    # Test 2: List configs
    try:
        response = requests.get(f"{BASE_URL}/api/v1/configs")
        assert response.status_code == 200
        data = response.json()
        assert CONFIG_NAME in data["configs"]
        print(f"✅ Config listing passed - found {len(data['configs'])} configs")
        passed += 1
    except Exception as e:
        print(f"❌ Config listing failed: {e}")
        failed += 1
    
    # Test 3: Get addresses
    try:
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/addresses")
        assert response.status_code == 200
        addresses = response.json()
        assert len(addresses) > 0
        print(f"✅ Address retrieval passed - found {len(addresses)} addresses")
        passed += 1
    except Exception as e:
        print(f"❌ Address retrieval failed: {e}")
        failed += 1
    
    # Test 4: Get specific address
    try:
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/addresses")
        addresses = response.json()
        if addresses:
            first_addr = addresses[0]["name"]
            response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/addresses/{first_addr}")
            assert response.status_code == 200
            addr = response.json()
            assert addr["name"] == first_addr
            assert "xpath" in addr
            print(f"✅ Specific address retrieval passed - got '{first_addr}'")
            passed += 1
        else:
            print("⚠️  Skipped specific address test - no addresses found")
    except Exception as e:
        print(f"❌ Specific address retrieval failed: {e}")
        failed += 1
    
    # Test 5: Check field format
    try:
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/addresses")
        addresses = response.json()
        if addresses:
            addr = addresses[0]
            # Check for kebab-case fields
            assert "parent-device-group" in addr
            assert "parent-template" in addr
            assert "parent-vsys" in addr
            print("✅ Field format check passed - using kebab-case")
            passed += 1
        else:
            print("⚠️  Skipped field format test - no addresses found")
    except Exception as e:
        print(f"❌ Field format check failed: {e}")
        failed += 1
    
    # Test 6: Device groups
    try:
        response = requests.get(f"{BASE_URL}/api/v1/configs/{CONFIG_NAME}/device-groups")
        assert response.status_code == 200
        dgs = response.json()
        assert isinstance(dgs, list)
        print(f"✅ Device groups retrieval passed - found {len(dgs)} device groups")
        passed += 1
    except Exception as e:
        print(f"❌ Device groups retrieval failed: {e}")
        failed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Summary:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   Total: {passed + failed}")
    
    return failed == 0

if __name__ == "__main__":
    import sys
    success = test_api_basics()
    sys.exit(0 if success else 1)
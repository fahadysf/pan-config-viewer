"""
Test runner that properly restarts the app with correct config path
"""
import os
import sys
import subprocess
import time

def run_tests_with_config(config_path, test_file):
    """Run tests with specific config path"""
    env = os.environ.copy()
    env["CONFIG_FILES_PATH"] = config_path
    
    print(f"\n🔍 Running {test_file} with CONFIG_FILES_PATH={config_path}")
    
    # Run pytest with the environment
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short", "-x"],
        env=env
    )
    
    return result.returncode

def main():
    """Main test runner"""
    print("🚀 Running tests with proper environment setup")
    
    # Get absolute paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_config_path = os.path.join(base_dir, "tests", "test_configs")
    real_config_path = os.path.join(base_dir, "config-files")
    
    # Run tests
    results = []
    
    # Test with sample config
    print("\n1️⃣ Testing with sample configuration...")
    results.append(run_tests_with_config(test_config_path, "tests/test_api.py"))
    
    # Test with real config
    print("\n2️⃣ Testing with real configuration...")
    results.append(run_tests_with_config(real_config_path, "tests/test_real_config.py"))
    
    # Summary
    failed = sum(1 for r in results if r != 0)
    passed = len(results) - failed
    
    print(f"\n📊 Test Summary:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    return 1 if failed > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
#\!/usr/bin/env python3
"""Check what's stored in ZODB cache"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zodb_cache import get_zodb_cache

# Load from ZODB
cache = get_zodb_cache()
data = cache.load_from_cache('pan-bkp-202507151414')

if data and 'addresses' in data:
    addresses = data['addresses']
    print(f"Loaded {len(addresses)} addresses from ZODB")
    
    # Check the type of first few items
    for i, addr in enumerate(addresses[:3]):
        print(f"\nItem {i}:")
        print(f"  Type: {type(addr)}")
        if hasattr(addr, '__dict__'):
            print(f"  __dict__: {addr.__dict__}")
        elif isinstance(addr, dict):
            print(f"  Dict keys: {addr.keys()}")
            print(f"  Name: {addr.get('name')}")
            print(f"  Type: {addr.get('type')}")
        else:
            print(f"  Value: {addr}")
else:
    print("No address data in ZODB cache")

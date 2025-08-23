#\!/usr/bin/env python3
"""Test filtering directly with cached data"""

import sys
sys.path.insert(0, '/Users/fahad/code/pan-config-viewer')

from background_cache import background_cache
from models import AddressObject, AddressType
from filtering import apply_filters, ADDRESS_FILTERS, FilterProcessor

# Get cached data
cached = background_cache.get_cached_data('pan-bkp-202507151414', 'addresses', 1, 1000)
if not cached:
    print("No cached data\!")
    sys.exit(1)

items = cached['items']
print(f"Total cached items: {len(items)}")

# Check types in cached data
types_seen = set()
for item in items:
    types_seen.add(item.get('type'))
print(f"Types in cache: {types_seen}")

# Count FQDN items
fqdn_count = sum(1 for item in items if item.get('type') == 'fqdn')
print(f"FQDN items in cache: {fqdn_count}")

# Now test filtering with advanced filters
print("\n--- Testing advanced filter type_eq=fqdn ---")

# Simulate what the API does
advanced_filters = {'type_eq': 'fqdn'}
filtered_data = background_cache.get_filtered_cached_data(
    'pan-bkp-202507151414', 'addresses',
    filters={'advanced': advanced_filters},
    page=1,
    page_size=100
)

if filtered_data:
    print(f"Filtered items: {filtered_data['total_items']}")
    if filtered_data['items']:
        for item in filtered_data['items'][:3]:
            print(f"  - {item['name']}: type={item.get('type')}")
else:
    print("No filtered data returned")

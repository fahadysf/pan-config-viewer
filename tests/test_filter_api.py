#\!/usr/bin/env python3
import requests

# Test type filtering
print("Testing type filter for FQDN addresses...")
url = "http://localhost:8000/api/v1/configs/pan-bkp-202507151414/addresses"
params = {
    "limit": 10,
    "filter.type.eq": "fqdn"
}

response = requests.get(url, params=params)
data = response.json()

print(f"Response status: {response.status_code}")
print(f"Total items: {data.get('total_items', 0)}")
print(f"Items returned: {len(data.get('items', []))}")

if data.get('items'):
    print("\nFirst few items:")
    for item in data['items'][:3]:
        print(f"  - {item['name']}: type={item.get('type')}, fqdn={item.get('fqdn')}")
else:
    print("\nNo items returned\!")
    
# Test without filter to see all items
print("\n\nTesting without filter to see available types...")
params = {"limit": 10}
response = requests.get(url, params=params)
data = response.json()

print(f"Total items: {data.get('total_items', 0)}")
if data.get('items'):
    print("Types found:")
    types_seen = set()
    for item in data['items']:
        types_seen.add(item.get('type', 'unknown'))
    print(f"  Types: {types_seen}")
    
    # Show some FQDN examples
    fqdn_items = [item for item in data['items'] if item.get('type') == 'fqdn']
    if fqdn_items:
        print(f"\nFound {len(fqdn_items)} FQDN items in first {len(data['items'])} results")
        for item in fqdn_items[:3]:
            print(f"  - {item['name']}: fqdn={item.get('fqdn')}")

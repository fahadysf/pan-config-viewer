# Address Objects API

The Address Objects API provides endpoints for querying IP addresses, FQDNs, and IP ranges configured in your Panorama setup.

## Endpoints

### List All Address Objects
```http
GET /api/v1/configs/{config}/addresses
```

### List Device-Group Address Objects
```http
GET /api/v1/configs/{config}/device-groups/{device_group}/addresses
```

### List Template Address Objects
```http
GET /api/v1/configs/{config}/templates/{template}/addresses
```

### Get Specific Address Object
```http
GET /api/v1/configs/{config}/addresses/{name}
```

## Address Object Schema

```json
{
  "name": "web-server-01",
  "type": "ip-netmask",
  "ip-netmask": "192.168.1.100/32",
  "ip-range": null,
  "fqdn": null,
  "description": "Production web server",
  "tag": ["production", "web"],
  "xpath": "/config/devices/entry/address/entry[123]",
  "parent-device-group": "DMZ",
  "parent-template": null,
  "parent-vsys": null
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique identifier for the address object |
| `type` | enum | Type of address: `ip-netmask`, `ip-range`, or `fqdn` |
| `ip-netmask` | string | IP address with netmask (e.g., "10.0.0.1/32") |
| `ip-range` | string | IP address range (e.g., "10.0.0.1-10.0.0.254") |
| `fqdn` | string | Fully qualified domain name |
| `description` | string | Optional description |
| `tag` | array | List of associated tags |
| `xpath` | string | XML path in configuration |
| `parent-device-group` | string | Parent device group name |
| `parent-template` | string | Parent template name |
| `parent-vsys` | string | Parent virtual system |

## Filtering Options

### Available Filter Fields

| Field | Type | Operators | Description | Examples |
|-------|------|-----------|-------------|----------|
| `name` | string | All text operators | Object name | `filter.name.contains=server`<br>`filter.name.starts_with=web-`<br>`filter.name.regex=^srv-\d+$` |
| `ip` | string | All text operators | IP address (alias for ip_netmask) | `filter.ip.starts_with=10.`<br>`filter.ip.equals=192.168.1.1`<br>`filter.ip.contains=.100` |
| `ip_netmask` | string | All text operators | IP with netmask | `filter.ip_netmask.equals=10.0.0.0/8`<br>`filter.ip_netmask.starts_with=172.16.` |
| `ip_range` | string | All text operators | IP range | `filter.ip_range.contains=10.0.0`<br>`filter.ip_range.starts_with=192.168.` |
| `fqdn` | string | All text operators | Domain name | `filter.fqdn.ends_with=.com`<br>`filter.fqdn.contains=mail`<br>`filter.fqdn.equals=www.example.com` |
| `type` | enum | `eq`, `ne`, `in`, `not_in` | Address type | `filter.type.equals=fqdn`<br>`filter.type.ne=ip-range`<br>`filter.type.in=fqdn,ip-netmask` |
| `tag` | array | `in`, `not_in`, `contains`, `not_contains` | Tags | `filter.tag.in=production`<br>`filter.tag.not_contains=test`<br>`filter.tag.contains=dmz` |
| `description` | string | All text operators | Description text | `filter.description.contains=server`<br>`filter.description.not_contains=deprecated` |
| `parent_device_group` | string | All text operators | Device group | `filter.parent_device_group.equals=DMZ`<br>`filter.parent_device_group.starts_with=Branch-` |
| `parent_template` | string | All text operators | Template | `filter.parent_template.equals=Base-Template` |
| `parent_vsys` | string | All text operators | Virtual system | `filter.parent_vsys.equals=vsys1` |
| `location` | computed | `eq`, `ne` | Computed location type | `filter.location.equals=shared`<br>`filter.location.equals=device-group` |

## Complete Examples

### Example 1: Find All IP Addresses in 10.0.0.0/8
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.ip.starts_with=10.&\
filter.type.equals=ip-netmask"
```

**Response:**
```json
{
  "items": [
    {
      "name": "internal-server-01",
      "type": "ip-netmask",
      "ip-netmask": "10.1.1.100/32",
      "description": "Internal application server",
      "tag": ["internal", "production"]
    },
    {
      "name": "database-cluster",
      "type": "ip-netmask",
      "ip-netmask": "10.2.0.0/24",
      "description": "Database cluster subnet",
      "tag": ["database", "critical"]
    }
  ],
  "total_items": 2,
  "page": 1,
  "page_size": 500,
  "total_pages": 1
}
```

### Example 2: Find All FQDN Addresses for a Domain
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.type.equals=fqdn&\
filter.fqdn.ends_with=.example.com"
```

### Example 3: Find Production Servers in DMZ
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.tag.in=production&\
filter.parent_device_group.equals=DMZ&\
filter.type.equals=ip-netmask"
```

### Example 4: Find Addresses by IP Range
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.type.equals=ip-range&\
filter.ip_range.contains=192.168"
```

### Example 5: Complex Multi-Filter Query
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.name.starts_with=web-&\
filter.ip.starts_with=10.&\
filter.tag.in=production,staging&\
filter.description.not_contains=deprecated&\
limit=50&\
offset=0"
```

## Device-Group Specific Queries

### Query Addresses in Specific Device Group
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/device-groups/DMZ-DG/addresses?\
filter.name.contains=server"
```

### Query Addresses in Template
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/templates/Branch-Template/addresses?\
filter.type.equals=fqdn"
```

## Common Use Cases

### 1. Subnet Analysis
Find all addresses in a specific subnet:
```bash
# Find all 192.168.1.0/24 addresses
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.ip.starts_with=192.168.1.&\
filter.type.equals=ip-netmask"
```

### 2. FQDN Audit
Find all external domains:
```bash
# Find all non-.internal domains
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.type.equals=fqdn&\
filter.fqdn.not_contains=.internal"
```

### 3. Tag-Based Inventory
Get all production assets:
```bash
# Find all production-tagged addresses
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.tag.contains=production"
```

### 4. Naming Convention Check
Verify naming standards:
```bash
# Find addresses not following naming convention
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.name.regex=^(?!srv-|web-|db-).*$"
```

### 5. Orphaned Objects
Find unused addresses:
```bash
# Find addresses without descriptions (potentially unused)
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.description.equals=&\
filter.tag.exists=false"
```

## Pagination

All list endpoints support pagination:

```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.type.equals=ip-netmask&\
limit=20&\
offset=40"
```

**Pagination Parameters:**
- `limit`: Number of items per page (default: 500, max: 1000)
- `offset`: Number of items to skip (default: 0)

## Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Invalid filter parameters |
| 404 | Configuration or endpoint not found |
| 500 | Internal server error |

## Performance Tips

1. **Use specific filters** to reduce result set size
2. **Combine filters** to narrow down results efficiently
3. **Use pagination** for large result sets
4. **Filter by type first** when looking for specific address types
5. **Use indexed fields** like `name` and `type` for faster queries

## Field Aliases

Some fields support aliases for convenience:

| Field | Aliases |
|-------|---------|
| `ip_netmask` | `ip` |
| `parent_device_group` | `device_group`, `dg` |
| `parent_template` | `template` |

## Limitations

- Maximum 1000 items per page
- Regex patterns are limited to 256 characters
- Filter values are limited to 1024 characters
- Maximum 20 filters per request

## Related Endpoints

- [Address Groups](address-groups.md) - Groups of address objects
- [Security Rules](security-rules.md) - Rules using address objects
- [NAT Rules](nat-rules.md) - NAT rules referencing addresses

## SDK Examples

### Python
```python
import requests

# Find all servers in DMZ
response = requests.get(
    "http://localhost:8000/api/v1/configs/panorama/addresses",
    params={
        "filter.name.contains": "server",
        "filter.parent_device_group.equals": "DMZ",
        "limit": 100
    }
)
addresses = response.json()["items"]
```

### JavaScript
```javascript
// Find all FQDN addresses
const params = new URLSearchParams({
    'filter.type.equals': 'fqdn',
    'filter.fqdn.ends_with': '.com'
});

fetch(`http://localhost:8000/api/v1/configs/panorama/addresses?${params}`)
    .then(response => response.json())
    .then(data => console.log(data.items));
```

### Go
```go
// Find addresses in subnet
params := url.Values{}
params.Add("filter.ip.starts_with", "10.0.0.")
params.Add("filter.type.equals", "ip-netmask")

resp, err := http.Get("http://localhost:8000/api/v1/configs/panorama/addresses?" + params.Encode())
```
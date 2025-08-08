# Service Objects API

The Service Objects API provides endpoints for querying TCP and UDP service definitions configured in your Panorama setup.

## Endpoints

### List All Service Objects
```http
GET /api/v1/configs/{config}/services
```

### List Device-Group Service Objects
```http
GET /api/v1/configs/{config}/device-groups/{device_group}/services
```

### List Template Service Objects
```http
GET /api/v1/configs/{config}/templates/{template}/services
```

### Get Specific Service Object
```http
GET /api/v1/configs/{config}/services/{name}
```

## Service Object Schema

```json
{
  "name": "custom-web-8080",
  "protocol": {
    "tcp": {
      "port": "8080",
      "source-port": "1024-65535"
    },
    "udp": null
  },
  "description": "Custom web service on port 8080",
  "tag": ["web", "custom"],
  "xpath": "/config/devices/entry/service/entry[45]",
  "parent-device-group": "DMZ",
  "parent-template": null,
  "parent-vsys": null
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique identifier for the service object |
| `protocol` | object | Protocol definition (tcp or udp) |
| `protocol.tcp` | object | TCP protocol configuration |
| `protocol.tcp.port` | string | Destination port(s) |
| `protocol.tcp.source-port` | string | Source port(s) |
| `protocol.udp` | object | UDP protocol configuration |
| `protocol.udp.port` | string | Destination port(s) |
| `protocol.udp.source-port` | string | Source port(s) |
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
| `name` | string | All text operators | Service name | `filter.name.contains=web`<br>`filter.name.starts_with=custom-`<br>`filter.name.regex=^tcp-\d+$` |
| `protocol` | computed | `eq`, `ne` | Protocol type (tcp/udp) | `filter.protocol.equals=tcp`<br>`filter.protocol.ne=udp` |
| `port` | computed | All operators | Destination port | `filter.port.equals=443`<br>`filter.port.gt=8000`<br>`filter.port.contains=8080` |
| `source_port` | computed | Text operators | Source port | `filter.source_port.contains=1024`<br>`filter.source_port.equals=any` |
| `tag` | array | `in`, `not_in`, `contains` | Tags | `filter.tag.in=web,critical`<br>`filter.tag.contains=custom` |
| `description` | string | All text operators | Description text | `filter.description.contains=application`<br>`filter.description.not_contains=deprecated` |
| `parent_device_group` | string | All text operators | Device group | `filter.parent_device_group.equals=DMZ` |

## Complete Examples

### Example 1: Find All HTTPS Services
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.protocol.equals=tcp&\
filter.port.equals=443"
```

**Response:**
```json
{
  "items": [
    {
      "name": "service-https",
      "protocol": {
        "tcp": {
          "port": "443"
        }
      },
      "description": "HTTPS traffic",
      "tag": ["web", "encrypted"]
    },
    {
      "name": "custom-https-app",
      "protocol": {
        "tcp": {
          "port": "443",
          "source-port": "1024-65535"
        }
      },
      "description": "Custom HTTPS application",
      "tag": ["application"]
    }
  ],
  "total_items": 2,
  "page": 1,
  "page_size": 500,
  "total_pages": 1
}
```

### Example 2: Find High-Port TCP Services
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.protocol.equals=tcp&\
filter.port.gte=8000&\
filter.port.lte=9000"
```

### Example 3: Find All UDP Services
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.protocol.equals=udp"
```

### Example 4: Find Services by Port Range
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.port.contains=8080-8090"
```

### Example 5: Find Custom Services with Tags
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.name.starts_with=custom-&\
filter.tag.in=production,critical&\
filter.protocol.equals=tcp"
```

## Port Filtering Examples

### Single Port
```bash
# Find services on port 80
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.port.equals=80"
```

### Port Range
```bash
# Find services with ports in 8000-9000 range
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.port.contains=80"  # Matches 80, 8080, 8081, etc.

# More specific range check
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.port.gte=8000&\
filter.port.lte=9000"
```

### Multiple Ports
```bash
# Find services on common web ports
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.port.in=80,443,8080,8443"
```

## Common Use Cases

### 1. Security Audit - Non-Standard Ports
Find web services on non-standard ports:
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.name.contains=web&\
filter.port.ne=80&\
filter.port.ne=443"
```

### 2. High-Risk Services
Find services with unrestricted source ports:
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.source_port.equals=any"
```

### 3. Protocol Analysis
Get TCP vs UDP service distribution:
```bash
# Count TCP services
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.protocol.equals=tcp"

# Count UDP services
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.protocol.equals=udp"
```

### 4. Custom Service Inventory
Find all custom-defined services:
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.name.starts_with=custom-"
```

### 5. Deprecated Service Cleanup
Find services marked as deprecated:
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.description.contains=deprecated&\
filter.tag.contains=remove"
```

## Device-Group Specific Queries

### Query Services in Specific Device Group
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/device-groups/DMZ-DG/services?\
filter.protocol.equals=tcp&\
filter.port.lt=1024"
```

### Query Services in Template
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/templates/Branch-Template/services?\
filter.tag.contains=branch"
```

## Advanced Filtering Patterns

### 1. Well-Known Ports (0-1023)
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.port.lt=1024"
```

### 2. Registered Ports (1024-49151)
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.port.gte=1024&\
filter.port.lte=49151"
```

### 3. Dynamic/Private Ports (49152-65535)
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.port.gte=49152"
```

### 4. Common Application Ports
```bash
# Database services
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.port.in=3306,5432,1433,1521,27017"

# Web services
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.port.in=80,443,8080,8443"

# Email services
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.port.in=25,110,143,465,587,993,995"
```

## Pagination

All list endpoints support pagination:

```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.protocol.equals=tcp&\
limit=25&\
offset=50"
```

**Pagination Parameters:**
- `limit`: Number of items per page (default: 500, max: 1000)
- `offset`: Number of items to skip (default: 0)

## Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Invalid filter parameters |
| 404 | Configuration or service not found |
| 500 | Internal server error |

## Performance Tips

1. **Filter by protocol first** when looking for TCP or UDP services
2. **Use exact port matching** when possible (`equals` vs `contains`)
3. **Combine filters** to reduce result set size
4. **Use pagination** for large service lists
5. **Cache frequently accessed service definitions**

## SDK Examples

### Python
```python
import requests

def find_services_by_port_range(start_port, end_port):
    """Find all services within a port range"""
    response = requests.get(
        "http://localhost:8000/api/v1/configs/panorama/services",
        params={
            "filter.port.gte": start_port,
            "filter.port.lte": end_port,
            "filter.protocol.equals": "tcp"
        }
    )
    return response.json()["items"]

# Find all services between ports 8000-9000
services = find_services_by_port_range(8000, 9000)
for service in services:
    print(f"{service['name']}: {service['protocol']['tcp']['port']}")
```

### JavaScript
```javascript
// Find all custom web services
async function findCustomWebServices() {
    const params = new URLSearchParams({
        'filter.name.starts_with': 'custom-',
        'filter.tag.contains': 'web',
        'filter.protocol.equals': 'tcp'
    });
    
    const response = await fetch(
        `http://localhost:8000/api/v1/configs/panorama/services?${params}`
    );
    const data = await response.json();
    return data.items;
}

findCustomWebServices().then(services => {
    services.forEach(service => {
        console.log(`${service.name}: TCP/${service.protocol.tcp.port}`);
    });
});
```

### Go
```go
package main

import (
    "encoding/json"
    "fmt"
    "net/http"
    "net/url"
)

// Find high-port services
func findHighPortServices() {
    params := url.Values{}
    params.Add("filter.port.gt", "49151")
    params.Add("filter.protocol.equals", "tcp")
    
    resp, err := http.Get("http://localhost:8000/api/v1/configs/panorama/services?" + params.Encode())
    if err != nil {
        panic(err)
    }
    defer resp.Body.Close()
    
    var result map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&result)
    
    items := result["items"].([]interface{})
    for _, item := range items {
        service := item.(map[string]interface{})
        fmt.Printf("Service: %s\n", service["name"])
    }
}
```

## Related Endpoints

- [Service Groups](service-groups.md) - Groups of service objects
- [Security Rules](security-rules.md) - Rules using service objects
- [NAT Rules](nat-rules.md) - NAT rules referencing services

## Best Practices

1. **Naming Conventions**: Use consistent prefixes like `custom-` for custom services
2. **Port Documentation**: Always include descriptions for non-standard ports
3. **Tag Usage**: Tag services by application, environment, or criticality
4. **Source Port Restrictions**: Avoid using "any" for source ports when possible
5. **Regular Audits**: Periodically review unused or deprecated services
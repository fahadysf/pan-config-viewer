# Quick Start Guide

Get up and running with the PAN Config Viewer API in minutes!

## Prerequisites

- Python 3.8 or higher
- PAN-OS Panorama configuration backup file (XML)
- 2GB RAM minimum
- 10GB disk space for large configurations

## Installation

### Using pip
```bash
pip install pan-config-viewer
```

### Using Docker
```bash
docker pull pan-config-viewer:latest
docker run -p 8000:8000 -v /path/to/configs:/configs pan-config-viewer
```

### From Source
```bash
git clone https://github.com/yourusername/pan-config-viewer.git
cd pan-config-viewer
pip install -r requirements.txt
```

## Configuration

### 1. Set Configuration Path
Create a `.env` file or set environment variables:

```bash
# .env file
CONFIG_FILES_PATH=/path/to/panorama/configs
DEFAULT_CONFIG=panorama-backup.xml
API_PORT=8000
API_HOST=0.0.0.0
```

### 2. Place Configuration Files
Copy your Panorama XML backup files to the configuration directory:

```bash
cp panorama-backup.xml /path/to/panorama/configs/
```

## Starting the Server

### Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker
```bash
docker run -d \
  --name pan-config-viewer \
  -p 8000:8000 \
  -v /path/to/configs:/configs \
  -e CONFIG_FILES_PATH=/configs \
  pan-config-viewer
```

## Verify Installation

### 1. Check API Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. List Available Configurations
```bash
curl http://localhost:8000/api/v1/configs
```

Expected response:
```json
{
  "configs": [
    "panorama-backup.xml",
    "panorama-prod.xml"
  ]
}
```

### 3. Access API Documentation
Open your browser and navigate to:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Your First API Calls

### 1. List All Address Objects
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?limit=10"
```

### 2. Search for Specific Addresses
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.name.contains=server"
```

### 3. Filter by IP Range
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.ip.starts_with=10.&\
filter.type.equals=ip-netmask"
```

### 4. Query Security Rules
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.action.equals=allow&\
limit=10"
```

### 5. Find Services by Port
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.port.equals=443&\
filter.protocol.equals=tcp"
```

## Using the Web Interface

The API includes a web-based viewer at http://localhost:8000/viewer

Features:
- Visual configuration browser
- Real-time filtering
- Export to CSV/JSON
- Advanced search capabilities

## Common Filtering Patterns

### Basic Contains Filter (Default)
```bash
# Find addresses containing "web"
curl "http://localhost:8000/api/v1/configs/panorama/addresses?filter.name=web"
```

### Exact Match
```bash
# Find exact address by name
curl "http://localhost:8000/api/v1/configs/panorama/addresses?filter.name.equals=web-server-01"
```

### Numeric Comparison
```bash
# Find services on high ports
curl "http://localhost:8000/api/v1/configs/panorama/services?filter.port.gt=8000"
```

### Multiple Filters (AND Logic)
```bash
# Find production servers in DMZ
curl "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.tag.in=production&\
filter.parent_device_group.equals=DMZ"
```

## Working with Pagination

### Basic Pagination
```bash
# Get first 20 items
curl "http://localhost:8000/api/v1/configs/panorama/addresses?limit=20&offset=0"

# Get next 20 items
curl "http://localhost:8000/api/v1/configs/panorama/addresses?limit=20&offset=20"
```

### Pagination Response
```json
{
  "items": [...],
  "total_items": 1250,
  "page": 1,
  "page_size": 20,
  "total_pages": 63,
  "has_next": true,
  "has_previous": false
}
```

## Python Quick Start

```python
import requests
import json

class PanConfigClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
    
    def get_addresses(self, **filters):
        """Get address objects with optional filters"""
        params = {f"filter.{k}": v for k, v in filters.items()}
        response = requests.get(
            f"{self.api_base}/configs/panorama/addresses",
            params=params
        )
        return response.json()
    
    def get_security_rules(self, **filters):
        """Get security rules with optional filters"""
        params = {f"filter.{k}": v for k, v in filters.items()}
        response = requests.get(
            f"{self.api_base}/configs/panorama/rules/security",
            params=params
        )
        return response.json()
    
    def search_by_ip(self, ip_prefix):
        """Search for addresses by IP prefix"""
        return self.get_addresses(
            **{"ip.starts_with": ip_prefix, "type.equals": "ip-netmask"}
        )

# Usage
client = PanConfigClient()

# Find all web servers
web_servers = client.get_addresses(**{"name.contains": "web"})
print(f"Found {web_servers['total_items']} web servers")

# Find allow rules from trust zone
trust_rules = client.get_security_rules(
    **{"from.in": "trust", "action.equals": "allow"}
)
print(f"Found {trust_rules['total_items']} allow rules from trust zone")

# Search by IP
subnet_addresses = client.search_by_ip("10.0.0")
for addr in subnet_addresses["items"][:5]:
    print(f"- {addr['name']}: {addr['ip-netmask']}")
```

## JavaScript Quick Start

```javascript
class PanConfigAPI {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.apiBase = `${baseUrl}/api/v1`;
    }
    
    async getAddresses(filters = {}) {
        const params = new URLSearchParams();
        Object.entries(filters).forEach(([key, value]) => {
            params.append(`filter.${key}`, value);
        });
        
        const response = await fetch(
            `${this.apiBase}/configs/panorama/addresses?${params}`
        );
        return response.json();
    }
    
    async getSecurityRules(filters = {}) {
        const params = new URLSearchParams();
        Object.entries(filters).forEach(([key, value]) => {
            params.append(`filter.${key}`, value);
        });
        
        const response = await fetch(
            `${this.apiBase}/configs/panorama/rules/security?${params}`
        );
        return response.json();
    }
}

// Usage
const api = new PanConfigAPI();

// Find all FQDN addresses
api.getAddresses({ 'type.equals': 'fqdn' })
    .then(data => {
        console.log(`Found ${data.total_items} FQDN addresses`);
        data.items.slice(0, 5).forEach(addr => {
            console.log(`- ${addr.name}: ${addr.fqdn}`);
        });
    });

// Find high-risk rules
api.getSecurityRules({
    'source.in': 'any',
    'destination.in': 'any',
    'action.equals': 'allow'
}).then(data => {
    console.log(`Found ${data.total_items} high-risk rules`);
});
```

## cURL Examples

### With Pretty Output
```bash
# Using jq for JSON formatting
curl -s "http://localhost:8000/api/v1/configs/panorama/addresses?limit=5" | jq '.'

# Using python for formatting
curl -s "http://localhost:8000/api/v1/configs/panorama/addresses?limit=5" | python -m json.tool
```

### Save to File
```bash
# Save all addresses to file
curl -s "http://localhost:8000/api/v1/configs/panorama/addresses" > addresses.json

# Save filtered results
curl -s "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.tag.in=production" > production_addresses.json
```

### Using Variables
```bash
# Set base URL
BASE_URL="http://localhost:8000/api/v1/configs/panorama"

# Query with variables
curl -s "$BASE_URL/addresses?filter.type.equals=fqdn"
curl -s "$BASE_URL/services?filter.port.gt=8000"
curl -s "$BASE_URL/rules/security?filter.disabled.equals=true"
```

## Troubleshooting

### Server Not Starting
```bash
# Check if port is in use
lsof -i :8000

# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip list | grep -E "fastapi|uvicorn|pydantic"
```

### No Configuration Found
```bash
# Verify config path
echo $CONFIG_FILES_PATH

# Check file permissions
ls -la /path/to/configs/

# Verify XML format
xmllint --noout /path/to/configs/panorama.xml
```

### Slow Performance
```bash
# Increase workers
gunicorn main:app -w 8 -k uvicorn.workers.UvicornWorker

# Enable caching
export ENABLE_CACHE=true
export CACHE_TTL=3600
```

## Next Steps

1. **[Explore Filtering](../guides/filtering/index.md)** - Master the powerful filtering system
2. **[API Reference](../api/index.md)** - Detailed endpoint documentation
3. **[Examples](../examples/index.md)** - Real-world usage examples
4. **[Advanced Usage](../guides/advanced.md)** - Performance optimization and best practices

## Getting Help

- 📖 [Full Documentation](../index.md)
- 🐛 [Report Issues](https://github.com/yourusername/pan-config-viewer/issues)
- 💬 [Community Forum](https://forum.example.com)
- 📧 [Email Support](mailto:support@example.com)
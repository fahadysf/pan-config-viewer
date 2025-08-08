# PAN-Config-Viewer Filtering Guide

This guide explains the comprehensive filtering system available in the PAN-Config-Viewer API.

## Overview

The filtering system allows you to filter API results using flexible query parameters. All filters are applied with AND logic, meaning items must match ALL specified filters to be included in the results.

## Filter Format

### Basic Format
```
?filter[field]=value
```

### With Operators
```
?filter[field][operator]=value
```

### Multiple Filters
```
?filter[field1]=value1&filter[field2]=value2
```

## Supported Operators

- `eq` - Equals (exact match)
- `ne` - Not equals
- `contains` - Contains substring (default for string fields)
- `not_contains` - Does not contain substring
- `starts_with` - Starts with substring
- `ends_with` - Ends with substring
- `in` - Value is in list / list contains value
- `not_in` - Value is not in list / list does not contain value
- `gt` - Greater than
- `lt` - Less than
- `gte` - Greater than or equal to
- `lte` - Less than or equal to
- `regex` - Regular expression match

## Filtering by Endpoint

### Address Objects

**Endpoint:** `/api/v1/configs/{config_name}/addresses`

**Available Filters:**
- `name` - Filter by address name
- `ip` - Filter by IP address/netmask
- `ip_range` - Filter by IP range
- `fqdn` - Filter by FQDN
- `description` - Filter by description
- `tag` - Filter by tags
- `location` - Filter by location (shared/device-group/template/vsys)

**Examples:**
```bash
# Addresses with "web" in name
GET /api/v1/configs/sample/addresses?filter[name]=web

# Addresses in 10.0.0.0/8 network
GET /api/v1/configs/sample/addresses?filter[ip]=10.0

# Addresses with specific tag
GET /api/v1/configs/sample/addresses?filter[tag]=production

# Addresses starting with "db-"
GET /api/v1/configs/sample/addresses?filter[name][starts_with]=db-
```

### Service Objects

**Endpoint:** `/api/v1/configs/{config_name}/services`

**Available Filters:**
- `name` - Filter by service name
- `protocol` - Filter by protocol (tcp/udp)
- `port` - Filter by port number
- `description` - Filter by description
- `tag` - Filter by tags

**Examples:**
```bash
# TCP services only
GET /api/v1/configs/sample/services?filter[protocol]=tcp

# Services on port 443
GET /api/v1/configs/sample/services?filter[port]=443

# Services with "https" in name
GET /api/v1/configs/sample/services?filter[name]=https
```

### Security Rules

**Endpoint:** `/api/v1/configs/{config_name}/security-policies`

**Available Filters:**
- `name` - Filter by rule name
- `source` - Filter by source addresses
- `destination` - Filter by destination addresses
- `source_zone` - Filter by source zones
- `destination_zone` - Filter by destination zones
- `service` - Filter by services
- `application` - Filter by applications
- `action` - Filter by action (allow/deny/drop)
- `disabled` - Filter by disabled status (true/false)
- `description` - Filter by description
- `tag` - Filter by tags

**Examples:**
```bash
# Allow rules only
GET /api/v1/configs/sample/security-policies?filter[action]=allow

# Rules from untrust to trust
GET /api/v1/configs/sample/security-policies?filter[source_zone]=untrust&filter[destination_zone]=trust

# Disabled rules
GET /api/v1/configs/sample/security-policies?filter[disabled]=true

# Rules with specific destination
GET /api/v1/configs/sample/security-policies?filter[destination]=10.0.0.0/8
```

### Address/Service Groups

**Endpoints:** 
- `/api/v1/configs/{config_name}/address-groups`
- `/api/v1/configs/{config_name}/service-groups`

**Available Filters:**
- `name` - Filter by group name
- `description` - Filter by description
- `member` - Filter by member objects
- `tag` - Filter by tags

**Examples:**
```bash
# Address groups containing specific member
GET /api/v1/configs/sample/address-groups?filter[member]=web-server-01

# Service groups with "critical" in name
GET /api/v1/configs/sample/service-groups?filter[name]=critical
```

### Device Groups

**Endpoint:** `/api/v1/configs/{config_name}/device-groups`

**Available Filters:**
- `name` - Filter by device group name
- `parent` - Filter by parent device group
- `description` - Filter by description

**Examples:**
```bash
# Device groups under "Shared"
GET /api/v1/configs/sample/device-groups?filter[parent]=Shared

# Device groups with "branch" in name
GET /api/v1/configs/sample/device-groups?filter[name]=branch
```

## Combining Filters with Pagination

Filters work seamlessly with pagination parameters:

```bash
# Get page 2 of web servers (25 per page)
GET /api/v1/configs/sample/addresses?filter[name]=web&page=2&page_size=25

# Get all results without pagination
GET /api/v1/configs/sample/addresses?filter[name]=web&disable_paging=true
```

## Performance Considerations

1. **Filter First, Paginate Second**: The system applies filters before pagination, ensuring accurate page counts and consistent results.

2. **Indexed Fields**: Filtering is performed in-memory on the parsed XML data. For large datasets, consider using more specific filters to reduce the result set.

3. **Case Sensitivity**: String comparisons are case-insensitive by default for better usability.

4. **Regular Expressions**: The `regex` operator supports full Python regex syntax but may impact performance on large datasets.

## Backwards Compatibility

The new filtering system maintains backwards compatibility with existing query parameters:

- `name` parameter continues to work alongside `filter[name]`
- `tag` parameter continues to work alongside `filter[tag]`
- Legacy parameters take precedence if both are specified

## Examples with cURL

```bash
# Basic filtering
curl "http://localhost:8000/api/v1/configs/sample/addresses?filter[name]=web"

# Multiple filters
curl "http://localhost:8000/api/v1/configs/sample/addresses?filter[name]=server&filter[ip]=192.168"

# With operators
curl "http://localhost:8000/api/v1/configs/sample/addresses?filter[name][starts_with]=db-"

# URL encoding for special characters
curl "http://localhost:8000/api/v1/configs/sample/addresses?filter%5Bname%5D%5Bregex%5D=%5Edb-%5B0-9%5D%2B%24"
```

## Python Example

```python
import requests

# Basic filtering
response = requests.get(
    "http://localhost:8000/api/v1/configs/sample/addresses",
    params={"filter[name]": "web", "page_size": 25}
)

# Multiple filters
response = requests.get(
    "http://localhost:8000/api/v1/configs/sample/security-policies",
    params={
        "filter[source_zone]": "untrust",
        "filter[destination_zone]": "trust",
        "filter[action]": "allow",
        "page": 1,
        "page_size": 50
    }
)
```

## Frontend Integration

The filtering system is designed to work seamlessly with DataTables server-side processing:

```javascript
$('#addressTable').DataTable({
    serverSide: true,
    ajax: {
        url: '/api/v1/configs/sample/addresses',
        data: function(d) {
            // Add custom filters
            if ($('#nameFilter').val()) {
                d['filter[name]'] = $('#nameFilter').val();
            }
            if ($('#ipFilter').val()) {
                d['filter[ip]'] = $('#ipFilter').val();
            }
            // Map DataTables parameters
            d.page = Math.floor(d.start / d.length) + 1;
            d.page_size = d.length;
        }
    }
});
```
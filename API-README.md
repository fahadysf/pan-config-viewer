# PAN-OS Panorama Configuration API - Complete Guide

This guide provides comprehensive examples for using the PAN-OS Panorama Configuration API, including all endpoints with pagination and filtering options.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Pagination](#pagination)
3. [Filtering](#filtering)
4. [Configuration Management](#configuration-management)
5. [Address Objects](#address-objects)
6. [Service Objects](#service-objects)
7. [Security Profiles](#security-profiles)
8. [Device Management](#device-management)
9. [Policies](#policies)
10. [Logging](#logging)
11. [System](#system)
12. [Advanced Examples](#advanced-examples)

## Getting Started

### Base URL
```
http://localhost:8000
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Response Format
All responses are in JSON format. Paginated endpoints return a standardized response structure.

## Pagination

All list endpoints support pagination to handle large datasets efficiently.

### Pagination Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number (1-based) |
| `page_size` | int | 500 | Items per page (1-10000) |
| `disable_paging` | bool | false | Return all items without pagination |

### Paginated Response Structure

```json
{
    "items": [...],           // Array of items for current page
    "total_items": 1500,      // Total number of items
    "page": 1,                // Current page number
    "page_size": 500,         // Items per page
    "total_pages": 3,         // Total number of pages
    "has_next": true,         // Whether there is a next page
    "has_previous": false     // Whether there is a previous page
}
```

### Pagination Examples

```bash
# Get first page with default page size (500 items)
curl http://localhost:8000/api/v1/configs/production/addresses

# Get second page with 100 items per page
curl "http://localhost:8000/api/v1/configs/production/addresses?page=2&page_size=100"

# Get all items without pagination (use with caution for large datasets)
curl "http://localhost:8000/api/v1/configs/production/addresses?disable_paging=true"

# Combine pagination with filtering
curl "http://localhost:8000/api/v1/configs/production/addresses?name=server&page=1&page_size=50"
```

## Filtering

### Basic Filtering
Most endpoints support basic filtering using query parameters:
- `name` - Filter by name (partial match)
- `tag` - Filter by tag
- `protocol` - Filter by protocol (for services)
- `location` - Filter by location (for addresses)

### Advanced Filtering
Use the `filter[field]` syntax for advanced filtering:

```bash
# Filter addresses by IP
curl "http://localhost:8000/api/v1/configs/production/addresses?filter[ip]=10.0.0"

# Filter with operators
curl "http://localhost:8000/api/v1/configs/production/addresses?filter[name][starts_with]=web"

# Multiple filters
curl "http://localhost:8000/api/v1/configs/production/addresses?filter[tag]=production&filter[ip]=10.0"
```

## Configuration Management

### List Available Configurations

```bash
# Get all available configuration files
curl http://localhost:8000/api/v1/configs

# Response
{
    "configs": ["production", "staging", "development"],
    "count": 3,
    "path": "./config-files"
}
```

### Get Configuration Info

```bash
# Get details about a specific configuration
curl http://localhost:8000/api/v1/configs/production/info

# Response
{
    "name": "production",
    "path": "./config-files/production.xml",
    "size": 15728640,
    "modified": 1708123456.789,
    "loaded": true
}
```

## Address Objects

### Get All Addresses (with pagination)

```bash
# Get first page of addresses
curl http://localhost:8000/api/v1/configs/production/addresses

# Get page 2 with 100 items per page
curl "http://localhost:8000/api/v1/configs/production/addresses?page=2&page_size=100"

# Get all addresses without pagination
curl "http://localhost:8000/api/v1/configs/production/addresses?disable_paging=true"

# Filter by name
curl "http://localhost:8000/api/v1/configs/production/addresses?name=web-server"

# Filter by location
curl "http://localhost:8000/api/v1/configs/production/addresses?location=shared"

# Advanced filtering by IP
curl "http://localhost:8000/api/v1/configs/production/addresses?filter[ip]=192.168"

# Multiple filters
curl "http://localhost:8000/api/v1/configs/production/addresses?filter[tag]=production&filter[location]=shared&page=1&page_size=50"
```

### Get Specific Address

```bash
# Get a specific address by exact name
curl http://localhost:8000/api/v1/configs/production/addresses/web-server-01

# Response
{
    "name": "web-server-01",
    "ip_netmask": "192.168.1.100/32",
    "description": "Production web server",
    "tag": ["production", "web"],
    "xpath": "/config/shared/address/entry[@name='web-server-01']",
    "parent_device_group": null,
    "parent_template": null,
    "parent_vsys": null
}
```

### Get Address Groups

```bash
# Get all address groups with pagination
curl http://localhost:8000/api/v1/configs/production/address-groups

# Get specific page
curl "http://localhost:8000/api/v1/configs/production/address-groups?page=2&page_size=50"

# Filter by name
curl "http://localhost:8000/api/v1/configs/production/address-groups?name=web-servers"

# Filter by member
curl "http://localhost:8000/api/v1/configs/production/address-groups?filter[member]=web-server"

# Get specific address group
curl http://localhost:8000/api/v1/configs/production/address-groups/web-servers-group
```

### Get Shared Addresses

```bash
# Get addresses from shared location only
curl http://localhost:8000/api/v1/configs/production/shared/addresses

# With pagination
curl "http://localhost:8000/api/v1/configs/production/shared/addresses?page=2&page_size=100"

# With filtering
curl "http://localhost:8000/api/v1/configs/production/shared/addresses?name=dmz"
```

## Service Objects

### Get All Services

```bash
# Get all services with default pagination
curl http://localhost:8000/api/v1/configs/production/services

# Get page 3 with 200 items per page
curl "http://localhost:8000/api/v1/configs/production/services?page=3&page_size=200"

# Filter by protocol
curl "http://localhost:8000/api/v1/configs/production/services?protocol=tcp"

# Filter by port
curl "http://localhost:8000/api/v1/configs/production/services?filter[port]=443"

# Combined filters
curl "http://localhost:8000/api/v1/configs/production/services?protocol=tcp&filter[port]=80&page=1"
```

### Get Specific Service

```bash
# Get a specific service by name
curl http://localhost:8000/api/v1/configs/production/services/tcp-443

# Response
{
    "name": "tcp-443",
    "protocol": {
        "tcp": {
            "port": "443",
            "source_port": null
        }
    },
    "description": "HTTPS service",
    "tag": ["web", "secure"],
    "xpath": "/config/shared/service/entry[@name='tcp-443']",
    "parent_device_group": null,
    "parent_template": null,
    "parent_vsys": null
}
```

### Get Service Groups

```bash
# Get all service groups
curl http://localhost:8000/api/v1/configs/production/service-groups

# With pagination
curl "http://localhost:8000/api/v1/configs/production/service-groups?page=2&page_size=25"

# Filter by name
curl "http://localhost:8000/api/v1/configs/production/service-groups?name=web"

# Get specific service group
curl http://localhost:8000/api/v1/configs/production/service-groups/web-services
```

## Security Profiles

### Get Vulnerability Profiles

```bash
# Get all vulnerability profiles
curl http://localhost:8000/api/v1/configs/production/security-profiles/vulnerability

# With pagination
curl "http://localhost:8000/api/v1/configs/production/security-profiles/vulnerability?page=1&page_size=20"

# Filter by name
curl "http://localhost:8000/api/v1/configs/production/security-profiles/vulnerability?name=strict"
```

### Get URL Filtering Profiles

```bash
# Get all URL filtering profiles
curl http://localhost:8000/api/v1/configs/production/security-profiles/url-filtering

# With custom page size
curl "http://localhost:8000/api/v1/configs/production/security-profiles/url-filtering?page_size=10"

# Filter by name
curl "http://localhost:8000/api/v1/configs/production/security-profiles/url-filtering?name=default"
```

## Device Management

### Get Device Groups

```bash
# Get all device groups with summary counts
curl http://localhost:8000/api/v1/configs/production/device-groups

# With pagination
curl "http://localhost:8000/api/v1/configs/production/device-groups?page=2&page_size=50"

# Filter by name
curl "http://localhost:8000/api/v1/configs/production/device-groups?name=branch"

# Filter by parent
curl "http://localhost:8000/api/v1/configs/production/device-groups?parent=headquarters"

# Advanced filtering
curl "http://localhost:8000/api/v1/configs/production/device-groups?filter[parent]=hq&filter[description]=branch"
```

### Get Device Group Details

```bash
# Get specific device group
curl http://localhost:8000/api/v1/configs/production/device-groups/branch-offices

# Response includes counts
{
    "name": "branch-offices",
    "description": "Branch office locations",
    "parent_dg": "headquarters",
    "devices_count": 25,
    "address_count": 150,
    "address_group_count": 20,
    "service_count": 75,
    "service_group_count": 10,
    "pre_security_rules_count": 100,
    "post_security_rules_count": 50,
    "pre_nat_rules_count": 25,
    "post_nat_rules_count": 10,
    "xpath": "/config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='branch-offices']"
}
```

### Get Device Group Objects

```bash
# Get addresses for a device group
curl http://localhost:8000/api/v1/configs/production/device-groups/branch-offices/addresses

# With pagination
curl "http://localhost:8000/api/v1/configs/production/device-groups/branch-offices/addresses?page=2&page_size=100"

# Get address groups
curl http://localhost:8000/api/v1/configs/production/device-groups/branch-offices/address-groups

# Get services
curl http://localhost:8000/api/v1/configs/production/device-groups/branch-offices/services

# Get service groups
curl http://localhost:8000/api/v1/configs/production/device-groups/branch-offices/service-groups

# All support pagination and filtering
curl "http://localhost:8000/api/v1/configs/production/device-groups/branch-offices/services?protocol=tcp&page=1&page_size=50"
```

### Get Templates

```bash
# Get all templates
curl http://localhost:8000/api/v1/configs/production/templates

# With pagination
curl "http://localhost:8000/api/v1/configs/production/templates?page=1&page_size=20"

# Filter by name
curl "http://localhost:8000/api/v1/configs/production/templates?name=branch"

# Get specific template
curl http://localhost:8000/api/v1/configs/production/templates/branch-template
```

### Get Template Stacks

```bash
# Get all template stacks
curl http://localhost:8000/api/v1/configs/production/template-stacks

# With pagination
curl "http://localhost:8000/api/v1/configs/production/template-stacks?page=1&page_size=10"

# Filter by name
curl "http://localhost:8000/api/v1/configs/production/template-stacks?name=branch"

# Filter by template member
curl "http://localhost:8000/api/v1/configs/production/template-stacks?filter[template]=base-template"

# Get specific template stack
curl http://localhost:8000/api/v1/configs/production/template-stacks/branch-stack
```

## Policies

### Get Security Rules for Device Group

```bash
# Get all rules for a device group
curl http://localhost:8000/api/v1/configs/production/device-groups/branch-offices/rules

# Get only pre-rules
curl "http://localhost:8000/api/v1/configs/production/device-groups/branch-offices/rules?rulebase=pre"

# Get only post-rules
curl "http://localhost:8000/api/v1/configs/production/device-groups/branch-offices/rules?rulebase=post"

# With pagination
curl "http://localhost:8000/api/v1/configs/production/device-groups/branch-offices/rules?page=2&page_size=100"

# With filtering
curl "http://localhost:8000/api/v1/configs/production/device-groups/branch-offices/rules?filter[action]=allow&filter[disabled]=false"
```

### Get All Security Policies

```bash
# Get all security policies from all device groups
curl http://localhost:8000/api/v1/configs/production/security-policies

# With pagination (important for large rulesets)
curl "http://localhost:8000/api/v1/configs/production/security-policies?page=1&page_size=200"

# Filter by rule name
curl "http://localhost:8000/api/v1/configs/production/security-policies?name=allow-web"

# Filter by device group
curl "http://localhost:8000/api/v1/configs/production/security-policies?device_group=branch-offices"

# Filter by action
curl "http://localhost:8000/api/v1/configs/production/security-policies?action=deny"

# Advanced filtering
curl "http://localhost:8000/api/v1/configs/production/security-policies?filter[source]=10.0.0.0&filter[destination]=any&filter[service]=tcp-443"

# Multiple filters with pagination
curl "http://localhost:8000/api/v1/configs/production/security-policies?filter[source_zone]=trust&filter[destination_zone]=untrust&filter[action]=allow&page=1&page_size=50"
```

## Logging

### Get Log Profiles

```bash
# Get all log forwarding profiles
curl http://localhost:8000/api/v1/configs/production/log-profiles

# With pagination
curl "http://localhost:8000/api/v1/configs/production/log-profiles?page=1&page_size=25"

# Filter by name
curl "http://localhost:8000/api/v1/configs/production/log-profiles?name=default"
```

### Get Schedules

```bash
# Get all schedules
curl http://localhost:8000/api/v1/configs/production/schedules

# With pagination
curl "http://localhost:8000/api/v1/configs/production/schedules?page=1&page_size=50"

# Filter by name
curl "http://localhost:8000/api/v1/configs/production/schedules?name=business-hours"
```

## System

### Health Check

```bash
# Check API health
curl http://localhost:8000/api/v1/health

# Response
{
    "status": "healthy",
    "config_path": "./config-files",
    "configs_available": 3,
    "configs_loaded": 1,
    "available_configs": ["production", "staging", "development"]
}
```

## Advanced Examples

### Iterating Through Paginated Results

```bash
#!/bin/bash
# Script to fetch all addresses page by page

CONFIG="production"
PAGE=1
PAGE_SIZE=100
HAS_NEXT=true

while [ "$HAS_NEXT" = "true" ]; do
    RESPONSE=$(curl -s "http://localhost:8000/api/v1/configs/$CONFIG/addresses?page=$PAGE&page_size=$PAGE_SIZE")
    
    # Process items
    echo "$RESPONSE" | jq '.items[]'
    
    # Check if there's a next page
    HAS_NEXT=$(echo "$RESPONSE" | jq -r '.has_next')
    PAGE=$((PAGE + 1))
done
```

### Complex Filtering with Pagination

```bash
# Find all allow rules from trust to untrust zone with web services
curl "http://localhost:8000/api/v1/configs/production/security-policies?\
filter[source_zone]=trust&\
filter[destination_zone]=untrust&\
filter[action]=allow&\
filter[service]=tcp-80&\
page=1&\
page_size=50"

# Find all addresses in a specific IP range
curl "http://localhost:8000/api/v1/configs/production/addresses?\
filter[ip]=10.0.0&\
filter[location]=device-group&\
page=1&\
page_size=100"
```

### Exporting All Objects

```bash
# Export all addresses without pagination (use cautiously)
curl "http://localhost:8000/api/v1/configs/production/addresses?disable_paging=true" \
    -o all-addresses.json

# Export addresses page by page
for PAGE in {1..10}; do
    curl "http://localhost:8000/api/v1/configs/production/addresses?page=$PAGE&page_size=500" \
        -o "addresses-page-$PAGE.json"
done
```

### Performance Considerations

1. **Default Page Size**: The default page size is 500 items, which provides a good balance between response size and number of requests.

2. **Maximum Page Size**: The maximum allowed page size is 10,000 items. Use this only when necessary.

3. **Disable Paging**: Use `disable_paging=true` only for small datasets or when you need all data at once. For large datasets, this may cause performance issues.

4. **Optimal Usage**: For large datasets, iterate through pages programmatically rather than disabling pagination.

### Error Handling

```bash
# Invalid page number
curl "http://localhost:8000/api/v1/configs/production/addresses?page=1000"
# Returns empty items array if page exceeds total_pages

# Invalid page size
curl "http://localhost:8000/api/v1/configs/production/addresses?page_size=20000"
# Returns 422 Unprocessable Entity - page_size must be <= 10000

# Non-existent configuration
curl http://localhost:8000/api/v1/configs/nonexistent/addresses
# Returns 404 Not Found
```

## Best Practices

1. **Always use pagination** for production systems to avoid memory issues with large datasets.

2. **Choose appropriate page sizes** based on your use case:
   - Small page sizes (10-100) for interactive UIs
   - Medium page sizes (100-500) for batch processing
   - Large page sizes (500-10000) for data export/migration

3. **Cache results** when possible, especially for data that doesn't change frequently.

4. **Use filtering** to reduce the dataset size before pagination.

5. **Handle pagination metadata** properly in your client applications to provide good user experience.

6. **Monitor performance** when using `disable_paging=true` or very large page sizes.

## Support

For issues or questions:
- Check the Swagger documentation at http://localhost:8000/docs
- Review error messages in API responses
- Check application logs for detailed error information
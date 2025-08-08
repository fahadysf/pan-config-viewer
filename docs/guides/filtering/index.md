# Filtering Guide

The PAN Config Viewer API provides a powerful and flexible filtering system that allows you to query configuration objects with precision. This guide covers everything you need to know about filtering.

## Overview

The filtering system supports:

- **15+ operators** for different comparison types
- **Dot notation syntax** for clean, readable queries
- **Type-aware filtering** for different data types
- **Multi-field filtering** with AND logic
- **Consistent behavior** across all endpoints

## Quick Start

### Basic Filter
```http
GET /api/v1/configs/{config}/addresses?filter.name=server
```
This uses the default `contains` operator to find addresses with "server" in the name.

### Explicit Operator
```http
GET /api/v1/configs/{config}/addresses?filter.name.equals=web-server-01
```
This finds an address with the exact name "web-server-01".

### Multiple Filters
```http
GET /api/v1/configs/{config}/addresses?filter.type.equals=fqdn&filter.tag.in=production
```
Multiple filters are combined with AND logic.

## Filter Syntax

The API uses a dot notation syntax for filters:

```
filter.<field>.<operator>=<value>
```

- **`filter`** - Required prefix for all filter parameters
- **`<field>`** - The field to filter on (e.g., `name`, `ip`, `port`)
- **`<operator>`** - The comparison operator (optional, defaults to `contains`)
- **`<value>`** - The value to compare against

### Examples

| Syntax | Description |
|--------|-------------|
| `filter.name=web` | Name contains "web" (default operator) |
| `filter.name.equals=web-01` | Name exactly equals "web-01" |
| `filter.ip.starts_with=10.` | IP starts with "10." |
| `filter.port.gt=8000` | Port greater than 8000 |
| `filter.tag.in=production` | Has "production" tag |

## Supported Operators

### Text Operators

| Operator | Aliases | Description | Example |
|----------|---------|-------------|---------|
| `contains` | - | Substring match (default) | `filter.name.contains=server` |
| `eq` | `equals` | Exact match | `filter.name.eq=web-01` |
| `ne` | `not_equals` | Not equal | `filter.protocol.ne=udp` |
| `starts_with` | - | Starts with prefix | `filter.ip.starts_with=192.168.` |
| `ends_with` | - | Ends with suffix | `filter.fqdn.ends_with=.com` |
| `not_contains` | - | Doesn't contain | `filter.description.not_contains=test` |
| `regex` | - | Regular expression | `filter.name.regex=^srv-\d+$` |

### Numeric Operators

| Operator | Aliases | Description | Example |
|----------|---------|-------------|---------|
| `gt` | `greater_than` | Greater than | `filter.port.gt=1024` |
| `lt` | `less_than` | Less than | `filter.count.lt=100` |
| `gte` | `greater_than_or_equal` | Greater or equal | `filter.port.gte=8080` |
| `lte` | `less_than_or_equal` | Less or equal | `filter.port.lte=9000` |

### List Operators

| Operator | Aliases | Description | Example |
|----------|---------|-------------|---------|
| `in` | - | Value in list | `filter.tag.in=production,staging` |
| `not_in` | - | Value not in list | `filter.zone.not_in=untrust` |

### Boolean Operators

| Operator | Aliases | Description | Example |
|----------|---------|-------------|---------|
| `eq` | `equals` | Boolean equals | `filter.disabled.eq=true` |
| `ne` | `not_equals` | Boolean not equals | `filter.log_end.ne=false` |

## Field-Specific Filtering

Different object types support different fields for filtering. Here's what you can filter on for each major object type:

### Address Objects

| Field | Type | Operators | Description |
|-------|------|-----------|-------------|
| `name` | string | All text operators | Object name |
| `ip` | string | All text operators | IP address (alias for ip_netmask) |
| `ip_netmask` | string | Text operators | IP with netmask |
| `ip_range` | string | Text operators | IP range |
| `fqdn` | string | Text operators | Fully qualified domain name |
| `type` | enum | `eq`, `ne` | Address type (fqdn/ip-netmask/ip-range) |
| `tag` | array | `in`, `not_in`, `contains` | Associated tags |
| `description` | string | All text operators | Description text |
| `parent_device_group` | string | Text operators | Device group location |

### Service Objects

| Field | Type | Operators | Description |
|-------|------|-----------|-------------|
| `name` | string | All text operators | Service name |
| `protocol` | enum | `eq`, `ne` | Protocol (tcp/udp) |
| `port` | string/int | All operators | Port number or range |
| `source_port` | string | Text operators | Source port |
| `tag` | array | `in`, `not_in`, `contains` | Associated tags |
| `description` | string | All text operators | Description text |

### Security Rules

| Field | Type | Operators | Description |
|-------|------|-----------|-------------|
| `name` | string | All text operators | Rule name |
| `uuid` | string | `eq`, `ne` | Rule UUID |
| `source` | array | List operators | Source addresses |
| `destination` | array | List operators | Destination addresses |
| `source_zone` | array | List operators | Source zones |
| `destination_zone` | array | List operators | Destination zones |
| `application` | array | List operators | Applications |
| `service` | array | List operators | Services |
| `action` | enum | `eq`, `ne` | Action (allow/deny/drop) |
| `disabled` | bool | `eq`, `ne` | Rule state |
| `log_start` | bool | `eq`, `ne` | Log at session start |
| `log_end` | bool | `eq`, `ne` | Log at session end |

### Device Groups

| Field | Type | Operators | Description |
|-------|------|-----------|-------------|
| `name` | string | All text operators | Device group name |
| `parent` | string | Text operators | Parent device group |
| `description` | string | All text operators | Description |
| `devices_count` | int | Numeric operators | Number of devices |
| `address_count` | int | Numeric operators | Number of addresses |
| `service_count` | int | Numeric operators | Number of services |

## Advanced Filtering Examples

### Complex Security Rule Query
Find high-risk allow rules (any-any with no logging):
```http
GET /api/v1/configs/panorama/rules/security?
  filter.source.in=any&
  filter.destination.in=any&
  filter.service.in=any&
  filter.action.equals=allow&
  filter.log_end.equals=false
```

### Address Range Query
Find all addresses in specific subnets:
```http
GET /api/v1/configs/panorama/addresses?
  filter.ip.starts_with=10.&
  filter.ip.not_contains=10.99&
  filter.type.equals=ip-netmask
```

### Service Port Range Query
Find all high-port TCP services:
```http
GET /api/v1/configs/panorama/services?
  filter.protocol.equals=tcp&
  filter.port.gte=8000&
  filter.port.lte=9000
```

### Tagged Object Query
Find production servers in DMZ:
```http
GET /api/v1/configs/panorama/addresses?
  filter.tag.in=production&
  filter.description.contains=DMZ&
  filter.type.equals=ip-netmask
```

### NAT Rule Analysis
Find NAT rules with source translation:
```http
GET /api/v1/configs/panorama/rules/nat?
  filter.source.starts_with=192.168.&
  filter.source_translation.exists=true&
  filter.disabled.equals=false
```

## Device-Group Specific Filtering

All filtering features work identically for device-group specific endpoints:

```http
# Shared objects
GET /api/v1/configs/panorama/addresses?filter.name.contains=server

# Device-group specific objects
GET /api/v1/configs/panorama/device-groups/DMZ-DG/addresses?filter.name.contains=server

# Template specific objects
GET /api/v1/configs/panorama/templates/Branch-Template/addresses?filter.name.contains=server
```

## Performance Considerations

### Best Practices

1. **Use specific filters first** - More selective filters reduce the dataset early
2. **Combine with pagination** - Use `limit` and `offset` with filters
3. **Use indexed fields** - `name`, `uuid`, and `type` are typically faster
4. **Avoid complex regex** - Simple string operations are more efficient

### Query Optimization

```http
# Good: Specific filters first
filter.type.equals=fqdn&filter.name.contains=mail

# Less optimal: Generic filter first
filter.name.contains=mail&filter.type.equals=fqdn
```

## Filter Validation

### Invalid Filters
Invalid filter parameters are silently ignored. The API will:
- Return empty result set if no objects match
- Return HTTP 400 for invalid operator syntax
- Return HTTP 404 for non-existent endpoints

### Type Coercion
The API automatically handles type conversion:
- Numeric strings are converted for numeric operators
- Boolean strings ("true"/"false") are converted for boolean operators
- Lists can be comma-separated strings or JSON arrays

## Common Patterns

### Finding Unused Objects
```http
# Find address objects not used in any rules
GET /api/v1/configs/panorama/addresses?filter.used_in.equals=0
```

### Compliance Checks
```http
# Find non-compliant rules (example: no logging)
GET /api/v1/configs/panorama/rules/security?
  filter.log_end.equals=false&
  filter.action.equals=allow
```

### Change Impact Analysis
```http
# Find all rules affected by an address change
GET /api/v1/configs/panorama/rules/security?
  filter.source.contains=old-server-01
```

## Troubleshooting

### No Results Returned
- Check field names are correct (use hyphenated or underscore)
- Verify operator is valid for the field type
- Ensure value format matches expected type

### Too Many Results
- Add more specific filters
- Use pagination to handle large result sets
- Consider using exact match instead of contains

### Performance Issues
- Reduce the number of complex regex filters
- Use more selective filters first
- Enable caching if available

## Next Steps

- [Explore all operators in detail](operators.md)
- [Learn about filter syntax](syntax.md)
- [See advanced filtering techniques](advanced.md)
- [Understand performance optimization](performance.md)
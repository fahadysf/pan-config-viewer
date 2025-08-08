# API Filtering Guide

This guide provides comprehensive documentation for all filtering options available in the PAN-OS Panorama Configuration API.

## Table of Contents
- [Overview](#overview)
- [Filter Syntax](#filter-syntax)
- [Available Operators](#available-operators)
- [Endpoint-Specific Filters](#endpoint-specific-filters)
- [Examples](#examples)

## Overview

The API supports two filtering approaches:
1. **Basic Filters**: Simple query parameters for common filtering needs
2. **Advanced Filters**: Powerful `filter.property.operator=value` syntax for precise filtering

All filters use AND logic - objects must match ALL specified filter conditions.

**Important**: Filtering is available on ALL endpoints that return lists of objects, including:
- Shared objects endpoints (e.g., `/addresses`, `/services`)
- Device-group specific endpoints (e.g., `/device-groups/{name}/addresses`)
- Template specific endpoints (e.g., `/templates/{name}/addresses`)
- All other collection endpoints

The same filtering syntax and operators work consistently across all endpoints.

## Filter Syntax

### Basic Query Parameters
```
GET /api/v1/configs/{config}/addresses?name=server&tag=production
```

### Advanced Filter Syntax
```
GET /api/v1/configs/{config}/addresses?filter.ip.starts_with=10.&filter.tag.in=production
```

If no operator is specified, `contains` is used by default:
```
GET /api/v1/configs/{config}/addresses?filter.name=server
```

## Available Operators

| Operator | Description | Example | Use Case |
|----------|-------------|---------|----------|
| `eq` / `equals` | Exact match | `filter.name.eq=web-server-01` | Find specific object |
| `ne` / `not_equals` | Not equal | `filter.protocol.ne=udp` | Exclude specific value |
| `contains` | Contains substring (default) | `filter.name=server` or `filter.name.contains=server` | Partial text search |
| `not_contains` | Doesn't contain | `filter.description.not_contains=deprecated` | Exclude by text |
| `starts_with` | Starts with prefix | `filter.ip.starts_with=192.168.` | IP prefix matching |
| `ends_with` | Ends with suffix | `filter.fqdn.ends_with=.example.com` | Domain matching |
| `in` | Value in list | `filter.tag.in=production` | Check membership |
| `not_in` | Value not in list | `filter.tag.not_in=test` | Exclude members |
| `gt` | Greater than | `filter.port.gt=8000` | Numeric comparison |
| `lt` | Less than | `filter.devices_count.lt=5` | Numeric comparison |
| `gte` | Greater or equal | `filter.port.gte=8080` | Numeric comparison |
| `lte` | Less or equal | `filter.port.lte=9000` | Numeric comparison |
| `regex` | Regex match | `filter.name.regex=^fw-.*-\\d+$` | Pattern matching |
| `exists` | Field exists | `filter.description.exists=true` | Check field presence |

## Endpoint-Specific Filters

### Address Objects (`/addresses`)

| Filter | Type | Description | Example |
|--------|------|-------------|---------|
| `name` | string | Address name | `filter.name.contains=dmz` |
| `ip` | string | IP address (alias for ip_netmask) | `filter.ip.starts_with=10.` |
| `ip_netmask` | string | IP with netmask | `filter.ip_netmask.equals=10.0.0.0/8` |
| `ip_range` | string | IP range | `filter.ip_range.contains=10.0.0` |
| `fqdn` | string | Fully qualified domain name | `filter.fqdn.ends_with=.com` |
| `type` | enum | Address type (fqdn/ip-netmask/ip-range) | `filter.type.equals=fqdn` |
| `tag` | array | Tags | `filter.tag.in=production` |
| `description` | string | Description text | `filter.description.contains=server` |
| `parent_device_group` | string | Device group location | `filter.parent_device_group.equals=branch` |
| `parent_template` | string | Template location | `filter.parent_template.equals=base` |
| `parent_vsys` | string | Virtual system | `filter.parent_vsys.equals=vsys1` |

### Service Objects (`/services`)

| Filter | Type | Description | Example |
|--------|------|-------------|---------|
| `name` | string | Service name | `filter.name.starts_with=http` |
| `protocol` | enum | Protocol (tcp/udp) | `filter.protocol.equals=tcp` |
| `port` | string/int | Port number or range | `filter.port.gt=8000` |
| `tag` | array | Tags | `filter.tag.in=web` |
| `description` | string | Description | `filter.description.contains=web` |
| `parent_device_group` | string | Device group | `filter.parent_device_group.equals=hq` |

### Address Groups (`/address-groups`)

| Filter | Type | Description | Example |
|--------|------|-------------|---------|
| `name` | string | Group name | `filter.name.contains=servers` |
| `member` | array | Group members | `filter.member.in=web-server-01` |
| `tag` | array | Tags | `filter.tag.in=production` |
| `description` | string | Description | `filter.description.contains=DMZ` |
| `parent_device_group` | string | Device group | `filter.parent_device_group.equals=branch` |

### Service Groups (`/service-groups`)

| Filter | Type | Description | Example |
|--------|------|-------------|---------|
| `name` | string | Group name | `filter.name.contains=web` |
| `member` | array | Group members | `filter.member.in=tcp-443` |
| `tag` | array | Tags | `filter.tag.in=critical` |
| `description` | string | Description | `filter.description.contains=services` |

### Device Groups (`/device-groups`)

| Filter | Type | Description | Example |
|--------|------|-------------|---------|
| `name` | string | Device group name | `filter.name.equals=headquarters` |
| `parent` | string | Parent device group | `filter.parent.equals=shared` |
| `parent_dg` | string | Parent (alias) | `filter.parent_dg.equals=shared` |
| `description` | string | Description | `filter.description.contains=branch` |
| `devices_count` | int | Number of devices | `filter.devices_count.gt=10` |
| `address_count` | int | Number of addresses | `filter.address_count.gte=100` |
| `service_count` | int | Number of services | `filter.service_count.lt=50` |
| `pre_security_rules_count` | int | Pre-rules count | `filter.pre_security_rules_count.gt=20` |
| `post_security_rules_count` | int | Post-rules count | `filter.post_security_rules_count.lte=10` |

### Security Rules (`/rules/security`)

| Filter | Type | Description | Example |
|--------|------|-------------|---------|
| `name` | string | Rule name | `filter.name.contains=allow` |
| `uuid` | string | Rule UUID | `filter.uuid.equals=123e4567-e89b` |
| `source` | array | Source addresses | `filter.source.in=10.0.0.0/8` |
| `destination` | array | Destination addresses | `filter.destination.in=any` |
| `source_zone` / `from` | array | Source zones | `filter.source_zone.in=trust` |
| `dest_zone` / `to` | array | Destination zones | `filter.dest_zone.in=untrust` |
| `application` | array | Applications | `filter.application.in=ssl` |
| `service` | array | Services | `filter.service.in=application-default` |
| `action` | enum | Action (allow/deny/drop) | `filter.action.equals=allow` |
| `disabled` | bool | Rule state | `filter.disabled.equals=false` |
| `source_user` | array | Source users | `filter.source_user.in=any` |
| `category` | array | URL categories | `filter.category.in=social-networking` |
| `tag` | array | Tags | `filter.tag.in=critical` |
| `device_group` | string | Device group | `filter.device_group.equals=branch` |
| `rule_type` | enum | Rule type (pre/post) | `filter.rule_type.equals=pre` |
| `log_start` | bool | Log at start | `filter.log_start.equals=true` |
| `log_end` | bool | Log at end | `filter.log_end.equals=true` |
| `log_setting` | string | Log profile | `filter.log_setting.equals=default` |

### NAT Rules (`/rules/nat`)

| Filter | Type | Description | Example |
|--------|------|-------------|---------|
| `name` | string | Rule name | `filter.name.contains=outbound` |
| `uuid` | string | Rule UUID | `filter.uuid.equals=123e4567` |
| `source` | array | Source addresses | `filter.source.in=internal` |
| `destination` | array | Destination addresses | `filter.destination.in=external` |
| `from` | array | Source zones | `filter.from.in=trust` |
| `to` | array | Destination zones | `filter.to.in=untrust` |
| `service` | string | Service | `filter.service.equals=any` |
| `source_translation_exists` | bool | Has source NAT | `filter.source_translation.exists=true` |
| `destination_translation_exists` | bool | Has destination NAT | `filter.destination_translation.exists=true` |
| `disabled` | bool | Rule state | `filter.disabled.equals=false` |
| `tag` | array | Tags | `filter.tag.in=nat` |
| `device_group` | string | Device group | `filter.device_group.equals=branch` |
| `rule_type` | enum | Rule type (pre/post) | `filter.rule_type.equals=pre` |

## Examples

### Address Object Filtering

```bash
# Find all addresses in 10.0.0.0/8 network
GET /api/v1/configs/panorama/addresses?filter.ip.starts_with=10.

# Find all FQDN addresses for example.com domain
GET /api/v1/configs/panorama/addresses?filter.type.equals=fqdn&filter.fqdn.ends_with=.example.com

# Find addresses with production tag in specific device group
GET /api/v1/configs/panorama/addresses?filter.tag.in=production&filter.parent_device_group.equals=headquarters

# Find addresses matching a regex pattern
GET /api/v1/configs/panorama/addresses?filter.name.regex=^(web|app)-server-\\d{2}$
```

### Service Filtering

```bash
# Find all TCP services on ports 8000-9000
GET /api/v1/configs/panorama/services?filter.protocol.equals=tcp&filter.port.gte=8000&filter.port.lte=9000

# Find services with names starting with "custom-"
GET /api/v1/configs/panorama/services?filter.name.starts_with=custom-

# Find high-port TCP services (>1024)
GET /api/v1/configs/panorama/services?filter.protocol.equals=tcp&filter.port.gt=1024
```

### Security Rule Filtering

```bash
# Find all allow rules from DMZ to any
GET /api/v1/configs/panorama/rules/security?filter.source_zone.in=DMZ&filter.destination.in=any&filter.action.equals=allow

# Find disabled rules with logging enabled
GET /api/v1/configs/panorama/rules/security?filter.disabled.equals=true&filter.log_end.equals=true

# Find rules for specific application
GET /api/v1/configs/panorama/rules/security?filter.application.in=ssl&filter.application.in=ssh

# Find rules with specific source and no logging
GET /api/v1/configs/panorama/rules/security?filter.source.in=10.0.0.0/8&filter.log_start.equals=false&filter.log_end.equals=false
```

### Device Group Filtering

```bash
# Find device groups with many devices
GET /api/v1/configs/panorama/device-groups?filter.devices_count.gt=10

# Find child device groups
GET /api/v1/configs/panorama/device-groups?filter.parent.not_equals=shared

# Find device groups with many security rules
GET /api/v1/configs/panorama/device-groups?filter.pre_security_rules_count.gt=50&filter.post_security_rules_count.gt=50
```

### Complex Multi-Filter Examples

```bash
# Find production web servers in DMZ
GET /api/v1/configs/panorama/addresses?filter.name.contains=web&filter.tag.in=production&filter.description.contains=DMZ

# Find high-risk allow rules (any-any with no logging)
GET /api/v1/configs/panorama/rules/security?filter.source.in=any&filter.destination.in=any&filter.service.in=any&filter.action.equals=allow&filter.log_end.equals=false

# Find NAT rules for specific subnet with source translation
GET /api/v1/configs/panorama/rules/nat?filter.source.starts_with=192.168.&filter.source_translation.exists=true
```

### Device-Group Specific Filtering

The same filtering capabilities work for device-group specific endpoints:

```bash
# Find servers in a specific device group
GET /api/v1/configs/panorama/device-groups/DMZ-DG/addresses?filter.name.contains=server

# Filter services by protocol in a device group
GET /api/v1/configs/panorama/device-groups/Branch-DG/services?filter.protocol.equals=tcp&filter.port.gte=8000

# Find security rules with specific tags in a device group
GET /api/v1/configs/panorama/device-groups/HQ-DG/rules?filter.tag.contains=critical&filter.action.equals=allow
```

## Performance Considerations

1. **Use specific filters**: More specific filters reduce the result set earlier
2. **Combine with pagination**: Use filtering with pagination for large datasets
3. **Use indexed fields**: Filters on `name`, `uuid`, and `type` are typically faster
4. **Avoid complex regex**: Simple string operations are faster than regex patterns

## Error Handling

Invalid filter parameters are silently ignored. The API will return:
- Empty result set if no objects match filters
- HTTP 400 for invalid operator syntax
- HTTP 404 for non-existent endpoints

## Filter Precedence

When multiple filters are specified:
1. All filters must match (AND logic)
2. Basic query parameters are processed first
3. Advanced filters are applied after basic filters
4. Pagination is applied last

## Tips and Best Practices

1. **Start broad, then narrow**: Begin with basic filters, add advanced filters as needed
2. **Use operator shortcuts**: Omit `_contains` as it's the default operator
3. **Test incrementally**: Add one filter at a time when building complex queries
4. **Use appropriate operators**: Use `starts_with` for IP prefixes, `ends_with` for domains
5. **Combine location and property filters**: Filter by device group AND object properties
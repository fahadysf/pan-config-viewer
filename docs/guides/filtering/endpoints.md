# Endpoint-Specific Filters

Each API endpoint supports filtering on fields specific to that resource type. This page documents all available filters for each endpoint.

## Address Objects

**Endpoint:** `/api/v1/configs/{config}/addresses`

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

### Example Queries

```bash
# Find all addresses in 10.0.0.0/8 network
GET /api/v1/configs/panorama/addresses?filter.ip.starts_with=10.

# Find all FQDN addresses for example.com domain
GET /api/v1/configs/panorama/addresses?filter.type.equals=fqdn&filter.fqdn.ends_with=.example.com

# Find addresses with production tag in specific device group
GET /api/v1/configs/panorama/addresses?filter.tag.in=production&filter.parent_device_group.equals=headquarters
```

## Service Objects

**Endpoint:** `/api/v1/configs/{config}/services`

| Filter | Type | Description | Example |
|--------|------|-------------|---------|
| `name` | string | Service name | `filter.name.starts_with=http` |
| `protocol` | enum | Protocol (tcp/udp) | `filter.protocol.equals=tcp` |
| `port` | string/int | Port number or range | `filter.port.gt=8000` |
| `tag` | array | Tags | `filter.tag.in=web` |
| `description` | string | Description | `filter.description.contains=web` |
| `parent_device_group` | string | Device group | `filter.parent_device_group.equals=hq` |
| `parent_template` | string | Template location | `filter.parent_template.equals=base` |

### Example Queries

```bash
# Find all TCP services on ports 8000-9000
GET /api/v1/configs/panorama/services?filter.protocol.equals=tcp&filter.port.gte=8000&filter.port.lte=9000

# Find services with names starting with "custom-"
GET /api/v1/configs/panorama/services?filter.name.starts_with=custom-

# Find high-port TCP services (>1024)
GET /api/v1/configs/panorama/services?filter.protocol.equals=tcp&filter.port.gt=1024
```

## Address Groups

**Endpoint:** `/api/v1/configs/{config}/address-groups`

| Filter | Type | Description | Example |
|--------|------|-------------|---------|
| `name` | string | Group name | `filter.name.contains=servers` |
| `member` | array | Group members | `filter.member.in=web-server-01` |
| `tag` | array | Tags | `filter.tag.in=production` |
| `description` | string | Description | `filter.description.contains=DMZ` |
| `parent_device_group` | string | Device group | `filter.parent_device_group.equals=branch` |
| `parent_template` | string | Template location | `filter.parent_template.equals=base` |

### Example Queries

```bash
# Find groups containing specific member
GET /api/v1/configs/panorama/address-groups?filter.member.in=web-server-01

# Find production server groups
GET /api/v1/configs/panorama/address-groups?filter.name.contains=server&filter.tag.in=production
```

## Service Groups

**Endpoint:** `/api/v1/configs/{config}/service-groups`

| Filter | Type | Description | Example |
|--------|------|-------------|---------|
| `name` | string | Group name | `filter.name.contains=web` |
| `member` | array | Group members | `filter.member.in=tcp-443` |
| `tag` | array | Tags | `filter.tag.in=critical` |
| `description` | string | Description | `filter.description.contains=services` |
| `parent_device_group` | string | Device group | `filter.parent_device_group.equals=hq` |

### Example Queries

```bash
# Find groups containing HTTPS service
GET /api/v1/configs/panorama/service-groups?filter.member.in=tcp-443

# Find critical service groups
GET /api/v1/configs/panorama/service-groups?filter.tag.in=critical
```

## Device Groups

**Endpoint:** `/api/v1/configs/{config}/device-groups`

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

### Example Queries

```bash
# Find device groups with many devices
GET /api/v1/configs/panorama/device-groups?filter.devices_count.gt=10

# Find child device groups
GET /api/v1/configs/panorama/device-groups?filter.parent.not_equals=shared

# Find device groups with many security rules
GET /api/v1/configs/panorama/device-groups?filter.pre_security_rules_count.gt=50
```

## Security Rules

**Endpoint:** `/api/v1/configs/{config}/rules/security`

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

### Example Queries

```bash
# Find all allow rules from DMZ to any
GET /api/v1/configs/panorama/rules/security?filter.source_zone.in=DMZ&filter.destination.in=any&filter.action.equals=allow

# Find disabled rules with logging enabled
GET /api/v1/configs/panorama/rules/security?filter.disabled.equals=true&filter.log_end.equals=true

# Find rules for specific application
GET /api/v1/configs/panorama/rules/security?filter.application.in=ssl&filter.application.in=ssh
```

## NAT Rules

**Endpoint:** `/api/v1/configs/{config}/rules/nat`

| Filter | Type | Description | Example |
|--------|------|-------------|---------|
| `name` | string | Rule name | `filter.name.contains=outbound` |
| `uuid` | string | Rule UUID | `filter.uuid.equals=123e4567` |
| `source` | array | Source addresses | `filter.source.in=internal` |
| `destination` | array | Destination addresses | `filter.destination.in=external` |
| `from` | array | Source zones | `filter.from.in=trust` |
| `to` | array | Destination zones | `filter.to.in=untrust` |
| `service` | string | Service | `filter.service.equals=any` |
| `source_translation` | object | Has source NAT | `filter.source_translation.exists=true` |
| `destination_translation` | object | Has destination NAT | `filter.destination_translation.exists=true` |
| `disabled` | bool | Rule state | `filter.disabled.equals=false` |
| `tag` | array | Tags | `filter.tag.in=nat` |
| `device_group` | string | Device group | `filter.device_group.equals=branch` |
| `rule_type` | enum | Rule type (pre/post) | `filter.rule_type.equals=pre` |

### Example Queries

```bash
# Find NAT rules for specific subnet with source translation
GET /api/v1/configs/panorama/rules/nat?filter.source.starts_with=192.168.&filter.source_translation.exists=true

# Find active outbound NAT rules
GET /api/v1/configs/panorama/rules/nat?filter.from.in=trust&filter.to.in=untrust&filter.disabled.equals=false
```

## Templates

**Endpoint:** `/api/v1/configs/{config}/templates`

| Filter | Type | Description | Example |
|--------|------|-------------|---------|
| `name` | string | Template name | `filter.name.contains=branch` |
| `description` | string | Description | `filter.description.contains=firewall` |
| `device_count` | int | Number of devices | `filter.device_count.gt=5` |

## Template Stacks

**Endpoint:** `/api/v1/configs/{config}/template-stacks`

| Filter | Type | Description | Example |
|--------|------|-------------|---------|
| `name` | string | Stack name | `filter.name.equals=branch-stack` |
| `member` | array | Template members | `filter.member.in=base-template` |
| `device_count` | int | Number of devices | `filter.device_count.gte=10` |

## Device-Group Specific Endpoints

All filtering capabilities work identically for device-group specific endpoints:

```bash
# Find servers in a specific device group
GET /api/v1/configs/panorama/device-groups/DMZ-DG/addresses?filter.name.contains=server

# Filter services by protocol in a device group
GET /api/v1/configs/panorama/device-groups/Branch-DG/services?filter.protocol.equals=tcp

# Find security rules with specific tags in a device group
GET /api/v1/configs/panorama/device-groups/HQ-DG/rules?filter.tag.contains=critical
```

## Template-Specific Endpoints

Templates support the same filtering as device groups:

```bash
# Find addresses in a template
GET /api/v1/configs/panorama/templates/branch-template/addresses?filter.type.equals=fqdn

# Filter services in a template
GET /api/v1/configs/panorama/templates/base-template/services?filter.port.lt=1024
```

## Common Filter Patterns

### Location-Based Filtering

```bash
# Find all objects in a specific device group
?filter.parent_device_group.equals=DMZ-DG

# Find objects in child device groups
?filter.parent_device_group.not_equals=shared

# Find objects in a specific template
?filter.parent_template.equals=branch-template
```

### Tag-Based Filtering

```bash
# Single tag
?filter.tag.in=production

# Multiple tags (must have all)
?filter.tag.in=production&filter.tag.in=critical

# Exclude tags
?filter.tag.not_in=test,development
```

### Count-Based Filtering

```bash
# Large groups
?filter.member_count.gt=100

# Small device groups
?filter.devices_count.lt=5

# Specific range
?filter.address_count.gte=50&filter.address_count.lte=200
```

## Performance Tips

1. **Filter early**: Apply most restrictive filters first
2. **Use indexed fields**: `name`, `uuid`, `type` are typically fastest
3. **Combine filters**: Multiple specific filters are better than one broad filter
4. **Limit regex use**: Regular expressions are powerful but slower

## Next Steps

- [Learn about filter operators →](operators.md)
- [View complex examples →](../../examples/complex-filters.md)
- [Explore pagination →](../pagination/index.md)
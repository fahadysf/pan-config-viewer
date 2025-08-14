# Filtering Guide

The PAN Config Viewer API provides a powerful and flexible filtering system that allows you to query configuration objects with precision. This guide covers everything you need to know about filtering.

## Overview

The filtering system supports:

- **15+ operators** for different comparison types
- **Dot notation syntax** for clean, readable queries
- **Type-aware filtering** for different data types
- **Multi-field filtering** with AND logic
- **Consistent behavior** across all endpoints

## Filtering Approaches

The API supports two complementary filtering approaches:

### 1. Basic Filters
Simple query parameters for common filtering needs:
```http
GET /api/v1/configs/{config}/addresses?name=server&tag=production
```

### 2. Advanced Filters
Powerful `filter.property.operator=value` syntax for precise filtering:
```http
GET /api/v1/configs/{config}/addresses?filter.ip.starts_with=10.&filter.tag.in=production
```

!!! info "Filter Logic"
    All filters use AND logic - objects must match ALL specified filter conditions.

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
| `filter.name=server` | Name contains "server" (default operator) |
| `filter.name.equals=web-01` | Name exactly equals "web-01" |
| `filter.port.gt=8000` | Port greater than 8000 |
| `filter.tag.in=production` | Has "production" tag |

## Quick Start Examples

### Find addresses in a specific network
```bash
GET /api/v1/configs/panorama/addresses?filter.ip.starts_with=192.168.
```

### Find TCP services on high ports
```bash
GET /api/v1/configs/panorama/services?filter.protocol.equals=tcp&filter.port.gt=1024
```

### Find security rules from DMZ
```bash
GET /api/v1/configs/panorama/rules/security?filter.source_zone.in=DMZ&filter.action.equals=allow
```

## Endpoint Availability

!!! success "Universal Support"
    Filtering is available on ALL endpoints that return lists of objects, including:
    
    - Shared objects endpoints (e.g., `/addresses`, `/services`)
    - Device-group specific endpoints (e.g., `/device-groups/{name}/addresses`)
    - Template specific endpoints (e.g., `/templates/{name}/addresses`)
    - All other collection endpoints

The same filtering syntax and operators work consistently across all endpoints.

## Performance Considerations

1. **Use specific filters**: More specific filters reduce the result set earlier
2. **Combine with pagination**: Use filtering with pagination for large datasets
3. **Use indexed fields**: Filters on `name`, `uuid`, and `type` are typically faster
4. **Avoid complex regex**: Simple string operations are faster than regex patterns

## Filter Precedence

When multiple filters are specified:

1. All filters must match (AND logic)
2. Basic query parameters are processed first
3. Advanced filters are applied after basic filters
4. Pagination is applied last

## Error Handling

- **Invalid filters**: Silently ignored, no error returned
- **No matches**: Returns empty result set
- **Invalid syntax**: Returns HTTP 400
- **Non-existent endpoint**: Returns HTTP 404

## Best Practices

1. **Start broad, then narrow**: Begin with basic filters, add advanced filters as needed
2. **Use operator shortcuts**: Omit `.contains` as it's the default operator
3. **Test incrementally**: Add one filter at a time when building complex queries
4. **Use appropriate operators**: Use `starts_with` for IP prefixes, `ends_with` for domains
5. **Combine location and property filters**: Filter by device group AND object properties

## Next Steps

- [View all available operators →](operators.md)
- [See endpoint-specific filters →](endpoints.md)
- [Explore complex filtering examples →](../../examples/complex-filters.md)
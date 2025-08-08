# Filter Operators Reference

This page provides a complete reference for all filtering operators supported by the PAN Config Viewer API.

## Operator Summary Table

| Operator | Aliases | Type | Description |
|----------|---------|------|-------------|
| `contains` | - | Text | Substring match (default) |
| `eq` | `equals` | Any | Exact match |
| `ne` | `not_equals` | Any | Not equal |
| `starts_with` | - | Text | Prefix match |
| `ends_with` | - | Text | Suffix match |
| `not_contains` | - | Text | Doesn't contain substring |
| `gt` | `greater_than` | Numeric | Greater than |
| `lt` | `less_than` | Numeric | Less than |
| `gte` | `greater_than_or_equal` | Numeric | Greater or equal |
| `lte` | `less_than_or_equal` | Numeric | Less or equal |
| `in` | - | List | Value in list |
| `not_in` | - | List | Value not in list |
| `regex` | - | Text | Regular expression match |
| `exists` | - | Any | Field exists (optional fields) |

## Text Operators

### contains (default)
Checks if the field contains the specified substring. This is the default operator when none is specified.

**Syntax:**
```
filter.field.contains=value
filter.field=value  # Same as above (default)
```

**Examples:**
```http
# Find addresses with "server" in the name
GET /api/v1/configs/panorama/addresses?filter.name.contains=server
GET /api/v1/configs/panorama/addresses?filter.name=server  # Same result

# Find descriptions containing "production"
GET /api/v1/configs/panorama/addresses?filter.description.contains=production
```

**Use Cases:**
- Partial name searches
- Finding objects with specific keywords
- Flexible string matching

---

### eq / equals
Performs an exact match comparison.

**Syntax:**
```
filter.field.eq=value
filter.field.equals=value  # Alias
```

**Examples:**
```http
# Find exact address by name
GET /api/v1/configs/panorama/addresses?filter.name.eq=web-server-01

# Find addresses of specific type
GET /api/v1/configs/panorama/addresses?filter.type.equals=fqdn

# Find TCP services
GET /api/v1/configs/panorama/services?filter.protocol.equals=tcp
```

**Use Cases:**
- Looking up specific objects
- Filtering by exact enum values
- Precise matching requirements

---

### ne / not_equals
Excludes items that match the specified value.

**Syntax:**
```
filter.field.ne=value
filter.field.not_equals=value  # Alias
```

**Examples:**
```http
# Find all non-TCP services
GET /api/v1/configs/panorama/services?filter.protocol.ne=tcp

# Exclude specific device group
GET /api/v1/configs/panorama/addresses?filter.parent_device_group.not_equals=DMZ

# Find all non-disabled rules
GET /api/v1/configs/panorama/rules/security?filter.disabled.ne=true
```

**Use Cases:**
- Exclusion filters
- Finding everything except specific values
- Negative matching

---

### starts_with
Matches values that begin with the specified prefix.

**Syntax:**
```
filter.field.starts_with=value
```

**Examples:**
```http
# Find all 10.x.x.x addresses
GET /api/v1/configs/panorama/addresses?filter.ip.starts_with=10.

# Find all addresses starting with "srv-"
GET /api/v1/configs/panorama/addresses?filter.name.starts_with=srv-

# Find rules in trust zones
GET /api/v1/configs/panorama/rules/security?filter.source_zone.starts_with=trust
```

**Use Cases:**
- IP subnet filtering
- Naming convention searches
- Prefix-based categorization

---

### ends_with
Matches values that end with the specified suffix.

**Syntax:**
```
filter.field.ends_with=value
```

**Examples:**
```http
# Find all .com domains
GET /api/v1/configs/panorama/addresses?filter.fqdn.ends_with=.com

# Find all addresses ending with "-prod"
GET /api/v1/configs/panorama/addresses?filter.name.ends_with=-prod

# Find internal domains
GET /api/v1/configs/panorama/addresses?filter.fqdn.ends_with=.internal
```

**Use Cases:**
- Domain filtering
- Suffix-based categorization
- Environment identification

---

### not_contains
Excludes items containing the specified substring.

**Syntax:**
```
filter.field.not_contains=value
```

**Examples:**
```http
# Find addresses without "test" in name
GET /api/v1/configs/panorama/addresses?filter.name.not_contains=test

# Exclude deprecated items
GET /api/v1/configs/panorama/services?filter.description.not_contains=deprecated

# Find non-temporary rules
GET /api/v1/configs/panorama/rules/security?filter.name.not_contains=temp
```

**Use Cases:**
- Excluding test/temporary objects
- Filtering out deprecated items
- Negative substring matching

---

### regex
Performs regular expression pattern matching.

**Syntax:**
```
filter.field.regex=pattern
```

**Examples:**
```http
# Find servers with numeric suffix
GET /api/v1/configs/panorama/addresses?filter.name.regex=^srv-\d+$

# Find IP addresses in specific pattern
GET /api/v1/configs/panorama/addresses?filter.ip.regex=^10\.1\.[0-9]{1,3}\.[0-9]{1,3}$

# Find rules with specific naming pattern
GET /api/v1/configs/panorama/rules/security?filter.name.regex=^(ALLOW|DENY)-.*-[0-9]{4}$
```

**Use Cases:**
- Complex pattern matching
- Validation of naming conventions
- Advanced string searches

## Numeric Operators

### gt / greater_than
Finds values greater than the specified number.

**Syntax:**
```
filter.field.gt=value
filter.field.greater_than=value  # Alias
```

**Examples:**
```http
# Find high-port services
GET /api/v1/configs/panorama/services?filter.port.gt=1024

# Find device groups with many devices
GET /api/v1/configs/panorama/device-groups?filter.devices_count.gt=10

# Find large address groups
GET /api/v1/configs/panorama/address-groups?filter.member_count.greater_than=50
```

---

### lt / less_than
Finds values less than the specified number.

**Syntax:**
```
filter.field.lt=value
filter.field.less_than=value  # Alias
```

**Examples:**
```http
# Find low-port services
GET /api/v1/configs/panorama/services?filter.port.lt=1024

# Find small device groups
GET /api/v1/configs/panorama/device-groups?filter.devices_count.less_than=5
```

---

### gte / greater_than_or_equal
Finds values greater than or equal to the specified number.

**Syntax:**
```
filter.field.gte=value
filter.field.greater_than_or_equal=value  # Alias
```

**Examples:**
```http
# Find services on port 8080 and above
GET /api/v1/configs/panorama/services?filter.port.gte=8080

# Find device groups with at least 20 addresses
GET /api/v1/configs/panorama/device-groups?filter.address_count.gte=20
```

---

### lte / less_than_or_equal
Finds values less than or equal to the specified number.

**Syntax:**
```
filter.field.lte=value
filter.field.less_than_or_equal=value  # Alias
```

**Examples:**
```http
# Find services on port 9000 and below
GET /api/v1/configs/panorama/services?filter.port.lte=9000

# Find device groups with up to 10 devices
GET /api/v1/configs/panorama/device-groups?filter.devices_count.lte=10
```

## List Operators

### in
Checks if the field value is in the specified list.

**Syntax:**
```
filter.field.in=value1,value2,value3
```

**Examples:**
```http
# Find objects with specific tags
GET /api/v1/configs/panorama/addresses?filter.tag.in=production,staging

# Find rules with specific applications
GET /api/v1/configs/panorama/rules/security?filter.application.in=web-browsing,ssl

# Find addresses in specific zones
GET /api/v1/configs/panorama/rules/security?filter.source_zone.in=trust,dmz
```

**Use Cases:**
- Multiple value matching
- Tag-based filtering
- Category searches

---

### not_in
Excludes items where the field value is in the specified list.

**Syntax:**
```
filter.field.not_in=value1,value2,value3
```

**Examples:**
```http
# Exclude specific tags
GET /api/v1/configs/panorama/addresses?filter.tag.not_in=test,deprecated

# Exclude untrusted zones
GET /api/v1/configs/panorama/rules/security?filter.source_zone.not_in=untrust,internet

# Find non-standard services
GET /api/v1/configs/panorama/services?filter.name.not_in=http,https,ssh
```

## Special Operators

### exists
Checks if an optional field exists (is not null).

**Syntax:**
```
filter.field.exists=true|false
```

**Examples:**
```http
# Find addresses with descriptions
GET /api/v1/configs/panorama/addresses?filter.description.exists=true

# Find rules without log settings
GET /api/v1/configs/panorama/rules/security?filter.log_setting.exists=false

# Find NAT rules with source translation
GET /api/v1/configs/panorama/rules/nat?filter.source_translation.exists=true
```

## Operator Compatibility Matrix

| Field Type | Compatible Operators |
|------------|---------------------|
| **String** | `contains`, `not_contains`, `eq`, `ne`, `starts_with`, `ends_with`, `regex`, `exists` |
| **Number** | `eq`, `ne`, `gt`, `lt`, `gte`, `lte`, `exists` |
| **Boolean** | `eq`, `ne`, `exists` |
| **Enum** | `eq`, `ne`, `in`, `not_in`, `exists` |
| **Array** | `in`, `not_in`, `contains`, `not_contains`, `exists` |
| **Object** | `exists` |

## Case Sensitivity

By default, all text comparisons are **case-insensitive**. This applies to:
- `contains`, `not_contains`
- `starts_with`, `ends_with`
- `eq`, `ne` (for strings)
- `in`, `not_in` (for strings)

## Value Formats

### String Values
- No quotes needed: `filter.name=server`
- Spaces are preserved: `filter.description=production server`
- Special characters are URL-encoded: `filter.name=server%2D01`

### Numeric Values
- Integers: `filter.port=80`
- Can be compared as strings: `filter.port=8080`
- Automatic type conversion: `filter.count.gt=10`

### Boolean Values
- Use `true` or `false`: `filter.disabled=true`
- Case-insensitive: `filter.disabled=True`

### List Values
- Comma-separated: `filter.tag.in=prod,staging,test`
- No spaces after commas: `filter.zone.in=trust,dmz`
- URL-encode if needed: `filter.tag.in=web%2Dserver,db%2Dserver`

### Regular Expressions
- Standard regex syntax: `filter.name.regex=^srv-\d+$`
- Escape special characters: `filter.ip.regex=10\.0\.0\.\d+`
- Case-insensitive by default

## Performance Tips

1. **Fastest operators**: `eq`, `ne`
2. **Fast operators**: `starts_with`, `contains`
3. **Moderate operators**: `ends_with`, `in`, `not_in`
4. **Slowest operators**: `regex`, complex `not_contains`

## Common Mistakes

### Wrong Operator for Field Type
```http
# ❌ Wrong: Using numeric operator on string field
GET /api/v1/configs/panorama/addresses?filter.name.gt=100

# ✅ Correct: Use appropriate operator
GET /api/v1/configs/panorama/addresses?filter.name.contains=server
```

### Missing URL Encoding
```http
# ❌ Wrong: Special characters not encoded
GET /api/v1/configs/panorama/addresses?filter.name=server-01&test

# ✅ Correct: Properly encoded
GET /api/v1/configs/panorama/addresses?filter.name=server%2D01%26test
```

### Incorrect List Format
```http
# ❌ Wrong: Spaces in list
GET /api/v1/configs/panorama/addresses?filter.tag.in=prod, test, dev

# ✅ Correct: No spaces
GET /api/v1/configs/panorama/addresses?filter.tag.in=prod,test,dev
```

## Next Steps

- [Learn about filter syntax](syntax.md)
- [See advanced filtering techniques](advanced.md)
- [Explore endpoint-specific filters](../endpoints/index.md)
- [View practical examples](../../examples/complex-filters.md)
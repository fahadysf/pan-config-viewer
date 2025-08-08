# Security Rules API

The Security Rules API provides endpoints for querying security policies configured in your Panorama setup, including pre-rules and post-rules at various hierarchy levels.

## Endpoints

### List All Security Rules
```http
GET /api/v1/configs/{config}/rules/security
```

### List Device-Group Security Rules
```http
GET /api/v1/configs/{config}/device-groups/{device_group}/rules/security
```

### List Pre-Rules
```http
GET /api/v1/configs/{config}/device-groups/{device_group}/pre-rules
```

### List Post-Rules
```http
GET /api/v1/configs/{config}/device-groups/{device_group}/post-rules
```

### Get Specific Security Rule
```http
GET /api/v1/configs/{config}/rules/security/{uuid}
```

## Security Rule Schema

```json
{
  "name": "Allow-Web-DMZ",
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "source": ["trust-zone", "10.0.0.0/8"],
  "destination": ["dmz-servers", "192.168.1.0/24"],
  "from": ["trust", "internal"],
  "to": ["dmz"],
  "source-user": ["any"],
  "category": ["any"],
  "application": ["web-browsing", "ssl"],
  "service": ["application-default"],
  "action": "allow",
  "log-start": false,
  "log-end": true,
  "disabled": false,
  "description": "Allow web traffic from trust to DMZ",
  "tag": ["production", "web-access"],
  "log-setting": "default-logging",
  "rule-type": "interzone",
  "negate-source": false,
  "negate-destination": false,
  "xpath": "/config/devices/entry/device-group/entry[2]/pre-rulebase/security/rules/entry[15]",
  "parent-device-group": "DMZ-DG"
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Rule name/identifier |
| `uuid` | string | Unique rule identifier |
| `source` | array | Source addresses/objects |
| `destination` | array | Destination addresses/objects |
| `from` | array | Source security zones |
| `to` | array | Destination security zones |
| `source-user` | array | Source users/groups |
| `category` | array | URL filtering categories |
| `application` | array | Applications/app groups |
| `service` | array | Services/service groups |
| `action` | enum | Action: allow, deny, drop, reset-client, reset-server, reset-both |
| `log-start` | boolean | Log at session start |
| `log-end` | boolean | Log at session end |
| `disabled` | boolean | Rule disabled state |
| `description` | string | Rule description |
| `tag` | array | Associated tags |
| `log-setting` | string | Log forwarding profile |
| `rule-type` | enum | Rule type: universal, interzone, intrazone |
| `negate-source` | boolean | Negate source condition |
| `negate-destination` | boolean | Negate destination condition |

## Filtering Options

### Available Filter Fields

| Field | Type | Operators | Description | Examples |
|-------|------|-----------|-------------|----------|
| `name` | string | All text operators | Rule name | `filter.name.contains=Allow`<br>`filter.name.starts_with=Block-`<br>`filter.name.regex=^(ALLOW\|DENY)-.*$` |
| `uuid` | string | `eq`, `ne` | Rule UUID | `filter.uuid.equals=123e4567-e89b-12d3` |
| `source` | array | List operators, contains | Source addresses | `filter.source.in=any`<br>`filter.source.contains=10.0.0.0/8`<br>`filter.source.not_contains=trust-servers` |
| `destination` | array | List operators, contains | Destination addresses | `filter.destination.in=any`<br>`filter.destination.contains=dmz`<br>`filter.destination.not_in=192.168.1.0/24` |
| `source_zone` / `from` | array | List operators | Source zones | `filter.source_zone.in=trust`<br>`filter.from.contains=internal`<br>`filter.from.not_in=untrust` |
| `dest_zone` / `to` | array | List operators | Destination zones | `filter.to.in=dmz`<br>`filter.dest_zone.contains=untrust` |
| `application` | array | List operators | Applications | `filter.application.in=web-browsing,ssl`<br>`filter.application.contains=facebook` |
| `service` | array | List operators | Services | `filter.service.in=application-default`<br>`filter.service.contains=tcp-443` |
| `action` | enum | `eq`, `ne`, `in` | Rule action | `filter.action.equals=allow`<br>`filter.action.ne=deny`<br>`filter.action.in=drop,reset-both` |
| `disabled` | boolean | `eq`, `ne` | Rule state | `filter.disabled.equals=false`<br>`filter.disabled.ne=true` |
| `source_user` | array | List operators | Source users | `filter.source_user.in=any`<br>`filter.source_user.contains=domain\\admins` |
| `category` | array | List operators | URL categories | `filter.category.in=social-networking`<br>`filter.category.not_contains=malware` |
| `tag` | array | List operators | Tags | `filter.tag.in=critical,production`<br>`filter.tag.contains=pci` |
| `log_start` | boolean | `eq`, `ne` | Start logging | `filter.log_start.equals=true` |
| `log_end` | boolean | `eq`, `ne` | End logging | `filter.log_end.equals=true` |
| `log_setting` | string | Text operators | Log profile | `filter.log_setting.equals=default`<br>`filter.log_setting.contains=syslog` |
| `rule_type` | enum | `eq`, `ne`, `in` | Rule type | `filter.rule_type.equals=interzone`<br>`filter.rule_type.in=universal,intrazone` |
| `device_group` | string | Text operators | Device group | `filter.device_group.equals=DMZ-DG` |

## Complete Examples

### Example 1: Find High-Risk Allow Rules (Any-Any)
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.source.in=any&\
filter.destination.in=any&\
filter.service.in=any&\
filter.application.in=any&\
filter.action.equals=allow"
```

**Response:**
```json
{
  "items": [
    {
      "name": "Temp-Allow-All",
      "uuid": "456e7890-a12b-34c5-d678-901234567890",
      "source": ["any"],
      "destination": ["any"],
      "from": ["any"],
      "to": ["any"],
      "application": ["any"],
      "service": ["any"],
      "action": "allow",
      "log-end": true,
      "disabled": false,
      "description": "TEMPORARY - Remove after testing",
      "tag": ["temporary", "high-risk"]
    }
  ],
  "total_items": 1,
  "page": 1,
  "page_size": 500,
  "total_pages": 1
}
```

### Example 2: Find Rules Without Logging
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.log_end.equals=false&\
filter.action.equals=allow&\
filter.disabled.equals=false"
```

### Example 3: Find Rules for Specific Application
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.application.contains=facebook&\
filter.action.equals=allow"
```

### Example 4: Find Disabled Rules
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.disabled.equals=true"
```

### Example 5: Find Rules by Source and Destination Zones
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.from.in=trust,internal&\
filter.to.in=dmz,untrust&\
filter.action.equals=allow"
```

## Security Audit Queries

### 1. Overly Permissive Rules
Find rules with "any" in critical fields:
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.source.in=any&\
filter.application.in=any&\
filter.action.equals=allow"
```

### 2. Rules Without Security Profiles
Find rules missing security profiles:
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.profile_setting.exists=false&\
filter.action.equals=allow"
```

### 3. Outbound Internet Access
Find rules allowing outbound internet:
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.to.contains=untrust&\
filter.destination.in=any&\
filter.action.equals=allow"
```

### 4. Administrative Access Rules
Find rules allowing administrative protocols:
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.application.in=ssh,telnet,ms-rdp&\
filter.action.equals=allow"
```

### 5. Compliance Violations
Find non-compliant rules (example: PCI-DSS):
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.tag.not_contains=pci-compliant&\
filter.to.contains=cardholder-data&\
filter.action.equals=allow"
```

## Zone-Based Filtering

### Inter-Zone Rules
```bash
# Trust to DMZ
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.from.in=trust&\
filter.to.in=dmz"

# DMZ to Internet
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.from.in=dmz&\
filter.to.in=untrust,internet"
```

### Intra-Zone Rules
```bash
# Within DMZ
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.from.in=dmz&\
filter.to.in=dmz&\
filter.rule_type.equals=intrazone"
```

## Application-Based Filtering

### Social Media Applications
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.application.in=facebook,twitter,instagram,linkedin&\
filter.action.equals=allow"
```

### File Transfer Applications
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.application.in=ftp,sftp,scp,dropbox&\
filter.action.equals=allow"
```

### High-Risk Applications
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.application.in=bittorrent,tor,ultrasurf&\
filter.action.ne=deny"
```

## Device-Group Specific Queries

### Pre-Rules in Device Group
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/device-groups/DMZ-DG/pre-rules?\
filter.action.equals=deny"
```

### Post-Rules in Device Group
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/device-groups/DMZ-DG/post-rules?\
filter.log_end.equals=true"
```

## Common Use Cases

### 1. Change Impact Analysis
Find rules affected by address object change:
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.source.contains=old-server-01"

curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.destination.contains=old-server-01"
```

### 2. Cleanup Candidates
Find potentially unused rules:
```bash
# Disabled rules
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.disabled.equals=true"

# Rules with "temp" or "test" in name
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.name.regex=(temp|test|tmp)"
```

### 3. Zero Trust Validation
Find rules not following zero trust principles:
```bash
# Rules with "any" user
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.source_user.in=any&\
filter.action.equals=allow"
```

### 4. Logging Compliance
Ensure all rules have logging enabled:
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.log_end.equals=false&\
filter.disabled.equals=false"
```

## Performance Optimization

### Indexed Fields for Fast Queries
- `name` - Rule name
- `uuid` - Unique identifier
- `action` - Allow/deny/drop
- `disabled` - Rule state

### Query Optimization Tips
1. Filter by `action` first when looking for allow/deny rules
2. Use `uuid` for direct rule lookup
3. Combine zone filters to narrow results
4. Use device-group specific endpoints when possible

## SDK Examples

### Python
```python
import requests

class SecurityRuleAnalyzer:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def find_risky_rules(self):
        """Find high-risk security rules"""
        params = {
            "filter.source.in": "any",
            "filter.destination.in": "any",
            "filter.action.equals": "allow",
            "filter.disabled.equals": "false"
        }
        response = requests.get(
            f"{self.base_url}/rules/security",
            params=params
        )
        return response.json()["items"]
    
    def find_rules_by_application(self, app_name):
        """Find rules allowing specific application"""
        params = {
            "filter.application.contains": app_name,
            "filter.action.equals": "allow"
        }
        response = requests.get(
            f"{self.base_url}/rules/security",
            params=params
        )
        return response.json()["items"]

# Usage
analyzer = SecurityRuleAnalyzer("http://localhost:8000/api/v1/configs/panorama")
risky_rules = analyzer.find_risky_rules()
print(f"Found {len(risky_rules)} high-risk rules")
```

### JavaScript
```javascript
class SecurityRuleClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }
    
    async findRulesWithoutLogging() {
        const params = new URLSearchParams({
            'filter.log_end.equals': 'false',
            'filter.action.equals': 'allow',
            'filter.disabled.equals': 'false'
        });
        
        const response = await fetch(
            `${this.baseUrl}/rules/security?${params}`
        );
        const data = await response.json();
        return data.items;
    }
    
    async findInterZoneRules(fromZone, toZone) {
        const params = new URLSearchParams({
            'filter.from.in': fromZone,
            'filter.to.in': toZone
        });
        
        const response = await fetch(
            `${this.baseUrl}/rules/security?${params}`
        );
        const data = await response.json();
        return data.items;
    }
}

// Usage
const client = new SecurityRuleClient('http://localhost:8000/api/v1/configs/panorama');
client.findRulesWithoutLogging().then(rules => {
    console.log(`Found ${rules.length} rules without logging`);
    rules.forEach(rule => {
        console.log(`- ${rule.name}: ${rule.source} -> ${rule.destination}`);
    });
});
```

## Related Endpoints

- [NAT Rules](nat-rules.md) - Network address translation rules
- [Address Objects](addresses.md) - Address objects used in rules
- [Service Objects](services.md) - Services referenced in rules
- [Application Objects](applications.md) - Applications used in rules

## Best Practices

1. **Naming Conventions**: Use descriptive names indicating purpose and traffic flow
2. **Logging**: Enable logging on all production rules
3. **Documentation**: Always include descriptions for rules
4. **Tags**: Use tags for compliance, environment, and criticality
5. **Regular Audits**: Periodically review for overly permissive rules
6. **Least Privilege**: Avoid using "any" in source, destination, or application fields
7. **Security Profiles**: Apply appropriate security profiles to all allow rules
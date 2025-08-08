# Complex Filtering Examples

This guide demonstrates advanced filtering techniques and real-world scenarios for querying your Panorama configuration.

## Multi-Criteria Filtering

### Security Audit: Find High-Risk Rules

Find overly permissive rules that pose security risks:

```bash
# Any-to-any allow rules without logging
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.source.in=any&\
filter.destination.in=any&\
filter.application.in=any&\
filter.service.in=any&\
filter.action.equals=allow&\
filter.log_end.equals=false"
```

### Compliance Check: PCI-DSS

Find rules that might violate PCI-DSS requirements:

```bash
# Unencrypted protocols to cardholder environment
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.destination.contains=cardholder&\
filter.application.in=telnet,ftp,http&\
filter.action.equals=allow"
```

### Network Segmentation Validation

Verify proper network segmentation:

```bash
# Direct access from untrust to internal databases
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.from.in=untrust,internet&\
filter.destination.contains=database&\
filter.action.equals=allow"
```

## Address Object Queries

### Subnet Analysis

Find all addresses in multiple subnets:

```bash
# Find addresses in either 10.0.0.0/8 or 172.16.0.0/12
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.type.equals=ip-netmask" \
| jq '.items[] | select(.["ip-netmask"] | startswith("10.") or startswith("172.16"))'
```

### FQDN Management

Find and categorize FQDN objects:

```bash
# External domains (non-.internal)
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.type.equals=fqdn&\
filter.fqdn.not_contains=.internal&\
filter.fqdn.not_contains=.local"

# Cloud service domains
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.type.equals=fqdn&\
filter.fqdn.regex=(amazonaws|azure|googlecloud)\.com$"
```

### Duplicate Detection

Find potential duplicate addresses:

```bash
# Find addresses with same IP but different names
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.type.equals=ip-netmask" \
| jq 'reduce .items[] as $item ({}; .[$item["ip-netmask"]] += [$item.name]) | 
  to_entries | map(select(.value | length > 1))'
```

## Service Analysis

### Port Range Analysis

Find services using specific port ranges:

```bash
# High-risk port ranges
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.port.contains=135-139&\
filter.protocol.equals=tcp"

# Custom application ports
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.port.gte=30000&\
filter.port.lte=32767"
```

### Service Inventory

Categorize services by usage:

```bash
# Database services
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.port.in=1433,1521,3306,5432,27017&\
filter.protocol.equals=tcp"

# Web services
curl -X GET "http://localhost:8000/api/v1/configs/panorama/services?\
filter.port.in=80,443,8080,8443&\
filter.protocol.equals=tcp"
```

## Application-Based Filtering

### Social Media Control

Find rules allowing social media:

```bash
# All social media applications
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.application.regex=(facebook|twitter|instagram|linkedin|tiktok)&\
filter.action.equals=allow"
```

### File Transfer Analysis

Identify file transfer permissions:

```bash
# File transfer protocols
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.application.in=ftp,sftp,scp,dropbox,google-drive,onedrive&\
filter.action.ne=deny"
```

### High-Risk Applications

Find rules allowing risky applications:

```bash
# P2P and anonymization tools
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.application.regex=(torrent|tor|proxy|vpn|ultrasurf)&\
filter.action.ne=deny&\
filter.disabled.equals=false"
```

## Zone-Based Analysis

### DMZ Security Posture

Analyze DMZ security configuration:

```bash
# Inbound to DMZ
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.from.in=untrust,internet&\
filter.to.in=dmz&\
filter.action.equals=allow"

# Outbound from DMZ
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.from.in=dmz&\
filter.to.not_in=dmz&\
filter.action.equals=allow"

# DMZ to internal
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.from.in=dmz&\
filter.to.in=trust,internal&\
filter.action.equals=allow"
```

### Zero Trust Validation

Check zero trust implementation:

```bash
# Rules without user identification
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.source_user.in=any&\
filter.to.in=trust,internal&\
filter.action.equals=allow"
```

## Tag-Based Queries

### Environment Separation

Verify environment isolation:

```bash
# Production to development access
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.source.contains=prod&\
filter.destination.contains=dev&\
filter.action.equals=allow"
```

### Critical Asset Protection

Find rules affecting critical assets:

```bash
# Access to critical tagged resources
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.destination.contains=critical&\
filter.tag.not_contains=approved&\
filter.action.equals=allow"
```

## NAT Rule Analysis

### Source NAT Audit

Find source NAT configurations:

```bash
# Outbound NAT rules
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/nat?\
filter.from.in=trust,internal&\
filter.to.in=untrust,internet&\
filter.source_translation.exists=true"
```

### Destination NAT Review

Analyze inbound NAT rules:

```bash
# Public to private NAT
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/nat?\
filter.from.in=untrust,internet&\
filter.destination_translation.exists=true&\
filter.disabled.equals=false"
```

## Complex Regex Patterns

### Naming Convention Validation

Check adherence to naming standards:

```bash
# Find non-compliant rule names
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.name.regex=^(?![A-Z]{2,}-[A-Z]+-[0-9]{4}$).*"

# Find non-compliant addresses
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.name.regex=^(?!(srv|web|db|app)-[a-z]+-[0-9]{2}$).*"
```

### IP Pattern Matching

Find specific IP patterns:

```bash
# Find IPs ending in .1 (likely gateways)
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.ip.regex=\\.1(/|$)&\
filter.type.equals=ip-netmask"

# Find /32 host addresses
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.ip.regex=/32$&\
filter.type.equals=ip-netmask"
```

## Performance Optimization Queries

### Large Result Set Handling

Efficiently process large datasets:

```bash
# Paginated retrieval with filtering
LIMIT=100
OFFSET=0
TOTAL=999999

while [ $OFFSET -lt $TOTAL ]; do
    RESPONSE=$(curl -s "http://localhost:8000/api/v1/configs/panorama/addresses?\
    filter.type.equals=ip-netmask&\
    limit=$LIMIT&\
    offset=$OFFSET")
    
    TOTAL=$(echo $RESPONSE | jq '.total_items')
    echo $RESPONSE | jq '.items[]' >> all_addresses.jsonl
    
    OFFSET=$((OFFSET + LIMIT))
done
```

### Parallel Queries

Execute multiple queries simultaneously:

```bash
# Parallel filtering for different object types
{
    curl -s "http://localhost:8000/api/v1/configs/panorama/addresses?filter.tag.in=production" &
    curl -s "http://localhost:8000/api/v1/configs/panorama/services?filter.tag.in=production" &
    curl -s "http://localhost:8000/api/v1/configs/panorama/rules/security?filter.tag.in=production" &
    wait
} | jq -s '.'
```

## Python Advanced Examples

```python
import requests
import concurrent.futures
from typing import List, Dict, Any

class AdvancedPanConfigAnalyzer:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
    
    def find_security_gaps(self) -> Dict[str, List[Any]]:
        """Identify potential security gaps in configuration"""
        gaps = {}
        
        # Overly permissive rules
        gaps['permissive_rules'] = self._query_rules({
            'source.in': 'any',
            'destination.in': 'any',
            'action.equals': 'allow'
        })
        
        # Rules without logging
        gaps['no_logging'] = self._query_rules({
            'log_end.equals': 'false',
            'action.equals': 'allow',
            'disabled.equals': 'false'
        })
        
        # Direct internet access
        gaps['direct_internet'] = self._query_rules({
            'from.in': 'trust,internal',
            'to.in': 'untrust,internet',
            'destination.in': 'any'
        })
        
        return gaps
    
    def analyze_attack_surface(self) -> Dict[str, Any]:
        """Analyze external attack surface"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                'inbound_rules': executor.submit(
                    self._query_rules, 
                    {'from.in': 'untrust,internet', 'action.equals': 'allow'}
                ),
                'public_services': executor.submit(
                    self._query_nat_rules,
                    {'from.in': 'untrust', 'destination_translation.exists': 'true'}
                ),
                'dmz_exposure': executor.submit(
                    self._query_rules,
                    {'to.in': 'dmz', 'from.in': 'untrust,internet'}
                )
            }
            
            results = {}
            for key, future in futures.items():
                results[key] = future.result()
            
            return results
    
    def find_unused_objects(self) -> Dict[str, List[str]]:
        """Find potentially unused configuration objects"""
        unused = {}
        
        # Addresses without description or tags
        addresses = self._query_addresses({
            'description.equals': '',
            'tag.exists': 'false'
        })
        unused['addresses'] = [a['name'] for a in addresses]
        
        # Disabled rules
        rules = self._query_rules({'disabled.equals': 'true'})
        unused['disabled_rules'] = [r['name'] for r in rules]
        
        # Services with 'old' or 'temp' in name
        services = self._query_services({'name.regex': '(old|temp|test)'})
        unused['temp_services'] = [s['name'] for s in services]
        
        return unused
    
    def _query_rules(self, filters: Dict[str, str]) -> List[Dict]:
        params = {f'filter.{k}': v for k, v in filters.items()}
        response = self.session.get(
            f"{self.base_url}/rules/security",
            params=params
        )
        return response.json().get('items', [])
    
    def _query_addresses(self, filters: Dict[str, str]) -> List[Dict]:
        params = {f'filter.{k}': v for k, v in filters.items()}
        response = self.session.get(
            f"{self.base_url}/addresses",
            params=params
        )
        return response.json().get('items', [])
    
    def _query_services(self, filters: Dict[str, str]) -> List[Dict]:
        params = {f'filter.{k}': v for k, v in filters.items()}
        response = self.session.get(
            f"{self.base_url}/services",
            params=params
        )
        return response.json().get('items', [])
    
    def _query_nat_rules(self, filters: Dict[str, str]) -> List[Dict]:
        params = {f'filter.{k}': v for k, v in filters.items()}
        response = self.session.get(
            f"{self.base_url}/rules/nat",
            params=params
        )
        return response.json().get('items', [])

# Usage
analyzer = AdvancedPanConfigAnalyzer("http://localhost:8000/api/v1/configs/panorama")

# Security gap analysis
gaps = analyzer.find_security_gaps()
print(f"Found {len(gaps['permissive_rules'])} overly permissive rules")
print(f"Found {len(gaps['no_logging'])} rules without logging")

# Attack surface analysis
attack_surface = analyzer.analyze_attack_surface()
print(f"Inbound rules: {len(attack_surface['inbound_rules'])}")
print(f"Public services: {len(attack_surface['public_services'])}")

# Cleanup candidates
unused = analyzer.find_unused_objects()
print(f"Potentially unused addresses: {len(unused['addresses'])}")
print(f"Disabled rules: {len(unused['disabled_rules'])}")
```

## JavaScript Advanced Examples

```javascript
class SecurityAuditor {
    constructor(apiUrl) {
        this.apiUrl = apiUrl;
    }
    
    async performComplianceCheck(standard = 'pci-dss') {
        const checks = {
            'pci-dss': {
                'unencrypted_protocols': {
                    'filter.application.in': 'telnet,ftp,http',
                    'filter.destination.contains': 'cardholder',
                    'filter.action.equals': 'allow'
                },
                'missing_logging': {
                    'filter.tag.contains': 'pci',
                    'filter.log_end.equals': 'false'
                },
                'any_source': {
                    'filter.source.in': 'any',
                    'filter.destination.contains': 'cardholder'
                }
            }
        };
        
        const results = {};
        const checkSet = checks[standard];
        
        for (const [checkName, filters] of Object.entries(checkSet)) {
            const params = new URLSearchParams(filters);
            const response = await fetch(
                `${this.apiUrl}/rules/security?${params}`
            );
            const data = await response.json();
            results[checkName] = {
                violation_count: data.total_items,
                violations: data.items
            };
        }
        
        return results;
    }
    
    async findShadowIT() {
        // Find unauthorized cloud applications
        const cloudApps = [
            'dropbox', 'google-drive', 'onedrive', 'box',
            'wetransfer', 'mega', 'mediafire'
        ];
        
        const params = new URLSearchParams({
            'filter.application.regex': cloudApps.join('|'),
            'filter.action.ne': 'deny',
            'filter.tag.not_contains': 'approved'
        });
        
        const response = await fetch(
            `${this.apiUrl}/rules/security?${params}`
        );
        return response.json();
    }
    
    async analyzeZeroTrust() {
        const violations = {};
        
        // Check for any-user rules
        const anyUserParams = new URLSearchParams({
            'filter.source_user.in': 'any',
            'filter.action.equals': 'allow'
        });
        const anyUserResp = await fetch(
            `${this.apiUrl}/rules/security?${anyUserParams}`
        );
        violations.any_user = await anyUserResp.json();
        
        // Check for missing MFA
        const noMfaParams = new URLSearchParams({
            'filter.tag.not_contains': 'mfa-required',
            'filter.to.in': 'trust,internal',
            'filter.from.in': 'untrust,internet'
        });
        const noMfaResp = await fetch(
            `${this.apiUrl}/rules/security?${noMfaParams}`
        );
        violations.no_mfa = await noMfaResp.json();
        
        return violations;
    }
}

// Usage
const auditor = new SecurityAuditor('http://localhost:8000/api/v1/configs/panorama');

// PCI-DSS compliance check
auditor.performComplianceCheck('pci-dss').then(results => {
    console.log('PCI-DSS Compliance Check Results:');
    for (const [check, data] of Object.entries(results)) {
        console.log(`${check}: ${data.violation_count} violations`);
    }
});

// Shadow IT detection
auditor.findShadowIT().then(data => {
    console.log(`Found ${data.total_items} potential shadow IT rules`);
    data.items.forEach(rule => {
        console.log(`- ${rule.name}: ${rule.application.join(', ')}`);
    });
});

// Zero Trust analysis
auditor.analyzeZeroTrust().then(violations => {
    console.log('Zero Trust Violations:');
    console.log(`Rules with any user: ${violations.any_user.total_items}`);
    console.log(`Rules missing MFA: ${violations.no_mfa.total_items}`);
});
```

## Shell Script Examples

### Automated Security Report

```bash
#!/bin/bash

API_URL="http://localhost:8000/api/v1/configs/panorama"
REPORT_DATE=$(date +%Y%m%d)
REPORT_FILE="security_report_${REPORT_DATE}.html"

# Generate HTML report
cat > $REPORT_FILE << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Security Configuration Report - $REPORT_DATE</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .critical { color: red; }
        .warning { color: orange; }
        .info { color: blue; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>Security Configuration Report</h1>
    <p>Generated: $(date)</p>
EOF

# High-risk rules
echo "<h2 class='critical'>High-Risk Rules</h2>" >> $REPORT_FILE
RISKY_RULES=$(curl -s "$API_URL/rules/security?\
filter.source.in=any&\
filter.destination.in=any&\
filter.action.equals=allow" | jq -r '.total_items')
echo "<p>Found $RISKY_RULES overly permissive rules</p>" >> $REPORT_FILE

# Rules without logging
echo "<h2 class='warning'>Rules Without Logging</h2>" >> $REPORT_FILE
NO_LOG=$(curl -s "$API_URL/rules/security?\
filter.log_end.equals=false&\
filter.disabled.equals=false" | jq -r '.total_items')
echo "<p>Found $NO_LOG active rules without logging</p>" >> $REPORT_FILE

# Disabled rules
echo "<h2 class='info'>Cleanup Candidates</h2>" >> $REPORT_FILE
DISABLED=$(curl -s "$API_URL/rules/security?\
filter.disabled.equals=true" | jq -r '.total_items')
echo "<p>Found $DISABLED disabled rules</p>" >> $REPORT_FILE

echo "</body></html>" >> $REPORT_FILE

echo "Report generated: $REPORT_FILE"
```

## Next Steps

- [Basic Query Examples](basic-queries.md)
- [Pagination Examples](pagination.md)
- [Python SDK Examples](python.md)
- [Performance Optimization](../guides/performance.md)
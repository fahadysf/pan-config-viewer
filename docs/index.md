# PAN Config Viewer API Documentation

<div align="center">

![PAN Config Viewer Logo](assets/banner.png)

[![API Version](https://img.shields.io/badge/API-v1.0.0-blue)](https://github.com/yourusername/pan-config-viewer)
[![Documentation Status](https://readthedocs.org/projects/pan-config-viewer/badge/?version=latest)](https://pan-config-viewer.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**A powerful REST API for querying and analyzing PAN-OS Panorama configurations**

[Get Started](getting-started.md){ .md-button .md-button--primary }
[API Reference](api/index.md){ .md-button }
[View on GitHub](https://github.com/yourusername/pan-config-viewer){ .md-button }

</div>

---

## 🚀 Features

<div class="grid cards" markdown>

- :material-filter: **Advanced Filtering**  
  Powerful filtering system with 15+ operators for precise queries

- :material-api: **RESTful API**  
  Clean, intuitive REST endpoints following industry best practices

- :material-speedometer: **High Performance**  
  Optimized for large configurations with efficient caching

- :material-book-open-page-variant: **Comprehensive Docs**  
  Detailed documentation with examples for every endpoint

- :material-pagination: **Smart Pagination**  
  Efficient pagination for handling large result sets

- :material-shield-check: **Type Safety**  
  Full Pydantic validation for all request/response models

</div>

## 📊 What Can You Query?

The PAN Config Viewer API provides read-only access to your Panorama configuration, allowing you to:

- **Address Objects**: Query IP addresses, FQDNs, and IP ranges
- **Service Objects**: Search services by port, protocol, or name
- **Security Rules**: Filter policies by source, destination, application, or action
- **NAT Rules**: Analyze NAT configurations with complex filters
- **Device Groups**: Browse hierarchical device group structures
- **Templates & Stacks**: Access template configurations
- **Security Profiles**: Query antivirus, anti-spyware, and other profiles
- **And much more!**

## 🎯 Key Use Cases

### Security Auditing
Analyze your security posture by querying rules with specific conditions:
```bash
# Find all rules allowing "any" source to "any" destination
GET /api/v1/configs/{config}/rules/security?filter.source.in=any&filter.destination.in=any
```

### Configuration Analysis
Search for specific objects across your entire configuration:
```bash
# Find all addresses in the 10.0.0.0/8 network
GET /api/v1/configs/{config}/addresses?filter.ip.starts_with=10.
```

### Compliance Reporting
Generate compliance reports by filtering on specific criteria:
```bash
# Find all disabled security rules
GET /api/v1/configs/{config}/rules/security?filter.disabled.equals=true
```

### Change Impact Analysis
Understand the impact of changes by querying related objects:
```bash
# Find all rules using a specific address object
GET /api/v1/configs/{config}/rules/security?filter.source.contains=webserver-01
```

## 🔍 Powerful Filtering System

Our advanced filtering system supports multiple operators for precise queries:

| Operator | Description | Example |
|----------|-------------|---------|
| `equals` / `eq` | Exact match | `filter.name.equals=firewall-01` |
| `contains` | Substring match | `filter.description.contains=production` |
| `starts_with` | Prefix match | `filter.ip.starts_with=192.168.` |
| `ends_with` | Suffix match | `filter.fqdn.ends_with=.example.com` |
| `gt`, `lt`, `gte`, `lte` | Numeric comparisons | `filter.port.gte=8000` |
| `in`, `not_in` | List membership | `filter.tag.in=critical` |
| `regex` | Pattern matching | `filter.name.regex=^srv-.*-prod$` |

[Explore All Operators →](guides/filtering/operators.md)

## 📖 Quick Examples

### Basic Query
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?limit=10"
```

### Filtered Query
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/addresses?\
filter.type.equals=fqdn&\
filter.fqdn.ends_with=.internal.com"
```

### Complex Multi-Filter Query
```bash
curl -X GET "http://localhost:8000/api/v1/configs/panorama/rules/security?\
filter.source_zone.in=DMZ&\
filter.action.equals=allow&\
filter.application.contains=web&\
filter.disabled.equals=false"
```

## 🚦 Getting Started

1. **[Installation](installation.md)** - Set up the API server
2. **[Configuration](configuration.md)** - Configure your environment
3. **[Quick Start](quickstart/index.md)** - Make your first API call
4. **[Filtering Guide](guides/filtering/index.md)** - Master the filtering system
5. **[API Reference](api/index.md)** - Explore all endpoints

## 📚 Documentation Structure

- **[Quick Start](quickstart/index.md)** - Get up and running quickly
- **[API Guide](api/index.md)** - Core concepts and usage patterns
- **[Filtering](guides/filtering/index.md)** - Deep dive into filtering capabilities
- **[Endpoints](api/endpoints/index.md)** - Detailed endpoint documentation
- **[Examples](examples/index.md)** - Real-world usage examples
- **[Reference](reference/index.md)** - API specifications and troubleshooting

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](developer/contributing.md) for details.

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/yourusername/pan-config-viewer/blob/main/LICENSE) file for details.

## 🆘 Support

- 📧 Email: support@example.com
- 💬 Slack: [Join our workspace](https://slack.example.com)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/pan-config-viewer/issues)
- 📖 Docs: [Read the Docs](https://pan-config-viewer.readthedocs.io)

---

<div align="center">
Made with ❤️ by the PAN Config Team
</div>
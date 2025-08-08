# PAN Config Viewer API Documentation

This directory contains the comprehensive documentation for the PAN Config Viewer API, built with MkDocs and Material for MkDocs.

## Documentation Structure

```
docs/
├── index.md                 # Home page
├── getting-started.md        # Getting started guide
├── installation.md          # Installation instructions
├── configuration.md         # Configuration guide
├── quickstart/             # Quick start guides
│   ├── index.md
│   ├── basic-usage.md
│   ├── authentication.md
│   └── first-requests.md
├── api/                    # API documentation
│   ├── index.md
│   ├── overview.md
│   ├── authentication.md
│   ├── pagination.md
│   ├── error-handling.md
│   ├── endpoints/          # Endpoint documentation
│   │   ├── addresses.md
│   │   ├── services.md
│   │   ├── security-rules.md
│   │   └── ...
│   └── objects/           # Object schemas
│       ├── address.md
│       ├── service.md
│       └── ...
├── guides/                # Guides and tutorials
│   ├── filtering/         # Filtering guide
│   │   ├── index.md
│   │   ├── operators.md
│   │   ├── syntax.md
│   │   └── advanced.md
│   ├── performance.md
│   └── ...
├── examples/             # Code examples
│   ├── index.md
│   ├── basic-queries.md
│   ├── complex-filters.md
│   ├── python.md
│   ├── javascript.md
│   └── ...
└── reference/           # Reference documentation
    ├── api-spec.md
    ├── changelog.md
    └── troubleshooting.md
```

## Building Documentation Locally

### Prerequisites

```bash
pip install -r docs/requirements.txt
```

### Development Server

Run the MkDocs development server with live reload:

```bash
mkdocs serve
```

The documentation will be available at http://localhost:8000

### Building Static Site

Build the static documentation site:

```bash
mkdocs build
```

The built site will be in the `site/` directory.

### Building with Docker

```bash
docker run --rm -it -v ${PWD}:/docs squidfunk/mkdocs-material build
```

## Key Features

### 1. Comprehensive Filtering Documentation

The documentation extensively covers all filtering capabilities:
- **15+ operators** with detailed examples
- **Field-specific filtering** for each object type
- **Complex query examples** for real-world scenarios
- **Performance optimization** tips

### 2. Interactive API Examples

- **cURL examples** for command-line usage
- **Python SDK** examples with classes
- **JavaScript** examples for web integration
- **Shell scripts** for automation

### 3. Endpoint Documentation

Each endpoint is documented with:
- **Request/response schemas**
- **All available filter fields**
- **Complete working examples**
- **Common use cases**
- **Performance tips**

### 4. Object Type Coverage

Detailed documentation for all object types:
- **Address Objects** (IP, FQDN, IP Range)
- **Service Objects** (TCP/UDP)
- **Security Rules** (Pre/Post rules)
- **NAT Rules**
- **Device Groups**
- **Templates**
- **Security Profiles**
- **And more...**

## Documentation Standards

### Writing Style

- Use clear, concise language
- Include practical examples
- Provide both simple and complex use cases
- Add performance considerations where relevant

### Code Examples

All code examples should:
- Be tested and working
- Include error handling where appropriate
- Follow language-specific best practices
- Include comments for clarity

### Formatting

- Use proper Markdown formatting
- Include tables for structured data
- Use admonitions for important notes
- Add syntax highlighting for code blocks

## Deployment

### GitHub Pages

The documentation is automatically deployed to GitHub Pages on push to main:

```yaml
# .github/workflows/docs.yml handles deployment
```

### Read the Docs

The documentation is also available on Read the Docs:
- Production: https://pan-config-viewer.readthedocs.io
- Latest: https://pan-config-viewer.readthedocs.io/en/latest/

### Manual Deployment

Deploy to a custom server:

```bash
mkdocs build
rsync -avz site/ user@server:/var/www/docs/
```

## Contributing

### Adding New Documentation

1. Create new `.md` files in appropriate directories
2. Update `mkdocs.yml` navigation if needed
3. Follow existing documentation patterns
4. Test locally with `mkdocs serve`
5. Submit PR with changes

### Updating Examples

1. Test all code examples
2. Ensure examples work with latest API version
3. Update response examples if API changes
4. Include error cases where appropriate

### Translations

To add translations:
1. Create language-specific directories (e.g., `docs/fr/`)
2. Translate content maintaining structure
3. Update `mkdocs.yml` with language configuration

## Search

The documentation includes full-text search powered by:
- MkDocs built-in search
- Algolia DocSearch (if configured)
- Read the Docs search

Search is optimized for:
- API endpoints
- Filter operators
- Object properties
- Code examples

## Analytics

Documentation usage is tracked via:
- Google Analytics (configured in mkdocs.yml)
- Read the Docs analytics
- GitHub Pages insights

## License

The documentation is licensed under the same license as the main project (Apache 2.0).

## Support

For documentation issues:
- Open an issue on GitHub
- Submit a PR with fixes
- Contact the documentation team

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Read the Docs](https://docs.readthedocs.io/)
- [API Documentation Best Practices](https://www.apimatic.io/blog/api-documentation-best-practices/)
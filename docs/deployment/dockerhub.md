# PAN-OS Configuration Viewer

[![Docker Pulls](https://img.shields.io/docker/pulls/fahadysf/pan-config-viewer)](https://hub.docker.com/r/fahadysf/pan-config-viewer)
[![Docker Image Size](https://img.shields.io/docker/image-size/fahadysf/pan-config-viewer)](https://hub.docker.com/r/fahadysf/pan-config-viewer)
[![GitHub](https://img.shields.io/github/license/fahadysf/pan-config-viewer)](https://github.com/fahadysf/pan-config-viewer)

A powerful web-based viewer and API for Palo Alto Networks Panorama configurations, providing instant search, filtering, and analysis capabilities for large-scale firewall deployments.

## 🚀 Quick Start

```bash
docker run -d \
  -p 8000:8000 \
  -v /path/to/your/configs:/app/config-files \
  fahadysf/pan-config-viewer:latest
```

Access the application at `http://localhost:8000`

## 📋 Features

### Core Capabilities
- **🔍 Instant Search**: Lightning-fast search across thousands of firewall objects
- **📊 Advanced Filtering**: Column-level filtering with multiple operators
- **📄 Pagination**: Efficient handling of large datasets with customizable page sizes
- **💾 Smart Caching**: ZODB-based caching for instant configuration loading
- **🎯 RESTful API**: Complete API with OpenAPI/Swagger documentation
- **🖥️ Modern UI**: React-based frontend with real-time updates

### Supported Objects
- **Network Objects**: Addresses, Address Groups
- **Services**: Service Objects, Service Groups  
- **Policies**: Security Rules, NAT Rules
- **Device Management**: Device Groups, Templates, Template Stacks
- **Security Profiles**: URL Filtering, Vulnerability Protection

## 🐳 Docker Configuration

### Basic Usage

```bash
# Run with default settings
docker run -d --name pan-viewer \
  -p 8000:8000 \
  -v $(pwd)/configs:/app/config-files \
  fahadysf/pan-config-viewer:latest
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | API server port | `8000` |
| `HOST` | API server host | `0.0.0.0` |
| `CACHE_DIR` | Cache directory path | `/app/cache` |
| `CONFIG_DIR` | Configuration files directory | `/app/config-files` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |

### Docker Compose

```yaml
version: '3.8'
services:
  pan-viewer:
    image: fahadysf/pan-config-viewer:latest
    ports:
      - "8000:8000"
    volumes:
      - ./config-files:/app/config-files
      - pan-cache:/app/cache
    environment:
      - LOG_LEVEL=INFO
    restart: unless-stopped

volumes:
  pan-cache:
```

## 📁 Volume Mounts

### Configuration Files
Mount your Panorama XML exports to `/app/config-files`:
```bash
-v /path/to/panorama/configs:/app/config-files
```

### Cache Persistence
For persistent caching between container restarts:
```bash
-v pan-cache:/app/cache
```

## 🔌 API Endpoints

The application provides a comprehensive REST API with the following key endpoints:

- `GET /api/v1/configs` - List available configurations
- `GET /api/v1/configs/{name}/addresses` - Get address objects
- `GET /api/v1/configs/{name}/services` - Get service objects
- `GET /api/v1/configs/{name}/security-policies` - Get security policies
- `GET /api/v1/configs/{name}/device-groups` - Get device groups

Full API documentation available at `http://localhost:8000/docs`

## 🛠️ Advanced Configuration

### Custom Cache Directory
```bash
docker run -d \
  -p 8000:8000 \
  -v /custom/cache/path:/app/cache \
  -v /path/to/configs:/app/config-files \
  fahadysf/pan-config-viewer:latest
```

### High Performance Settings
```bash
docker run -d \
  -p 8000:8000 \
  --cpus="4" \
  --memory="8g" \
  -v /path/to/configs:/app/config-files \
  -e LOG_LEVEL=WARNING \
  fahadysf/pan-config-viewer:latest
```

## 📊 Performance

- **Load Time**: < 2 seconds for 40,000+ objects
- **Search Response**: < 100ms for complex queries
- **Memory Usage**: ~500MB for typical Panorama configuration
- **Cache Efficiency**: 95%+ hit rate after initial load

## 🔒 Security

- Read-only access to configuration files
- No authentication required (deploy behind reverse proxy for production)
- No external dependencies or telemetry
- Runs as non-root user in container

## 📝 Requirements

- **Docker**: 20.10+ or Docker Desktop
- **Memory**: Minimum 2GB RAM recommended
- **Storage**: 100MB + size of configuration files
- **Panorama Configs**: XML exports from Panorama 10.x or 11.x

## 🤝 Support

- **Documentation**: [GitHub Wiki](https://github.com/fahadysf/pan-config-viewer/wiki)
- **Issues**: [GitHub Issues](https://github.com/fahadysf/pan-config-viewer/issues)
- **Source Code**: [GitHub Repository](https://github.com/fahadysf/pan-config-viewer)

## 📄 License

MIT License - See [LICENSE](https://github.com/fahadysf/pan-config-viewer/blob/main/LICENSE) for details

---

**Made with ❤️ for the PAN-OS community**
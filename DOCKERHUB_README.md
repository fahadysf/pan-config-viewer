# PAN-OS Configuration Viewer

[![Docker Pulls](https://img.shields.io/docker/pulls/fahadysf/pan-config-viewer)](https://hub.docker.com/r/fahadysf/pan-config-viewer)
[![Docker Image Size](https://img.shields.io/docker/image-size/fahadysf/pan-config-viewer)](https://hub.docker.com/r/fahadysf/pan-config-viewer)
[![GitHub](https://img.shields.io/github/license/fahadysf/pan-config-viewer)](https://github.com/fahadysf/pan-config-viewer)

A powerful web-based viewer and API for Palo Alto Networks Panorama and Firewall configurations, providing instant search, filtering, and analysis capabilities for large-scale firewall deployments.

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
- **⚡ Non-blocking Loading**: Async configuration parsing with loading status indicators

### Supported Objects
- **Network Objects**: Addresses, Address Groups
- **Services**: Service Objects, Service Groups  
- **Policies**: Security Rules (with full rule details)
- **Device Management**: Device Groups, Templates
- **Security Profiles**: URL Filtering, Vulnerability Protection
- **Firewall Support**: Both Panorama and standalone firewall configurations

## 📁 Configuration Files Directory

The application expects PAN-OS configuration XML files to be placed in the `/app/config-files` directory inside the container. Use Docker volumes to mount your local configuration directory.

### Supported Configuration Files
- **Panorama exports**: Full configuration exports from Panorama
- **Firewall exports**: Configuration exports from standalone firewalls
- **File format**: XML files (typically with `.xml` extension)
- **File naming**: Any descriptive name (e.g., `panorama-prod.xml`, `fw-branch-office.xml`)

### How Configuration Loading Works
1. On startup, the application scans `/app/config-files` for XML files
2. Each configuration is parsed asynchronously without blocking the web server
3. Parsed data is cached using ZODB for instant subsequent loads
4. The UI shows loading progress for each configuration
5. Configurations become available as soon as they're parsed

## 🐳 Docker Usage

### Basic Docker Run

```bash
# Create local directories for configs and cache
mkdir -p pan-configs pan-cache

# Place your XML configuration files in pan-configs/
cp your-panorama-export.xml pan-configs/

# Run the container
docker run -d --name pan-viewer \
  -p 8000:8000 \
  -v $(pwd)/pan-configs:/app/config-files \
  -v $(pwd)/pan-cache:/app/cache \
  fahadysf/pan-config-viewer:latest
```

### Docker Compose Setup

Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  pan-viewer:
    image: fahadysf/pan-config-viewer:latest
    container_name: pan-config-viewer
    ports:
      - "8000:8000"
    volumes:
      # Mount your configuration files directory
      - ./config-files:/app/config-files
      # Named volume for cache persistence
      - pan-cache:/app/cache
    environment:
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  # Named volume for cache persistence across container restarts
  pan-cache:
```

Then run:
```bash
# Create config directory and add your files
mkdir -p config-files
cp /path/to/your/*.xml config-files/

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

## 📂 Volume Mounts Explained

### `/app/config-files` - Configuration Files
**Purpose**: This is where you place your PAN-OS configuration XML files
```bash
-v /your/local/config/directory:/app/config-files
```

**Example directory structure**:
```
/your/local/config/directory/
├── panorama-production.xml
├── panorama-staging.xml
├── firewall-branch1.xml
└── firewall-branch2.xml
```

### `/app/cache` - Cache Directory
**Purpose**: Persistent storage for parsed configuration cache
```bash
-v /your/local/cache/directory:/app/cache
```
Or use a named volume:
```bash
-v pan-cache:/app/cache
```

**Benefits of cache persistence**:
- Instant loading of previously parsed configurations
- Survives container restarts
- Reduces CPU usage on subsequent loads

## 🔧 Cache Directory Permissions

The cache directory needs proper permissions for the container user (UID 1000).

### Option 1: Set permissions before running
```bash
mkdir -p pan-cache
chmod 777 pan-cache
```

### Option 2: Use named Docker volume (recommended)
Docker automatically handles permissions with named volumes:
```bash
docker volume create pan-cache
docker run -v pan-cache:/app/cache ...
```

### Option 3: Run without cache persistence
Simply omit the cache volume mount, but configurations will be re-parsed on each container restart:
```bash
docker run -d \
  -p 8000:8000 \
  -v /path/to/configs:/app/config-files \
  fahadysf/pan-config-viewer:latest
```

## 🌐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | API server port | `8000` |
| `HOST` | API server host | `0.0.0.0` |
| `CACHE_DIR` | Cache directory path | `/app/cache` |
| `CONFIG_DIR` | Configuration files directory | `/app/config-files` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |

## 🔌 API Endpoints

The application provides a comprehensive REST API:

### Core Endpoints
- `GET /api/v1/configs` - List available configurations
- `GET /api/v1/configs/{name}/addresses` - Get address objects
- `GET /api/v1/configs/{name}/address-groups` - Get address groups
- `GET /api/v1/configs/{name}/services` - Get service objects
- `GET /api/v1/configs/{name}/service-groups` - Get service groups
- `GET /api/v1/configs/{name}/security-policies` - Get security policies
- `GET /api/v1/configs/{name}/device-groups` - Get device groups
- `GET /api/v1/parsing-status` - Get parsing status for all configs

### Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI Schema: `http://localhost:8000/openapi.json`

## 🚀 Production Deployment

### Using Docker Compose for Production

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'
services:
  pan-viewer:
    image: fahadysf/pan-config-viewer:latest
    container_name: pan-config-viewer-prod
    ports:
      - "127.0.0.1:8000:8000"  # Bind only to localhost
    volumes:
      - /opt/pan-configs:/app/config-files:ro  # Read-only mount
      - pan-cache-prod:/app/cache
    environment:
      - LOG_LEVEL=WARNING
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

volumes:
  pan-cache-prod:
```

Run with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Reverse Proxy Configuration (Nginx)

```nginx
server {
    listen 443 ssl http2;
    server_name pan-viewer.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support for real-time updates
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 📊 Performance Optimization

### Large Configurations (>100MB XML files)
```bash
docker run -d \
  -p 8000:8000 \
  --cpus="4" \
  --memory="8g" \
  -v /path/to/configs:/app/config-files \
  -v pan-cache:/app/cache \
  -e LOG_LEVEL=WARNING \
  fahadysf/pan-config-viewer:latest
```

### Multiple Configurations
For setups with many configuration files:
1. Use cache persistence (critical for performance)
2. Allocate sufficient memory (2GB + 500MB per large config)
3. Consider SSD storage for cache directory

## 🔍 Troubleshooting

### Permission Denied Errors
```bash
ERROR:zodb_cache:Error checking cache validity: [Errno 13] Permission denied
```
**Solution**: Fix cache directory permissions or use a named volume

### Configuration Not Loading
1. Check file is valid XML: `xmllint --noout your-config.xml`
2. Verify file is in mounted directory: `docker exec pan-viewer ls /app/config-files`
3. Check logs: `docker logs pan-viewer`

### High Memory Usage
- Normal for large configurations (>40,000 objects)
- Use memory limits in production
- Cache persistence reduces memory pressure on restarts

### Slow Initial Load
- First-time parsing is CPU intensive
- Subsequent loads use cache (< 2 seconds)
- Check parsing status at `/api/v1/parsing-status`

## 🔒 Security Considerations

- **Read-only access**: Application only reads configuration files
- **No authentication**: Deploy behind reverse proxy with auth for production
- **Network isolation**: Bind to localhost only in production
- **Container security**: Runs as non-root user (UID 1000)
- **No telemetry**: No external connections or data collection

## 📝 System Requirements

- **Docker**: 20.10+ or Docker Desktop
- **Memory**: Minimum 2GB RAM (4GB+ recommended for large configs)
- **Storage**: 100MB for application + size of configs + cache
- **CPU**: 2+ cores recommended for faster parsing
- **Configuration Files**: XML exports from PAN-OS 10.x or 11.x

## 🤝 Support & Contributing

- **Documentation**: [GitHub Wiki](https://github.com/fahadysf/pan-config-viewer/wiki)
- **Issues**: [GitHub Issues](https://github.com/fahadysf/pan-config-viewer/issues)
- **Source Code**: [GitHub Repository](https://github.com/fahadysf/pan-config-viewer)
- **Docker Hub**: [fahadysf/pan-config-viewer](https://hub.docker.com/r/fahadysf/pan-config-viewer)

## 📄 License

MIT License - See [LICENSE](https://github.com/fahadysf/pan-config-viewer/blob/main/LICENSE) for details

---

**Made with ❤️ for the PAN-OS community**
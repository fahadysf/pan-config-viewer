# Docker Setup Guide

## Quick Start

1. **Fix cache permissions (required for ZODB persistence):**
   ```bash
   ./fix-cache-permissions.sh
   ```

2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   - Open http://localhost:8000 in your browser

## Cache Directory Permissions

The application uses ZODB for persistent caching of parsed configurations. The cache directory needs to be writable by the container user (UID 1000).

### Option 1: Use the fix script (recommended)
```bash
./fix-cache-permissions.sh
```

### Option 2: Manual fix
```bash
mkdir -p cache
chmod 777 cache
```

### Option 3: Disable cache persistence
If you don't need cache persistence between container restarts, you can remove the cache volume mount from docker-compose.yml:

```yaml
volumes:
  # - ./cache:/app/cache  # Comment out or remove this line
```

## Troubleshooting

### Permission Denied Errors
If you see errors like:
```
ERROR:zodb_cache:Error checking cache validity: [Errno 13] Permission denied
```

This means the cache directory doesn't have proper permissions. Run:
```bash
./fix-cache-permissions.sh
docker-compose restart
```

### Cache Not Persisting
If cache isn't persisting between container restarts:
1. Ensure the cache volume is mounted in docker-compose.yml
2. Check that the cache directory has proper permissions
3. Verify ZODB files are being created: `ls -la cache/`

## Production Deployment

For production, use docker-compose.prod.yml:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

You can customize the cache directory location:
```bash
CACHE_DIR=/path/to/cache docker-compose -f docker-compose.prod.yml up -d
```
#!/bin/sh
set -e

# Ensure cache directory has correct permissions
if [ -d "/app/cache" ]; then
    # Check if we can write to the cache directory
    if ! touch /app/cache/.test 2>/dev/null; then
        echo "Warning: Cache directory is not writable. ZODB caching will be disabled."
        echo "To fix this, ensure the cache directory is writable by UID 1000"
    else
        rm -f /app/cache/.test
        echo "Cache directory is writable. ZODB caching enabled."
    fi
fi

# Execute the main command
exec "$@"
#!/bin/bash
# Script to fix cache directory permissions for Docker

CACHE_DIR="${1:-./cache}"

echo "Fixing permissions for cache directory: $CACHE_DIR"

# Create cache directory if it doesn't exist
mkdir -p "$CACHE_DIR"

# Set permissions to allow container user (UID 1000) to write
# Using 777 for simplicity, but you could use 775 with proper group setup
chmod 777 "$CACHE_DIR"

# If running on macOS or Linux with different user
if [ "$(uname)" == "Darwin" ]; then
    echo "macOS detected - permissions set to 777"
elif [ "$(uname)" == "Linux" ]; then
    # On Linux, you might want to set ownership to UID 1000
    if [ "$EUID" -eq 0 ]; then
        chown 1000:1000 "$CACHE_DIR"
        echo "Linux detected - ownership set to UID 1000"
    else
        echo "Linux detected - run as root to set ownership, or permissions set to 777"
    fi
fi

echo "Cache directory permissions fixed"
echo "You can now run: docker-compose up"
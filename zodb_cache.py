"""
ZODB-based persistent cache for PAN-OS configuration parser.
Uses MD5 hashing to detect config changes and caches parsed objects.
"""

import os
import hashlib
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import pickle

import ZODB
from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
import transaction
from persistent import Persistent
from persistent.mapping import PersistentMapping
from persistent.list import PersistentList

from models import AddressObject, AddressGroup, ServiceObject, ServiceGroup, SecurityRule

logger = logging.getLogger(__name__)

class CachedConfig(Persistent):
    """Persistent container for cached configuration data"""
    
    def __init__(self, config_name: str, md5_hash: str):
        self.config_name = config_name
        self.md5_hash = md5_hash
        self.parse_timestamp = time.time()
        self.data = PersistentMapping()
        
    def set_data(self, key: str, value: Any):
        """Store data in the cache"""
        # Convert regular lists to PersistentList for ZODB
        if isinstance(value, list):
            # Store the actual Python objects, not PersistentList
            # We'll serialize them properly
            self.data[key] = value
        else:
            self.data[key] = value
    
    def get_data(self, key: str) -> Any:
        """Retrieve data from the cache"""
        return self.data.get(key)
    
    def has_data(self, key: str) -> bool:
        """Check if data exists in the cache"""
        return key in self.data


class ZODBCache:
    """ZODB-based cache manager for configuration data"""
    
    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.connections = {}
        self.databases = {}
        
    def _get_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of a file"""
        md5_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(8192), b''):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    
    def _get_cache_path(self, config_name: str) -> Path:
        """Get the cache file path for a configuration"""
        return self.cache_dir / f"{config_name}.zodb"
    
    def _open_database(self, config_name: str) -> Tuple[DB, Any]:
        """Open or create a ZODB database for a configuration"""
        cache_path = self._get_cache_path(config_name)
        
        # Reuse existing connection if available
        if config_name in self.databases:
            db = self.databases[config_name]
            connection = self.connections[config_name]
        else:
            storage = FileStorage(str(cache_path))
            db = DB(storage)
            connection = db.open()
            self.databases[config_name] = db
            self.connections[config_name] = connection
            
        return db, connection
    
    def is_cache_valid(self, config_name: str, xml_path: str) -> bool:
        """Check if cached data is valid for the current XML file"""
        try:
            # Calculate current file hash
            current_hash = self._get_file_hash(xml_path)
            
            # Check if cache file exists
            cache_path = self._get_cache_path(config_name)
            if not cache_path.exists():
                logger.info(f"No cache found for {config_name}")
                return False
            
            # Open the database and check the hash
            db, connection = self._open_database(config_name)
            root = connection.root()
            
            if 'config' not in root:
                logger.info(f"Cache file exists but no config data for {config_name}")
                return False
            
            cached_config = root['config']
            if cached_config.md5_hash != current_hash:
                logger.info(f"Cache invalidated for {config_name}: MD5 mismatch")
                logger.info(f"  Cached MD5: {cached_config.md5_hash}")
                logger.info(f"  Current MD5: {current_hash}")
                return False
            
            logger.info(f"Valid cache found for {config_name} (MD5: {current_hash[:8]}...)")
            return True
            
        except Exception as e:
            logger.error(f"Error checking cache validity: {e}")
            return False
    
    def load_from_cache(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Load cached configuration data"""
        try:
            db, connection = self._open_database(config_name)
            root = connection.root()
            
            if 'config' not in root:
                return None
            
            cached_config = root['config']
            
            # Return all cached data
            result = {}
            for key in cached_config.data.keys():
                result[key] = cached_config.get_data(key)
            
            logger.info(f"Loaded {len(result)} object types from cache for {config_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error loading from cache: {e}")
            return None
    
    def save_to_cache(self, config_name: str, xml_path: str, data: Dict[str, Any]):
        """Save configuration data to cache"""
        try:
            # Calculate file hash
            md5_hash = self._get_file_hash(xml_path)
            
            # Open or create database
            db, connection = self._open_database(config_name)
            root = connection.root()
            
            # Create new cached config
            cached_config = CachedConfig(config_name, md5_hash)
            
            # Store all data
            for key, value in data.items():
                cached_config.set_data(key, value)
            
            # Save to database
            root['config'] = cached_config
            transaction.commit()
            
            logger.info(f"Saved {len(data)} object types to cache for {config_name} (MD5: {md5_hash[:8]}...)")
            
            # Log cache file size
            cache_path = self._get_cache_path(config_name)
            size_mb = cache_path.stat().st_size / (1024 * 1024)
            logger.info(f"Cache file size: {size_mb:.2f} MB")
            
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
            transaction.abort()
    
    def clear_cache(self, config_name: str):
        """Clear cache for a specific configuration"""
        try:
            # Close any open connections
            if config_name in self.connections:
                self.connections[config_name].close()
                del self.connections[config_name]
            
            if config_name in self.databases:
                self.databases[config_name].close()
                del self.databases[config_name]
            
            # Delete the cache file
            cache_path = self._get_cache_path(config_name)
            if cache_path.exists():
                cache_path.unlink()
                logger.info(f"Cleared cache for {config_name}")
                
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    def get_cache_stats(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Get statistics about cached data"""
        try:
            cache_path = self._get_cache_path(config_name)
            if not cache_path.exists():
                return None
            
            db, connection = self._open_database(config_name)
            root = connection.root()
            
            if 'config' not in root:
                return None
            
            cached_config = root['config']
            
            stats = {
                'config_name': cached_config.config_name,
                'md5_hash': cached_config.md5_hash,
                'parse_timestamp': cached_config.parse_timestamp,
                'cache_file_size': cache_path.stat().st_size,
                'object_types': list(cached_config.data.keys()),
                'object_counts': {}
            }
            
            # Count objects of each type
            for key in cached_config.data.keys():
                data = cached_config.get_data(key)
                if isinstance(data, (list, PersistentList)):
                    stats['object_counts'][key] = len(data)
                else:
                    stats['object_counts'][key] = 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return None
    
    def close_all(self):
        """Close all open database connections"""
        for connection in self.connections.values():
            connection.close()
        for db in self.databases.values():
            db.close()
        self.connections.clear()
        self.databases.clear()


# Global cache instance
_cache_instance = None

def get_zodb_cache() -> ZODBCache:
    """Get or create the global ZODB cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = ZODBCache()
    return _cache_instance
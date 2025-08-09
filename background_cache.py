"""
Background pre-parsing and caching service for large configuration files
"""
import asyncio
import threading
import time
import logging
from typing import Dict, List, Any, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
import traceback

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class CacheStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class CacheProgress:
    """Track caching progress for each object type"""
    object_type: str
    status: CacheStatus = CacheStatus.NOT_STARTED
    total_items: int = 0
    cached_items: int = 0
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    @property
    def progress_percentage(self) -> float:
        if self.total_items == 0:
            return 0.0
        return (self.cached_items / self.total_items) * 100
    
    @property
    def elapsed_time(self) -> float:
        if not self.start_time:
            return 0.0
        end = self.end_time or time.time()
        return end - self.start_time

class BackgroundCacheManager:
    """Manages background pre-parsing and caching of configuration objects"""
    
    BATCH_SIZE = 1000  # Process objects in batches of 1000
    MAX_WORKERS = 4    # Maximum parallel workers
    
    # Object types to cache with their retrieval methods
    OBJECT_TYPES = [
        'addresses',
        'address_groups',
        'services',
        'service_groups',
        'device_groups',
        'security_rules',
        'nat_rules',
        'templates',
        'template_stacks',
        'vulnerability_profiles',
        'antivirus_profiles',
        'spyware_profiles',
        'url_filtering_profiles',
        'file_blocking_profiles',
        'wildfire_profiles',
        'data_filtering_profiles',
        'security_profile_groups',
        'zone_protection_profiles',
        'log_settings',
        'schedules'
    ]
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.progress: Dict[str, CacheProgress] = {}
        self.parsers: Dict[str, Any] = {}  # Config name -> parser instance
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=self.MAX_WORKERS)
        self._tasks: Dict[str, Set[asyncio.Future]] = {}
        self._stop_event = threading.Event()
        self._ready_configs: Set[str] = set()  # Track fully cached configs
        
        # Initialize progress tracking
        for obj_type in self.OBJECT_TYPES:
            self.progress[obj_type] = CacheProgress(object_type=obj_type)
    
    def mark_config_ready(self, config_name: str) -> None:
        """Mark a configuration as fully cached and ready"""
        with self._lock:
            self._ready_configs.add(config_name)
            logger.info(f"Configuration '{config_name}' marked as ready")
    
    def is_config_ready(self, config_name: str) -> bool:
        """Check if a configuration is fully cached"""
        with self._lock:
            return config_name in self._ready_configs
    
    def start_caching(self, config_name: str, parser) -> None:
        """Start background caching for a configuration"""
        logger.info(f"Starting background caching for config: {config_name}")
        
        # Store parser reference
        with self._lock:
            self.parsers[config_name] = parser
            if config_name not in self._tasks:
                self._tasks[config_name] = set()
        
        # Start caching in background thread
        thread = threading.Thread(
            target=self._run_caching,
            args=(config_name, parser),
            daemon=True
        )
        thread.start()
    
    def _run_caching(self, config_name: str, parser) -> None:
        """Run caching process in background"""
        try:
            # Create tasks for each object type
            futures = []
            
            for obj_type in self.OBJECT_TYPES:
                future = self._executor.submit(
                    self._cache_object_type,
                    config_name,
                    parser,
                    obj_type
                )
                futures.append(future)
            
            # Wait for all tasks to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error in caching task: {e}")
                    
        except Exception as e:
            logger.error(f"Error in background caching: {e}")
    
    def _cache_object_type(self, config_name: str, parser, obj_type: str) -> None:
        """Cache a specific object type in batches"""
        cache_key = f"{config_name}:{obj_type}"
        progress = self.progress[obj_type]
        
        try:
            logger.info(f"Starting to cache {obj_type} for {config_name}")
            progress.status = CacheStatus.IN_PROGRESS
            progress.start_time = time.time()
            
            # Get retrieval method for this object type
            method_name = f"get_all_{obj_type}"
            if obj_type == 'address_groups':
                method_name = "get_address_groups"
            elif obj_type == 'service_groups':
                method_name = "get_service_groups"
            elif obj_type == 'device_groups':
                method_name = "get_device_group_summaries"
            elif obj_type == 'security_rules':
                method_name = "get_all_security_rules"
            elif obj_type == 'nat_rules':
                method_name = "get_all_nat_rules"
            elif obj_type == 'template_stacks':
                method_name = "get_template_stacks"
            elif obj_type == 'vulnerability_profiles':
                method_name = "get_vulnerability_profiles"
            elif obj_type == 'antivirus_profiles':
                method_name = "get_antivirus_profiles"
            elif obj_type == 'spyware_profiles':
                method_name = "get_spyware_profiles"
            elif obj_type == 'url_filtering_profiles':
                method_name = "get_url_filtering_profiles"
            elif obj_type == 'file_blocking_profiles':
                method_name = "get_file_blocking_profiles"
            elif obj_type == 'wildfire_profiles':
                method_name = "get_wildfire_analysis_profiles"
            elif obj_type == 'data_filtering_profiles':
                method_name = "get_data_filtering_profiles"
            elif obj_type == 'security_profile_groups':
                method_name = "get_security_profile_groups"
            elif obj_type == 'zone_protection_profiles':
                method_name = "get_zone_protection_profiles"
            elif obj_type == 'log_settings':
                method_name = "get_log_settings"
            
            # Check if method exists
            if not hasattr(parser, method_name):
                logger.warning(f"Parser doesn't have method {method_name}")
                progress.status = CacheStatus.COMPLETED
                progress.end_time = time.time()
                return
            
            # Get all objects
            method = getattr(parser, method_name)
            all_objects = method()
            
            if not all_objects:
                all_objects = []
            
            progress.total_items = len(all_objects)
            logger.info(f"Found {progress.total_items} {obj_type} to cache")
            
            # Process in batches
            batches = []
            for i in range(0, len(all_objects), self.BATCH_SIZE):
                batch = all_objects[i:i + self.BATCH_SIZE]
                batches.append(batch)
            
            # Cache each batch
            with self._lock:
                if cache_key not in self.cache:
                    self.cache[cache_key] = {
                        'data': [],
                        'batches': {},
                        'total': len(all_objects)
                    }
            
            for batch_idx, batch in enumerate(batches):
                if self._stop_event.is_set():
                    break
                
                # Convert objects to dictionaries for caching
                batch_data = []
                for obj in batch:
                    try:
                        if hasattr(obj, 'dict'):
                            # Use by_alias=True to ensure field names use hyphens
                            batch_data.append(obj.dict(by_alias=True))
                        elif hasattr(obj, '__dict__'):
                            batch_data.append(obj.__dict__)
                        else:
                            batch_data.append(str(obj))
                    except Exception as e:
                        logger.error(f"Error serializing object: {e}")
                        continue
                
                # Store batch in cache
                with self._lock:
                    self.cache[cache_key]['batches'][batch_idx] = batch_data
                    self.cache[cache_key]['data'].extend(batch_data)
                    progress.cached_items += len(batch_data)
                
                logger.debug(f"Cached batch {batch_idx + 1}/{len(batches)} of {obj_type} "
                           f"({progress.cached_items}/{progress.total_items})")
                
                # Small delay to prevent overwhelming the system
                time.sleep(0.01)
            
            progress.status = CacheStatus.COMPLETED
            progress.end_time = time.time()
            logger.info(f"Completed caching {obj_type}: {progress.cached_items} items in "
                       f"{progress.elapsed_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error caching {obj_type}: {e}\n{traceback.format_exc()}")
            progress.status = CacheStatus.FAILED
            progress.error = str(e)
            progress.end_time = time.time()
    
    def get_cached_data(self, config_name: str, obj_type: str, 
                       page: int = 1, page_size: int = 100) -> Optional[Dict[str, Any]]:
        """Get cached data for a specific object type with pagination"""
        cache_key = f"{config_name}:{obj_type}"
        
        with self._lock:
            if cache_key not in self.cache:
                return None
            
            cached = self.cache[cache_key]
            data = cached.get('data', [])
            
            if not data:
                return None
            
            # Apply pagination
            total_items = len(data)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            items = data[start_idx:end_idx]
            
            return {
                'items': items,
                'total_items': total_items,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_items + page_size - 1) // page_size,
                'has_next': end_idx < total_items,
                'has_previous': page > 1,
                'from_cache': True
            }
    
    def get_filtered_cached_data(self, config_name: str, obj_type: str,
                                filters: Dict[str, Any],
                                page: int = 1, page_size: int = 100) -> Optional[Dict[str, Any]]:
        """Get filtered cached data with pagination - optimized for performance"""
        cache_key = f"{config_name}:{obj_type}"
        
        with self._lock:
            if cache_key not in self.cache:
                return None
            
            cached = self.cache[cache_key]
            data = cached.get('data', [])
            
            if not data:
                return None
            
            # Debug logging
            if filters.get('advanced'):
                logger.debug(f"Advanced filters received: {filters.get('advanced')}")
            
            # Apply filters efficiently using list comprehension
            filtered_items = data
            
            # Location filter (for addresses)
            if obj_type == 'addresses' and filters.get('location'):
                location = filters['location']
                if location == "shared":
                    filtered_items = [a for a in filtered_items if not a.get('parent-device-group') 
                                     and not a.get('parent-template') and not a.get('parent-vsys')]
                elif location == "device-group":
                    filtered_items = [a for a in filtered_items if a.get('parent-device-group')]
                elif location == "template":
                    filtered_items = [a for a in filtered_items if a.get('parent-template')]
                elif location == "vsys":
                    filtered_items = [a for a in filtered_items if a.get('parent-vsys')]
            
            # Name filter
            if filters.get('name'):
                name_lower = filters['name'].lower()
                filtered_items = [item for item in filtered_items 
                                 if name_lower in item.get('name', '').lower()]
            
            # Tag filter
            if filters.get('tag'):
                tag = filters['tag']
                filtered_items = [item for item in filtered_items 
                                 if item.get('tag') and tag in item.get('tag')]
            
            # Apply advanced filters if present
            advanced_filters = filters.get('advanced', {})
            if advanced_filters:
                # Convert cached data to proper model objects for filtering
                if obj_type == 'addresses':
                    from models import AddressObject
                    from filtering import apply_filters, ADDRESS_FILTERS
                    
                    # Convert cached dictionaries to AddressObject instances
                    address_objects = []
                    logger.debug(f"Reconstructing {len(filtered_items)} items to AddressObject")
                    for item in filtered_items:
                        try:
                            # Create AddressObject from cached data
                            addr_data = {
                                'name': item.get('name'),
                                'description': item.get('description'),
                                'tag': item.get('tag'),
                                'xpath': item.get('xpath'),
                                'parent_device_group': item.get('parent-device-group'),
                                'parent_template': item.get('parent-template'),
                                'parent_vsys': item.get('parent-vsys')
                            }
                            
                            # Add type-specific fields
                            if item.get('ip-netmask'):
                                addr_data['ip_netmask'] = item.get('ip-netmask')
                            if item.get('ip-range'):
                                addr_data['ip_range'] = item.get('ip-range')
                            if item.get('fqdn'):
                                addr_data['fqdn'] = item.get('fqdn')
                            
                            addr_obj = AddressObject(**addr_data)
                            address_objects.append(addr_obj)
                        except Exception as e:
                            # Log the error for debugging
                            logger.error(f"Failed to reconstruct AddressObject for {item.get('name')}: {e}")
                            continue
                    
                    # Apply advanced filters to objects
                    logger.debug(f"Applying filters to {len(address_objects)} reconstructed objects")
                    filtered_objects = apply_filters(address_objects, advanced_filters, ADDRESS_FILTERS)
                    logger.debug(f"Filter result: {len(filtered_objects)} objects matched")
                    
                    # Convert back to dictionary format for caching consistency
                    filtered_items = []
                    for obj in filtered_objects:
                        item_dict = {
                            'name': obj.name,
                            'description': obj.description,
                            'tag': obj.tag,
                            'xpath': obj.xpath,
                            'parent-device-group': obj.parent_device_group,
                            'parent-template': obj.parent_template,
                            'parent-vsys': obj.parent_vsys,
                            'type': obj.type.value if obj.type else None
                        }
                        
                        # Add type-specific fields
                        if obj.ip_netmask:
                            item_dict['ip-netmask'] = obj.ip_netmask
                        if obj.ip_range:
                            item_dict['ip-range'] = obj.ip_range
                        if obj.fqdn:
                            item_dict['fqdn'] = obj.fqdn
                            
                        filtered_items.append(item_dict)
            
            # Apply pagination to filtered results
            total_items = len(filtered_items)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_items = filtered_items[start_idx:end_idx]
            
            return {
                'items': paginated_items,
                'total_items': total_items,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_items + page_size - 1) // page_size,
                'has_next': end_idx < total_items,
                'has_previous': page > 1,
                'from_cache': True
            }
    
    def is_cached(self, config_name: str, obj_type: str) -> bool:
        """Check if data is cached for a specific object type"""
        cache_key = f"{config_name}:{obj_type}"
        with self._lock:
            return cache_key in self.cache and len(self.cache[cache_key].get('data', [])) > 0
    
    def get_cache_status(self, config_name: str) -> Dict[str, Any]:
        """Get caching status for all object types"""
        status = {}
        total_items = 0
        cached_items = 0
        
        for obj_type in self.OBJECT_TYPES:
            progress = self.progress[obj_type]
            cache_key = f"{config_name}:{obj_type}"
            
            is_cached = self.is_cached(config_name, obj_type)
            
            status[obj_type] = {
                'status': progress.status.value,
                'total_items': progress.total_items,
                'cached_items': progress.cached_items,
                'progress': progress.progress_percentage,
                'elapsed_time': progress.elapsed_time,
                'is_cached': is_cached,
                'error': progress.error
            }
            
            total_items += progress.total_items
            cached_items += progress.cached_items
        
        overall_progress = (cached_items / total_items * 100) if total_items > 0 else 0
        
        return {
            'config': config_name,
            'overall_progress': overall_progress,
            'total_items': total_items,
            'cached_items': cached_items,
            'object_types': status
        }
    
    def clear_cache(self, config_name: Optional[str] = None) -> None:
        """Clear cache for a specific config or all configs"""
        with self._lock:
            if config_name:
                # Clear specific config
                keys_to_remove = [k for k in self.cache.keys() if k.startswith(f"{config_name}:")]
                for key in keys_to_remove:
                    del self.cache[key]
                
                # Reset progress for this config
                for progress in self.progress.values():
                    progress.status = CacheStatus.NOT_STARTED
                    progress.cached_items = 0
                    progress.total_items = 0
                    progress.error = None
                    progress.start_time = None
                    progress.end_time = None
            else:
                # Clear all cache
                self.cache.clear()
                
                # Reset all progress
                for obj_type in self.OBJECT_TYPES:
                    self.progress[obj_type] = CacheProgress(object_type=obj_type)
    
    def stop(self):
        """Stop background caching"""
        self._stop_event.set()
        self._executor.shutdown(wait=False)

# Global instance
background_cache = BackgroundCacheManager()
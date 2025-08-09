"""
Async cache manager for handling lazy loading of configuration data
"""
import asyncio
import time
import uuid
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class CacheTask:
    task_id: str
    status: TaskStatus
    config_name: str
    resource_type: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    data: Optional[Any] = None
    error: Optional[str] = None
    progress: int = 0  # Progress percentage
    
    @property
    def is_expired(self) -> bool:
        """Check if task has expired (older than 5 minutes)"""
        return datetime.now() - self.created_at > timedelta(minutes=5)

class AsyncCacheManager:
    """Manages async loading and caching of configuration data"""
    
    def __init__(self):
        self.tasks: Dict[str, CacheTask] = {}
        self.cache: Dict[str, Any] = {}  # Cache key -> data
        self._lock = threading.Lock()
        self._cleanup_interval = 300  # Clean up expired tasks every 5 minutes
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Start background thread to clean up expired tasks"""
        def cleanup():
            while True:
                time.sleep(self._cleanup_interval)
                self._cleanup_expired_tasks()
        
        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()
    
    def _cleanup_expired_tasks(self):
        """Remove expired tasks from memory"""
        with self._lock:
            expired_ids = [
                task_id for task_id, task in self.tasks.items()
                if task.is_expired
            ]
            for task_id in expired_ids:
                del self.tasks[task_id]
    
    def create_task(self, config_name: str, resource_type: str) -> str:
        """Create a new loading task"""
        task_id = str(uuid.uuid4())
        task = CacheTask(
            task_id=task_id,
            status=TaskStatus.PENDING,
            config_name=config_name,
            resource_type=resource_type,
            created_at=datetime.now()
        )
        
        with self._lock:
            self.tasks[task_id] = task
        
        return task_id
    
    def update_task_status(
        self, 
        task_id: str, 
        status: TaskStatus,
        data: Optional[Any] = None,
        error: Optional[str] = None,
        progress: Optional[int] = None
    ):
        """Update task status and data"""
        with self._lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = status
                
                if data is not None:
                    task.data = data
                
                if error is not None:
                    task.error = error
                
                if progress is not None:
                    task.progress = progress
                
                if status == TaskStatus.COMPLETED:
                    task.completed_at = datetime.now()
                    # Store in cache
                    cache_key = f"{task.config_name}:{task.resource_type}"
                    self.cache[cache_key] = data
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current task status"""
        with self._lock:
            if task_id not in self.tasks:
                return None
            
            task = self.tasks[task_id]
            return {
                "task_id": task.task_id,
                "status": task.status.value,
                "progress": task.progress,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "error": task.error,
                "has_data": task.data is not None
            }
    
    def get_task_data(self, task_id: str) -> Optional[Any]:
        """Get task data if completed"""
        with self._lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                if task.status == TaskStatus.COMPLETED:
                    return task.data
        return None
    
    def get_cached_data(self, config_name: str, resource_type: str) -> Optional[Any]:
        """Get data from cache if available"""
        cache_key = f"{config_name}:{resource_type}"
        with self._lock:
            return self.cache.get(cache_key)
    
    def invalidate_cache(self, config_name: Optional[str] = None):
        """Invalidate cache for a specific config or all configs"""
        with self._lock:
            if config_name:
                # Remove all cache entries for this config
                keys_to_remove = [
                    key for key in self.cache.keys()
                    if key.startswith(f"{config_name}:")
                ]
                for key in keys_to_remove:
                    del self.cache[key]
            else:
                # Clear all cache
                self.cache.clear()
    
    async def process_task_async(
        self, 
        task_id: str,
        loader_func,
        *args,
        **kwargs
    ):
        """Process a task asynchronously"""
        try:
            # Update status to processing
            self.update_task_status(task_id, TaskStatus.PROCESSING, progress=10)
            
            # Run the loader function in a thread pool
            loop = asyncio.get_event_loop()
            
            # Simulate progress updates
            async def update_progress():
                for i in range(20, 100, 20):
                    await asyncio.sleep(0.5)
                    self.update_task_status(task_id, TaskStatus.PROCESSING, progress=i)
            
            # Start progress updates
            progress_task = asyncio.create_task(update_progress())
            
            # Execute the loader function
            result = await loop.run_in_executor(None, loader_func, *args, **kwargs)
            
            # Cancel progress updates
            progress_task.cancel()
            
            # Update task with result
            self.update_task_status(
                task_id, 
                TaskStatus.COMPLETED, 
                data=result,
                progress=100
            )
            
        except Exception as e:
            self.update_task_status(
                task_id,
                TaskStatus.FAILED,
                error=str(e)
            )

# Global instance
cache_manager = AsyncCacheManager()
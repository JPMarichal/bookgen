"""
Redis cache implementation for performance optimization.

Provides caching for embeddings, validation results, and frequently
accessed data to improve system performance.
"""
import json
import logging
import hashlib
from typing import Optional, Any, Dict, List
from functools import wraps
import redis
import os

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Redis-based caching system for performance optimization.
    
    Features:
    - Caching for embeddings, validation results, and frequent queries
    - Configurable TTL (time-to-live)
    - Automatic serialization/deserialization
    - Connection pooling
    """
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        db: int = None,
        password: str = None,
        max_connections: int = 50,
        socket_timeout: int = 5,
        socket_connect_timeout: int = 5,
    ):
        """
        Initialize Redis cache.
        
        Args:
            host: Redis host (default from env REDIS_HOST or 'localhost')
            port: Redis port (default from env REDIS_PORT or 6379)
            db: Redis database number (default from env REDIS_DB or 0)
            password: Redis password (default from env REDIS_PASSWORD)
            max_connections: Maximum connections in pool
            socket_timeout: Socket timeout in seconds
            socket_connect_timeout: Socket connect timeout in seconds
        """
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = port or int(os.getenv("REDIS_PORT", "6379"))
        self.db = db or int(os.getenv("REDIS_DB", "0"))
        self.password = password or os.getenv("REDIS_PASSWORD")
        
        # Create connection pool
        self.pool = redis.ConnectionPool(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            max_connections=max_connections,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            decode_responses=True,
        )
        
        self.client = redis.Redis(connection_pool=self.pool)
        self._hits = 0
        self._misses = 0
        
        logger.info(f"Redis cache initialized: {self.host}:{self.port}/{self.db}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            value = self.client.get(key)
            if value is not None:
                self._hits += 1
                return json.loads(value)
            self._misses += 1
            return None
        except redis.RedisError as e:
            logger.error(f"Redis get error for key {key}: {e}")
            self._misses += 1
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time-to-live in seconds (default 1 hour)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            serialized = json.dumps(value)
            self.client.setex(key, ttl, serialized)
            return True
        except (redis.RedisError, TypeError, ValueError) as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted, False otherwise
        """
        try:
            return self.client.delete(key) > 0
        except redis.RedisError as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists, False otherwise
        """
        try:
            return self.client.exists(key) > 0
        except redis.RedisError as e:
            logger.error(f"Redis exists error for key {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """
        Clear all keys in current database.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.flushdb()
            logger.info(f"Cleared Redis database {self.db}")
            return True
        except redis.RedisError as e:
            logger.error(f"Redis clear error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._hits + self._misses
        hit_ratio = self._hits / total_requests if total_requests > 0 else 0.0
        
        return {
            'hits': self._hits,
            'misses': self._misses,
            'total_requests': total_requests,
            'hit_ratio': hit_ratio,
        }
    
    def reset_stats(self):
        """Reset cache statistics"""
        self._hits = 0
        self._misses = 0
    
    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values from cache.
        
        Args:
            keys: List of cache keys
            
        Returns:
            Dictionary mapping keys to values (only existing keys)
        """
        try:
            pipeline = self.client.pipeline()
            for key in keys:
                pipeline.get(key)
            values = pipeline.execute()
            
            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    self._hits += 1
                    result[key] = json.loads(value)
                else:
                    self._misses += 1
            
            return result
        except redis.RedisError as e:
            logger.error(f"Redis get_many error: {e}")
            self._misses += len(keys)
            return {}
    
    def set_many(
        self,
        mapping: Dict[str, Any],
        ttl: int = 3600
    ) -> bool:
        """
        Set multiple values in cache.
        
        Args:
            mapping: Dictionary of key-value pairs
            ttl: Time-to-live in seconds
            
        Returns:
            True if all successful, False otherwise
        """
        try:
            pipeline = self.client.pipeline()
            for key, value in mapping.items():
                serialized = json.dumps(value)
                pipeline.setex(key, ttl, serialized)
            pipeline.execute()
            return True
        except (redis.RedisError, TypeError, ValueError) as e:
            logger.error(f"Redis set_many error: {e}")
            return False
    
    def close(self):
        """Close Redis connection"""
        self.pool.disconnect()
        logger.info("Redis cache connection closed")


# Global cache instance
_cache_instance: Optional[RedisCache] = None


def get_cache() -> RedisCache:
    """
    Get global cache instance (singleton pattern).
    
    Returns:
        RedisCache instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance


def cache_key(*args, prefix: str = "bookgen") -> str:
    """
    Generate a cache key from arguments.
    
    Args:
        *args: Arguments to include in key
        prefix: Key prefix
        
    Returns:
        Cache key string
    """
    key_parts = [prefix] + [str(arg) for arg in args]
    key_string = ":".join(key_parts)
    # Hash long keys to avoid Redis key length limits
    if len(key_string) > 200:
        hash_value = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{hash_value}"
    return key_string


def cached(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache key
        
    Example:
        @cached(ttl=1800, key_prefix="validation")
        def validate_source(url: str):
            # Expensive validation logic
            return result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache = get_cache()
            key = cache_key(
                key_prefix or func.__name__,
                *args,
                *[f"{k}={v}" for k, v in sorted(kwargs.items())]
            )
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return result
            
            # Cache miss - execute function
            logger.debug(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(key, result, ttl=ttl)
            
            return result
        return wrapper
    return decorator

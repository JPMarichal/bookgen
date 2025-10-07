"""
Cache module for performance optimization.
"""
from .redis_cache import (
    RedisCache,
    get_cache,
    cache_key,
    cached,
)

__all__ = [
    'RedisCache',
    'get_cache',
    'cache_key',
    'cached',
]

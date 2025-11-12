"""Caching utilities for API calls."""

import time
import hashlib
import json
from typing import Any, Callable, Optional
from functools import wraps
from collections import OrderedDict

from .config import settings


class TTLCache:
    """Time-to-live cache with maximum size limit."""

    def __init__(self, max_size: int = 100, ttl: int = 3600):
        """
        Initialize TTL cache.

        Args:
            max_size: Maximum number of items to cache
            ttl: Time-to-live in seconds
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        self.timestamps = {}

    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired."""
        if key not in self.timestamps:
            return True
        return time.time() - self.timestamps[key] > self.ttl

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key in self.cache and not self._is_expired(key):
            # Move to end (mark as recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        elif key in self.cache:
            # Remove expired entry
            del self.cache[key]
            del self.timestamps[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        # If key exists, move to end
        if key in self.cache:
            self.cache.move_to_end(key)

        self.cache[key] = value
        self.timestamps[key] = time.time()

        # Evict oldest if cache is full
        if len(self.cache) > self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.timestamps.clear()

    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)


# Global cache instances
_stock_price_cache = TTLCache(max_size=settings.CACHE_MAX_SIZE, ttl=settings.CACHE_TTL)
_financials_cache = TTLCache(max_size=settings.CACHE_MAX_SIZE, ttl=settings.CACHE_TTL * 24)  # Longer TTL for financials
_technical_cache = TTLCache(max_size=settings.CACHE_MAX_SIZE, ttl=settings.CACHE_TTL)


def _make_cache_key(*args, **kwargs) -> str:
    """
    Create a cache key from function arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Hash of arguments as cache key
    """
    key_data = {
        'args': args,
        'kwargs': kwargs
    }
    key_json = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_json.encode()).hexdigest()


def cached(cache: TTLCache):
    """
    Decorator to cache function results.

    Args:
        cache: TTLCache instance to use

    Returns:
        Decorated function with caching
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{_make_cache_key(*args, **kwargs)}"

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        # Add cache management methods
        wrapper.cache = cache
        wrapper.clear_cache = cache.clear

        return wrapper
    return decorator


def get_stock_price_cache() -> TTLCache:
    """Get the stock price cache instance."""
    return _stock_price_cache


def get_financials_cache() -> TTLCache:
    """Get the financials cache instance."""
    return _financials_cache


def get_technical_cache() -> TTLCache:
    """Get the technical indicators cache instance."""
    return _technical_cache


def clear_all_caches() -> None:
    """Clear all cache instances."""
    _stock_price_cache.clear()
    _financials_cache.clear()
    _technical_cache.clear()

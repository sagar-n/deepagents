"""Unit tests for caching utilities."""

import pytest
import time
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.utils.cache import TTLCache, cached


class TestTTLCache:
    """Test TTL cache implementation."""

    def test_cache_set_get(self):
        """Test basic cache set and get operations."""
        cache = TTLCache(max_size=10, ttl=60)

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_cache_miss(self):
        """Test cache miss returns None."""
        cache = TTLCache(max_size=10, ttl=60)
        assert cache.get("nonexistent") is None

    def test_cache_expiration(self):
        """Test cache expiration after TTL."""
        cache = TTLCache(max_size=10, ttl=1)  # 1 second TTL

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Wait for expiration
        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_cache_max_size(self):
        """Test cache eviction when max size is reached."""
        cache = TTLCache(max_size=2, ttl=60)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1

        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_cache_clear(self):
        """Test clearing the cache."""
        cache = TTLCache(max_size=10, ttl=60)

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.size() == 0

    def test_cached_decorator(self):
        """Test the cached decorator."""
        cache = TTLCache(max_size=10, ttl=60)
        call_count = [0]

        @cached(cache)
        def expensive_function(x):
            call_count[0] += 1
            return x * 2

        # First call should execute
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count[0] == 1

        # Second call should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count[0] == 1  # Not incremented

        # Different argument should execute
        result3 = expensive_function(10)
        assert result3 == 20
        assert call_count[0] == 2

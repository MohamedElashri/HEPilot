"""
Cache utilities for the HEPilot arXiv adapter.

This module provides a simple file-based caching mechanism to store and retrieve
responses from external APIs, such as the arXiv API. The cache helps to avoid
redundant API calls and improves performance.
"""

import hashlib
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)

class FileCache:
    """
    A simple file-based cache for API responses.
    """
    def __init__(self, cache_dir: Path, ttl: timedelta = timedelta(days=1)):
        """
        Initialize the file cache.

        Args:
            cache_dir: The directory to store cache files.
            ttl: The time-to-live for cache entries.
        """
        self.cache_dir = cache_dir
        self.ttl = ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, url: str) -> str:
        """
        Generate a cache key from a URL.
        """
        return hashlib.sha256(url.encode()).hexdigest()

    def get(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a cached response for a given URL.

        Args:
            url: The URL of the request.

        Returns:
            The cached response data, or None if not found or expired.
        """
        cache_key = self._get_cache_key(url)
        cache_file = self.cache_dir / cache_key

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)

            # Check if the cache entry has expired
            cached_timestamp = datetime.fromisoformat(cached_data["timestamp"])
            if datetime.now(timezone.utc) - cached_timestamp > self.ttl:
                logger.info(f"Cache expired for {url}")
                return None

            return cached_data["data"]
        except (IOError, json.JSONDecodeError) as e:
            logger.warning(f"Could not read cache file {cache_file}: {e}")
            return None

    def set(self, url: str, data: Any):
        """
        Cache a response for a given URL.

        Args:
            url: The URL of the request.
            data: The response data to cache.
        """
        cache_key = self._get_cache_key(url)
        cache_file = self.cache_dir / cache_key

        cache_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "url": url,
            "data": data
        }

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
        except IOError as e:
            logger.error(f"Could not write to cache file {cache_file}: {e}")

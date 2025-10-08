"""
Cache manager for tracking processed ArXiv papers with version history.

This module implements a robust caching system that tracks ArXiv papers by their
stable IDs and versions, preventing redundant downloads and reprocessing unless
a new version is available on ArXiv.
"""

import json
import re
import hashlib
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid5, NAMESPACE_URL


class CacheEntry:
    """Represents a cached paper entry with version tracking."""
    
    def __init__(
        self,
        arxiv_id: str,
        version: str,
        document_id: str,
        file_hash_sha256: str,
        processing_timestamp: str,
        output_dir: str,
        source_url: str,
        title: str
    ) -> None:
        """
        Initialize cache entry.
        
        Args:
            arxiv_id: ArXiv paper ID (e.g., '2301.12345')
            version: Version string (e.g., 'v2')
            document_id: UUID string for the document
            file_hash_sha256: SHA256 hash of the PDF file
            processing_timestamp: ISO timestamp of processing
            output_dir: Directory containing processed outputs
            source_url: Original ArXiv URL
            title: Paper title
        """
        self.arxiv_id: str = arxiv_id
        self.version: str = version
        self.document_id: str = document_id
        self.file_hash_sha256: str = file_hash_sha256
        self.processing_timestamp: str = processing_timestamp
        self.output_dir: str = output_dir
        self.source_url: str = source_url
        self.title: str = title
    
    def to_dict(self) -> Dict[str, str]:
        """
        Convert cache entry to dictionary.
        
        Returns:
            Dictionary representation of cache entry
        """
        return {
            'arxiv_id': self.arxiv_id,
            'version': self.version,
            'document_id': self.document_id,
            'file_hash_sha256': self.file_hash_sha256,
            'processing_timestamp': self.processing_timestamp,
            'output_dir': self.output_dir,
            'source_url': self.source_url,
            'title': self.title
        }
    
    @staticmethod
    def from_dict(data: Dict[str, str]) -> 'CacheEntry':
        """
        Create cache entry from dictionary.
        
        Args:
            data: Dictionary with cache entry data
            
        Returns:
            CacheEntry instance
        """
        return CacheEntry(**data)


class CacheManager:
    """Manages cache database for ArXiv papers with version tracking."""
    
    def __init__(self, cache_dir: Path) -> None:
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory to store cache database
        """
        self.cache_dir: Path = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file: Path = self.cache_dir / "arxiv_cache.json"
        self.cache: Dict[str, CacheEntry] = self._load_cache()
    
    def _load_cache(self) -> Dict[str, CacheEntry]:
        """
        Load cache from disk.
        
        Returns:
            Dictionary mapping arxiv_id to CacheEntry
        """
        if not self.cache_file.exists():
            return {}
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data: Dict[str, Any] = json.load(f)
            cache: Dict[str, CacheEntry] = {}
            for arxiv_id, entry_data in data.items():
                cache[arxiv_id] = CacheEntry.from_dict(entry_data)
            return cache
        except Exception as e:
            print(f"Warning: Failed to load cache, starting fresh: {e}")
            return {}
    
    def _save_cache(self) -> None:
        """Save cache to disk."""
        data: Dict[str, Dict[str, str]] = {
            arxiv_id: entry.to_dict()
            for arxiv_id, entry in self.cache.items()
        }
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def extract_arxiv_id_and_version(url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract ArXiv ID and version from URL.
        
        Args:
            url: ArXiv URL (e.g., 'http://arxiv.org/pdf/2301.12345v2')
            
        Returns:
            Tuple of (arxiv_id, version) or (None, None) if parsing fails
        """
        # Match patterns like: 2301.12345v2, 2301.12345, hep-ex/0123456v1, etc.
        patterns: list[str] = [
            r'arxiv\.org/(?:pdf|abs)/([a-zA-Z\-]+/\d+|\d+\.\d+)(v\d+)?',
            r'arxiv\.org/(?:pdf|abs)/([a-zA-Z\-]+/\d+|\d+\.\d+)/?$'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                arxiv_id: str = match.group(1)
                version: str = match.group(2) if match.lastindex >= 2 and match.group(2) else 'v1'
                return arxiv_id, version
        return None, None
    
    @staticmethod
    def generate_stable_document_id(arxiv_id: str) -> UUID:
        """
        Generate stable UUID for ArXiv paper.
        
        Uses UUID5 with ArXiv ID to ensure same paper always gets same UUID.
        
        Args:
            arxiv_id: ArXiv paper ID (e.g., '2301.12345')
            
        Returns:
            Stable UUID for this ArXiv paper
        """
        # Use ArXiv URL as namespace for consistent UUIDs
        arxiv_url: str = f"https://arxiv.org/abs/{arxiv_id}"
        return uuid5(NAMESPACE_URL, arxiv_url)
    
    def should_process(
        self,
        arxiv_id: str,
        version: str,
        file_hash: Optional[str] = None
    ) -> bool:
        """
        Check if paper needs processing.
        
        Args:
            arxiv_id: ArXiv paper ID
            version: Version string
            file_hash: Optional SHA256 hash of downloaded file
            
        Returns:
            True if paper should be processed, False if cache is valid
        """
        if arxiv_id not in self.cache:
            return True
        cached_entry: CacheEntry = self.cache[arxiv_id]
        if cached_entry.version != version:
            return True
        if file_hash and cached_entry.file_hash_sha256 != file_hash:
            return True
        cached_output_dir: Path = Path(cached_entry.output_dir)
        if not cached_output_dir.exists():
            return True
        required_files: list[str] = [
            'document_metadata.json',
            'chunks.json'
        ]
        for filename in required_files:
            if not (cached_output_dir / filename).exists():
                return True
        return False
    
    def get_cached_entry(self, arxiv_id: str) -> Optional[CacheEntry]:
        """
        Get cached entry for ArXiv ID.
        
        Args:
            arxiv_id: ArXiv paper ID
            
        Returns:
            CacheEntry if exists, None otherwise
        """
        return self.cache.get(arxiv_id)
    
    def add_entry(
        self,
        arxiv_id: str,
        version: str,
        document_id: UUID,
        file_hash_sha256: str,
        output_dir: Path,
        source_url: str,
        title: str
    ) -> None:
        """
        Add or update cache entry.
        
        Args:
            arxiv_id: ArXiv paper ID
            version: Version string
            document_id: Document UUID
            file_hash_sha256: SHA256 hash of PDF
            output_dir: Output directory path
            source_url: Original ArXiv URL
            title: Paper title
        """
        entry: CacheEntry = CacheEntry(
            arxiv_id=arxiv_id,
            version=version,
            document_id=str(document_id),
            file_hash_sha256=file_hash_sha256,
            processing_timestamp=datetime.now(timezone.utc).isoformat(),
            output_dir=str(output_dir),
            source_url=source_url,
            title=title
        )
        self.cache[arxiv_id] = entry
        self._save_cache()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            'total_papers': len(self.cache),
            'cache_file_exists': self.cache_file.exists()
        }
    
    def clear_cache(self) -> None:
        """Clear all cache entries."""
        self.cache = {}
        if self.cache_file.exists():
            self.cache_file.unlink()

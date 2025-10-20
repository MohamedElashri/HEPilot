"""
Source Collector Port Interfaces

Defines abstract protocols for the data acquisition pipeline:
- Scraper: Fetch raw content from sources
- Cleaner: Convert raw content to plain text
- Chunker: Split text into token-aware windows
- DocStore: Persist chunks and metadata
"""

from typing import Protocol, List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RawDoc:
    """Raw document fetched from source."""
    url: str
    content: bytes
    content_type: str
    metadata: Dict[str, Any]
    fetched_at: datetime


@dataclass
class Chunk:
    """Processed text chunk ready for embedding."""
    id: str
    document_id: str
    text: str
    position: int
    token_count: int
    section_path: List[str]
    metadata: Dict[str, Any]


class Scraper(Protocol):
    """Fetch raw content from a source."""
    
    async def fetch(self, url: str) -> RawDoc:
        """
        Fetch raw document from URL.
        
        Args:
            url: Source URL to fetch
            
        Returns:
            RawDoc with content and metadata
            
        Raises:
            ScraperError: If fetch fails
        """
        ...


class Cleaner(Protocol):
    """Convert raw content to plain text."""
    
    def clean(self, raw: RawDoc) -> str:
        """
        Extract and clean text from raw document.
        
        Args:
            raw: Raw document with content
            
        Returns:
            Clean plain text
            
        Raises:
            CleanerError: If conversion fails
        """
        ...


class Chunker(Protocol):
    """Split text into token-aware chunks."""
    
    def split(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Clean text to split
            metadata: Document metadata
            
        Returns:
            List of chunks with overlap
            
        Raises:
            ChunkerError: If splitting fails
        """
        ...


class DocStore(Protocol):
    """Persist chunks and metadata."""
    
    async def add(self, chunks: List[Chunk]) -> None:
        """
        Store chunks in persistent storage.
        
        Args:
            chunks: List of chunks to store
            
        Raises:
            DocStoreError: If storage fails
        """
        ...
    
    async def get(self, chunk_id: str) -> Optional[Chunk]:
        """
        Retrieve chunk by ID.
        
        Args:
            chunk_id: Unique chunk identifier
            
        Returns:
            Chunk if found, None otherwise
        """
        ...

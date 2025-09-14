#!/usr/bin/env python3
"""
Data Models for HEPilot ArXiv Adapter
Contains shared data classes used across the adapter modules.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


@dataclass
class DocumentInfo:
    """Information about a discovered document."""
    document_id: str
    source_type: str
    source_url: str
    title: str
    authors: List[str]
    discovery_timestamp: str
    estimated_size: int
    content_type: str = "application/pdf"
    priority_score: float = 1.0
    abstract: str = ""
    arxiv_id: str = ""


@dataclass
class AcquiredDocument:
    """Information about an acquired document."""
    document_id: str
    local_path: str
    file_hash_sha256: str
    file_hash_sha512: str
    file_size: int
    download_timestamp: str
    download_status: str
    validation_status: str
    retry_count: int = 0


@dataclass
class Chunk:
    """A chunk of processed document content."""
    chunk_id: str
    document_id: str
    chunk_index: int
    total_chunks: int
    content: str
    token_count: int
    chunk_type: str = "text"
    section_path: List[str] = None
    has_overlap_previous: bool = False
    has_overlap_next: bool = False
    content_features: Dict[str, int] = None
    
    def __post_init__(self):
        if self.section_path is None:
            self.section_path = []
        if self.content_features is None:
            self.content_features = {
                "heading_count": 0,
                "list_count": 0,
                "table_count": 0,
                "equation_count": 0
            }

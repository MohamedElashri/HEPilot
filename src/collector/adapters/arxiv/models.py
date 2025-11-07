"""
Data models for ArXiv adapter pipeline.

This module defines typed data structures for each pipeline stage,
ensuring type safety and schema compliance.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class AdapterConfig(BaseModel):
    """Adapter configuration model."""
    name: str
    version: str
    source_type: str
    processing_config: Dict[str, Any]
    profile: str
    config_hash: str


class DiscoveredDocument(BaseModel):
    """Discovered document from arXiv API."""
    document_id: UUID
    source_type: str = "arxiv"
    source_url: str
    title: str
    authors: Optional[List[str]] = None
    discovery_timestamp: datetime
    estimated_size: int
    content_type: str = "application/pdf"
    priority_score: Optional[float] = None
    arxiv_id: Optional[str] = None
    arxiv_version: Optional[str] = None


class AcquiredDocument(BaseModel):
    """Document acquisition result."""
    document_id: UUID
    local_path: str
    file_hash_sha256: str
    file_hash_sha512: str
    file_size: int
    download_timestamp: datetime
    download_status: str
    retry_count: int = 0
    validation_status: str
    arxiv_id: Optional[str] = None
    arxiv_version: Optional[str] = None


class ProcessingMetadata(BaseModel):
    """Processing execution metadata."""
    processor_used: str
    processing_timestamp: datetime
    processing_duration: float
    conversion_warnings: List[str] = Field(default_factory=list)


class ChunkContent(BaseModel):
    """Individual chunk with metadata."""
    chunk_id: UUID
    document_id: UUID
    chunk_index: int
    total_chunks: int
    content: str
    token_count: int
    chunk_type: str = "text"
    section_path: Optional[List[str]] = None
    has_overlap_previous: bool = False
    has_overlap_next: bool = False
    content_features: Optional[Dict[str, int]] = None


class DocumentMetadata(BaseModel):
    """Comprehensive document metadata."""
    document_id: UUID
    source_type: str = "arxiv"
    original_url: str
    local_path: Optional[str] = None
    title: str
    authors: Optional[List[str]] = None
    publication_date: Optional[str] = None
    subject_categories: Optional[List[str]] = None
    language: str = "en"
    file_hash: str
    file_size: int
    processing_timestamp: datetime
    adapter_version: str
    experiment_tags: Optional[List[str]] = None
    collaboration: Optional[str] = None
    license: Optional[str] = None
    arxiv_id: Optional[str] = None
    arxiv_version: Optional[str] = None


class LogEntry(BaseModel):
    """Structured log entry."""
    timestamp: datetime
    level: str
    component: str
    message: str
    context: Optional[Dict[str, Any]] = None

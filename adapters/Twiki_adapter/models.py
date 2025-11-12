from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict, Optional, List
from uuid import UUID

class DiscoveredDocument(BaseModel):
    document_id: UUID
    source_type: str
    source_url: str 
    title: str 
    authors: Optional[List[str]]
    discovery_timestamp: datetime
    estimated_size: int
    content_type: Optional[str]
    priority_score: Optional[float] = None

class AcquiredDocument(BaseModel):
    document_id: UUID
    local_path: str
    source_url: str
    file_hash_sha256: str
    file_hash_sha512: str
    file_size: int
    download_timestamp: datetime
    download_status: str
    retry_count: int = 0
    validation_status: Optional[str]

class ProcessingMetadata(BaseModel):
    processor_used: str
    processing_timestamp: datetime
    processing_duration: float
    conversion_warnings: List[str]

class DocumentMetadata(BaseModel):
    # Schema fortwiki document metadata
    document_id: UUID
    source_type: str
    original_url: str
    local_path: str
    title: str
    authors: Optional[List[str]] = None
    publication_date: Optional[str] = None
    subject_categories: Optional[List[str]] = None
    language: Optional[str] = "en"
    file_hash: str
    file_size: int
    processing_timestamp: datetime
    adapter_version: str
    experiment_tags: Optional[List[str]] = None
    collaboration: Optional[str] = None
    license: Optional[str] = None

class LogEntry(BaseModel):
    timestamp: datetime
    level:str
    component: str
    message: str
    context: Optional[Dict[str,Any]] = None

class AdapterConfig(BaseModel):
    name: str
    version: str 
    source_type: str 
    config_hash: str = Field(default="0" * 64)
    processing_config: Dict[str, Any]
    embedding_config: Optional[Dict[str, Any]] = None

class ChunkContent(BaseModel):
    chunk_id: UUID
    document_id: UUID
    chunk_index: int
    total_chunks: int
    content: str
    token_count: int
    chunk_type: str 
    section_path: Optional[List[str]] = None
    has_overlap_provious: bool = False
    has_overlap_next: bool = False
    content_features: Optional[Dict[str, int]] = None

"""SQLAlchemy models for embedding layer database schema."""

from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class Document(Base):
    """Document metadata table."""
    
    __tablename__ = 'documents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type = Column(String(50), nullable=False)
    source_id = Column(String(500), nullable=False)
    title = Column(Text)
    authors = Column(JSONB)
    publication_date = Column(TIMESTAMP)
    source_url = Column(Text)
    meta = Column(JSONB)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    __table_args__ = (
        # Unique constraint on source_type + source_id
        {'schema': None}  # Use default schema
    )


class DocSegment(Base):
    """Document chunks/segments table."""
    
    __tablename__ = 'doc_segments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doc_id = Column(UUID(as_uuid=True), ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    text = Column(Text, nullable=False)
    section_path = Column(JSONB)
    position_in_doc = Column(Integer, nullable=False)
    token_count = Column(Integer, nullable=False)
    overlap_start = Column(Integer, nullable=False)
    overlap_end = Column(Integer, nullable=False)
    meta = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

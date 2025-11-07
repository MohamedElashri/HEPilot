"""Tests for collector validation utilities."""

import json
import pytest
from pathlib import Path
from uuid import uuid4
from src.collector.validation import CollectorSchemaValidator, CollectorValidationError


@pytest.fixture
def validator():
    """Create a validator instance."""
    return CollectorSchemaValidator()


@pytest.fixture
def standards_dir():
    """Get standards directory."""
    return Path(__file__).resolve().parents[3] / "standards" / "schemas"


def test_validator_initialization(validator):
    """Test validator initializes correctly."""
    assert validator is not None
    assert validator.schema_dir.exists()


def test_chunk_metadata_validation_valid(validator):
    """Test valid chunk metadata passes validation."""
    payload = {
        "chunk_id": "123e4567-e89b-12d3-a456-426614174000",
        "document_id": "123e4567-e89b-12d3-a456-426614174001",
        "chunk_index": 0,
        "total_chunks": 10,
        "token_count": 512,
        "character_count": 2048,
        "contains_equations": False,
        "contains_tables": False,
    }
    # Should not raise
    validator.validate_chunk_metadata(payload)


def test_chunk_metadata_validation_missing_required(validator):
    """Test chunk metadata validation fails on missing required fields."""
    payload = {
        "chunk_id": "123e4567-e89b-12d3-a456-426614174000",
        # Missing required fields
    }
    with pytest.raises(CollectorValidationError) as exc_info:
        validator.validate_chunk_metadata(payload)
    assert "validation" in str(exc_info.value).lower()


def test_catalog_validation_valid(validator):
    """Test valid catalog passes validation."""
    payload = {
        "creation_timestamp": "2025-10-27T12:00:00Z",
        "adapter_version": "1.0.0",
        "total_documents": 1,
        "total_chunks": 10,
        "documents": [
            {
                "document_id": "123e4567-e89b-12d3-a456-426614174000",
                "source_type": "arxiv",
                "title": "Test Document",
                "chunk_count": 10,
                "file_path": "document_123/",
            }
        ],
    }
    # Should not raise
    validator.validate_catalog(payload)


def test_discovery_output_validation_valid(validator):
    """Test valid discovery output passes validation."""
    payload = {
        "discovered_documents": [
            {
                "document_id": "123e4567-e89b-12d3-a456-426614174000",
                "source_type": "arxiv",
                "source_url": "https://arxiv.org/pdf/1234.5678.pdf",
                "title": "Test Paper",
                "discovery_timestamp": "2025-10-27T12:00:00Z",
                "estimated_size": 500000,
            }
        ]
    }
    # Should not raise
    validator.validate_discovery_output(payload)


def test_document_metadata_validation_valid(validator):
    """Test valid document metadata passes validation."""
    payload = {
        "document_id": "123e4567-e89b-12d3-a456-426614174000",
        "source_type": "arxiv",
        "original_url": "https://arxiv.org/pdf/1234.5678.pdf",
        "title": "Test Paper",
        "file_hash": "a" * 64,
        "file_size": 500000,
        "processing_timestamp": "2025-10-27T12:00:00Z",
        "adapter_version": "1.0.0",
    }
    # Should not raise
    validator.validate_document_metadata(payload)


def test_processing_metadata_validation_valid(validator):
    """Test valid processing metadata passes validation."""
    payload = {
        "processor_used": "docling/1.2.3",
        "processing_timestamp": "2025-10-27T12:00:00Z",
        "processing_duration": 12.5,
        "conversion_warnings": [],
    }
    # Should not raise
    validator.validate_processing_metadata(payload)


def test_processing_metadata_with_warnings(validator):
    """Test processing metadata with warnings."""
    payload = {
        "processor_used": "docling/1.2.3",
        "processing_timestamp": "2025-10-27T12:00:00Z",
        "processing_duration": 15.3,
        "conversion_warnings": [
            "Failed to parse equation on line 42",
            "Table structure ambiguous",
        ],
    }
    # Should not raise
    validator.validate_processing_metadata(payload)


def test_unknown_schema_key(validator):
    """Test unknown schema key raises error."""
    with pytest.raises(CollectorValidationError) as exc_info:
        validator._validate("unknown_schema", {})
    assert "unknown schema key" in str(exc_info.value).lower()


def test_invalid_json_format(validator):
    """Test validation catches type errors."""
    payload = {
        "chunk_id": str(uuid4()),
        "document_id": str(uuid4()),
        "chunk_index": "not-an-integer",  # Invalid type
        "total_chunks": 10,
        "token_count": 512,
        "character_count": 2048,
        "contains_equations": False,
        "contains_tables": False,
    }
    with pytest.raises(CollectorValidationError):
        validator.validate_chunk_metadata(payload)

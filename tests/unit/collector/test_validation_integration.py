"""Integration tests for collector validation pipeline."""

import json
import pytest
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

from src.collector.validation import CollectorSchemaValidator, CollectorValidationError
from src.collector.pipeline import (
    CollectorPipeline,
    CollectorRequest,
    ProcessedDocument,
)
from src.collector.ports import Chunk, RawDoc


@pytest.fixture
def validator():
    """Create validator instance."""
    return CollectorSchemaValidator()


@pytest.fixture
def sample_discovery_output():
    """Create sample discovery output."""
    return {
        "discovered_documents": [
            {
                "document_id": str(uuid4()),
                "source_type": "arxiv",
                "source_url": "https://arxiv.org/pdf/2410.12345.pdf",
                "title": "Test Paper on HEP",
                "authors": ["Alice Smith", "Bob Jones"],
                "discovery_timestamp": datetime.now(timezone.utc).isoformat(),
                "estimated_size": 500000,
                "content_type": "application/pdf",
            }
        ]
    }


@pytest.fixture
def sample_processing_metadata():
    """Create sample processing metadata."""
    return {
        "processor_used": "docling/1.2.3",
        "processing_timestamp": datetime.now(timezone.utc).isoformat(),
        "processing_duration": 12.5,
        "conversion_warnings": ["Table structure ambiguous on page 5"],
    }


@pytest.fixture
def sample_document_metadata():
    """Create sample document metadata."""
    return {
        "document_id": str(uuid4()),
        "source_type": "arxiv",
        "original_url": "https://arxiv.org/pdf/2410.12345.pdf",
        "title": "Test Paper on HEP",
        "authors": ["Alice Smith", "Bob Jones"],
        "publication_date": "2025-10-27",
        "subject_categories": ["hep-ex", "hep-ph"],
        "file_hash": "a" * 64,
        "file_size": 500000,
        "processing_timestamp": datetime.now(timezone.utc).isoformat(),
        "adapter_version": "1.0.0",
    }


class TestEndToEndValidation:
    """Test end-to-end validation pipeline."""

    def test_validate_complete_pipeline_output(
        self,
        validator,
        sample_discovery_output,
        sample_processing_metadata,
        sample_document_metadata,
    ):
        """Test validating complete pipeline output."""
        # All should validate without errors
        validator.validate_discovery_output(sample_discovery_output)
        validator.validate_processing_metadata(sample_processing_metadata)
        validator.validate_document_metadata(sample_document_metadata)

    def test_validate_chunk_metadata_batch(self, validator):
        """Test validating multiple chunk metadata entries."""
        doc_id = str(uuid4())
        chunk_metadata = [
            {
                "chunk_id": str(uuid4()),
                "document_id": doc_id,
                "chunk_index": i,
                "total_chunks": 3,
                "token_count": 512,
                "character_count": 2048,
                "contains_equations": i == 1,  # Second chunk has equations
                "contains_tables": i == 2,  # Third chunk has tables
                "section_hierarchy": [f"Section {i+1}"],
                "chunk_type": "text",
            }
            for i in range(3)
        ]

        # Validate each chunk
        for metadata in chunk_metadata:
            validator.validate_chunk_metadata(metadata)

    def test_validate_catalog_with_multiple_sources(self, validator):
        """Test validating catalog with multiple source types."""
        catalog = {
            "creation_timestamp": datetime.now(timezone.utc).isoformat(),
            "adapter_version": "1.0.0",
            "total_documents": 5,
            "total_chunks": 50,
            "source_distribution": {"arxiv": 3, "indico": 1, "other": 1},
            "documents": [
                {
                    "document_id": str(uuid4()),
                    "source_type": source_type,
                    "title": f"Document {i}",
                    "chunk_count": 10,
                    "file_path": f"doc_{i}/",
                }
                for i, source_type in enumerate(
                    ["arxiv", "arxiv", "arxiv", "indico", "other"]
                )
            ],
        }

        validator.validate_catalog(catalog)


class TestValidationErrorHandling:
    """Test validation error handling and messages."""

    def test_chunk_metadata_missing_field_error_message(self, validator):
        """Test error message for missing required field."""
        incomplete_metadata = {
            "chunk_id": str(uuid4()),
            # Missing required fields
        }

        with pytest.raises(CollectorValidationError) as exc_info:
            validator.validate_chunk_metadata(incomplete_metadata)

        error_msg = str(exc_info.value)
        assert "validation" in error_msg.lower()
        assert "chunk_metadata" in error_msg.lower()

    def test_catalog_invalid_document_structure(self, validator):
        """Test error for invalid document structure in catalog."""
        invalid_catalog = {
            "creation_timestamp": datetime.now(timezone.utc).isoformat(),
            "adapter_version": "1.0.0",
            "total_documents": 1,
            "total_chunks": 10,
            "documents": [
                {
                    "document_id": str(uuid4()),
                    # Missing required fields: source_type, title, chunk_count, file_path
                }
            ],
        }

        with pytest.raises(CollectorValidationError):
            validator.validate_catalog(invalid_catalog)

    def test_processing_metadata_wrong_type(self, validator):
        """Test error for wrong data type."""
        invalid_metadata = {
            "processor_used": "docling/1.2.3",
            "processing_timestamp": datetime.now(timezone.utc).isoformat(),
            "processing_duration": "not_a_number",  # Should be float
        }

        with pytest.raises(CollectorValidationError):
            validator.validate_processing_metadata(invalid_metadata)


class TestSchemaVersioning:
    """Test schema versioning and compatibility."""

    def test_validator_uses_correct_schema_dir(self, tmp_path):
        """Test validator can use custom schema directory."""
        custom_schema_dir = tmp_path / "custom_schemas"
        custom_schema_dir.mkdir()

        validator = CollectorSchemaValidator(schema_dir=custom_schema_dir)
        assert validator.schema_dir == custom_schema_dir

    def test_schema_files_exist(self):
        """Test that all referenced schema files exist."""
        validator = CollectorSchemaValidator()

        schema_files = [
            "chunk_metadata.schema.json",
            "catalog.schema.json",
            "discovery_output.schema.json",
            "document_metadata.schema.json",
            "processing_metadata.schema.json",
        ]

        for schema_file in schema_files:
            schema_path = validator.schema_dir / schema_file
            assert schema_path.exists(), f"Schema file missing: {schema_file}"


class TestRealWorldScenarios:
    """Test real-world validation scenarios."""

    def test_arxiv_paper_complete_flow(self, validator):
        """Test complete validation flow for an ArXiv paper."""
        doc_id = str(uuid4())

        # Discovery
        discovery = {
            "discovered_documents": [
                {
                    "document_id": doc_id,
                    "source_type": "arxiv",
                    "source_url": "https://arxiv.org/pdf/2410.12345.pdf",
                    "title": "Measurement of CP violation in B decays",
                    "authors": ["LHCb Collaboration"],
                    "discovery_timestamp": "2025-10-27T12:00:00Z",
                    "estimated_size": 1500000,
                }
            ]
        }
        validator.validate_discovery_output(discovery)

        # Processing
        processing = {
            "processor_used": "docling/1.2.3",
            "processing_timestamp": "2025-10-27T12:05:00Z",
            "processing_duration": 45.2,
            "conversion_warnings": [],
        }
        validator.validate_processing_metadata(processing)

        # Document metadata
        document = {
            "document_id": doc_id,
            "source_type": "arxiv",
            "original_url": "https://arxiv.org/pdf/2410.12345.pdf",
            "title": "Measurement of CP violation in B decays",
            "authors": ["LHCb Collaboration"],
            "publication_date": "2025-10-27",
            "subject_categories": ["hep-ex"],
            "file_hash": "b" * 64,
            "file_size": 1500000,
            "processing_timestamp": "2025-10-27T12:05:00Z",
            "adapter_version": "1.0.0",
        }
        validator.validate_document_metadata(document)

        # Chunks
        for i in range(5):
            chunk = {
                "chunk_id": str(uuid4()),
                "document_id": doc_id,
                "chunk_index": i,
                "total_chunks": 5,
                "token_count": 512,
                "character_count": 2048,
                "contains_equations": i in [1, 2],
                "contains_tables": i == 3,
                "section_hierarchy": [["Introduction", "Methods", "Results"][i % 3]],
            }
            validator.validate_chunk_metadata(chunk)

        # Catalog
        catalog = {
            "creation_timestamp": "2025-10-27T12:06:00Z",
            "adapter_version": "1.0.0",
            "total_documents": 1,
            "total_chunks": 5,
            "source_distribution": {"arxiv": 1},
            "documents": [
                {
                    "document_id": doc_id,
                    "source_type": "arxiv",
                    "title": "Measurement of CP violation in B decays",
                    "chunk_count": 5,
                    "file_path": f"arxiv_{doc_id}/",
                }
            ],
        }
        validator.validate_catalog(catalog)

    def test_large_document_with_many_chunks(self, validator):
        """Test validation of large document with many chunks."""
        doc_id = str(uuid4())

        # Create 100 chunks
        chunk_metadata = [
            {
                "chunk_id": str(uuid4()),
                "document_id": doc_id,
                "chunk_index": i,
                "total_chunks": 100,
                "token_count": 512,
                "character_count": 2048,
                "contains_equations": i % 10 == 0,
                "contains_tables": i % 20 == 0,
            }
            for i in range(100)
        ]

        # Should validate all without issues
        for metadata in chunk_metadata:
            validator.validate_chunk_metadata(metadata)

    def test_mixed_source_types_catalog(self, validator):
        """Test catalog with documents from multiple sources."""
        source_types = (
            ["arxiv"] * 5 + ["indico"] * 3 + ["internal_notes"] + ["other"]
        )
        
        catalog = {
            "creation_timestamp": datetime.now(timezone.utc).isoformat(),
            "adapter_version": "1.0.0",
            "total_documents": 10,
            "total_chunks": 100,
            "source_distribution": {
                "arxiv": 5,
                "indico": 3,
                "internal_notes": 1,
                "other": 1,
            },
            "documents": [
                {
                    "document_id": str(uuid4()),
                    "source_type": source_types[i],
                    "title": f"Document {i}",
                    "chunk_count": 10,
                    "file_path": f"doc_{i}/",
                }
                for i in range(10)
            ],
        }

        validator.validate_catalog(catalog)

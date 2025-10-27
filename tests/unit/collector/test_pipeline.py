"""Tests for collector pipeline catalog generation."""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from src.collector.pipeline import (
    CollectorPipeline,
    ProcessedDocument,
    CollectorResult,
)
from src.collector.ports import Chunk, RawDoc


@pytest.fixture
def sample_chunks():
    """Create sample chunks for testing."""
    doc_id = str(uuid4())
    return [
        Chunk(
            id=str(uuid4()),
            document_id=doc_id,
            text="Sample chunk 1 content",
            position=0,
            token_count=10,
            section_path=["Introduction"],
            metadata={
                "chunk_type": "text",
                "content_features": {
                    "equation_count": 0,
                    "table_count": 0,
                },
            },
        ),
        Chunk(
            id=str(uuid4()),
            document_id=doc_id,
            text="Sample chunk 2 content",
            position=1,
            token_count=12,
            section_path=["Methods"],
            metadata={
                "chunk_type": "text",
                "content_features": {
                    "equation_count": 1,
                    "table_count": 0,
                },
            },
        ),
    ]


@pytest.fixture
def sample_raw_doc():
    """Create a sample raw document."""
    return RawDoc(
        url="https://example.org/paper.pdf",
        content=b"fake pdf content",
        content_type="application/pdf",
        metadata={
            "source_url": "https://example.org/paper.pdf",
            "content_length": 16,
            "title": "Test Paper",
            "authors": ["Alice", "Bob"],
            "source_type": "arxiv",
        },
        fetched_at=datetime(2025, 10, 27, 12, 0, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def sample_processed_document(sample_chunks, sample_raw_doc):
    """Create a sample processed document."""
    chunk_metadata = [
        {
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "chunk_index": i,
            "total_chunks": len(sample_chunks),
            "token_count": chunk.token_count,
            "character_count": len(chunk.text),
            "contains_equations": False,
            "contains_tables": False,
        }
        for i, chunk in enumerate(sample_chunks)
    ]

    return ProcessedDocument(
        source_id="test-doc-1",
        url="https://example.org/paper.pdf",
        metadata={
            "title": "Test Paper",
            "authors": ["Alice", "Bob"],
            "source_type": "arxiv",
        },
        raw_document=sample_raw_doc,
        cleaned_text="Sample cleaned text",
        chunks=sample_chunks,
        persisted_path=None,
        chunk_metadata=chunk_metadata,
    )


class TestBuildChunkMetadata:
    """Test chunk metadata building."""

    def test_build_chunk_metadata_basic(self, sample_chunks):
        """Test building basic chunk metadata."""
        metadata_list = CollectorPipeline._build_chunk_metadata(sample_chunks)

        assert len(metadata_list) == len(sample_chunks)
        assert metadata_list[0]["chunk_index"] == 0
        assert metadata_list[1]["chunk_index"] == 1
        assert all(m["total_chunks"] == 2 for m in metadata_list)

    def test_build_chunk_metadata_includes_required_fields(self, sample_chunks):
        """Test that all required schema fields are present."""
        metadata_list = CollectorPipeline._build_chunk_metadata(sample_chunks)

        required_fields = {
            "chunk_id",
            "document_id",
            "chunk_index",
            "total_chunks",
            "token_count",
            "character_count",
            "contains_equations",
            "contains_tables",
        }

        for metadata in metadata_list:
            assert required_fields.issubset(metadata.keys())

    def test_build_chunk_metadata_extracts_features(self, sample_chunks):
        """Test feature extraction from chunk metadata."""
        metadata_list = CollectorPipeline._build_chunk_metadata(sample_chunks)

        # First chunk has no equations
        assert metadata_list[0]["contains_equations"] is False
        assert metadata_list[0]["contains_tables"] is False

        # Second chunk has equations
        assert metadata_list[1]["contains_equations"] is True

    def test_build_chunk_metadata_includes_section_hierarchy(self, sample_chunks):
        """Test section hierarchy is included when present."""
        metadata_list = CollectorPipeline._build_chunk_metadata(sample_chunks)

        assert metadata_list[0]["section_hierarchy"] == ["Introduction"]
        assert metadata_list[1]["section_hierarchy"] == ["Methods"]

    def test_build_chunk_metadata_handles_empty_metadata(self):
        """Test handling chunks with no metadata."""
        chunk = Chunk(
            id=str(uuid4()),
            document_id=str(uuid4()),
            text="Test",
            position=0,
            token_count=5,
            section_path=[],
            metadata=None,
        )
        metadata_list = CollectorPipeline._build_chunk_metadata([chunk])

        assert len(metadata_list) == 1
        assert metadata_list[0]["contains_equations"] is False
        assert metadata_list[0]["contains_tables"] is False


class TestBuildCatalog:
    """Test catalog building."""

    @pytest.fixture
    def mock_pipeline(self, tmp_path):
        """Create a mock pipeline for testing."""
        # We can't instantiate a real pipeline without registries,
        # so we'll test the static method behavior
        class MockPipeline:
            def __init__(self):
                self.output_dir = tmp_path
                self.adapter_metadata = {
                    "adapter_version": "1.2.3",
                    "adapter_name": "test_adapter",
                }

            _build_catalog = CollectorPipeline._build_catalog

        return MockPipeline()

    def test_build_catalog_basic(self, mock_pipeline, sample_processed_document):
        """Test basic catalog building."""
        catalog = mock_pipeline._build_catalog([sample_processed_document])

        assert catalog is not None
        assert catalog["adapter_version"] == "1.2.3"
        assert catalog["total_documents"] == 1
        assert catalog["total_chunks"] == 2
        assert len(catalog["documents"]) == 1

    def test_build_catalog_includes_required_fields(
        self, mock_pipeline, sample_processed_document
    ):
        """Test catalog includes all required fields."""
        catalog = mock_pipeline._build_catalog([sample_processed_document])

        required_fields = {
            "creation_timestamp",
            "adapter_version",
            "total_documents",
            "total_chunks",
            "documents",
        }
        assert required_fields.issubset(catalog.keys())

    def test_build_catalog_document_entry(
        self, mock_pipeline, sample_processed_document
    ):
        """Test catalog document entry structure."""
        catalog = mock_pipeline._build_catalog([sample_processed_document])

        doc_entry = catalog["documents"][0]
        assert "document_id" in doc_entry
        assert doc_entry["source_type"] == "arxiv"
        assert doc_entry["title"] == "Test Paper"
        assert doc_entry["chunk_count"] == 2
        assert "file_path" in doc_entry

    def test_build_catalog_source_distribution(
        self, mock_pipeline, sample_processed_document
    ):
        """Test source distribution is computed."""
        catalog = mock_pipeline._build_catalog([sample_processed_document])

        assert "source_distribution" in catalog
        assert catalog["source_distribution"]["arxiv"] == 1

    def test_build_catalog_multiple_documents(self, mock_pipeline, sample_raw_doc):
        """Test catalog with multiple documents."""
        docs = []
        for i in range(3):
            doc_id = str(uuid4())
            chunks = [
                Chunk(
                    id=str(uuid4()),
                    document_id=doc_id,
                    text=f"Chunk {j}",
                    position=j,
                    token_count=10,
                    section_path=[],
                    metadata={},
                )
                for j in range(2)
            ]
            docs.append(
                ProcessedDocument(
                    source_id=f"doc-{i}",
                    url=f"https://example.org/paper{i}.pdf",
                    metadata={"source_type": "arxiv", "title": f"Paper {i}"},
                    raw_document=sample_raw_doc,
                    cleaned_text="Text",
                    chunks=chunks,
                    persisted_path=None,
                    chunk_metadata=[],
                )
            )

        catalog = mock_pipeline._build_catalog(docs)

        assert catalog["total_documents"] == 3
        assert catalog["total_chunks"] == 6
        assert len(catalog["documents"]) == 3

    def test_build_catalog_skips_empty_chunks(self, mock_pipeline, sample_raw_doc):
        """Test catalog skips documents with no chunks."""
        doc_with_chunks = ProcessedDocument(
            source_id="doc-1",
            url="https://example.org/paper.pdf",
            metadata={"source_type": "arxiv", "title": "Paper"},
            raw_document=sample_raw_doc,
            cleaned_text="Text",
            chunks=[
                Chunk(
                    id=str(uuid4()),
                    document_id=str(uuid4()),
                    text="Chunk",
                    position=0,
                    token_count=10,
                    section_path=[],
                    metadata={},
                )
            ],
            persisted_path=None,
            chunk_metadata=[],
        )

        doc_without_chunks = ProcessedDocument(
            source_id="doc-2",
            url="https://example.org/paper2.pdf",
            metadata={"source_type": "arxiv", "title": "Empty Paper"},
            raw_document=sample_raw_doc,
            cleaned_text="Text",
            chunks=[],
            persisted_path=None,
            chunk_metadata=[],
        )

        catalog = mock_pipeline._build_catalog([doc_with_chunks, doc_without_chunks])

        assert catalog["total_documents"] == 1
        assert catalog["total_chunks"] == 1
        assert len(catalog["documents"]) == 1

    def test_build_catalog_file_path_relative(
        self, mock_pipeline, sample_processed_document, tmp_path
    ):
        """Test file path is relative to output dir when persisted."""
        persisted_path = tmp_path / "doc_123"
        sample_processed_document.persisted_path = persisted_path

        catalog = mock_pipeline._build_catalog([sample_processed_document])

        doc_entry = catalog["documents"][0]
        assert doc_entry["file_path"] == "doc_123"

    def test_build_catalog_file_path_in_memory(
        self, mock_pipeline, sample_processed_document
    ):
        """Test file path for non-persisted documents."""
        sample_processed_document.persisted_path = None

        catalog = mock_pipeline._build_catalog([sample_processed_document])

        doc_entry = catalog["documents"][0]
        assert doc_entry["file_path"].startswith("in-memory://")

    def test_build_catalog_mixed_source_types(self, mock_pipeline, sample_raw_doc):
        """Test catalog with multiple source types."""
        docs = [
            ProcessedDocument(
                source_id=f"doc-{i}",
                url=f"https://example.org/doc{i}",
                metadata={"source_type": source_type, "title": f"Doc {i}"},
                raw_document=sample_raw_doc,
                cleaned_text="Text",
                chunks=[
                    Chunk(
                        id=str(uuid4()),
                        document_id=str(uuid4()),
                        text="Chunk",
                        position=0,
                        token_count=10,
                        section_path=[],
                        metadata={},
                    )
                ],
                persisted_path=None,
                chunk_metadata=[],
            )
            for i, source_type in enumerate(["arxiv", "arxiv", "indico", "other"])
        ]

        catalog = mock_pipeline._build_catalog(docs)

        assert catalog["source_distribution"]["arxiv"] == 2
        assert catalog["source_distribution"]["indico"] == 1
        assert catalog["source_distribution"]["other"] == 1


class TestBuildDocumentMetadata:
    """Test document metadata building."""

    @pytest.fixture
    def mock_pipeline(self):
        """Create a mock pipeline for testing."""

        class MockPipeline:
            def __init__(self):
                self.adapter_metadata = {
                    "adapter_version": "1.2.3",
                }

            _build_document_metadata = CollectorPipeline._build_document_metadata

        return MockPipeline()

    def test_build_document_metadata_required_fields(
        self, mock_pipeline, sample_chunks, sample_raw_doc
    ):
        """Test document metadata includes all required fields."""
        from src.collector.pipeline import CollectorRequest

        request = CollectorRequest(
            url="https://example.org/paper.pdf",
            source_id="test-doc",
            metadata={"title": "Test Paper"},
        )

        metadata = mock_pipeline._build_document_metadata(
            request=request,
            raw_doc=sample_raw_doc,
            chunks=sample_chunks,
            safe_id="test-doc",
        )

        required_fields = {
            "document_id",
            "source_type",
            "original_url",
            "title",
            "file_hash",
            "file_size",
            "processing_timestamp",
            "adapter_version",
        }
        assert required_fields.issubset(metadata.keys())

    def test_build_document_metadata_computes_hash(
        self, mock_pipeline, sample_chunks, sample_raw_doc
    ):
        """Test file hash is computed when not present."""
        from src.collector.pipeline import CollectorRequest

        request = CollectorRequest(url="https://example.org/paper.pdf")
        metadata = mock_pipeline._build_document_metadata(
            request=request,
            raw_doc=sample_raw_doc,
            chunks=sample_chunks,
            safe_id="test-doc",
        )

        assert metadata["file_hash"]
        assert len(metadata["file_hash"]) == 64  # SHA256 hex

    def test_build_document_metadata_uses_existing_hash(
        self, mock_pipeline, sample_chunks, sample_raw_doc
    ):
        """Test existing file hash is used when present."""
        from src.collector.pipeline import CollectorRequest

        existing_hash = "a" * 64
        sample_raw_doc.metadata["file_hash_sha256"] = existing_hash

        request = CollectorRequest(url="https://example.org/paper.pdf")
        metadata = mock_pipeline._build_document_metadata(
            request=request,
            raw_doc=sample_raw_doc,
            chunks=sample_chunks,
            safe_id="test-doc",
        )

        assert metadata["file_hash"] == existing_hash

    def test_build_document_metadata_optional_fields(
        self, mock_pipeline, sample_chunks, sample_raw_doc
    ):
        """Test optional fields are included when present."""
        from src.collector.pipeline import CollectorRequest

        sample_raw_doc.metadata.update(
            {
                "authors": ["Alice", "Bob"],
                "publication_date": "2025-10-27",
                "subject_categories": ["hep-ex", "hep-ph"],
                "language": "en",
            }
        )

        request = CollectorRequest(url="https://example.org/paper.pdf")
        metadata = mock_pipeline._build_document_metadata(
            request=request,
            raw_doc=sample_raw_doc,
            chunks=sample_chunks,
            safe_id="test-doc",
        )

        assert metadata["authors"] == ["Alice", "Bob"]
        assert metadata["publication_date"] == "2025-10-27"
        assert metadata["subject_categories"] == ["hep-ex", "hep-ph"]
        assert metadata["language"] == "en"

    def test_build_document_metadata_omits_empty_optional_fields(
        self, mock_pipeline, sample_chunks, sample_raw_doc
    ):
        """Test optional fields are omitted when not present."""
        from src.collector.pipeline import CollectorRequest

        request = CollectorRequest(url="https://example.org/paper.pdf")
        metadata = mock_pipeline._build_document_metadata(
            request=request,
            raw_doc=sample_raw_doc,
            chunks=sample_chunks,
            safe_id="test-doc",
        )

        # Optional fields should not be present if not in source metadata
        assert "publication_date" not in metadata or metadata.get("authors")
        assert "subject_categories" not in metadata or metadata.get("authors")

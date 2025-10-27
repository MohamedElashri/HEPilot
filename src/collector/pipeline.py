"""Collector pipeline orchestration layer.

Provides an adapter-agnostic pipeline that wires the collector ports
(`Scraper`, `Cleaner`, `Chunker`, `DocStore`) using the global adapter
registries. The pipeline returns structured results while optionally
persisting artifacts to disk when requested.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import json
import os

from .ports import Chunk, Chunker, Cleaner, DocStore, RawDoc, Scraper
from .registry import (
    chunker_registry,
    cleaner_registry,
    docstore_registry,
    scraper_registry,
)
from .validation import CollectorSchemaValidator, CollectorValidationError


@dataclass(slots=True)
class CollectorRequest:
    """Request to process a single source document."""

    url: str
    source_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CollectorError:
    """Error emitted while processing a request."""

    url: str
    message: str


@dataclass(slots=True)
class ProcessedDocument:
    """In-memory representation of a processed document."""

    source_id: Optional[str]
    url: str
    metadata: Dict[str, Any]
    raw_document: RawDoc
    cleaned_text: str
    chunks: List[Chunk]
    persisted_path: Optional[Path] = None
    chunk_metadata: List[Dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class CollectorResult:
    """Aggregate result returned by the collector pipeline."""

    documents: List[ProcessedDocument] = field(default_factory=list)
    errors: List[CollectorError] = field(default_factory=list)
    catalog: Optional[Dict[str, Any]] = None


class CollectorPipeline:
    """Adapter-driven pipeline for scraping, cleaning, and chunking sources."""

    def __init__(
        self,
        *,
        scraper: str,
        cleaner: str,
        chunker: str,
        docstore: Optional[str] = None,
        component_config: Optional[Dict[str, Dict[str, Any]]] = None,
        persist_output: Optional[bool] = None,
        output_dir: Optional[Path] = None,
        adapter_metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialise the pipeline with adapter names and configuration.

        Args:
            scraper: Registered scraper adapter name.
            cleaner: Registered cleaner adapter name.
            chunker: Registered chunker adapter name.
            docstore: Optional registered docstore adapter name.
            component_config: Adapter-specific init kwargs keyed by component
                type ("scraper", "cleaner", "chunker", "docstore").
            persist_output: Whether to persist artifacts to disk. Defaults to
                False unless `HP_COLLECTOR_PERSIST_OUTPUT` env var is truthy.
            output_dir: Directory used when persistence is enabled.
        """

        config = component_config or {}

        self.scraper: Scraper = self._instantiate_adapter(
            scraper_registry, scraper, config.get("scraper", {})
        )
        self.cleaner: Cleaner = self._instantiate_adapter(
            cleaner_registry, cleaner, config.get("cleaner", {})
        )
        self.chunker: Chunker = self._instantiate_adapter(
            chunker_registry, chunker, config.get("chunker", {})
        )

        self.docstore: Optional[DocStore] = None
        if docstore:
            self.docstore = self._instantiate_adapter(
                docstore_registry, docstore, config.get("docstore", {})
            )

        # Determine persistence behaviour (flag or environment override).
        env_flag = os.getenv("HP_COLLECTOR_PERSIST_OUTPUT", "false").lower()
        env_persist = env_flag in {"1", "true", "yes", "on"}
        if persist_output is None:
            self.persist_output = env_persist
        else:
            self.persist_output = persist_output

        self.output_dir = output_dir or Path(".data/collector")
        if self.persist_output:
            self.output_dir.mkdir(parents=True, exist_ok=True)

        self.adapter_metadata = adapter_metadata or {}
        self.schema_validator = CollectorSchemaValidator()

    @staticmethod
    def _instantiate_adapter(registry, name: str, kwargs: Dict[str, Any]):
        adapter_cls = registry.get(name)
        return adapter_cls(**kwargs)

    async def collect(self, requests: Iterable[CollectorRequest]) -> CollectorResult:
        """Process the provided requests and return the aggregated result."""

        result = CollectorResult()

        for request in requests:
            try:
                raw_doc = await self.scraper.fetch(request.url)
                combined_metadata = {
                    **(request.metadata or {}),
                    **(raw_doc.metadata or {}),
                }
                if (
                    "source_type" not in combined_metadata
                    and "source_type" in self.adapter_metadata
                ):
                    combined_metadata["source_type"] = self.adapter_metadata["source_type"]
                raw_doc.metadata = combined_metadata

                cleaned_text = self.cleaner.clean(raw_doc)
                chunks = self.chunker.split(cleaned_text, combined_metadata)

                if not chunks:
                    raise RuntimeError("Chunker returned no chunks for document")

                chunk_metadata = self._build_chunk_metadata(chunks)
                try:
                    self._validate_chunk_metadata(chunk_metadata)
                except CollectorValidationError as exc:
                    raise RuntimeError(
                        f"Chunk metadata validation failed: {exc}"
                    ) from exc

                if self.docstore:
                    await self.docstore.add(chunks)

                persisted_path = None
                if self.persist_output:
                    persisted_path = self._persist_document(
                        request=request,
                        raw_doc=raw_doc,
                        cleaned_text=cleaned_text,
                        chunks=chunks,
                        chunk_metadata=chunk_metadata,
                    )

                processed = ProcessedDocument(
                    source_id=request.source_id,
                    url=request.url,
                    metadata=combined_metadata,
                    raw_document=raw_doc,
                    cleaned_text=cleaned_text,
                    chunks=chunks,
                    persisted_path=persisted_path,
                    chunk_metadata=chunk_metadata,
                )
                result.documents.append(processed)

            except Exception as exc:  # noqa: BLE001 broad but intentional here
                result.errors.append(
                    CollectorError(url=request.url, message=str(exc))
                )

        try:
            catalog = self._build_catalog(result.documents)
            if catalog is not None:
                self.schema_validator.validate_catalog(catalog)
                result.catalog = catalog
                if self.persist_output:
                    catalog_path = self.output_dir / "catalog.json"
                    catalog_path.write_text(
                        json.dumps(catalog, indent=2),
                        encoding="utf-8",
                    )
        except CollectorValidationError as exc:
            raise RuntimeError(f"Catalog validation failed: {exc}") from exc

        return result

    def _persist_document(
        self,
        *,
        request: CollectorRequest,
        raw_doc: RawDoc,
        cleaned_text: str,
        chunks: List[Chunk],
        chunk_metadata: List[Dict[str, Any]],
    ) -> Path:
        """Persist document artefacts to disk and return the directory path.

        The current implementation writes a minimal structure intended to be
        replaced with standards-compliant persistence in a later iteration.
        """

        doc_id = request.source_id or raw_doc.metadata.get("document_id")
        safe_id = (doc_id or os.urandom(8).hex()).replace("/", "_")

        doc_dir = self.output_dir / safe_id
        chunks_dir = doc_dir / "chunks"
        doc_dir.mkdir(parents=True, exist_ok=True)
        chunks_dir.mkdir(parents=True, exist_ok=True)

        # Write cleaned text for inspection (temporary compatibility feature).
        cleaned_path = doc_dir / "cleaned.txt"
        cleaned_path.write_text(cleaned_text, encoding="utf-8")

        # Store chunk payloads as simple JSON lines for now.
        chunks_path = chunks_dir / "chunks.jsonl"
        with chunks_path.open("w", encoding="utf-8") as handle:
            for chunk in chunks:
                payload = {
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "text": chunk.text,
                    "position": chunk.position,
                    "token_count": chunk.token_count,
                    "section_path": chunk.section_path,
                    "metadata": chunk.metadata,
                }
                handle.write(json.dumps(payload))
                handle.write("\n")

        metadata_path = chunks_dir / "chunk_metadata.jsonl"
        with metadata_path.open("w", encoding="utf-8") as handle:
            for metadata in chunk_metadata:
                handle.write(json.dumps(metadata))
                handle.write("\n")

        # Build and validate document metadata
        document_metadata_payload = self._build_document_metadata(
            request=request,
            raw_doc=raw_doc,
            chunks=chunks,
            safe_id=safe_id,
        )
        try:
            self.schema_validator.validate_document_metadata(document_metadata_payload)
        except CollectorValidationError as exc:
            raise RuntimeError(
                f"Document metadata validation failed: {exc}"
            ) from exc

        document_metadata_path = doc_dir / "document_metadata.json"
        document_metadata_path.write_text(
            json.dumps(document_metadata_payload, indent=2),
            encoding="utf-8",
        )

        # Validate and persist processing metadata if available
        processing_metadata = raw_doc.metadata.get("processing_metadata")
        if processing_metadata:
            try:
                self.schema_validator.validate_processing_metadata(processing_metadata)
            except CollectorValidationError as exc:
                raise RuntimeError(
                    f"Processing metadata validation failed: {exc}"
                ) from exc

            processing_metadata_path = doc_dir / "processing_metadata.json"
            processing_metadata_path.write_text(
                json.dumps(processing_metadata, indent=2),
                encoding="utf-8",
            )

        return doc_dir

    def _build_document_metadata(
        self,
        *,
        request: CollectorRequest,
        raw_doc: RawDoc,
        chunks: List[Chunk],
        safe_id: str,
    ) -> Dict[str, Any]:
        """Build standards-compliant document metadata payload."""
        metadata = raw_doc.metadata or {}
        document_id = (
            chunks[0].document_id if chunks else safe_id
        )

        # Calculate file hash if not present
        file_hash = metadata.get("file_hash_sha256", "")
        if not file_hash and raw_doc.content:
            import hashlib
            file_hash = hashlib.sha256(raw_doc.content).hexdigest()

        payload: Dict[str, Any] = {
            "document_id": document_id,
            "source_type": metadata.get("source_type", "other"),
            "original_url": request.url,
            "title": metadata.get("title", ""),
            "file_hash": file_hash,
            "file_size": metadata.get("content_length", len(raw_doc.content) if raw_doc.content else 0),
            "processing_timestamp": datetime.now(timezone.utc).isoformat(),
            "adapter_version": self.adapter_metadata.get("adapter_version", "0.0.0"),
        }

        # Optional fields
        if "authors" in metadata and metadata["authors"]:
            payload["authors"] = metadata["authors"]
        if "publication_date" in metadata:
            payload["publication_date"] = metadata["publication_date"]
        if "subject_categories" in metadata:
            payload["subject_categories"] = metadata["subject_categories"]
        if "language" in metadata:
            payload["language"] = metadata["language"]

        return payload

    @staticmethod
    def _build_chunk_metadata(chunks: List[Chunk]) -> List[Dict[str, Any]]:
        total_chunks = len(chunks)
        metadata_list: List[Dict[str, Any]] = []
        for index, chunk in enumerate(chunks):
            features = chunk.metadata.get("content_features", {}) if chunk.metadata else {}
            payload: Dict[str, Any] = {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "chunk_index": index,
                "total_chunks": total_chunks,
                "token_count": chunk.token_count,
                "character_count": len(chunk.text),
                "contains_equations": bool(features.get("equation_count")),
                "contains_tables": bool(features.get("table_count")),
            }
            if chunk.section_path:
                payload["section_hierarchy"] = chunk.section_path
            chunk_type = (chunk.metadata or {}).get("chunk_type")
            if chunk_type:
                payload["chunk_type"] = chunk_type
            metadata_list.append(payload)
        return metadata_list

    def _validate_chunk_metadata(self, metadata: List[Dict[str, Any]]) -> None:
        for payload in metadata:
            self.schema_validator.validate_chunk_metadata(payload)

    def _build_catalog(self, documents: List[ProcessedDocument]) -> Optional[Dict[str, Any]]:
        adapter_version = self.adapter_metadata.get("adapter_version", "0.0.0")
        creation_timestamp = datetime.now(timezone.utc).isoformat()

        catalog_documents: List[Dict[str, Any]] = []
        source_distribution: Dict[str, int] = {}
        total_chunks = 0

        for doc in documents:
            if not doc.chunks:
                continue
            document_id = doc.chunks[0].document_id
            source_type = doc.metadata.get("source_type", "other")
            source_distribution[source_type] = source_distribution.get(source_type, 0) + 1
            chunk_count = len(doc.chunks)
            total_chunks += chunk_count
            file_path: str
            if doc.persisted_path:
                try:
                    file_path = str(doc.persisted_path.relative_to(self.output_dir))
                except ValueError:
                    file_path = str(doc.persisted_path)
            else:
                file_path = f"in-memory://{document_id}"

            catalog_documents.append(
                {
                    "document_id": document_id,
                    "source_type": source_type,
                    "title": doc.metadata.get("title", ""),
                    "chunk_count": chunk_count,
                    "file_path": file_path,
                }
            )

        total_documents = len(catalog_documents)

        catalog: Dict[str, Any] = {
            "creation_timestamp": creation_timestamp,
            "adapter_version": adapter_version,
            "total_documents": total_documents,
            "total_chunks": total_chunks,
            "documents": catalog_documents,
        }

        if source_distribution:
            catalog["source_distribution"] = source_distribution

        return catalog


__all__ = [
    "CollectorPipeline",
    "CollectorRequest",
    "CollectorResult",
    "ProcessedDocument",
    "CollectorError",
]

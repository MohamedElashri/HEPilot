"""Port adapter implementations for the ArXiv collector.

These classes provide concrete implementations of the collector ports
(`Scraper`, `Cleaner`, `Chunker`, `DocStore`) so the generic
`CollectorPipeline` can orchestrate ingestion without bespoke logic.
"""

from __future__ import annotations

import asyncio
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4, uuid5, NAMESPACE_URL

import requests

from src.collector.config import ProcessingConfig
from src.collector.ports import Chunk, Chunker, Cleaner, DocStore, RawDoc, Scraper

from .chunking import ArxivChunker as LegacyArxivChunker
from .models import AcquiredDocument, ChunkContent
from .processing import ArxivProcessor


class ArxivScraper(Scraper):
    """Fetch ArXiv PDFs over HTTP."""

    def __init__(
        self,
        *,
        timeout_seconds: int = 120,
        user_agent: str = "HEPilot-ArXiv-Collector/1.0",
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    async def fetch(self, url: str) -> RawDoc:
        content, content_type = await asyncio.to_thread(self._fetch_sync, url)
        metadata = {
            "source_url": url,
            "content_length": len(content),
        }
        return RawDoc(
            url=url,
            content=content,
            content_type=content_type or "application/pdf",
            metadata=metadata,
            fetched_at=datetime.now(timezone.utc),
        )

    def _fetch_sync(self, url: str) -> tuple[bytes, Optional[str]]:
        response = self.session.get(url, timeout=self.timeout_seconds)
        response.raise_for_status()
        return response.content, response.headers.get("Content-Type")


class ArxivCleaner(Cleaner):
    """Convert raw PDF bytes to cleaned markdown text."""

    def __init__(
        self,
        *,
        processing_config: Optional[ProcessingConfig] = None,
    ) -> None:
        self.processing_config = processing_config or ProcessingConfig(
            chunk_size=512,
            chunk_overlap=0.1,
            preserve_tables=True,
            preserve_equations=True,
        )
        extras = self.processing_config.extras
        self.processor = ArxivProcessor(
            preserve_tables=self.processing_config.preserve_tables,
            preserve_equations=self.processing_config.preserve_equations,
            enrich_formulas=extras.get("enrich_formulas", True),
            table_mode=extras.get("table_mode", "fast"),
            exclude_references=extras.get("exclude_references", True),
            exclude_acknowledgments=extras.get("exclude_acknowledgments", True),
            exclude_author_lists=extras.get("exclude_author_lists", True),
            processing_timeout=extras.get("processing_timeout", 0),
        )

    def clean(self, raw: RawDoc) -> str:
        document_uuid = _document_uuid(raw)
        with TemporaryDirectory(prefix="hepilot-arxiv-") as tmp_dir:
            tmp_dir_path = Path(tmp_dir)
            pdf_path = tmp_dir_path / "document.pdf"
            pdf_path.write_bytes(raw.content)

            sha256 = hashlib.sha256(raw.content).hexdigest()
            sha512 = hashlib.sha512(raw.content).hexdigest()

            acquired = AcquiredDocument(
                document_id=document_uuid,
                local_path=str(pdf_path),
                file_hash_sha256=sha256,
                file_hash_sha512=sha512,
                file_size=len(raw.content),
                download_timestamp=datetime.now(timezone.utc),
                download_status="success",
                retry_count=0,
                validation_status="passed",
                arxiv_id=raw.metadata.get("arxiv_id"),
                arxiv_version=raw.metadata.get("arxiv_version"),
            )

            output_dir = tmp_dir_path / "processed"
            output_dir.mkdir(parents=True, exist_ok=True)
            markdown_path, proc_metadata = self.processor.process(acquired, output_dir)

            if not markdown_path or not markdown_path.exists():
                raise RuntimeError("ArxivProcessor failed to generate markdown output")

            # Attach processing metadata to raw doc for pipeline validation/persistence
            raw.metadata["processing_metadata"] = {
                "processor_used": proc_metadata.processor_used,
                "processing_timestamp": proc_metadata.processing_timestamp.isoformat(),
                "processing_duration": proc_metadata.processing_duration,
                "conversion_warnings": proc_metadata.conversion_warnings,
            }

            return markdown_path.read_text(encoding="utf-8")


class ArxivChunkerAdapter(Chunker):
    """Transform markdown text into token-aware chunks."""

    def __init__(
        self,
        *,
        chunk_size: int = 512,
        chunk_overlap: float = 0.1,
        model_name: str = "BAAI/bge-large-en-v1.5",
        use_model_tokenizer: bool = True,
        cache_dir: str = ".model_cache",
    ) -> None:
        self.chunker = LegacyArxivChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            model_name=model_name,
            use_model_tokenizer=use_model_tokenizer,
            cache_dir=cache_dir,
        )

    def split(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        document_uuid = _document_uuid_from_metadata(metadata)
        with TemporaryDirectory(prefix="hepilot-chunks-") as tmp_dir:
            markdown_path = Path(tmp_dir) / "document.md"
            markdown_path.write_text(text, encoding="utf-8")
            chunk_contents = self.chunker.chunk(markdown_path, document_uuid)

        return [_convert_chunk(content, metadata) for content in chunk_contents]


class ArxivInMemoryDocStore(DocStore):
    """Simple in-memory store used primarily for testing flows."""

    def __init__(self) -> None:
        self._chunks: Dict[str, Chunk] = {}

    async def add(self, chunks: List[Chunk]) -> None:
        for chunk in chunks:
            self._chunks[chunk.id] = chunk

    async def get(self, chunk_id: str) -> Optional[Chunk]:
        return self._chunks.get(chunk_id)


def _document_uuid(raw: RawDoc) -> UUID:
    meta = raw.metadata or {}
    if "document_id" in meta:
        try:
            return UUID(str(meta["document_id"]))
        except Exception:
            pass
    if "source_id" in meta:
        return uuid5(NAMESPACE_URL, str(meta["source_id"]))
    return uuid5(NAMESPACE_URL, raw.url)


def _document_uuid_from_metadata(metadata: Dict[str, Any]) -> UUID:
    if "document_id" in metadata:
        try:
            return UUID(str(metadata["document_id"]))
        except Exception:
            pass
    if "source_id" in metadata:
        return uuid5(NAMESPACE_URL, str(metadata["source_id"]))
    return uuid4()


def _convert_chunk(chunk: ChunkContent, doc_metadata: Dict[str, Any]) -> Chunk:
    metadata: Dict[str, Any] = {
        "chunk_type": chunk.chunk_type,
        "content_features": chunk.content_features,
        "source_url": doc_metadata.get("source_url"),
        "title": doc_metadata.get("title"),
        "authors": doc_metadata.get("authors"),
        "arxiv_id": doc_metadata.get("arxiv_id"),
        "arxiv_version": doc_metadata.get("arxiv_version"),
    }

    return Chunk(
        id=str(chunk.chunk_id),
        document_id=str(chunk.document_id),
        text=chunk.content,
        position=chunk.chunk_index,
        token_count=chunk.token_count,
        section_path=chunk.section_path or [],
        metadata=metadata,
    )


__all__ = [
    "ArxivScraper",
    "ArxivCleaner",
    "ArxivChunkerAdapter",
    "ArxivInMemoryDocStore",
]

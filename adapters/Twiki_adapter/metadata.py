"""
Metadata manager for generating TWiki document metadata and catalog. 

Creates document_metadata.json, catalog.json, and maintains processing_log.json
according to the given schemas. 
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID 
from adapters.Twiki_adapter.models import DiscoveredDocument, AcquiredDocument, DocumentMetadata, LogEntry


class TwikiMetadataManager:
    """Manages metadata generation and catalog maintenance for Twiki documents."""

    def __init__(self, adapter_version: str = "1.0.0") -> None:
        self.adapter_version: str = adapter_version
        self.log_entries: List[LogEntry] = []

    def create_document_metadata(
            self,
            discovered: DiscoveredDocument,
            acquired: AcquiredDocument,
            markdown_path: Path
    ) -> DocumentMetadata:
        # creating metadata for a Twiki document.

        title: str = self._extract_title(markdown_path)
        experiment_tags: List[str] = ["LHCb"]
        collaboration: str = "LHCb Collaboration"

        return DocumentMetadata(
            document_id = discovered.document_id,
            source_type="twiki",
            original_url=discovered.source_url,
            local_path=acquired.local_path, 
            title=title, 
            authors=None, # hoping there is none listed
            publication_date=None, # I personally could not find anything
            subject_categories=["lhcb", "detector", "documentation"],
            language="en",
            file_hash=acquired.file_hash_sha256,
            file_size=acquired.file_size, 
            processing_timestamp=datetime.now(timezone.utc),
            adapter_version=self.adapter_version,
            experiment_tags=experiment_tags,
            collaboration=collaboration, 
            license="CERN Twiki Terms of Use"
        )
    
    def _extract_title(self, markdown_path: Path) -> str:
        # Extract title from markdown or filename
        try: 
            with open(markdown_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#'):
                    return first_line.lstrip('#').strip()
        
        except Exception:
            pass
        return markdown_path.stem
    
    def save_document_metadata(self, metadata: DocumentMetadata, output_path: Path) -> None:
        # saving document metadata to JSON
        data: Dict[str, Any] = {
            k: v for k, v in {
                "document_id": str(metadata.document_id),
                "source_type": metadata.source_type,
                "original_url": metadata.original_url,
                "local_path": metadata.local_path,
                "title": metadata.title, 
                "authors": metadata.authors,
                "publication_date": metadata.publication_date, 
                "subject_categories": metadata.subject_categories,
                "language": metadata.language,
                "file_hash": metadata.file_hash,
                "file_size": metadata.file_size,
                "processing_timestamp": metadata.processing_timestamp.isoformat(),
                "adapter_version": metadata.adapter_version,
                "experiment_tags": metadata.experiment_tags,
                "collaboration": metadata.collaboration,
                "license": metadata.license
            }.items() if v is not None
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def create_catalog_entry(self, metadata: DocumentMetadata, chunk_count: int) -> Dict[str, Any]:

        return {
            "document_id": str(metadata.document_id),
            "title": metadata.title,
            "source_type": metadata.source_type,
            "source_url": metadata.original_url,
            "chunk_count": chunk_count,
            "processing_timestamp": metadata.processing_timestamp.isoformat(),
            "adapter_version": metadata.adapter_version
        }
    
    def save_catalog(self, entries: List[Dict[str, Any]], output_path: Path) -> None:
        catalog_data: Dict[str, Any] = {
            "catalog_version": "1.0",
            "document_count": len(entries),
            "documents": entries
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(catalog_data, f, indent=2)
    
    def log(self, level: str, component: str, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Add structured log entry."""
        entry: LogEntry = LogEntry(
            timestamp=datetime.now(timezone.utc),
            level=level,
            component=component,
            message=message,
            context=context
        )
        self.log_entries.append(entry)

    def save_log(self, output_path: Path) -> None:
        """Write processing_log.json."""
        log_data = [
            {
                "timestamp": e.timestamp.isoformat(),
                "level": e.level,
                "component": e.component,
                "message": e.message,
                "context": e.context
            }
            for e in self.log_entries
        ]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2)



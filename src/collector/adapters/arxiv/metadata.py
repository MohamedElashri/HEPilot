"""
Metadata manager for generating comprehensive document metadata and catalog.

Creates document_metadata.json, catalog.json, and maintains processing_log.json
according to HEPilot specification schemas.
"""

import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID
from .models import DiscoveredDocument, AcquiredDocument, DocumentMetadata, LogEntry


class MetadataManager:
    """Manages metadata generation and catalog maintenance."""
    
    def __init__(self, adapter_version: str = "1.0.0", include_authors: bool = False) -> None:
        """
        Initialize metadata manager.
        
        Args:
            adapter_version: Version of the adapter
            include_authors: Whether to include authors in metadata
        """
        self.adapter_version: str = adapter_version
        self.include_authors: bool = include_authors
        self.log_entries: List[LogEntry] = []
    
    def create_document_metadata(
        self,
        discovered: DiscoveredDocument,
        acquired: AcquiredDocument,
        markdown_path: Path
    ) -> DocumentMetadata:
        """
        Create comprehensive document metadata.
        
        Args:
            discovered: Discovery information
            acquired: Acquisition information
            markdown_path: Path to processed markdown
            
        Returns:
            Document metadata object
        """
        arxiv_id: str = self._extract_arxiv_id(discovered.source_url)
        categories: List[str] = self._extract_categories(arxiv_id)
        publication_date: Optional[str] = None
        experiment_tags: List[str] = self._detect_experiments(discovered.title)
        authors_list: Optional[List[str]] = discovered.authors if self.include_authors else None
        return DocumentMetadata(
            document_id=discovered.document_id,
            source_type="arxiv",
            original_url=discovered.source_url,
            local_path=acquired.local_path,
            title=discovered.title,
            authors=authors_list,
            publication_date=publication_date,
            subject_categories=categories,
            language="en",
            file_hash=acquired.file_hash_sha256,
            file_size=acquired.file_size,
            processing_timestamp=datetime.now(timezone.utc),
            adapter_version=self.adapter_version,
            experiment_tags=experiment_tags if experiment_tags else None,
            collaboration=self._detect_collaboration(discovered.title, discovered.authors or []),
            license="arXiv.org perpetual license",
            arxiv_id=discovered.arxiv_id,
            arxiv_version=discovered.arxiv_version
        )
    
    def _extract_arxiv_id(self, url: str) -> str:
        """
        Extract arXiv ID from URL.
        
        Args:
            url: arXiv URL
            
        Returns:
            arXiv ID
        """
        match = re.search(r'(\d{4}\.\d{4,5})', url)
        if match:
            return match.group(1)
        return "unknown"
    
    def _extract_categories(self, arxiv_id: str) -> List[str]:
        """
        Extract subject categories from arXiv ID.
        
        Args:
            arxiv_id: arXiv identifier
            
        Returns:
            List of categories
        """
        return ["hep-ex"]
    
    def _detect_experiments(self, title: str) -> List[str]:
        """
        Detect HEP experiments mentioned in title.
        
        Args:
            title: Document title
            
        Returns:
            List of experiment tags
        """
        experiments: Dict[str, str] = {
            'lhcb': 'LHCb',
            'atlas': 'ATLAS',
            'cms': 'CMS',
            'alice': 'ALICE',
            'belle': 'Belle',
            'babar': 'BaBar',
        }
        title_lower: str = title.lower()
        detected: List[str] = []
        for key, value in experiments.items():
            if key in title_lower:
                detected.append(value)
        return detected
    
    def _detect_collaboration(self, title: str, authors: List[str]) -> Optional[str]:
        """
        Detect collaboration from title or authors.
        
        Args:
            title: Document title
            authors: List of authors
            
        Returns:
            Collaboration name or None
        """
        collaborations: List[str] = [
            'LHCb Collaboration',
            'ATLAS Collaboration',
            'CMS Collaboration',
            'ALICE Collaboration',
        ]
        title_lower: str = title.lower()
        for collab in collaborations:
            if collab.lower() in title_lower:
                return collab
        for author in authors:
            if 'collaboration' in author.lower():
                return author
        return None
    
    def save_document_metadata(self, metadata: DocumentMetadata, output_path: Path) -> None:
        """
        Save document metadata to JSON file.
        
        Args:
            metadata: Document metadata
            output_path: Path to output JSON file
        """
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
                "license": metadata.license,
                "arxiv_id": metadata.arxiv_id,
                "arxiv_version": metadata.arxiv_version
            }.items() if v is not None
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def create_catalog_entry(self, metadata: DocumentMetadata, chunk_count: int) -> Dict[str, Any]:
        """
        Create catalog entry for a processed document.
        
        Args:
            metadata: Document metadata
            chunk_count: Number of chunks created
            
        Returns:
            Catalog entry dictionary
        """
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
        """
        Save catalog to JSON file.
        
        Args:
            entries: List of catalog entries
            output_path: Path to catalog.json
        """
        catalog_data: Dict[str, Any] = {
            "catalog_version": "1.0",
            "document_count": len(entries),
            "documents": entries
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(catalog_data, f, indent=2)
    
    def log(self, level: str, component: str, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Add structured log entry.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            component: Component name
            message: Log message
            context: Additional context data
        """
        entry: LogEntry = LogEntry(
            timestamp=datetime.now(timezone.utc),
            level=level,
            component=component,
            message=message,
            context=context
        )
        self.log_entries.append(entry)
    
    def save_log(self, output_path: Path) -> None:
        """
        Save processing log to JSON file.
        
        Args:
            output_path: Path to processing_log.json
        """
        log_data: List[Dict[str, Any]] = [
            {
                "timestamp": entry.timestamp.isoformat(),
                "level": entry.level,
                "component": entry.component,
                "message": entry.message,
                "context": entry.context
            }
            for entry in self.log_entries
        ]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2)

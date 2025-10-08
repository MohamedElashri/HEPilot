"""
Discovery module for searching and identifying ArXiv papers.

Uses the arXiv API to search for High-Energy Physics papers
and generates discovery output compliant with HEPilot schema.
"""

import arxiv
import uuid
import json
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone
from pathlib import Path
from models import DiscoveredDocument
from cache_manager import CacheManager


class ArxivDiscovery:
    """Discovers HEP papers from arXiv API."""
    
    def __init__(self, max_results: Optional[int] = None, include_authors: bool = False) -> None:
        """
        Initialize ArXiv discovery module.
        
        Args:
            max_results: Maximum number of papers to discover (None for unlimited)
            include_authors: Whether to include author lists in discovery output
        """
        self.max_results: Optional[int] = max_results
        self.include_authors: bool = include_authors
        self.client: arxiv.Client = arxiv.Client()
    
    def search(self, query: str = "cat:hep-ex OR cat:hep-ph") -> List[DiscoveredDocument]:
        """
        Search arXiv for papers matching query.
        
        Args:
            query: arXiv API query string
            
        Returns:
            List of discovered documents
        """
        discovered: List[DiscoveredDocument] = []
        search: arxiv.Search = arxiv.Search(
            query=query,
            max_results=self.max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        for result in self.client.results(search):
            if self._is_redacted(result):
                continue
            doc: DiscoveredDocument = self._result_to_document(result)
            discovered.append(doc)
        return discovered
    
    def _is_redacted(self, result: arxiv.Result) -> bool:
        """
        Check if a paper is withdrawn or redacted.
        
        Args:
            result: arXiv search result
            
        Returns:
            True if paper is redacted/withdrawn
        """
        title_lower: str = result.title.lower()
        return any([
            'withdrawn' in title_lower,
            'redacted' in title_lower,
            result.title.startswith('[REDACTED]'),
        ])
    
    def _result_to_document(self, result: arxiv.Result) -> DiscoveredDocument:
        """
        Convert arXiv result to DiscoveredDocument.
        
        Args:
            result: arXiv search result
            
        Returns:
            Discovered document model
        """
        arxiv_id, version = CacheManager.extract_arxiv_id_and_version(result.pdf_url)
        if arxiv_id is None:
            doc_id: uuid.UUID = uuid.uuid4()
        else:
            doc_id: uuid.UUID = CacheManager.generate_stable_document_id(arxiv_id)
        authors: Optional[List[str]] = None
        if self.include_authors:
            authors = [author.name for author in result.authors]
        estimated_size: int = self._estimate_pdf_size(result)
        return DiscoveredDocument(
            document_id=doc_id,
            source_type="arxiv",
            source_url=result.pdf_url,
            title=result.title,
            authors=authors,
            discovery_timestamp=datetime.now(timezone.utc),
            estimated_size=estimated_size,
            content_type="application/pdf",
            priority_score=None,
            arxiv_id=arxiv_id,
            arxiv_version=version
        )
    
    def _estimate_pdf_size(self, result: arxiv.Result) -> int:
        """
        Estimate PDF size based on abstract length.
        
        Args:
            result: arXiv search result
            
        Returns:
            Estimated size in bytes
        """
        base_size: int = 500_000
        abstract_factor: float = len(result.summary) / 200.0
        return int(base_size * (1.0 + abstract_factor * 0.5))
    
    def save_discovery_output(self, documents: List[DiscoveredDocument], output_path: Path) -> None:
        """
        Save discovery output to JSON file.
        
        Args:
            documents: List of discovered documents
            output_path: Path to output JSON file
        """
        output_data: Dict[str, Any] = {
            "discovered_documents": [
                {
                    k: v for k, v in {
                        "document_id": str(doc.document_id),
                        "source_type": doc.source_type,
                        "source_url": doc.source_url,
                        "title": doc.title,
                        "authors": doc.authors,
                        "discovery_timestamp": doc.discovery_timestamp.isoformat(),
                        "estimated_size": doc.estimated_size,
                        "content_type": doc.content_type,
                        "arxiv_id": doc.arxiv_id,
                        "arxiv_version": doc.arxiv_version
                    }.items() if v is not None
                }
                for doc in documents
            ]
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)

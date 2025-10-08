"""
Discovery module for searching and identifying ArXiv papers.

Uses the arXiv API to search for High-Energy Physics papers
and generates discovery output compliant with HEPilot schema.
"""

import uuid
import json
import requests
import xml.etree.ElementTree as ET
import time
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
            max_results: Maximum number of papers to discover (None for All)
            include_authors: Whether to include author lists in discovery output
        """
        self.max_results: Optional[int] = max_results
        self.include_authors: bool = include_authors
        self.api_url: str = "https://export.arxiv.org/api/query"
        self.page_size: int = 100
        self.delay_seconds: float = 3.0
        self.session: requests.Session = requests.Session()
        self.session.headers.update({"User-Agent": "HEPilot-ArXiv-Adapter/1.0"})
    
    def search(self, query: str = "cat:hep-ex OR cat:hep-ph") -> List[DiscoveredDocument]:
        """
        Search arXiv for papers matching query.
        
        Args:
            query: arXiv API query string
            
        Returns:
            List of discovered documents
        """
        discovered: List[DiscoveredDocument] = []
        start: int = 0
        total_fetched: int = 0
        
        while True:
            if self.max_results and total_fetched >= self.max_results:
                break
            
            results, total_results = self._fetch_page(query, start)
            
            if not results:
                break
            
            for result in results:
                if self.max_results and total_fetched >= self.max_results:
                    break
                    
                if self._is_redacted_entry(result):
                    continue
                    
                doc: DiscoveredDocument = self._entry_to_document(result)
                discovered.append(doc)
                total_fetched += 1
            
            start += len(results)
            
            if start >= total_results:
                break
            
            time.sleep(self.delay_seconds)
        
        return discovered
    
    def _fetch_page(self, query: str, start: int) -> Tuple[List[ET.Element], int]:
        """
        Fetch a single page of results from ArXiv API.
        
        Args:
            query: Search query
            start: Starting index
            
        Returns:
            Tuple of (list of entry elements, total_results)
        """
        import logging
        logger = logging.getLogger(__name__)
        
        params: Dict[str, Any] = {
            "search_query": query,
            "start": start,
            "max_results": self.page_size,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        
        logger.info(f"Requesting page (start: {start}, max: {self.page_size}): {self.api_url}")
        
        try:
            response: requests.Response = self.session.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()
            
            root: ET.Element = ET.fromstring(response.content)
            
            ns = {"atom": "http://www.w3.org/2005/Atom", 
                  "opensearch": "http://a9.com/-/spec/opensearch/1.1/"}
            
            total_results_elem = root.find("opensearch:totalResults", ns)
            total_results: int = int(total_results_elem.text) if total_results_elem is not None else 0
            
            entries: List[ET.Element] = root.findall("atom:entry", ns)
            
            logger.info(f"Got page: {len(entries)} entries, {total_results} total results")
            
            return entries, total_results
            
        except Exception as e:
            import logging
            logging.error(f"Error fetching ArXiv page: {e}")
            return [], 0
    
    def _is_redacted_entry(self, entry: ET.Element) -> bool:
        """
        Check if a paper is withdrawn or redacted.
        
        Args:
            entry: XML entry element
            
        Returns:
            True if paper is redacted/withdrawn
        """
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        title_elem = entry.find("atom:title", ns)
        if title_elem is None:
            return True
        
        title_lower: str = title_elem.text.lower() if title_elem.text else ""
        return any([
            'withdrawn' in title_lower,
            'redacted' in title_lower,
            title_lower.startswith('[redacted]'),
        ])
    
    def _entry_to_document(self, entry: ET.Element) -> DiscoveredDocument:
        """
        Convert arXiv XML entry to DiscoveredDocument.
        
        Args:
            entry: XML entry element
            
        Returns:
            Discovered document model
        """
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        
        title_elem = entry.find("atom:title", ns)
        title: str = title_elem.text.strip() if title_elem is not None and title_elem.text else "Unknown"
        
        pdf_link = None
        for link in entry.findall("atom:link", ns):
            if link.get("title") == "pdf":
                pdf_link = link.get("href")
                break
        
        if not pdf_link:
            id_elem = entry.find("atom:id", ns)
            if id_elem is not None and id_elem.text:
                pdf_link = id_elem.text.replace("/abs/", "/pdf/") + ".pdf"
        
        arxiv_id, version = CacheManager.extract_arxiv_id_and_version(pdf_link) if pdf_link else (None, None)
        
        if arxiv_id is None:
            doc_id: uuid.UUID = uuid.uuid4()
        else:
            doc_id: uuid.UUID = CacheManager.generate_stable_document_id(arxiv_id)
        
        authors: Optional[List[str]] = None
        if self.include_authors:
            authors = []
            for author in entry.findall("atom:author", ns):
                name_elem = author.find("atom:name", ns)
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text.strip())
        
        estimated_size: int = 500000
        
        return DiscoveredDocument(
            document_id=doc_id,
            source_type="arxiv",
            source_url=pdf_link or "",
            title=title,
            authors=authors,
            discovery_timestamp=datetime.now(timezone.utc),
            estimated_size=estimated_size,
            content_type="application/pdf",
            priority_score=None,
            arxiv_id=arxiv_id,
            arxiv_version=version
        )
    
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

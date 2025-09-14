#!/usr/bin/env python3
"""
Discovery Module for HEPilot ArXiv Adapter
Handles discovering LHCb papers from arXiv using both API and OAI-PMH interfaces.
"""

import asyncio
import logging
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

import aiohttp

from models import DocumentInfo
from unified_cache import UnifiedCache


class ArxivDiscovery:
    """Discovery module for arXiv papers containing LHCb."""
    
    def __init__(self, config: Dict[str, Any], output_dir: Path, cache: UnifiedCache = None):
        """Initialize the discovery module.
        
        Args:
            config: Adapter configuration dictionary
            output_dir: Output directory path
            cache: Unified cache instance (optional)
        """
        self.config = config
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache = cache or UnifiedCache(output_dir, Path(self.config["x_extension"]["cache_dir"]))
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def discover_documents(self, max_results: int = None) -> Dict[str, Any]:
        """Discover LHCb papers from arXiv.
        
        Args:
            max_results: Maximum number of results to return. If None, returns all available papers.
        
        Returns:
            Dictionary with discovered documents and rate limit information.
        """
        discovered_docs = []
        
        # Search via arXiv API - collect all papers when max_results is None
        api_docs = await self._search_arxiv_api(max_results=max_results)
        discovered_docs.extend(api_docs)
        
        # Search via OAI-PMH - collect all papers when max_results is None
        # Note: For simplicity, we're limiting OAI-PMH results when max_results is specified
        oai_max_results = None if max_results is None else (max_results // 2)
        oai_docs = await self._search_oai_pmh(max_results=oai_max_results)
        discovered_docs.extend(oai_docs)
        
        # Remove duplicates
        seen_ids = set()
        unique_docs = []
        for doc in discovered_docs:
            if doc.arxiv_id not in seen_ids:
                seen_ids.add(doc.arxiv_id)
                unique_docs.append(doc)
        
        # Apply max_results limit if specified
        result_docs = unique_docs
        if max_results is not None:
            result_docs = unique_docs[:max_results]
            
        self.logger.info(f"Discovered {len(result_docs)} unique papers out of {len(discovered_docs)} total")
        
        return {
            "rate_limit_status": {
                "limit": 1000,
                "remaining": 950,
                "reset_timestamp": datetime.now(timezone.utc).isoformat()
            },
            "discovered_documents": [self._doc_to_dict(doc) for doc in result_docs]
        }
    
    async def _search_arxiv_api(self, max_results: int = None) -> List[DocumentInfo]:
        """Search arXiv API for LHCb papers.
        
        Args:
            max_results: Maximum number of results to return. If None, returns all available papers.
            
        Returns:
            List of DocumentInfo objects for discovered papers.
        """
        query = 'abs:"lhcb" OR ti:"lhcb" OR abs:"LHCb" OR ti:"LHCb"'
        batch_size = 100  # arXiv API recommends a max of 100 results per request
        documents = []
        start = 0
        total_results_limit = max_results if max_results is not None else float('inf')
        
        while True:
            # Don't request more than needed if max_results is specified
            current_batch_size = min(batch_size, total_results_limit - len(documents)) if max_results is not None else batch_size
            
            if current_batch_size <= 0:
                break
                
            url = (f"http://export.arxiv.org/api/query?search_query={query}&start={start}"
                   f"&max_results={current_batch_size}&sortBy=submittedDate&sortOrder=descending")
            
            # Check cache first
            cached_content = self.cache.get_api_response(url)
            if cached_content:
                self.logger.info(f"Using cached content for {url}")
                content = cached_content
            else:
                self.logger.info(f"Fetching arXiv API results (batch {start}-{start+current_batch_size})")
                async with self.session.get(url) as response:
                    content = await response.text()
                    self.cache.set_api_response(url, content)
                # Respect arXiv API rate limits (3 seconds between requests)
                await asyncio.sleep(3)
                
            # Parse XML response
            root = ET.fromstring(content)
            ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
            
            batch_documents = []
            for entry in root.findall('atom:entry', ns):
                doc = self._parse_arxiv_entry(entry, ns)
                if doc:
                    batch_documents.append(doc)
            
            # If we got fewer results than requested, we've reached the end
            # But skip this check if we're using cached responses
            received_count = len(batch_documents)
            documents.extend(batch_documents)
            
            self.logger.info(f"Received {received_count} documents from arXiv API (total: {len(documents)})")
            
            # Stop if we got fewer results than requested or reached the limit
            if received_count < current_batch_size or (max_results is not None and len(documents) >= max_results):
                break
                
            # Move to next batch
            start += current_batch_size
            
        return documents
    
    async def _search_oai_pmh(self, max_results: int = None) -> List[DocumentInfo]:
        """Search arXiv OAI-PMH for LHCb papers.
        
        Args:
            max_results: Maximum number of results to return. If None, returns all available papers.
            
        Returns:
            List of DocumentInfo objects for discovered papers.
        """
        documents = []
        total_results_limit = max_results if max_results is not None else float('inf')
        resumption_token = None
        iteration = 0
        max_iterations = 10  # Safety limit to prevent infinite loops
        consecutive_empty_batches = 0
        
        while iteration < max_iterations:
            # Don't fetch more if we've already reached the limit
            if max_results is not None and len(documents) >= max_results:
                break
                
            # Stop if we've had too many consecutive empty batches
            if consecutive_empty_batches >= 3:
                self.logger.info("Stopping OAI-PMH search after 3 consecutive empty batches")
                break
                
            # Construct URL based on whether we have a resumption token
            if resumption_token:
                url = f"http://export.arxiv.org/oai2?verb=ListRecords&resumptionToken={resumption_token}"
            else:
                url = "http://export.arxiv.org/oai2?verb=ListRecords&metadataPrefix=oai_dc&set=physics:hep-ex"
            
            # Check cache first
            cached_content = self.cache.get_api_response(url)
            if cached_content:
                self.logger.info(f"Using cached content for {url}")
                content = cached_content
            else:
                try:
                    self.logger.info(f"Fetching OAI-PMH results (batch {iteration+1})")
                    async with self.session.get(url) as response:
                        content = await response.text()
                        self.cache.set_api_response(url, content)
                    # Respect OAI-PMH rate limits (2 seconds between requests)
                    await asyncio.sleep(2)
                except Exception as e:
                    self.logger.warning(f"OAI-PMH search failed: {e}")
                    break

            try:
                root = ET.fromstring(content)
                ns = {'oai': 'http://www.openarchives.org/OAI/2.0/', 'dc': 'http://purl.org/dc/elements/1.1/'}
                
                # Process records in this batch
                batch_documents = []
                for record in root.findall('.//oai:record', ns):
                    header = record.find('oai:header', ns)
                    if header is None or header.get('status') == 'deleted':
                        continue

                    metadata = record.find('oai:metadata', ns)
                    if metadata is None:
                        continue
                        
                    dc_metadata = metadata.find('dc:dc', ns)
                    if dc_metadata is None:
                        continue
                    
                    title_elem = dc_metadata.find('dc:title', ns)
                    if title_elem is None or title_elem.text is None:
                        continue
                    title = title_elem.text.strip()
                    
                    abstract_elem = dc_metadata.find('dc:description', ns)
                    abstract = ""
                    if abstract_elem is not None and abstract_elem.text is not None:
                        abstract = abstract_elem.text.strip()

                    if not self._contains_lhcb(title, abstract):
                        continue

                    identifier_elem = dc_metadata.find('dc:identifier', ns)
                    if identifier_elem is None or identifier_elem.text is None:
                        continue
                        
                    identifier = identifier_elem.text
                    # Try to extract arXiv ID
                    if '/' in identifier:
                        arxiv_id = identifier.split('/')[-1]
                    elif 'arxiv.org' in identifier:
                        arxiv_id = identifier.split('arxiv.org/')[-1]
                    else:
                        arxiv_id = identifier
                        
                    # Normalize arxiv_id to remove any version suffixes
                    if 'v' in arxiv_id and arxiv_id[arxiv_id.rfind('v')-1].isdigit():
                        arxiv_id = arxiv_id[:arxiv_id.rfind('v')]
                        
                    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                    
                    authors = []
                    for creator in dc_metadata.findall('dc:creator', ns):
                        if creator.text:
                            authors.append(creator.text)
                    
                    # Generate a deterministic document ID from the arXiv ID
                    document_id = str(uuid.uuid5(uuid.NAMESPACE_URL, arxiv_id))

                    doc = DocumentInfo(
                        document_id=document_id,
                        source_type="arxiv",
                        source_url=pdf_url,
                        title=title,
                        authors=authors,
                        discovery_timestamp=datetime.now(timezone.utc).isoformat(),
                        estimated_size=512*1024,  # Estimate 512KB
                        abstract=abstract,
                        arxiv_id=arxiv_id
                    )
                    batch_documents.append(doc)
                    
                    # Stop if we've reached the limit
                    if max_results is not None and len(documents) + len(batch_documents) >= max_results:
                        break
                
                # Add batch documents to our results
                documents.extend(batch_documents[:int(total_results_limit) - len(documents) if max_results is not None else None])
                self.logger.info(f"Found {len(batch_documents)} LHCb papers in OAI-PMH batch {iteration+1} (total: {len(documents)})")
                
                # Track consecutive empty batches
                if len(batch_documents) == 0:
                    consecutive_empty_batches += 1
                else:
                    consecutive_empty_batches = 0
                
                # Check for resumption token for next page
                resumption_token_elem = root.find('.//oai:resumptionToken', ns)
                resumption_token = resumption_token_elem.text if resumption_token_elem is not None and resumption_token_elem.text else None
                
                # If no resumption token or we've reached max, we're done
                if not resumption_token or (max_results is not None and len(documents) >= max_results):
                    break
                    
                iteration += 1

            except Exception as e:
                self.logger.warning(f"OAI-PMH parsing failed at iteration {iteration}: {e}")
                break
                
        return documents[:max_results] if max_results is not None else documents
    
    def _parse_arxiv_entry(self, entry, ns) -> Optional[DocumentInfo]:
        """Parse a single arXiv entry from API response.
        
        Args:
            entry: XML entry element
            ns: XML namespaces
            
        Returns:
            DocumentInfo object or None if not LHCb-related
        """
        try:
            title = entry.find('atom:title', ns).text.strip()
            summary = entry.find('atom:summary', ns).text.strip()
            
            # Check if LHCb is mentioned
            if not self._contains_lhcb(title, summary):
                return None
            
            arxiv_id = entry.find('atom:id', ns).text.split('/')[-1]
            
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns)
                if name is not None:
                    authors.append(name.text)
            
            pdf_url = None
            for link in entry.findall('atom:link', ns):
                if link.get('type') == 'application/pdf':
                    pdf_url = link.get('href')
                    break
            
            if not pdf_url:
                return None
            
            # Generate a deterministic document ID from the arXiv ID
            document_id = str(uuid.uuid5(uuid.NAMESPACE_URL, arxiv_id))

            return DocumentInfo(
                document_id=document_id,
                source_type="arxiv",
                source_url=pdf_url,
                title=title,
                authors=authors,
                discovery_timestamp=datetime.now(timezone.utc).isoformat(),
                estimated_size=1024*1024,  # Estimate 1MB
                abstract=summary,
                arxiv_id=arxiv_id
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing arXiv entry: {e}")
            return None
    
    def _contains_lhcb(self, title: str, abstract: str) -> bool:
        """Check if title or abstract contains LHCb.
        
        Args:
            title: Document title
            abstract: Document abstract
            
        Returns:
            True if LHCb is mentioned, False otherwise
        """
        text = f"{title} {abstract}".lower()
        return "lhcb" in text
    
    def _doc_to_dict(self, doc: DocumentInfo) -> Dict[str, Any]:
        """Convert DocumentInfo to specification-compliant dictionary.
        
        Args:
            doc: DocumentInfo object
            
        Returns:
            Dictionary representation of the document
        """
        doc_dict = {
            "document_id": doc.document_id,
            "source_type": doc.source_type,
            "source_url": doc.source_url,
            "title": doc.title,
            "authors": doc.authors,
            "discovery_timestamp": doc.discovery_timestamp,
            "estimated_size": doc.estimated_size,
            "content_type": doc.content_type,
            "priority_score": doc.priority_score
        }
        
        # Only include non-empty fields
        if doc.abstract:
            doc_dict["abstract"] = doc.abstract
        if doc.arxiv_id:
            doc_dict["arxiv_id"] = doc.arxiv_id
            
        return doc_dict

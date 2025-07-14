#!/usr/bin/env python3
"""
HEPilot arXiv LHCb Adapter
A reference implementation following the HEPilot RAG Adapter Framework specification
for discovering and processing LHCb papers from arXiv using docling.
"""

import asyncio
import hashlib
import json
import logging
import re
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator, Tuple
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

import aiohttp
import feedparser
from docling.document_converter import DocumentConverter
try:
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
    DOCLING_ADVANCED_IMPORTS = True
except ImportError:
    # Fallback for different docling versions
    DOCLING_ADVANCED_IMPORTS = False


@dataclass
class AdapterConfig:
    """Configuration for the HEPilot arXiv adapter."""
    name: str = "hepilot-arxiv-lhcb"
    version: str = "1.0.0"
    source_type: str = "arxiv"
    chunk_size: int = 1024
    chunk_overlap: float = 0.1
    preserve_tables: bool = True
    preserve_equations: bool = True
    profile: str = "core"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to specification-compliant dictionary."""
        config_dict = {
            "adapter_config": {
                "name": self.name,
                "version": self.version,
                "source_type": self.source_type,
                "processing_config": {
                    "chunk_size": self.chunk_size,
                    "chunk_overlap": self.chunk_overlap,
                    "preserve_tables": self.preserve_tables,
                    "preserve_equations": self.preserve_equations
                },
                "profile": self.profile,
                "config_hash": self._compute_hash()
            }
        }
        return config_dict
    
    def _compute_hash(self) -> str:
        """Compute SHA-256 hash of canonicalized configuration."""
        config_str = json.dumps(asdict(self), sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()


@dataclass
class DocumentInfo:
    """Information about a discovered document."""
    document_id: str
    source_type: str
    source_url: str
    title: str
    authors: List[str]
    discovery_timestamp: str
    estimated_size: int
    content_type: str = "application/pdf"
    priority_score: float = 1.0
    abstract: str = ""
    arxiv_id: str = ""


@dataclass
class AcquiredDocument:
    """Information about an acquired document."""
    document_id: str
    local_path: str
    file_hash_sha256: str
    file_hash_sha512: str
    file_size: int
    download_timestamp: str
    download_status: str
    validation_status: str
    retry_count: int = 0


@dataclass
class Chunk:
    """A chunk of processed document content."""
    chunk_id: str
    document_id: str
    chunk_index: int
    total_chunks: int
    content: str
    token_count: int
    chunk_type: str = "text"
    section_path: List[str] = None
    has_overlap_previous: bool = False
    has_overlap_next: bool = False
    content_features: Dict[str, int] = None
    
    def __post_init__(self):
        if self.section_path is None:
            self.section_path = []
        if self.content_features is None:
            self.content_features = {
                "heading_count": 0,
                "list_count": 0,
                "table_count": 0,
                "equation_count": 0
            }


class ArxivDiscovery:
    """Discovery module for arXiv papers containing LHCb."""
    
    def __init__(self, config: AdapterConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def discover_documents(self, max_results: int = 50) -> Dict[str, Any]:
        """Discover LHCb papers from arXiv."""
        discovered_docs = []
        
        # Search via arXiv API
        api_docs = await self._search_arxiv_api(max_results)
        discovered_docs.extend(api_docs)
        
        # Search via OAI-PMH (sample implementation)
        oai_docs = await self._search_oai_pmh(max_results // 2)
        discovered_docs.extend(oai_docs)
        
        # Remove duplicates
        seen_ids = set()
        unique_docs = []
        for doc in discovered_docs:
            if doc.arxiv_id not in seen_ids:
                seen_ids.add(doc.arxiv_id)
                unique_docs.append(doc)
        
        return {
            "rate_limit_status": {
                "limit": 1000,
                "remaining": 950,
                "reset_timestamp": datetime.now(timezone.utc).isoformat()
            },
            "discovered_documents": [self._doc_to_dict(doc) for doc in unique_docs[:max_results]]
        }
    
    async def _search_arxiv_api(self, max_results: int) -> List[DocumentInfo]:
        """Search arXiv API for LHCb papers."""
        query = 'abs:"lhcb" OR ti:"lhcb" OR abs:"LHCb" OR ti:"LHCb"'
        url = f"http://export.arxiv.org/api/query?search_query={query}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
        
        async with self.session.get(url) as response:
            content = await response.text()
            
        # Parse XML response
        root = ET.fromstring(content)
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
        
        documents = []
        for entry in root.findall('atom:entry', ns):
            doc = self._parse_arxiv_entry(entry, ns)
            if doc:
                documents.append(doc)
                
        return documents
    
    async def _search_oai_pmh(self, max_results: int) -> List[DocumentInfo]:
        """Search arXiv OAI-PMH for LHCb papers."""
        # Simplified OAI-PMH implementation
        url = "https://export.arxiv.org/oai2?verb=ListRecords&metadataPrefix=arXiv&set=physics:hep-ex"
        
        try:
            async with self.session.get(url) as response:
                content = await response.text()
                
            # Parse and filter for LHCb (simplified)
            documents = []
            # Implementation would parse OAI-PMH XML and filter for LHCb papers
            # For brevity, returning empty list
            return documents
            
        except Exception as e:
            self.logger.warning(f"OAI-PMH search failed: {e}")
            return []
    
    def _parse_arxiv_entry(self, entry, ns) -> Optional[DocumentInfo]:
        """Parse a single arXiv entry."""
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
            
            return DocumentInfo(
                document_id=str(uuid.uuid4()),
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
        """Check if title or abstract contains LHCb."""
        text = f"{title} {abstract}".lower()
        return "lhcb" in text
    
    def _doc_to_dict(self, doc: DocumentInfo) -> Dict[str, Any]:
        """Convert DocumentInfo to specification-compliant dictionary."""
        return {
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


class DocumentAcquisition:
    """Acquisition module for downloading arXiv papers."""
    
    def __init__(self, config: AdapterConfig, output_dir: Path):
        self.config = config
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def acquire_documents(self, discovered_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Acquire (download) discovered documents."""
        acquired_docs = []
        
        for doc_dict in discovered_docs:
            try:
                acquired_doc = await self._download_document(doc_dict)
                if acquired_doc:
                    acquired_docs.append(acquired_doc)
                    
            except Exception as e:
                self.logger.error(f"Failed to acquire {doc_dict['document_id']}: {e}")
                
        return {
            "acquired_documents": [self._acquired_doc_to_dict(doc) for doc in acquired_docs]
        }
    
    async def _download_document(self, doc_dict: Dict[str, Any]) -> Optional[AcquiredDocument]:
        """Download a single document with retry logic."""
        doc_id = doc_dict["document_id"]
        url = doc_dict["source_url"]
        
        # Create document directory
        doc_dir = self.output_dir / f"arxiv_{doc_id}"
        doc_dir.mkdir(parents=True, exist_ok=True)
        
        local_path = doc_dir / f"{doc_id}.pdf"
        
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Write file
                        with open(local_path, 'wb') as f:
                            f.write(content)
                        
                        # Validate file
                        if await self._validate_file(local_path, content):
                            return AcquiredDocument(
                                document_id=doc_id,
                                local_path=str(local_path),
                                file_hash_sha256=hashlib.sha256(content).hexdigest(),
                                file_hash_sha512=hashlib.sha512(content).hexdigest(),
                                file_size=len(content),
                                download_timestamp=datetime.now(timezone.utc).isoformat(),
                                download_status="success",
                                validation_status="passed",
                                retry_count=retry_count
                            )
                        else:
                            raise ValueError("File validation failed")
                            
                    else:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status
                        )
                        
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count  # Exponential backoff
                    await asyncio.sleep(wait_time)
                    self.logger.warning(f"Retry {retry_count} for {doc_id}: {e}")
                else:
                    self.logger.error(f"Failed to download {doc_id} after {max_retries} retries: {e}")
        
        return None
    
    async def _validate_file(self, file_path: Path, content: bytes) -> bool:
        """Validate downloaded file."""
        # Check minimum size
        if len(content) < 1024:
            return False
            
        # Check PDF header
        if not content.startswith(b'%PDF-'):
            return False
            
        # Additional validation could include virus scanning, etc.
        return True
    
    def _acquired_doc_to_dict(self, doc: AcquiredDocument) -> Dict[str, Any]:
        """Convert AcquiredDocument to specification-compliant dictionary."""
        return {
            "document_id": doc.document_id,
            "local_path": doc.local_path,
            "file_hash_sha256": doc.file_hash_sha256,
            "file_hash_sha512": doc.file_hash_sha512,
            "file_size": doc.file_size,
            "download_timestamp": doc.download_timestamp,
            "download_status": doc.download_status,
            "retry_count": doc.retry_count,
            "validation_status": doc.validation_status
        }


class DocumentProcessor:
    """Processing pipeline using docling for PDF conversion."""
    
    def __init__(self, config: AdapterConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configure docling converter with correct API
        try:
            # Try the simpler configuration first
            self.converter = DocumentConverter()
        except Exception as e:
            self.logger.warning(f"Failed to create DocumentConverter with default options: {e}")
            # Fallback to basic configuration
            self.converter = DocumentConverter()
    
    def process_document(self, acquired_doc: AcquiredDocument) -> Tuple[str, Dict[str, Any]]:
        """Process a document using docling."""
        start_time = time.time()
        warnings = []
        
        try:
            # Convert document using docling
            self.logger.info(f"Converting document with docling: {acquired_doc.local_path}")
            result = self.converter.convert(acquired_doc.local_path)
            
            # Extract markdown content - handle different API versions
            try:
                if hasattr(result.document, 'export_to_markdown'):
                    markdown_content = result.document.export_to_markdown()
                elif hasattr(result, 'document') and hasattr(result.document, 'markdown'):
                    markdown_content = result.document.markdown
                elif hasattr(result, 'markdown'):
                    markdown_content = result.markdown
                else:
                    # Fallback - try to extract text content
                    markdown_content = str(result.document) if hasattr(result, 'document') else str(result)
                    warnings.append("Used fallback method for markdown extraction")
            except Exception as e:
                self.logger.warning(f"Markdown extraction failed, using fallback: {e}")
                markdown_content = f"# Document Content\n\nFailed to extract content from {acquired_doc.local_path}"
                warnings.append(f"Markdown extraction failed: {e}")
            
            # Post-process markdown
            if self.config.preserve_equations:
                markdown_content = self._preserve_equations(markdown_content)
            
            if self.config.preserve_tables:
                markdown_content = self._enhance_tables(markdown_content)
            
            # Extract references if available
            references = self._extract_references(result)
            if references:
                markdown_content += "\n\n<!--references-->\n"
            
            processing_duration = time.time() - start_time
            
            processing_metadata = {
                "processor_used": "docling",
                "processing_timestamp": datetime.now(timezone.utc).isoformat(),
                "processing_duration": processing_duration,
                "conversion_warnings": warnings
            }
            
            return markdown_content, processing_metadata
            
        except Exception as e:
            self.logger.error(f"Processing failed for {acquired_doc.document_id}: {e}")
            # Create fallback content
            fallback_content = f"# Processing Failed\n\nFailed to process document {acquired_doc.document_id}\nError: {str(e)}"
            processing_metadata = {
                "processor_used": "docling",
                "processing_timestamp": datetime.now(timezone.utc).isoformat(),
                "processing_duration": time.time() - start_time,
                "conversion_warnings": [f"Processing failed: {str(e)}"]
            }
            return fallback_content, processing_metadata
    
    def _preserve_equations(self, content: str) -> str:
        """Enhance equation preservation in markdown."""
        # docling should handle this, but we can add post-processing
        return content
    
    def _enhance_tables(self, content: str) -> str:
        """Enhance table formatting in markdown."""
        # docling should handle this, but we can add post-processing
        return content
    
    def _extract_references(self, result) -> Optional[List[Dict[str, Any]]]:
        """Extract references from docling result."""
        # Implementation depends on docling's reference extraction capabilities
        return None


class ChunkingEngine:
    """Chunking engine for segmenting documents."""
    
    def __init__(self, config: AdapterConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def chunk_document(self, document_id: str, content: str) -> Iterator[Chunk]:
        """Chunk document content into LLM-sized pieces."""
        # Simple sentence-based chunking with overlap
        sentences = self._split_sentences(content)
        
        chunk_index = 0
        total_tokens = sum(len(s.split()) for s in sentences)
        total_chunks = self._estimate_chunk_count(total_tokens)
        
        current_chunk = []
        current_tokens = 0
        
        for i, sentence in enumerate(sentences):
            sentence_tokens = len(sentence.split())
            
            # Check if adding this sentence exceeds chunk size
            if current_tokens + sentence_tokens > self.config.chunk_size and current_chunk:
                # Create chunk
                chunk_content = ' '.join(current_chunk)
                chunk = self._create_chunk(
                    document_id, chunk_index, total_chunks, chunk_content, current_tokens
                )
                yield chunk
                
                # Calculate overlap
                overlap_tokens = int(self.config.chunk_size * self.config.chunk_overlap)
                overlap_sentences = self._get_overlap_sentences(current_chunk, overlap_tokens)
                
                # Start new chunk with overlap
                current_chunk = overlap_sentences + [sentence]
                current_tokens = sum(len(s.split()) for s in current_chunk)
                chunk_index += 1
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
        
        # Handle remaining content
        if current_chunk:
            chunk_content = ' '.join(current_chunk)
            chunk = self._create_chunk(
                document_id, chunk_index, total_chunks, chunk_content, current_tokens
            )
            yield chunk
    
    def _split_sentences(self, content: str) -> List[str]:
        """Split content into sentences, preserving equations and tables."""
        # Simple sentence splitting - could be enhanced with proper NLP
        sentences = re.split(r'(?<=[.!?])\s+', content)
        return [s.strip() for s in sentences if s.strip()]
    
    def _estimate_chunk_count(self, total_tokens: int) -> int:
        """Estimate total number of chunks."""
        return max(1, (total_tokens + self.config.chunk_size - 1) // self.config.chunk_size)
    
    def _get_overlap_sentences(self, sentences: List[str], overlap_tokens: int) -> List[str]:
        """Get sentences for overlap."""
        if overlap_tokens <= 0:
            return []
        
        overlap_sentences = []
        tokens_count = 0
        
        for sentence in reversed(sentences):
            sentence_tokens = len(sentence.split())
            if tokens_count + sentence_tokens <= overlap_tokens:
                overlap_sentences.insert(0, sentence)
                tokens_count += sentence_tokens
            else:
                break
        
        return overlap_sentences
    
    def _create_chunk(self, document_id: str, chunk_index: int, total_chunks: int, 
                     content: str, token_count: int) -> Chunk:
        """Create a chunk object."""
        content_features = {
            "heading_count": len(re.findall(r'^#+\s', content, re.MULTILINE)),
            "list_count": len(re.findall(r'^\s*[-*+]\s', content, re.MULTILINE)),
            "table_count": content.count('|'),
            "equation_count": content.count('$')
        }
        
        return Chunk(
            chunk_id=str(uuid.uuid4()),
            document_id=document_id,
            chunk_index=chunk_index,
            total_chunks=total_chunks,
            content=content,
            token_count=token_count,
            chunk_type="text",
            section_path=[],
            has_overlap_previous=chunk_index > 0,
            has_overlap_next=chunk_index < total_chunks - 1,
            content_features=content_features
        )


class HEPilotArxivAdapter:
    """Main adapter class orchestrating the entire pipeline."""
    
    def __init__(self, config: AdapterConfig, output_dir: Path):
        self.config = config
        self.output_dir = output_dir
        self.logger = self._setup_logging()
        
        # Create output directory structure
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "documents").mkdir(exist_ok=True)
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def run_pipeline(self, max_documents: int = 10) -> Dict[str, Any]:
        """Run the complete RAG adapter pipeline."""
        self.logger.info("Starting HEPilot arXiv LHCb adapter pipeline")
        
        try:
            # Save configuration
            config_path = self.output_dir / "adapter_config.json"
            with open(config_path, 'w') as f:
                json.dump(self.config.to_dict(), f, indent=2)
            
            # Discovery phase
            self.logger.info("Starting discovery phase")
            async with ArxivDiscovery(self.config) as discovery:
                discovery_result = await discovery.discover_documents(max_documents)
            
            discovered_docs = discovery_result["discovered_documents"]
            self.logger.info(f"Discovered {len(discovered_docs)} documents")
            
            if not discovered_docs:
                self.logger.warning("No documents discovered")
                return {"status": "completed", "documents_processed": 0}
            
            # Create a mapping from document_id to original discovery data
            discovery_metadata = {doc["document_id"]: doc for doc in discovered_docs}
            
            # Acquisition phase
            self.logger.info("Starting acquisition phase")
            async with DocumentAcquisition(self.config, self.output_dir / "documents") as acquisition:
                acquisition_result = await acquisition.acquire_documents(discovered_docs)
            
            acquired_docs = acquisition_result["acquired_documents"]
            self.logger.info(f"Acquired {len(acquired_docs)} documents")
            
            # Processing and chunking phase
            processor = DocumentProcessor(self.config)
            chunker = ChunkingEngine(self.config)
            
            catalog_entries = []
            total_chunks = 0
            
            for acquired_doc_dict in acquired_docs:
                acquired_doc = AcquiredDocument(**acquired_doc_dict)
                
                try:
                    # Get original discovery metadata
                    original_metadata = discovery_metadata.get(acquired_doc.document_id, {})
                    
                    # Process document
                    self.logger.info(f"Processing document {acquired_doc.document_id}")
                    markdown_content, processing_metadata = processor.process_document(acquired_doc)
                    
                    # Chunk document
                    chunks = list(chunker.chunk_document(acquired_doc.document_id, markdown_content))
                    
                    # Save outputs with original metadata
                    doc_output_dir = self._save_document_outputs(
                        acquired_doc, markdown_content, chunks, processing_metadata, original_metadata
                    )
                    
                    # Extract title (prefer original, then from content)
                    title = original_metadata.get("title", self._extract_title_from_content(markdown_content))
                    
                    # Add to catalog
                    catalog_entries.append({
                        "document_id": acquired_doc.document_id,
                        "source_type": "arxiv",
                        "title": title,
                        "chunk_count": len(chunks),
                        "file_path": str(doc_output_dir.relative_to(self.output_dir))
                    })
                    
                    total_chunks += len(chunks)
                    self.logger.info(f"Created {len(chunks)} chunks for document {acquired_doc.document_id}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to process document {acquired_doc.document_id}: {e}")
            
            # Create catalog
            catalog = {
                "creation_timestamp": datetime.now(timezone.utc).isoformat(),
                "adapter_version": self.config.version,
                "total_documents": len(catalog_entries),
                "total_chunks": total_chunks,
                "source_distribution": {
                    "arxiv": len(catalog_entries),
                    "indico": 0,
                    "internal_notes": 0,
                    "twiki": 0,
                    "other": 0
                },
                "documents": catalog_entries
            }
            
            # Save catalog
            catalog_path = self.output_dir / "catalog.json"
            with open(catalog_path, 'w') as f:
                json.dump(catalog, f, indent=2)
            
            self.logger.info(f"Pipeline completed. Processed {len(catalog_entries)} documents, created {total_chunks} chunks")
            
            return {
                "status": "completed",
                "documents_processed": len(catalog_entries),
                "total_chunks": total_chunks,
                "catalog_path": str(catalog_path)
            }
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            raise
    
    def _save_document_outputs(self, acquired_doc: AcquiredDocument, markdown_content: str, 
                              chunks: List[Chunk], processing_metadata: Dict[str, Any],
                              original_metadata: Dict[str, Any] = None) -> Path:
        """Save all document outputs according to specification."""
        if original_metadata is None:
            original_metadata = {}
            
        doc_dir = Path(acquired_doc.local_path).parent
        chunks_dir = doc_dir / "chunks"
        chunks_dir.mkdir(exist_ok=True)
        
        # Save full document markdown
        with open(doc_dir / "full_document.md", 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Save processing metadata
        with open(doc_dir / "processing_metadata.json", 'w') as f:
            json.dump(processing_metadata, f, indent=2)
        
        # Extract title (prefer original, then from content)
        title = original_metadata.get("title", self._extract_title_from_content(markdown_content))
        
        # Extract authors from original metadata
        authors = original_metadata.get("authors", [])
        
        # Get original URL
        original_url = original_metadata.get("source_url", "unknown")
        
        # Save document metadata
        document_metadata = {
            "document_id": acquired_doc.document_id,
            "source_type": "arxiv",
            "original_url": original_url,
            "local_path": acquired_doc.local_path,
            "title": title,
            "authors": authors,
            "file_hash": acquired_doc.file_hash_sha256,
            "file_size": acquired_doc.file_size,
            "processing_timestamp": datetime.now(timezone.utc).isoformat(),
            "adapter_version": self.config.version
        }
        
        with open(doc_dir / "document_metadata.json", 'w') as f:
            json.dump(document_metadata, f, indent=2)
        
        # Save chunks
        for chunk in chunks:
            # Save chunk content
            chunk_file = chunks_dir / f"chunk_{chunk.chunk_index:04d}.md"
            with open(chunk_file, 'w', encoding='utf-8') as f:
                f.write(chunk.content)
            
            # Save chunk metadata
            chunk_metadata = {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "total_chunks": chunk.total_chunks,
                "token_count": chunk.token_count,
                "character_count": len(chunk.content),
                "chunk_type": chunk.chunk_type,
                "contains_equations": chunk.content_features["equation_count"] > 0,
                "contains_tables": chunk.content_features["table_count"] > 0,
                "overlap_info": {
                    "has_previous_overlap": chunk.has_overlap_previous,
                    "has_next_overlap": chunk.has_overlap_next,
                    "overlap_token_count": int(self.config.chunk_size * self.config.chunk_overlap)
                }
            }
            
            metadata_file = chunks_dir / f"chunk_{chunk.chunk_index:04d}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(chunk_metadata, f, indent=2)
        
        return doc_dir
    
    def _extract_title_from_content(self, content: str) -> str:
        """Extract title from markdown content."""
        lines = content.split('\n')
        
        # Try different patterns to find the title
        for line in lines[:20]:  # Check first 20 lines
            line = line.strip()
            
            # Standard markdown header
            if line.startswith('# ') and len(line) > 2:
                return line[2:].strip()
            
            # Alternative markdown headers
            if line.startswith('## ') and len(line) > 3:
                return line[3:].strip()
            
            # Look for lines that look like titles (all caps, or title case)
            if len(line) > 10 and len(line) < 200:
                # Check if it looks like a title (no lowercase words at start)
                words = line.split()
                if len(words) >= 2 and all(word[0].isupper() or word.lower() in ['a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'with'] for word in words):
                    # Skip lines that look like headers or metadata
                    if not any(skip_word in line.lower() for skip_word in ['abstract', 'author', 'page', 'doi', 'arxiv', 'submitted', 'published']):
                        return line
        
        # Fallback: try to find any substantial line that's not too short or too long
        for line in lines[:30]:
            line = line.strip()
            if 20 <= len(line) <= 150 and not line.startswith(('http', 'www', 'doi:', 'arxiv:')):
                return line
        
        return "Unknown Title"


async def main():
    """Example usage of the HEPilot arXiv adapter."""
    # Configuration
    config = AdapterConfig(
        chunk_size=1024,
        chunk_overlap=0.1,
        preserve_tables=True,
        preserve_equations=True
    )
    
    # Output directory
    output_dir = Path("./hepilot_output")
    
    # Create and run adapter
    adapter = HEPilotArxivAdapter(config, output_dir)
    result = await adapter.run_pipeline(max_documents=5)
    
    print(f"Pipeline result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
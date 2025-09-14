#!/usr/bin/env python3
"""
HEPilot arXiv LHCb Adapter - Main Orchestrator
A reference implementation following the HEPilot RAG Adapter Framework specification
for discovering and processing LHCb papers from arXiv using docling.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Tuple
from tqdm import tqdm

from models import AcquiredDocument, Chunk
from discovery import ArxivDiscovery
from acquisition import DocumentAcquisition
from processing import DocumentProcessor
from chunking import ChunkingEngine
from unified_cache import UnifiedCache
from progress_tracker import ProgressTracker


class HEPilotArxivAdapter:
    """Main orchestrator for the HEPilot arXiv adapter pipeline."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the HEPilot ArXiv adapter.
        
        Args:
            config: Adapter configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Setup paths
        self.output_dir = Path(self.config.get("x_extension", {}).get("output_dir", "./hepilot_output"))
        self.cache_dir = Path(self.config.get("x_extension", {}).get("cache_dir", "./hepilot_output/cache"))
        
        # Initialize unified cache and progress tracker
        self.unified_cache = UnifiedCache(self.output_dir, self.cache_dir)
        self.progress_tracker = ProgressTracker(self.output_dir)
        
        # Configuration options
        self.skip_processed = self.config.get("x_extension", {}).get("skip_processed", True)
        
        # Ensure output directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "documents").mkdir(exist_ok=True)

    async def discover(self, max_documents: int = None, fetch_all: bool = False) -> List[Dict[str, Any]]:
        """Discover documents from arXiv.
        
        Args:
            max_documents: Maximum number of documents to discover
            fetch_all: Whether to fetch all available papers before filtering
            
        Returns:
            List of discovered document dictionaries
        """
        self.logger.info("Step 1: Discovering LHCb papers from arXiv...")
        
        discovery_max = None if fetch_all else max_documents
        self.logger.info(f"Discovery mode: {'All papers' if fetch_all else f'Limited to {max_documents} papers'}")
        
        async with ArxivDiscovery(self.config, self.output_dir, self.unified_cache) as discovery:
            discovery_result = await discovery.discover_documents(discovery_max)
            
        discovered_docs = discovery_result["discovered_documents"]
        self.logger.info(f"Discovered {len(discovered_docs)} documents")
        
        return discovered_docs

    async def acquire(self, discovered_docs: List[Dict[str, Any]], max_documents: int = None) -> List[Dict[str, Any]]:
        """Acquire documents from the discovered list.
        
        Args:
            discovered_docs: List of discovered document dictionaries
            max_documents: Maximum number of documents to acquire
            
        Returns:
            List of acquired document dictionaries
        """
        self.logger.info("Step 2: Acquiring (downloading) discovered papers...")
        
        # Skip already processed documents if configured
        if self.skip_processed:
            filtered_docs = []
            for doc in discovered_docs:
                if not self.unified_cache.is_document_processed(doc["document_id"]):
                    filtered_docs.append(doc)
                else:
                    self.logger.info(f"Skipping already processed document {doc['document_id']}")
            
            discovered_docs = filtered_docs
            self.logger.info(f"After filtering, {len(discovered_docs)} documents remain for processing")
        
        # If we're limiting how many to acquire and process, apply the limit here
        if max_documents and len(discovered_docs) > max_documents:
            self.logger.info(f"Limiting acquisition to {max_documents} documents out of {len(discovered_docs)} discovered")
            discovered_docs = discovered_docs[:max_documents]
        
        async with DocumentAcquisition(self.config, self.output_dir) as acquisition:
            acquisition_result = await acquisition.acquire_documents(discovered_docs)
            
        acquired_docs = acquisition_result["acquired_documents"]
        self.logger.info(f"Acquired {len(acquired_docs)} documents")
        
        return acquired_docs

    def process_and_chunk(self, acquired_docs: List[Dict[str, Any]], discovered_docs: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
        """Process and chunk acquired documents.
        
        Args:
            acquired_docs: List of acquired document dictionaries
            discovered_docs: List of original discovered document dictionaries
            
        Returns:
            Tuple of (catalog_entries, total_chunks)
        """
        self.logger.info("Step 3: Processing and chunking documents...")
        
        # Filter for documents that need processing
        papers_to_process = self.progress_tracker.get_papers_needing_processing(acquired_docs)
        
        processor = DocumentProcessor(self.config)
        chunker = ChunkingEngine(self.config, self.output_dir)
        
        catalog_entries = []
        total_chunks = 0

        discovery_metadata = {doc["document_id"]: doc for doc in discovered_docs}

        # Handle already processed documents first
        for acquired_doc_dict in acquired_docs:
            doc_id = acquired_doc_dict["document_id"]
            progress = self.progress_tracker._progress_data.get(doc_id)
            
            if progress and progress.processing_status == "completed":
                # Add already processed document to catalog
                original_metadata = discovery_metadata.get(doc_id, {})
                title = original_metadata.get("title", f"Document {doc_id}")
                
                # Try to get chunk count from progress tracker or estimate
                chunk_count = progress.chunk_count if progress.chunk_count > 0 else 1
                
                # Create catalog entry for already processed document
                doc_dir = self.output_dir / "documents" / f"arxiv_{doc_id}"
                catalog_entries.append({
                    "document_id": doc_id,
                    "source_type": "arxiv",
                    "title": title,
                    "chunk_count": chunk_count,
                    "file_path": str(doc_dir.relative_to(self.output_dir)) if doc_dir.exists() else f"documents/arxiv_{doc_id}"
                })
                total_chunks += chunk_count
        
        if not papers_to_process:
            skipped_count = len(acquired_docs)
            self.logger.info(f"All {skipped_count} papers already processed, no new processing needed")
            return catalog_entries, total_chunks
        
        skipped_count = len(acquired_docs) - len(papers_to_process)
        if skipped_count > 0:
            self.logger.info(f"Skipping {skipped_count} already processed papers")
        
        self.logger.info(f"Processing {len(papers_to_process)} new papers")

        for acquired_doc_dict in tqdm(papers_to_process, desc="Processing papers", unit="paper"):
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
                
                # Update catalog entry if it exists (from already processed), otherwise add new one
                existing_entry = None
                for entry in catalog_entries:
                    if entry["document_id"] == acquired_doc.document_id:
                        existing_entry = entry
                        break
                
                if existing_entry:
                    # Update existing entry
                    existing_entry.update({
                        "title": title,
                        "chunk_count": len(chunks),
                        "file_path": str(doc_output_dir.relative_to(self.output_dir))
                    })
                    total_chunks = total_chunks - existing_entry.get("chunk_count", 0) + len(chunks)
                else:
                    # Add new catalog entry
                    catalog_entries.append({
                        "document_id": acquired_doc.document_id,
                        "source_type": "arxiv",
                        "title": title,
                        "chunk_count": len(chunks),
                        "file_path": str(doc_output_dir.relative_to(self.output_dir))
                    })
                    total_chunks += len(chunks)
                
                self.logger.info(f"Created {len(chunks)} chunks for document {acquired_doc.document_id}")
                
                # Mark processing as completed in progress tracker
                self.progress_tracker.mark_processing_completed(acquired_doc.document_id, len(chunks))
                
                # Update document state in unified cache
                self.unified_cache.set_document_processed(
                    acquired_doc.document_id,
                    acquired_doc.file_hash_sha256,
                    metadata={
                        "title": title,
                        "chunk_count": len(chunks),
                        "file_path": str(doc_output_dir.relative_to(self.output_dir))
                    }
                )
                
            except Exception as e:
                self.logger.error(f"Failed to process document {acquired_doc.document_id}: {e}")
                self.progress_tracker.mark_processing_failed(acquired_doc.document_id, str(e))
                self.unified_cache.set_document_failed(acquired_doc.document_id, str(e))
        
        return catalog_entries, total_chunks

    def show_progress_summary(self) -> None:
        """Display progress summary to the user."""
        summary = self.progress_tracker.get_summary()
        failed = self.progress_tracker.get_failed_papers()
        
        self.logger.info("=== Progress Summary ===")
        self.logger.info(f"Total papers tracked: {summary['total_papers']}")
        self.logger.info(f"Download progress: {summary['download']['completed']}/{summary['total_papers']} completed, {summary['download']['failed']} failed, {summary['download']['pending']} pending")
        self.logger.info(f"Processing progress: {summary['processing']['completed']}/{summary['total_papers']} completed, {summary['processing']['failed']} failed, {summary['processing']['pending']} pending")
        self.logger.info(f"Fully completed: {summary['fully_completed']}/{summary['total_papers']}")
        self.logger.info(f"Total chunks created: {summary['total_chunks_created']}")
        
        if failed['download_failed']:
            self.logger.warning(f"Download failures: {len(failed['download_failed'])}")
            for failure in failed['download_failed'][:5]:  # Show first 5
                self.logger.warning(f"  - {failure['arxiv_id']}: {failure['error']}")
            if len(failed['download_failed']) > 5:
                self.logger.warning(f"  ... and {len(failed['download_failed']) - 5} more")
        
        if failed['processing_failed']:
            self.logger.warning(f"Processing failures: {len(failed['processing_failed'])}")
            for failure in failed['processing_failed'][:5]:  # Show first 5
                self.logger.warning(f"  - {failure['arxiv_id']}: {failure['error']}")
            if len(failed['processing_failed']) > 5:
                self.logger.warning(f"  ... and {len(failed['processing_failed']) - 5} more")

    def create_catalog(self, catalog_entries: List[Dict[str, Any]], total_chunks: int) -> Dict[str, Any]:
        """Create the final catalog.json file.
        
        Args:
            catalog_entries: List of document catalog entries
            total_chunks: Total number of chunks created
            
        Returns:
            Dictionary with pipeline completion information
        """
        self.logger.info("Step 4: Creating catalog...")
        
        catalog = {
            "creation_timestamp": datetime.now(timezone.utc).isoformat(),
            "adapter_version": self.config["version"],
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
    
    def _save_document_outputs(self, acquired_doc: AcquiredDocument, markdown_content: str, 
                               chunks: List[Chunk], processing_metadata: Dict[str, Any],
                               original_metadata: Dict[str, Any] = None) -> Path:
        """Save all document outputs according to specification.
        
        Args:
            acquired_doc: Acquired document information
            markdown_content: Processed markdown content
            chunks: List of document chunks
            processing_metadata: Processing metadata dictionary
            original_metadata: Original discovery metadata
            
        Returns:
            Path to the document output directory
        """
        if original_metadata is None:
            original_metadata = {}
            
        # Ensure we're using the documents folder structure
        doc_id = acquired_doc.document_id
        doc_dir = self.output_dir / "documents" / f"arxiv_{doc_id}"
        doc_dir.mkdir(parents=True, exist_ok=True)
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
        
        # Save document metadata, respecting exclude_authors config
        document_metadata = {
            "document_id": acquired_doc.document_id,
            "source_type": "arxiv",
            "original_url": original_metadata.get("source_url", ""),
            "local_path": acquired_doc.local_path,
            "title": title,
            "file_hash": acquired_doc.file_hash_sha256,
            "file_size": acquired_doc.file_size,
            "processing_timestamp": datetime.now(timezone.utc).isoformat(),
            "adapter_version": self.config["version"]
        }
        
        # Only include authors if not excluded by configuration
        exclude_authors = self.config.get("x_extension", {}).get("exclude_authors", True)
        if not exclude_authors and authors:
            document_metadata["authors"] = authors
        
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
                    "overlap_token_count": int(self.config["processing_config"]["chunk_size"] * self.config["processing_config"]["chunk_overlap"])
                }
            }
            
            metadata_file = chunks_dir / f"chunk_{chunk.chunk_index:04d}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(chunk_metadata, f, indent=2)
        
        return doc_dir
    
    def _extract_title_from_content(self, content: str) -> str:
        """Extract title from markdown content.
        
        Args:
            content: Markdown content
            
        Returns:
            Extracted title or fallback
        """
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

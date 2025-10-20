"""
Main orchestrator for ArXiv adapter pipeline.

Coordinates discovery, acquisition, processing, and chunking stages
to produce HEPilot-compliant output for RAG system ingestion.
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime, timezone
from config import ConfigManager
from discovery import ArxivDiscovery
from acquisition import ArxivAcquisition
from processing import ArxivProcessor
from chunking import ArxivChunker
from metadata import MetadataManager
from cache_manager import CacheManager, CacheEntry
from models import DiscoveredDocument, AcquiredDocument, ChunkContent, DocumentMetadata
from utils import (Colors, print_header, print_config, print_cache_summary, 
                   print_status, validate_pdf_exists, get_pdf_path)


class ArxivAdapterPipeline:
    """Orchestrates the complete ArXiv adapter pipeline."""
    
    def __init__(self, config_path: Path, output_dir: Path, max_results: Optional[int] = None, enable_cache: bool = True, verbose: bool = False) -> None:
        """
        Initialize adapter pipeline.
        
        Args:
            config_path: Path to adapter_config.json
            output_dir: Directory for output files
            max_results: Maximum number of papers to process (None for All)
            enable_cache: Whether to enable caching system
            verbose: Enable verbose debug output (auto-enabled in dev mode)
        """
        self.config_manager: ConfigManager = ConfigManager(config_path)
        self.output_dir: Path = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_results: Optional[int] = max_results
        self.enable_cache: bool = enable_cache
        self.verbose: bool = verbose
        self.cache_manager: Optional[CacheManager] = None
        if enable_cache:
            self.cache_manager = CacheManager(output_dir / "cache")
        self.metadata_manager: MetadataManager = MetadataManager(
            adapter_version=self.config_manager.config.version,
            include_authors=self.config_manager.get_include_authors_metadata()
        )
        self.discovery: ArxivDiscovery = ArxivDiscovery(
            max_results=max_results,
            include_authors=self.config_manager.get_include_authors_metadata()
        )
        self.acquisition: ArxivAcquisition = ArxivAcquisition(
            download_dir=output_dir / "downloads",
            verbose=self.verbose
        )
        self.processor: ArxivProcessor = ArxivProcessor(
            preserve_tables=self.config_manager.get_preserve_tables(),
            preserve_equations=self.config_manager.get_preserve_equations(),
            enrich_formulas=self.config_manager.get_enrich_formulas(),
            table_mode=self.config_manager.get_table_mode(),
            exclude_references=self.config_manager.get_exclude_references(),
            exclude_acknowledgments=self.config_manager.get_exclude_acknowledgments(),
            exclude_author_lists=self.config_manager.get_exclude_author_lists(),
            processing_timeout=self.config_manager.get_processing_timeout()
        )
        self.chunker: ArxivChunker = ArxivChunker(
            chunk_size=self.config_manager.get_chunk_size(),
            chunk_overlap=self.config_manager.get_chunk_overlap(),
            model_name=self.config_manager.get_embedding_model_name(),
            use_model_tokenizer=self.config_manager.get_use_model_tokenizer(),
            cache_dir=self.config_manager.get_model_cache_dir()
        )
        
        self._print_configuration()
    
    def _print_configuration(self) -> None:
        """Print pipeline configuration in a colorful format."""
        config_display: Dict[str, Any] = {
            "Pipeline Settings": {
                "max_results": self.max_results if self.max_results else "All",
                "cache_enabled": self.enable_cache,
                "verbose_mode": self.verbose,
                "output_directory": str(self.output_dir)
            },
            "Processing Config": {
                "chunk_size": self.config_manager.get_chunk_size(),
                "chunk_overlap": self.config_manager.get_chunk_overlap(),
                "preserve_tables": self.config_manager.get_preserve_tables(),
                "preserve_equations": self.config_manager.get_preserve_equations(),
                "enrich_formulas": self.config_manager.get_enrich_formulas(),
                "table_mode": self.config_manager.get_table_mode(),
                "exclude_references": self.config_manager.get_exclude_references(),
                "exclude_acknowledgments": self.config_manager.get_exclude_acknowledgments(),
                "exclude_author_lists": self.config_manager.get_exclude_author_lists(),
                "processing_timeout": f"{self.config_manager.get_processing_timeout()}s"
            },
            "Embedding Model": {
                "model_name": self.config_manager.get_embedding_model_name(),
                "use_model_tokenizer": self.config_manager.get_use_model_tokenizer(),
                "cache_dir": str(self.config_manager.get_model_cache_dir())
            }
        }
        print_config(config_display)
    
    def _categorize_papers(self, discovered: List[DiscoveredDocument]) -> Tuple[List[DiscoveredDocument], List[DiscoveredDocument], List[DiscoveredDocument]]:
        """
        Categorize discovered papers into download, process, or cached based on cache state and file existence.
        
        Args:
            discovered: List of discovered documents
            
        Returns:
            Tuple of (to_download, to_process_from_cache, fully_cached)
        """
        to_download: List[DiscoveredDocument] = []
        to_process_from_cache: List[DiscoveredDocument] = []
        fully_cached: List[DiscoveredDocument] = []
        
        for doc in discovered:
            if not doc.arxiv_id:
                to_download.append(doc)
                continue
            
            # Get cache entry
            cached_entry: Optional[CacheEntry] = self.cache_manager.get_cached_entry(doc.arxiv_id) if self.cache_manager else None
            
            # Check if PDF exists on disk
            pdf_path: Path = get_pdf_path(self.output_dir, str(doc.document_id))
            pdf_exists: bool = validate_pdf_exists(pdf_path)
            
            # Check if output directory exists with chunks
            output_dir: Path = self.output_dir / "documents" / f"arxiv_{doc.document_id}"
            chunks_dir: Path = output_dir / "chunks"
            has_processed_output: bool = chunks_dir.exists() and any(chunks_dir.glob("chunk_*.md"))
            
            # Decision logic
            if not cached_entry:
                # No cache entry - check disk
                if pdf_exists:
                    if has_processed_output:
                        # Downloaded and processed, but no cache - load from disk
                        if self.verbose:
                            print(f"[CACHE] → Recovered: {doc.arxiv_id} {doc.arxiv_version} (no cache entry)")
                        fully_cached.append(doc)
                    else:
                        # Downloaded but not processed
                        if self.verbose:
                            print(f"[CACHE] → Process: {doc.arxiv_id} {doc.arxiv_version} (downloaded, no cache)")
                        to_process_from_cache.append(doc)
                else:
                    # Not downloaded, new paper
                    if self.verbose:
                        print(f"[CACHE] → New paper: {doc.arxiv_id} {doc.arxiv_version}")
                    to_download.append(doc)
            
            elif cached_entry.version != (doc.arxiv_version or "v1"):
                # Version changed - need to re-download and reprocess
                if self.verbose:
                    print(f"[CACHE] → New version: {doc.arxiv_id} {cached_entry.version} → {doc.arxiv_version}")
                to_download.append(doc)
            
            elif cached_entry.download_status != "success":
                # Download failed or pending
                if pdf_exists:
                    # File exists despite cache saying failed - use it
                    if self.verbose:
                        print(f"[CACHE] → Process: {doc.arxiv_id} {doc.arxiv_version} (PDF exists, cache outdated)")
                    to_process_from_cache.append(doc)
                else:
                    # Need to download
                    if self.verbose:
                        print(f"[CACHE] → Download: {doc.arxiv_id} {doc.arxiv_version} (download {cached_entry.download_status})")
                    to_download.append(doc)
            
            elif cached_entry.processing_status == "success":
                # Fully successful - validate output still exists
                if has_processed_output:
                    if self.verbose:
                        print(f"[CACHE] ✓ Cached: {doc.arxiv_id} {doc.arxiv_version}")
                    fully_cached.append(doc)
                else:
                    # Cache says success but output missing - reprocess
                    if pdf_exists:
                        if self.verbose:
                            print(f"[CACHE] → Reprocess: {doc.arxiv_id} {doc.arxiv_version} (output missing)")
                        to_process_from_cache.append(doc)
                    else:
                        if self.verbose:
                            print(f"[CACHE] → Re-download: {doc.arxiv_id} {doc.arxiv_version} (all missing)")
                        to_download.append(doc)
            
            else:
                # Processing failed/pending/timeout
                if pdf_exists:
                    # PDF exists, retry processing
                    if self.verbose:
                        print(f"[CACHE] → Retry: {doc.arxiv_id} {doc.arxiv_version} (processing {cached_entry.processing_status})")
                    to_process_from_cache.append(doc)
                else:
                    # PDF missing, need to re-download
                    if self.verbose:
                        print(f"[CACHE] → Re-download: {doc.arxiv_id} {doc.arxiv_version} (PDF missing)")
                    to_download.append(doc)
        
        return to_download, to_process_from_cache, fully_cached
    
    def run(self, query: str = "all:lhcb", download_only: bool = False, process_only: bool = False) -> bool:
        """
        Run the complete pipeline.
        
        Args:
            query: arXiv search query (default: all:lhcb for LHCb papers across all categories)
            download_only: If True, only download PDFs without processing
            process_only: If True, only process already downloaded PDFs
            
        Returns:
            True if pipeline succeeded, False otherwise
        """
        try:
            import logging
            if not self.verbose:
                logging.getLogger().setLevel(logging.WARNING)
                for handler in logging.getLogger().handlers:
                    handler.setLevel(logging.WARNING)
            
            self.metadata_manager.log("INFO", "pipeline", "Starting ArXiv adapter pipeline", {
                "query": query,
                "max_results": self.max_results,
                "cache_enabled": self.enable_cache,
                "download_only": download_only,
                "process_only": process_only
            })
            if self.enable_cache and self.cache_manager:
                cache_stats = self.cache_manager.get_cache_stats()
                self.metadata_manager.log("INFO", "cache", f"Cache initialized with {cache_stats['total_papers']} existing entries")
                if self.verbose:
                    print(f"\n[CACHE] Loaded cache with {cache_stats['total_papers']} existing papers")
            
            # Process-only mode: skip discovery, only process downloaded PDFs
            if process_only:
                return self._run_process_only_mode()
            
            discovered: List[DiscoveredDocument] = self._run_discovery(query)
            if not discovered:
                print_status("WARNING", "No documents discovered")
                return False
            
            catalog_entries: List[Dict[str, Any]] = []
            
            # Categorize papers based on cache state and file existence
            if self.enable_cache and self.cache_manager:
                to_download, to_process_from_cache, fully_cached = self._categorize_papers(discovered)
                
                # Print colorful summary
                print_cache_summary(len(fully_cached), len(to_download), len(to_process_from_cache))
                
                # Load fully cached papers
                for cached_doc in fully_cached:
                    cached_entry = self.cache_manager.get_cached_entry(cached_doc.arxiv_id)
                    if cached_entry:
                        self._load_from_cache(cached_entry, catalog_entries)
            else:
                to_download = discovered
                to_process_from_cache = []
                fully_cached = []
            if to_download:
                if not self.verbose:
                    print(f"\nAcquiring {len(to_download)} papers...\n")
                acquired: List[AcquiredDocument] = self._run_acquisition(to_download)
                if acquired:
                    if self.enable_cache and self.cache_manager:
                        for disc, acq in zip(to_download, acquired):
                            if acq.download_status == "success" and disc.arxiv_id:
                                cached_entry = self.cache_manager.get_cached_entry(disc.arxiv_id)
                                doc_dir: Path = self.output_dir / "documents" / f"arxiv_{acq.document_id}"
                                
                                if not cached_entry or cached_entry.version != (disc.arxiv_version or "v1"):
                                    # New paper or new version - create fresh cache entry
                                    self.cache_manager.add_entry(
                                        arxiv_id=disc.arxiv_id,
                                        version=disc.arxiv_version or "v1",
                                        document_id=acq.document_id,
                                        file_hash_sha256=acq.file_hash_sha256,
                                        output_dir=doc_dir,
                                        source_url=disc.source_url,
                                        title=disc.title,
                                        download_status="success",
                                        processing_status="pending"
                                    )
                                    if self.verbose:
                                        print(f"[CACHE] ✓ Downloaded: {disc.arxiv_id} {disc.arxiv_version}")
                                elif cached_entry.download_status != "success":
                                    # Existing paper but download status needs update
                                    self.cache_manager.add_entry(
                                        arxiv_id=disc.arxiv_id,
                                        version=disc.arxiv_version or "v1",
                                        document_id=acq.document_id,
                                        file_hash_sha256=acq.file_hash_sha256,
                                        output_dir=doc_dir,
                                        source_url=disc.source_url,
                                        title=disc.title,
                                        download_status="success",
                                        processing_status=cached_entry.processing_status  # Preserve existing status
                                    )
                                    if self.verbose:
                                        print(f"[CACHE] ✓ Updated download status: {disc.arxiv_id} {disc.arxiv_version}")
                    
                    # Skip processing in download-only mode
                    if download_only:
                        print(f"\n{Colors.GREEN}✓ Downloaded {len(acquired)} papers (processing skipped){Colors.RESET}\n")
                        self.metadata_manager.log("INFO", "pipeline", "Download-only mode: processing skipped")
                    else:
                        print(f"\nProcessing {len(acquired)} papers...\n")
                        try:
                            from tqdm import tqdm
                            papers_iter = tqdm(zip(to_download, acquired), total=len(acquired), desc="Processing", disable=self.verbose)
                        except ImportError:
                            papers_iter = zip(to_download, acquired)
                        for disc, acq in papers_iter:
                            if acq.download_status != "success":
                                continue
                            if self.enable_cache and self.cache_manager:
                                success: bool = self._process_document_with_cache(disc, acq, catalog_entries)
                            else:
                                success: bool = self._process_document(disc, acq, catalog_entries)
                            if not success:
                                self.metadata_manager.log("WARNING", "pipeline", 
                                    f"Failed to process document: {disc.title}")
                                if self.enable_cache and self.cache_manager and disc.arxiv_id:
                                    self.cache_manager.update_processing_status(disc.arxiv_id, "failed")
            
            # Skip retry processing in download-only mode
            if to_process_from_cache and self.enable_cache and self.cache_manager and not download_only:
                print(f"\n{Colors.CYAN}Processing {len(to_process_from_cache)} papers from cache...{Colors.RESET}\n")
                try:
                    from tqdm import tqdm
                    retry_iter = tqdm(to_process_from_cache, desc="Processing", disable=self.verbose)
                except ImportError:
                    retry_iter = to_process_from_cache
                for doc in retry_iter:
                    cached_entry = self.cache_manager.get_cached_entry(doc.arxiv_id)
                    if not cached_entry:
                        if self.verbose:
                            print(f"{Colors.RED}[ERROR]{Colors.RESET} No cache entry found for {doc.arxiv_id}")
                        continue
                    
                    # Validate PDF exists using utility function
                    pdf_path: Path = get_pdf_path(self.output_dir, cached_entry.document_id)
                    if not validate_pdf_exists(pdf_path):
                        if self.verbose:
                            print(f"{Colors.RED}[ERROR]{Colors.RESET} Missing or invalid PDF: {doc.arxiv_id} {doc.arxiv_version}")
                        print_status("ERROR", f"Cannot process {doc.arxiv_id}: PDF file missing or corrupted")
                        if self.cache_manager:
                            self.cache_manager.update_processing_status(doc.arxiv_id, "failed")
                        continue
                    acq = AcquiredDocument(
                        document_id=UUID(cached_entry.document_id),
                        local_path=str(pdf_path),
                        file_hash_sha256=cached_entry.file_hash_sha256,
                        file_hash_sha512="",
                        file_size=pdf_path.stat().st_size if pdf_path.exists() else 0,
                        download_timestamp=datetime.now(timezone.utc),
                        download_status="success",
                        retry_count=0,
                        validation_status="passed",
                        arxiv_id=doc.arxiv_id,
                        arxiv_version=doc.arxiv_version
                    )
                    if self.verbose:
                        print(f"[CACHE] ⟳ Retry processing: {doc.arxiv_id} {doc.arxiv_version}")
                    success: bool = self._process_document_with_cache(doc, acq, catalog_entries)
                    if not success:
                        self.metadata_manager.log("WARNING", "pipeline",
                            f"Retry failed for document: {doc.title}")
            self._save_catalog(catalog_entries)
            self._save_log()
            self.metadata_manager.log("INFO", "pipeline", "Pipeline completed successfully", {
                "documents_processed": len(catalog_entries)
            })
            return True
        except Exception as e:
            self.metadata_manager.log("ERROR", "pipeline", f"Pipeline failed: {str(e)}")
            self._save_log()
            return False
    
    def _run_process_only_mode(self) -> bool:
        """
        Process-only mode: Find and process all downloaded PDFs that haven't been processed yet.
        
        Returns:
            True if processing succeeded, False otherwise
        """
        try:
            print_header("Process-Only Mode")
            print(f"{Colors.CYAN}Scanning for unprocessed PDFs...{Colors.RESET}\n")
            
            downloads_dir = self.output_dir / "downloads"
            if not downloads_dir.exists():
                print_status("WARNING", "Downloads directory not found. No PDFs to process.")
                return False
            
            # Find all downloaded PDFs
            pdf_files = list(downloads_dir.glob("*.pdf"))
            if not pdf_files:
                print_status("WARNING", "No PDF files found in downloads directory")
                return False
            
            catalog_entries: List[Dict[str, Any]] = []
            unprocessed_count = 0
            
            # Check each PDF to see if it needs processing
            for pdf_path in pdf_files:
                # Extract document_id from filename (format: arxiv_<uuid>.pdf)
                filename = pdf_path.stem
                if not filename.startswith("arxiv_"):
                    continue
                
                document_id_str = filename.replace("arxiv_", "")
                try:
                    document_id = UUID(document_id_str)
                except ValueError:
                    if self.verbose:
                        print(f"{Colors.YELLOW}[SKIP]{Colors.RESET} Invalid UUID in filename: {filename}")
                    continue
                
                # Check if already processed (has chunks directory with content)
                output_dir = self.output_dir / "documents" / f"arxiv_{document_id}"
                chunks_dir = output_dir / "chunks"
                has_chunks = chunks_dir.exists() and any(chunks_dir.glob("chunk_*.md"))
                
                if has_chunks:
                    # Already processed, load into catalog
                    if self.verbose:
                        print(f"[SKIP] Already processed: {filename}")
                    # Load existing catalog entry if available
                    doc_metadata_path = output_dir / "document_metadata.json"
                    if doc_metadata_path.exists():
                        import json
                        with open(doc_metadata_path, 'r', encoding='utf-8') as f:
                            doc_metadata = json.load(f)
                        catalog_entries.append({
                            "document_id": str(document_id),
                            "title": doc_metadata.get("title", "Unknown"),
                            "arxiv_id": doc_metadata.get("arxiv_id"),
                            "source_url": doc_metadata.get("source_url", ""),
                            "document_dir": str(output_dir)
                        })
                    continue
                
                # Need to process this PDF
                unprocessed_count += 1
                
                # Check cache for metadata
                arxiv_id = None
                arxiv_version = None
                source_url = None
                title = f"Document {document_id_str[:8]}"
                
                if self.enable_cache and self.cache_manager:
                    # Try to find this document in cache by document_id
                    cache_stats = self.cache_manager.get_cache_stats()
                    for cached_arxiv_id, cached_entry in self.cache_manager.cache.items():
                        if cached_entry.document_id == document_id_str:
                            arxiv_id = cached_arxiv_id
                            arxiv_version = cached_entry.version
                            source_url = cached_entry.source_url
                            title = cached_entry.title
                            break
                
                # Create minimal DiscoveredDocument for processing
                discovered_doc = DiscoveredDocument(
                    document_id=document_id,
                    title=title,
                    source_url=source_url or f"file://{pdf_path}",
                    discovery_timestamp=datetime.now(timezone.utc),
                    estimated_size=pdf_path.stat().st_size,
                    arxiv_id=arxiv_id,
                    arxiv_version=arxiv_version
                )
                
                # Create AcquiredDocument from existing file
                acquired_doc = AcquiredDocument(
                    document_id=document_id,
                    local_path=str(pdf_path),
                    file_hash_sha256="",  # Will be calculated if needed
                    file_hash_sha512="",
                    file_size=pdf_path.stat().st_size,
                    download_timestamp=datetime.now(timezone.utc),
                    download_status="success",
                    retry_count=0,
                    validation_status="passed",
                    arxiv_id=arxiv_id,
                    arxiv_version=arxiv_version
                )
                
                # Process the document
                print(f"{Colors.CYAN}Processing:{Colors.RESET} {title}")
                if self.enable_cache and self.cache_manager and arxiv_id:
                    success = self._process_document_with_cache(discovered_doc, acquired_doc, catalog_entries)
                else:
                    success = self._process_document(discovered_doc, acquired_doc, catalog_entries)
                
                if not success:
                    self.metadata_manager.log("WARNING", "processing", 
                        f"Failed to process: {title}")
            
            # Save outputs
            self._save_catalog(catalog_entries)
            self._save_log()
            
            print(f"\n{Colors.GREEN}✓ Process-only mode completed{Colors.RESET}")
            print(f"  Processed: {unprocessed_count}")
            print(f"  Skipped (already processed): {len(pdf_files) - unprocessed_count}")
            print(f"  Total catalog entries: {len(catalog_entries)}\n")
            
            self.metadata_manager.log("INFO", "pipeline", "Process-only mode completed", {
                "processed": unprocessed_count,
                "skipped": len(pdf_files) - unprocessed_count,
                "total_catalog_entries": len(catalog_entries)
            })
            
            return True
            
        except Exception as e:
            self.metadata_manager.log("ERROR", "pipeline", f"Process-only mode failed: {str(e)}")
            self._save_log()
            return False
    
    def _run_discovery(self, query: str) -> List[DiscoveredDocument]:
        """
        Run discovery phase.
        
        Args:
            query: Search query
            
        Returns:
            List of discovered documents
        """
        self.metadata_manager.log("INFO", "discovery", "Starting discovery phase", {
            "query": query
        })
        discovered: List[DiscoveredDocument] = self.discovery.search(query)
        self.metadata_manager.log("INFO", "discovery", f"Discovered {len(discovered)} documents")
        self.discovery.save_discovery_output(
            discovered,
            self.output_dir / "discovery_output.json"
        )
        return discovered
    
    def _run_acquisition(self, documents: List[DiscoveredDocument]) -> List[AcquiredDocument]:
        """
        Run acquisition phase.
        
        Args:
            documents: Documents to acquire
            
        Returns:
            List of acquisition results
        """
        self.metadata_manager.log("INFO", "acquisition", f"Starting acquisition of {len(documents)} documents")
        acquired: List[AcquiredDocument] = self.acquisition.acquire(documents)
        successful: int = sum(1 for a in acquired if a.download_status == "success")
        self.metadata_manager.log("INFO", "acquisition", 
            f"Acquisition complete: {successful}/{len(acquired)} successful")
        self.acquisition.save_acquisition_output(
            acquired,
            self.output_dir / "acquisition_output.json"
        )
        return acquired
    
    def _process_document_with_cache(
        self,
        discovered: DiscoveredDocument,
        acquired: AcquiredDocument,
        catalog_entries: List[Dict[str, Any]]
    ) -> bool:
        """
        Process single document with cache checking.
        
        Args:
            discovered: Discovery information
            acquired: Acquisition information
            catalog_entries: List to append catalog entry to
            
        Returns:
            True if successful, False otherwise
        """
        if not discovered.arxiv_id or not self.cache_manager:
            return self._process_document(discovered, acquired, catalog_entries)
        should_process: bool = self.cache_manager.should_process(
            discovered.arxiv_id,
            discovered.arxiv_version or "v1",
            acquired.file_hash_sha256
        )
        if not should_process:
            self.metadata_manager.log("INFO", "cache", 
                f"Using cached version: {discovered.title} ({discovered.arxiv_id} {discovered.arxiv_version})")
            if self.verbose:
                print(f"[CACHE] ✓ Using cached: {discovered.arxiv_id} {discovered.arxiv_version} - {discovered.title[:60]}...")
            cached_entry = self.cache_manager.get_cached_entry(discovered.arxiv_id)
            if cached_entry:
                return self._load_from_cache(cached_entry, catalog_entries)
        if self.verbose:
            print(f"[CACHE] ⟳ Processing: {discovered.arxiv_id} {discovered.arxiv_version} - {discovered.title[:60]}...")
        success: bool = self._process_document(discovered, acquired, catalog_entries)
        if success and discovered.arxiv_id:
            self.cache_manager.update_processing_status(discovered.arxiv_id, "success")
            self.metadata_manager.log("INFO", "cache", 
                f"Cached: {discovered.title} ({discovered.arxiv_id} {discovered.arxiv_version})")
            if self.verbose:
                print(f"[CACHE] ✓ Processed: {discovered.arxiv_id} {discovered.arxiv_version}")
        elif not success and discovered.arxiv_id:
            self.cache_manager.update_processing_status(discovered.arxiv_id, "failed")
        return success
    
    def _load_from_cache(
        self,
        cached_entry,
        catalog_entries: List[Dict[str, Any]]
    ) -> bool:
        """
        Load document information from cache.
        
        Args:
            cached_entry: Cached entry information
            catalog_entries: List to append catalog entry to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc_dir: Path = Path(cached_entry.output_dir)
            metadata_file: Path = doc_dir / "document_metadata.json"
            chunks_dir: Path = doc_dir / "chunks"
            if not metadata_file.exists() or not chunks_dir.exists():
                return False
            import json
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata_data: Dict[str, Any] = json.load(f)
            chunk_files: list = [f for f in chunks_dir.glob("chunk_*_metadata.json")]
            chunk_count: int = len(chunk_files)
            catalog_entry: Dict[str, Any] = {
                "document_id": metadata_data["document_id"],
                "title": metadata_data["title"],
                "source_type": metadata_data["source_type"],
                "original_url": metadata_data["original_url"],
                "chunk_count": chunk_count,
                "file_hash": metadata_data["file_hash"],
                "processing_timestamp": metadata_data["processing_timestamp"],
                "adapter_version": metadata_data["adapter_version"]
            }
            catalog_entries.append(catalog_entry)
            return True
        except Exception as e:
            self.metadata_manager.log("ERROR", "cache", 
                f"Failed to load from cache: {str(e)}")
            return False
    
    def _process_document(
        self,
        discovered: DiscoveredDocument,
        acquired: AcquiredDocument,
        catalog_entries: List[Dict[str, Any]]
    ) -> bool:
        """
        Process single document through processing and chunking.
        
        Args:
            discovered: Discovery information
            acquired: Acquisition information
            catalog_entries: List to append catalog entry to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.metadata_manager.log("INFO", "processing", 
                f"Processing document: {discovered.title}")
            doc_dir: Path = self.output_dir / "documents" / f"arxiv_{acquired.document_id}"
            doc_dir.mkdir(parents=True, exist_ok=True)
            markdown_path, proc_metadata = self.processor.process(acquired, self.output_dir / "documents")
            if not markdown_path.exists():
                self.metadata_manager.log("ERROR", "processing", 
                    f"Processing failed: {discovered.title}")
                return False
            self.processor.save_processing_metadata(
                proc_metadata,
                doc_dir / "processing_metadata.json"
            )
            self.metadata_manager.log("INFO", "chunking", 
                f"Chunking document: {discovered.title}")
            chunks: List[ChunkContent] = self.chunker.chunk(markdown_path, discovered.document_id)
            self.chunker.save_chunks(chunks, doc_dir)
            self.metadata_manager.log("INFO", "chunking", 
                f"Created {len(chunks)} chunks")
            doc_metadata: DocumentMetadata = self.metadata_manager.create_document_metadata(
                discovered, acquired, markdown_path
            )
            self.metadata_manager.save_document_metadata(
                doc_metadata,
                doc_dir / "document_metadata.json"
            )
            catalog_entry: Dict[str, Any] = self.metadata_manager.create_catalog_entry(
                doc_metadata, len(chunks)
            )
            catalog_entries.append(catalog_entry)
            return True
        except Exception as e:
            self.metadata_manager.log("ERROR", "processing", 
                f"Failed to process document: {str(e)}")
            return False
    
    def _save_catalog(self, entries: List[Dict[str, Any]]) -> None:
        """
        Save catalog file.
        
        Args:
            entries: Catalog entries
        """
        self.metadata_manager.save_catalog(
            entries,
            self.output_dir / "catalog.json"
        )
    
    
    def _save_log(self) -> None:
        """Save processing log."""
        self.metadata_manager.save_log(
            self.output_dir / "processing_log.json"
        )


def main() -> int:
    """
    Main entry point for ArXiv adapter.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="HEPilot ArXiv Adapter - Discover and process HEP papers from arXiv"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("adapter_config.json"),
        help="Path to adapter configuration file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output"),
        help="Output directory for processed documents"
    )
    parser.add_argument(
        "--query",
        type=str,
        default="all:lhcb",
        help="arXiv search query (default: all:lhcb for LHCb papers)"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=None,
        help="Maximum number of papers to process (for dev mode)"
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Development mode (process only 5 papers)"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching system (reprocess all papers)"
    )
    parser.add_argument(
        "--download-only",
        action="store_true",
        help="Download PDFs only, skip processing"
    )
    parser.add_argument(
        "--process-only",
        action="store_true",
        help="Process already downloaded PDFs only, skip discovery and download"
    )
    args = parser.parse_args()
    
    # Validate mutually exclusive options
    if args.download_only and args.process_only:
        print("ERROR: --download-only and --process-only cannot be used together")
        return 1
    
    max_results: Optional[int] = args.max_results
    if args.dev:
        max_results = 5
    pipeline: ArxivAdapterPipeline = ArxivAdapterPipeline(
        config_path=args.config,
        output_dir=args.output,
        max_results=max_results,
        enable_cache=not args.no_cache,
        verbose=args.dev or args.max_results is not None
    )
    success: bool = pipeline.run(
        query=args.query,
        download_only=args.download_only,
        process_only=args.process_only
    )
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

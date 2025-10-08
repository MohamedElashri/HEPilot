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
from cache_manager import CacheManager
from models import DiscoveredDocument, AcquiredDocument, ChunkContent, DocumentMetadata


class ArxivAdapterPipeline:
    """Orchestrates the complete ArXiv adapter pipeline."""
    
    def __init__(self, config_path: Path, output_dir: Path, max_results: Optional[int] = None, enable_cache: bool = True) -> None:
        """
        Initialize adapter pipeline.
        
        Args:
            config_path: Path to adapter_config.json
            output_dir: Directory for output files
            max_results: Maximum number of papers to process (None for unlimited)
            enable_cache: Whether to enable caching system
        """
        self.config_manager: ConfigManager = ConfigManager(config_path)
        self.output_dir: Path = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_results: Optional[int] = max_results
        self.enable_cache: bool = enable_cache
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
            download_dir=output_dir / "downloads"
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
    
    def run(self, query: str = "cat:hep-ex OR cat:hep-ph") -> bool:
        """
        Run the complete pipeline.
        
        Args:
            query: arXiv search query
            
        Returns:
            True if pipeline succeeded, False otherwise
        """
        try:
            self.metadata_manager.log("INFO", "pipeline", "Starting ArXiv adapter pipeline", {
                "query": query,
                "max_results": self.max_results,
                "cache_enabled": self.enable_cache
            })
            if self.enable_cache and self.cache_manager:
                cache_stats = self.cache_manager.get_cache_stats()
                self.metadata_manager.log("INFO", "cache", f"Cache initialized with {cache_stats['total_papers']} existing entries")
                print(f"\n[CACHE] Loaded cache with {cache_stats['total_papers']} existing papers")
            discovered: List[DiscoveredDocument] = self._run_discovery(query)
            if not discovered:
                self.metadata_manager.log("WARNING", "pipeline", "No documents discovered")
                return False
            catalog_entries: List[Dict[str, Any]] = []
            to_download: List[DiscoveredDocument] = []
            to_process_from_cache: List[DiscoveredDocument] = []
            fully_cached: List[DiscoveredDocument] = []
            if self.enable_cache and self.cache_manager:
                for doc in discovered:
                    if not doc.arxiv_id:
                        to_download.append(doc)
                        continue
                    cached_entry = self.cache_manager.get_cached_entry(doc.arxiv_id)
                    if not cached_entry:
                        print(f"[CACHE] → New paper: {doc.arxiv_id} {doc.arxiv_version}")
                        to_download.append(doc)
                    elif cached_entry.version != (doc.arxiv_version or "v1"):
                        print(f"[CACHE] → New version: {doc.arxiv_id} {cached_entry.version} → {doc.arxiv_version}")
                        to_download.append(doc)
                    elif cached_entry.processing_status != "success":
                        print(f"[CACHE] → Retry ({cached_entry.processing_status}): {doc.arxiv_id} {doc.arxiv_version}")
                        to_process_from_cache.append(doc)
                    else:
                        print(f"[CACHE] ✓ Cached: {doc.arxiv_id} {doc.arxiv_version}")
                        fully_cached.append(doc)
                print(f"\n[CACHE] Summary: {len(fully_cached)} cached, {len(to_download)} new/updated, {len(to_process_from_cache)} retry\n")
                for cached_doc in fully_cached:
                    cached_entry = self.cache_manager.get_cached_entry(cached_doc.arxiv_id)
                    if cached_entry:
                        self._load_from_cache(cached_entry, catalog_entries)
            else:
                to_download = discovered
            if to_download:
                acquired: List[AcquiredDocument] = self._run_acquisition(to_download)
                if acquired:
                    if self.enable_cache and self.cache_manager:
                        for disc, acq in zip(to_download, acquired):
                            if acq.download_status == "success" and disc.arxiv_id:
                                doc_dir: Path = self.output_dir / "documents" / f"arxiv_{acq.document_id}"
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
                                print(f"[CACHE] ✓ Downloaded: {disc.arxiv_id} {disc.arxiv_version}")
                    for disc, acq in zip(to_download, acquired):
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
            if to_process_from_cache and self.enable_cache and self.cache_manager:
                print(f"\n[CACHE] Retrying {len(to_process_from_cache)} previously failed papers\n")
                for doc in to_process_from_cache:
                    cached_entry = self.cache_manager.get_cached_entry(doc.arxiv_id)
                    if not cached_entry:
                        continue
                    pdf_path: Path = self.output_dir / "downloads" / f"{cached_entry.document_id}.pdf"
                    if not pdf_path.exists():
                        print(f"[CACHE] ✗ Missing PDF for retry: {doc.arxiv_id} {doc.arxiv_version}")
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
            print(f"[CACHE] ✓ Using cached: {discovered.arxiv_id} {discovered.arxiv_version} - {discovered.title[:60]}...")
            cached_entry = self.cache_manager.get_cached_entry(discovered.arxiv_id)
            if cached_entry:
                return self._load_from_cache(cached_entry, catalog_entries)
        print(f"[CACHE] ⟳ Processing: {discovered.arxiv_id} {discovered.arxiv_version} - {discovered.title[:60]}...")
        success: bool = self._process_document(discovered, acquired, catalog_entries)
        if success and discovered.arxiv_id:
            self.cache_manager.update_processing_status(discovered.arxiv_id, "success")
            self.metadata_manager.log("INFO", "cache", 
                f"Cached: {discovered.title} ({discovered.arxiv_id} {discovered.arxiv_version})")
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
        default="cat:hep-ex OR cat:hep-ph",
        help="arXiv search query"
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
    args = parser.parse_args()
    max_results: Optional[int] = args.max_results
    if args.dev:
        max_results = 5
    pipeline: ArxivAdapterPipeline = ArxivAdapterPipeline(
        config_path=args.config,
        output_dir=args.output,
        max_results=max_results,
        enable_cache=not args.no_cache
    )
    success: bool = pipeline.run(query=args.query)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

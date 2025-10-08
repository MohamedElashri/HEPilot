"""
Main orchestrator for ArXiv adapter pipeline.

Coordinates discovery, acquisition, processing, and chunking stages
to produce HEPilot-compliant output for RAG system ingestion.
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import ConfigManager
from discovery import ArxivDiscovery
from acquisition import ArxivAcquisition
from processing import ArxivProcessor
from chunking import ArxivChunker
from metadata import MetadataManager
from models import DiscoveredDocument, AcquiredDocument, ChunkContent, DocumentMetadata


class ArxivAdapterPipeline:
    """Orchestrates the complete ArXiv adapter pipeline."""
    
    def __init__(self, config_path: Path, output_dir: Path, max_results: Optional[int] = None) -> None:
        """
        Initialize adapter pipeline.
        
        Args:
            config_path: Path to adapter_config.json
            output_dir: Directory for output files
            max_results: Maximum number of papers to process (None for unlimited)
        """
        self.config_manager: ConfigManager = ConfigManager(config_path)
        self.output_dir: Path = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_results: Optional[int] = max_results
        self.metadata_manager: MetadataManager = MetadataManager(
            adapter_version=self.config_manager.config.version,
            include_authors=self.config_manager.get_include_authors_metadata()
        )
        self.discovery: ArxivDiscovery = ArxivDiscovery(max_results=max_results)
        self.acquisition: ArxivAcquisition = ArxivAcquisition(
            download_dir=output_dir / "downloads"
        )
        self.processor: ArxivProcessor = ArxivProcessor(
            preserve_tables=self.config_manager.get_preserve_tables(),
            preserve_equations=self.config_manager.get_preserve_equations(),
            enrich_formulas=self.config_manager.get_enrich_formulas(),
            exclude_references=self.config_manager.get_exclude_references(),
            exclude_acknowledgments=self.config_manager.get_exclude_acknowledgments(),
            exclude_author_lists=self.config_manager.get_exclude_author_lists()
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
                "max_results": self.max_results
            })
            discovered: List[DiscoveredDocument] = self._run_discovery(query)
            if not discovered:
                self.metadata_manager.log("WARNING", "pipeline", "No documents discovered")
                return False
            acquired: List[AcquiredDocument] = self._run_acquisition(discovered)
            if not acquired:
                self.metadata_manager.log("ERROR", "pipeline", "No documents acquired")
                return False
            catalog_entries: List[Dict[str, Any]] = []
            for disc, acq in zip(discovered, acquired):
                if acq.download_status != "success":
                    continue
                success: bool = self._process_document(disc, acq, catalog_entries)
                if not success:
                    self.metadata_manager.log("WARNING", "pipeline", 
                        f"Failed to process document: {disc.title}")
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
    args = parser.parse_args()
    max_results: Optional[int] = args.max_results
    if args.dev:
        max_results = 5
    pipeline: ArxivAdapterPipeline = ArxivAdapterPipeline(
        config_path=args.config,
        output_dir=args.output,
        max_results=max_results
    )
    success: bool = pipeline.run(query=args.query)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

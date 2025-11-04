"""
Main orchestrator for Twiki adapter pipeline
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

from twiki_config import TwikiConfigManager
from twiki_discovery import TwikiDiscovery
from acquisition import TwikiAcquisition
from twiki_processing import TwikiProcessor
from twiki_chunker import TWikiChunker
from metadata import TwikiMetadataManager
from models import DiscoveredDocument, AcquiredDocument, ChunkContent, DocumentMetadata

class TwikiAdapterPipeline:

    def __init__(self, config_path: Path, input_dir: Path, output_dir: Path, verbose: bool = False) -> None:
        self.config_manager = TwikiConfigManager(config_path)
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose

        # Initialize modules
        self.discovery = TwikiDiscovery()
        self.acquisition = TwikiAcquisition(download_dir=self.output_dir / "downloads", verbose=verbose) # type: ignore
        self.processor = TwikiProcessor(
            exclude_edit_metadata=self.config_manager.get_exclude_edit_metadata(),
            exclude_raw_macros=self.config_manager.get_exclude_raw_macros(),
            preserve_equations=self.config_manager.get_preserve_equations(),
            preserve_tables=self.config_manager.get_preserve_tables()
        )
        self.chunker = TWikiChunker(
            chunk_size=self.config_manager.get_chunk_size(),
            chunk_overlap=self.config_manager.get_chunk_overlap(),
            model_name=self.config_manager.get_embedding_model_name(),
            use_model_tokenizer=self.config_manager.get_use_model_tokenizer(),
            cache_dir=self.config_manager.get_model_cache_dir(),
            verbose=self.verbose
        )
        self.metadata_manager = TwikiMetadataManager(adapter_version=self.config_manager.get_adapter_version())

    def run(self) -> bool:
        try:
            print(f"\n[INFO] Starting TWiki adapter pipeline at {datetime.now(timezone.utc).isoformat()}\n")

            discovered_docs = self._run_discovery()
            if not discovered_docs:
                print("[WARN] No TWiki files found to process.")
                return False

            acquired_docs = self._run_acquisition(discovered_docs)

            processed_docs = self._run_processing(acquired_docs)

            self._run_chunking(processed_docs)

            print("\n[INFO] TWiki pipeline completed successfully.")
            return True
        except Exception as e:
            print(f"[ERROR] Pipeline failed: {e}")
            return False
        
    def _run_discovery(self) -> List[DiscoveredDocument]:
        print("[INFO] Discovering TWiki documents...")
        discovered: List[DiscoveredDocument] = []

        for path in self.input_dir.glob("*.txt"):
            doc = DiscoveredDocument(
                document_id=uuid.uuid5(uuid.NAMESPACE_URL, str(path.resolve())),
                source_type="twiki",
                source_url=f"file://{path.resolve()}",
                title=path.stem,
                authors=None,
                discovery_timestamp=datetime.now(timezone.utc),
                estimated_size=path.stat().st_size,
                content_type="text/plain"
            )
            discovered.append(doc)

        self.discovery.save_discovery_output(discovered, self.output_dir / "discovery_output.json")
        print(f"[INFO] Discovered {len(discovered)} TWiki files.")
        return discovered
    
    def _run_acquisition(self, discovered_docs: List[DiscoveredDocument]) -> List[AcquiredDocument]:
        # registering local TWiki files as AcquiredDocuments.
        print("[INFO] Registering TWiki files as acquired documents...")
        acquired_docs = []
        for doc in discovered_docs:
            acquired = self.acquisition.register_local(doc) # type: ignore
            acquired_docs.append(acquired)
        return acquired_docs
    
    def _run_processing(self, acquired_docs: List[AcquiredDocument]) -> List[Path]:
        print("[INFO] Processing Twiki text files...")
        processed =[]
        for doc in acquired_docs:
            md_path, metadata = self.processor.process(doc, self.output_dir / "processed")
            self.processor.save_processing_metadata(metadata, md_path.parent / "processing_metadata.json")
            processed.append(md_path)
        return processed
    
    def _run_chunking(self, processed_docs: List[Path]) -> None:
        print("[INFO] Chunking processed Twiki documents...")
        for md_path in processed_docs:
            document_id = uuid.uuid5(uuid.NAMESPACE_URL, str(md_path))
            chunks = self.chunker.chunk_document(md_path, document_id)
            self.chunker.save_chunks(chunks, self.output_dir/"chunks")

    def main() -> int: # type: ignore
        parser = argparse.ArgumentParser(
        description="HEPilot TWiki Adapter - Process local TWiki documents"
    )
        parser.add_argument(
        "--config",
        type=Path,
        default=Path("adapter_config.json"),
        help="Path to adapter configuration"
    )
        parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input directory containing TWiki .txt files"
    )
        parser.add_argument(
        "--output",
        type=Path,
        default=Path("output_twiki"),
        help="Output directory"
    )
        parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

        args = parser.parse_args()

        pipeline = TwikiAdapterPipeline(
            config_path=args.config,
            input_dir=args.input,
            output_dir=args.output,
            verbose=args.verbose
        )

        success = pipeline.run()
        return 0 if success else 1

    
    if __name__ == "__main__":
        sys.exit(main())

    

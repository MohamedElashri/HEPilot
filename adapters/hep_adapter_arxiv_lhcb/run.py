#!/usr/bin/env python3
"""
HEPilot arXiv LHCb Adapter Runner
This script provides a command-line interface to run the HEPilot arXiv LHCb adapter,
allowing for flexible configuration and execution of the document processing pipeline.
"""

import asyncio
import argparse
from pathlib import Path
import json
import logging

from hepilot_arxiv_adapter import HEPilotArxivAdapter, AdapterConfig


def main():
    """Main function to run the adapter with command-line arguments."""
    parser = argparse.ArgumentParser(description="Run the HEPilot arXiv LHCb adapter.")
    
    # Execution control
    parser.add_argument("--max-documents", type=int, default=10, help="Maximum number of documents to process.")
    parser.add_argument("--output-dir", type=str, default="./hepilot_output", help="Directory to store the output.")
    parser.add_argument("--skip-processed", action="store_true", help="Skip documents that have already been processed.")
    
    # Adapter configuration
    parser.add_argument("--chunk-size", type=int, default=1024, help="Chunk size for document processing.")
    parser.add_argument("--chunk-overlap", type=float, default=0.1, help="Chunk overlap for document processing.")
    parser.add_argument("--preserve-tables", action="store_true", default=True, help="Preserve tables in the output.")
    parser.add_argument("--preserve-equations", action="store_true", default=True, help="Preserve equations in the output.")
    parser.add_argument("--preserve-inline-equations", action="store_true", default=True, help="Preserve inline equations in the output.")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Create adapter configuration
    config = AdapterConfig(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        preserve_tables=args.preserve_tables,
        preserve_equations=args.preserve_equations,
        preserve_inline_equations=args.preserve_inline_equations
    )

    # Output directory
    output_dir = Path(args.output_dir)

    # Create and run adapter
    adapter = HEPilotArxivAdapter(config, output_dir)

    # Handle skipping of processed documents
    if args.skip_processed:
        logger.info("Checking for already processed documents...")
        # In a real implementation, you would check a database or a manifest file.
        # For this example, we'll just log a message.
        logger.info("Skipping of processed documents is not fully implemented in this example.")

    logger.info(f"Starting adapter with the following configuration:\n{json.dumps(config.to_dict(), indent=2)}")

    # Run the pipeline
    try:
        result = asyncio.run(adapter.run_pipeline(max_documents=args.max_documents))
        logger.info(f"Pipeline completed successfully: {result}")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)


if __name__ == "__main__":
    main()


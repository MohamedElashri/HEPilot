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
import yaml

from hepilot_arxiv_adapter import HEPilotArxivAdapter, AdapterConfig


def main():
    """Main function to run the adapter with command-line arguments."""
    parser = argparse.ArgumentParser(description="Run the HEPilot arXiv LHCb adapter.")
    
    # Config file
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to the configuration file.")

    # Execution control
    parser.add_argument("--max-documents", type=int, help="Maximum number of documents to process.")
    parser.add_argument("--output-dir", type=str, help="Directory to store the output.")
    parser.add_argument("--skip-processed", action="store_true", help="Skip documents that have already been processed.")
    
    # Adapter configuration
    parser.add_argument("--chunk-size", type=int, help="Chunk size for document processing.")
    parser.add_argument("--chunk-overlap", type=float, help="Chunk overlap for document processing.")
    parser.add_argument("--preserve-tables", action="store_true", help="Preserve tables in the output.")
    parser.add_argument("--preserve-equations", action="store_true", help="Preserve equations in the output.")
    parser.add_argument("--preserve-inline-equations", action="store_true", help="Preserve inline equations in the output.")
    parser.add_argument("--tokenizer-model", type=str, help="The tokenizer model to use.")
    parser.add_argument("--cache-dir", type=str, help="Directory to store cache files.")
    parser.add_argument("--state-file", type=str, help="File to store the processing state.")

    args = parser.parse_args()

    # Load configuration from file
    config_path = Path(args.config)
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config_from_file = yaml.safe_load(f)
    else:
        config_from_file = {}

    # Create adapter configuration, overriding file config with command-line args
    config = AdapterConfig(
        name=config_from_file.get("name", "hepilot-arxiv-lhcb"),
        version=config_from_file.get("version", "1.0.0"),
        source_type=config_from_file.get("source_type", "arxiv"),
        profile=config_from_file.get("profile", "core"),
        chunk_size=args.chunk_size or config_from_file.get("chunk_size", 1024),
        chunk_overlap=args.chunk_overlap or config_from_file.get("chunk_overlap", 0.1),
        preserve_tables=args.preserve_tables or config_from_file.get("preserve_tables", True),
        preserve_equations=args.preserve_equations or config_from_file.get("preserve_equations", True),
        preserve_inline_equations=args.preserve_inline_equations or config_from_file.get("preserve_inline_equations", True),
        tokenizer_model=args.tokenizer_model or config_from_file.get("tokenizer_model", "BAAI/bge-large-en-v1.5"),
        cache_dir=args.cache_dir or config_from_file.get("cache_dir", "./hepilot_output/cache"),
        state_file=args.state_file or config_from_file.get("state_file", "./hepilot_output/state.json")
    )

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Output directory
    output_dir = Path(args.output_dir or config_from_file.get("output_dir", "./hepilot_output"))

    # Skip processed documents or not
    skip_processed = args.skip_processed or config_from_file.get("skip_processed", False)

    # Create and run adapter
    adapter = HEPilotArxivAdapter(config, output_dir, skip_processed=skip_processed)


    logger.info(f"Starting adapter with the following configuration:\n{json.dumps(config.to_dict(), indent=2)}")

    # Run the pipeline
    max_docs = args.max_documents or config_from_file.get("max_documents", 10)
    try:
        result = asyncio.run(adapter.run_pipeline(max_documents=max_docs))
        logger.info(f"Pipeline completed successfully: {result}")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)


if __name__ == "__main__":
    main()


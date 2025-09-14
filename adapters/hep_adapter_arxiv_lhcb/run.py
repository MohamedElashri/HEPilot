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
from colorama import Fore, Style, init

from hepilot_arxiv_adapter import HEPilotArxivAdapter

def _setup_logging() -> logging.Logger:
    """Setup logging configuration with colored output for different log levels."""
    # Initialize colorama
    init(autoreset=True)
    
    logger = logging.getLogger("hepilot_arxiv_adapter")
    logger.setLevel(logging.INFO)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    # Remove any existing handlers to avoid duplicates
    for handler in logger.handlers[:]:  # Use a copy to safely modify during iteration
        logger.removeHandler(handler)
    
    # Create new handler with colored formatting
    handler = logging.StreamHandler()
    
    # Custom formatter with colors
    class ColoredFormatter(logging.Formatter):
        FORMATS = {
            logging.DEBUG: '%(asctime)s - %(name)s - ' + Fore.CYAN + '%(levelname)s' + Style.RESET_ALL + ' - %(message)s',
            logging.INFO: '%(asctime)s - %(name)s - ' + Fore.GREEN + '%(levelname)s' + Style.RESET_ALL + ' - %(message)s',
            logging.WARNING: '%(asctime)s - %(name)s - ' + Fore.YELLOW + '%(levelname)s' + Style.RESET_ALL + ' - %(message)s',
            logging.ERROR: '%(asctime)s - %(name)s - ' + Fore.RED + '%(levelname)s' + Style.RESET_ALL + ' - %(message)s',
            logging.CRITICAL: '%(asctime)s - %(name)s - ' + Fore.RED + Style.BRIGHT + '%(levelname)s' + Style.RESET_ALL + ' - %(message)s'
        }

        def format(self, record):
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)
    
    handler.setFormatter(ColoredFormatter())
    logger.addHandler(handler)
    
    return logger

async def main():
    """Main function to run the adapter with command-line arguments."""
    parser = argparse.ArgumentParser(description="Run the HEPilot arXiv LHCb adapter.")
    
    # Config file
    parser.add_argument("--config", type=str, default="adapter_config.json", help="Path to the configuration file.")

    args = parser.parse_args()

    # Load configuration from file
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Configuration file not found at {config_path}")
        return

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Setup logging
    logger = _setup_logging()

    # Create and run adapter
    adapter = HEPilotArxivAdapter(config["adapter_config"])

    logger.info(f"Starting adapter with the following configuration:\n{json.dumps(config, indent=2)}")

    # Run the pipeline
    try:
        # Handle "all" as a special case for max_documents
        max_docs_config = config["adapter_config"]["x_extension"].get("max_documents")
        if max_docs_config == "all":
            max_documents = None
            fetch_all = True
        else:
            max_documents = max_docs_config
            fetch_all = config["adapter_config"]["x_extension"].get("fetch_all", False)
        
        discovered_docs = await adapter.discover(
            max_documents=max_documents,
            fetch_all=fetch_all
        )

        if not discovered_docs:
            logger.warning("No documents discovered, pipeline complete.")
            return

        acquired_docs = await adapter.acquire(
            discovered_docs,
            max_documents=max_documents
        )

        if not acquired_docs:
            logger.warning("No documents acquired, pipeline complete.")
            return

        catalog_entries, total_chunks = adapter.process_and_chunk(acquired_docs, discovered_docs)

        result = adapter.create_catalog(catalog_entries, total_chunks)
        
        # Show progress summary
        adapter.show_progress_summary()

        logger.info(f"Pipeline completed successfully: {result}")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
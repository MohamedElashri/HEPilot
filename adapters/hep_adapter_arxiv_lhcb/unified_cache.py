"""
Unified Cache Management for the HEPilot arXiv adapter.

This module provides a unified caching system that handles:
1. API response caching
2. Document processing state tracking
3. Path-aware content deduplication

It eliminates redundant storage and processing by checking if documents
have already been downloaded or processed in the same working directory.
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Set
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Setup colored logging
def setup_logging():
    """Setup logging configuration with colored output for different log levels."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    # Remove any existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
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

# Get configured logger
logger = setup_logging()

class UnifiedCache:
    """
    Unified caching system that handles API responses, document state tracking,
    and filesystem-based content deduplication.
    """
    def __init__(self, 
                output_dir: Path,
                cache_dir: Optional[Path] = None, 
                state_file: Optional[Path] = None,
                ttl: timedelta = timedelta(days=1)):
        """
        Initialize the unified cache.

        Args:
            output_dir: The directory where documents are stored
            cache_dir: The directory to store cache files (defaults to output_dir/cache)
            state_file: Path to the state file (defaults to output_dir/cache_state.json)
            ttl: The time-to-live for cache entries
        """
        self.output_dir = output_dir
        self.cache_dir = cache_dir or (output_dir / "cache")
        self.state_file = state_file or (output_dir / "cache_state.json")
        self.ttl = ttl
        
        # Create directories if they don't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache and state storage
        self.api_cache: Dict[str, Any] = {}
        self.document_state: Dict[str, Dict[str, Any]] = {}
        self.content_hash_map: Dict[str, str] = {}  # Maps content hashes to document IDs
        
        # Load existing state
        self._load_state()
        
        # Scan filesystem to update state
        self._scan_filesystem()
    
    def _load_state(self):
        """Load the cache state from the state file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                    self.api_cache = state_data.get("api_cache", {})
                    self.document_state = state_data.get("document_state", {})
                    self.content_hash_map = state_data.get("content_hash_map", {})
                    
                # Filter out expired API cache entries
                current_time = datetime.now(timezone.utc)
                expired_keys = []
                for url, cache_entry in self.api_cache.items():
                    if "timestamp" in cache_entry:
                        cached_timestamp = datetime.fromisoformat(cache_entry["timestamp"])
                        if current_time - cached_timestamp > self.ttl:
                            expired_keys.append(url)
                
                for key in expired_keys:
                    del self.api_cache[key]
                    
                logger.info(f"Loaded cache state with {len(self.api_cache)} API entries and {len(self.document_state)} document entries")
            except (IOError, json.JSONDecodeError) as e:
                logger.warning(f"Could not load cache state file {self.state_file}: {e}")
                self._initialize_empty_state()
        else:
            self._initialize_empty_state()
    
    def _initialize_empty_state(self):
        """Initialize empty cache state."""
        self.api_cache = {}
        self.document_state = {}
        self.content_hash_map = {}
        logger.info("Initialized empty cache state")
    
    def _save_state(self):
        """Save the current cache state to the state file."""
        try:
            state_data = {
                "api_cache": self.api_cache,
                "document_state": self.document_state,
                "content_hash_map": self.content_hash_map,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2)
                
            logger.debug(f"Saved cache state to {self.state_file}")
        except IOError as e:
            logger.error(f"Could not write to cache state file {self.state_file}: {e}")
    
    def _scan_filesystem(self):
        """
        Scan the filesystem for existing documents and update the cache state.
        This ensures the cache is aware of documents that might have been
        downloaded or processed in previous runs or by other tools.
        """
        documents_dir = self.output_dir / "documents"
        if not documents_dir.exists():
            return
            
        logger.info(f"Scanning filesystem for existing documents in {documents_dir}")
        
        # Count for statistics
        docs_found = 0
        docs_added_to_state = 0
        
        # Scan for document directories (named arxiv_<uuid>)
        for doc_dir in documents_dir.glob("arxiv_*"):
            if not doc_dir.is_dir():
                continue
                
            docs_found += 1
            document_id = doc_dir.name.replace("arxiv_", "")
            
            # Check if document metadata exists
            metadata_file = doc_dir / "document_metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        
                    # Check if document content exists
                    content_file = doc_dir / "full_document.md"
                    pdf_file_path = metadata.get("local_path")
                    pdf_file = Path(pdf_file_path) if pdf_file_path else None
                    
                    # Update state if document is complete
                    if content_file.exists() and (pdf_file and pdf_file.exists()):
                        # Get file hash from metadata or compute it
                        file_hash = metadata.get("file_hash")
                        if not file_hash and pdf_file:
                            file_hash = self._compute_file_hash(pdf_file)
                            
                        # Check if we have chunks
                        chunks_dir = doc_dir / "chunks"
                        chunk_count = len(list(chunks_dir.glob("chunk_*.md"))) if chunks_dir.exists() else 0
                        
                        # Update document state
                        self.document_state[document_id] = {
                            "status": "processed",
                            "file_hash": file_hash,
                            "title": metadata.get("title", "Unknown"),
                            "chunk_count": chunk_count,
                            "file_path": str(doc_dir.relative_to(self.output_dir)),
                            "local_pdf_path": pdf_file_path
                        }
                        
                        # Update content hash map
                        if file_hash:
                            self.content_hash_map[file_hash] = document_id
                            
                        docs_added_to_state += 1
                        
                except (IOError, json.JSONDecodeError) as e:
                    logger.warning(f"Could not read metadata for document {document_id}: {e}")
                    continue
        
        logger.info(f"Filesystem scan complete: found {docs_found} document directories, added {docs_added_to_state} to state")
        
        # Save updated state
        if docs_added_to_state > 0:
            self._save_state()
    
    def _compute_file_hash(self, file_path: Path) -> str:
        """
        Compute SHA-256 hash of a file.
        """
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except IOError as e:
            logger.warning(f"Could not compute hash for file {file_path}: {e}")
            return ""
    
    def _get_cache_key(self, url: str) -> str:
        """
        Generate a cache key from a URL.
        """
        return hashlib.sha256(url.encode()).hexdigest()
    
    def get_api_response(self, url: str) -> Optional[Any]:
        """
        Retrieve a cached API response for a given URL.

        Args:
            url: The URL of the request.

        Returns:
            The cached response data, or None if not found or expired.
        """
        cache_entry = self.api_cache.get(url)
        if not cache_entry:
            return None
            
        # Check if the cache entry has expired
        current_time = datetime.now(timezone.utc)
        cached_timestamp = datetime.fromisoformat(cache_entry["timestamp"])
        if current_time - cached_timestamp > self.ttl:
            logger.info(f"Cache expired for {url}")
            del self.api_cache[url]
            self._save_state()
            return None
            
        # Return cached data
        logger.info(f"Using cached API response for {url}")
        return cache_entry["data"]
    
    def set_api_response(self, url: str, data: Any):
        """
        Cache an API response for a given URL.

        Args:
            url: The URL of the request.
            data: The response data to cache.
        """
        self.api_cache[url] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "url": url,
            "data": data
        }
        
        # Only save state periodically for API responses to avoid excessive writes
        if len(self.api_cache) % 5 == 0:
            self._save_state()
    
    def is_document_processed(self, document_id: str, file_hash: Optional[str] = None) -> bool:
        """
        Check if a document has been successfully processed.

        Args:
            document_id: The ID of the document.
            file_hash: Optional file hash to check content-based duplication.

        Returns:
            True if the document has been processed, False otherwise.
        """
        # First check if we have this document in our state
        doc_state = self.document_state.get(document_id)
        if doc_state and doc_state.get("status") == "processed":
            logger.info(f"Document {document_id} found in cache state as processed")
            return True
            
        # If we have a file hash, check content-based duplication
        if file_hash and file_hash in self.content_hash_map:
            existing_doc_id = self.content_hash_map[file_hash]
            logger.info(f"Document with same content hash exists: {existing_doc_id}")
            return True
        
        # Check if document exists on disk
        doc_dir = self.output_dir / "documents" / f"arxiv_{document_id}"
        if doc_dir.exists():
            content_file = doc_dir / "full_document.md"
            if content_file.exists():
                logger.info(f"Document {document_id} found on disk at {doc_dir}")
                # Add to our state so we'll find it next time
                metadata_file = doc_dir / "document_metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        # Get PDF path and hash if available
                        pdf_file_path = metadata.get("local_path")
                        file_hash = metadata.get("file_hash")
                        
                        if file_hash:
                            # Update our state
                            chunks_dir = doc_dir / "chunks"
                            chunk_count = len(list(chunks_dir.glob("chunk_*.md"))) if chunks_dir.exists() else 0
                            
                            self.document_state[document_id] = {
                                "status": "processed",
                                "file_hash": file_hash,
                                "title": metadata.get("title", "Unknown"),
                                "chunk_count": chunk_count,
                                "file_path": str(doc_dir.relative_to(self.output_dir)),
                                "local_pdf_path": pdf_file_path
                            }
                            
                            # Update content hash map
                            self.content_hash_map[file_hash] = document_id
                            
                            # Save the state
                            self._save_state()
                            
                            return True
                    except Exception as e:
                        logger.warning(f"Error processing document metadata for {document_id}: {e}")
            
        logger.debug(f"Document {document_id} not found in cache state or on disk")
        return False

    def get_document_by_hash(self, file_hash: str) -> Optional[str]:
        """
        Get document ID for a given content hash.

        Args:
            file_hash: The hash of the file content.

        Returns:
            Document ID if found, None otherwise.
        """
        return self.content_hash_map.get(file_hash)
    
    def set_document_processed(self, document_id: str, file_hash: str, metadata: Dict[str, Any]):
        """
        Mark a document as processed and update its metadata.

        Args:
            document_id: The ID of the document.
            file_hash: The hash of the document content.
            metadata: Additional metadata about the document.
        """
        self.document_state[document_id] = {
            "status": "processed",
            "file_hash": file_hash,
            **metadata
        }
        
        # Update content hash map
        if file_hash:
            self.content_hash_map[file_hash] = document_id
            
        self._save_state()
    
    def set_document_failed(self, document_id: str, error_message: str):
        """
        Mark a document as failed during processing.

        Args:
            document_id: The ID of the document.
            error_message: The error message explaining the failure.
        """
        self.document_state[document_id] = {
            "status": "failed",
            "error": error_message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self._save_state()
        
    def get_document_metadata(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a document.

        Args:
            document_id: The ID of the document.

        Returns:
            Document metadata if found, None otherwise.
        """
        return self.document_state.get(document_id)
        
    def get_all_processed_documents(self) -> List[Dict[str, Any]]:
        """
        Get a list of all successfully processed documents.

        Returns:
            List of document metadata dictionaries.
        """
        return [
            {"document_id": doc_id, **metadata}
            for doc_id, metadata in self.document_state.items()
            if metadata.get("status") == "processed"
        ]

    def clear_cache(self, clear_api: bool = True, clear_documents: bool = False):
        """
        Clear the cache selectively.

        Args:
            clear_api: Whether to clear API response cache.
            clear_documents: Whether to clear document state (use with caution).
        """
        if clear_api:
            self.api_cache = {}
            logger.info("Cleared API response cache")
            
        if clear_documents:
            self.document_state = {}
            self.content_hash_map = {}
            logger.warning("Cleared document state cache")
            
        if clear_api or clear_documents:
            self._save_state()

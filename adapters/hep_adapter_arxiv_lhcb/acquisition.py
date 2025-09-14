#!/usr/bin/env python3
"""
Acquisition Module for HEPilot ArXiv Adapter
Handles downloading and validating arXiv papers with retry logic.
"""

import asyncio
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

import aiohttp

from models import AcquiredDocument


class DocumentAcquisition:
    """Acquisition module for downloading arXiv papers."""
    
    def __init__(self, config: Dict[str, Any], output_dir: Path):
        """Initialize the acquisition module.
        
        Args:
            config: Adapter configuration dictionary
            output_dir: Output directory path
        """
        self.config = config
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def acquire_documents(self, discovered_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Acquire (download) discovered documents.
        
        Args:
            discovered_docs: List of discovered document dictionaries
            
        Returns:
            Dictionary containing acquired documents information
        """
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
        """Download a single document with retry logic.
        
        Args:
            doc_dict: Document dictionary from discovery
            
        Returns:
            AcquiredDocument object or None if download failed
        """
        doc_id = doc_dict["document_id"]
        url = doc_dict["source_url"]
        
        # Create document directory
        doc_dir = self.output_dir / "documents" / f"arxiv_{doc_id}"
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
        """Validate downloaded file.
        
        Args:
            file_path: Path to the downloaded file
            content: File content as bytes
            
        Returns:
            True if file is valid, False otherwise
        """
        # Check minimum size
        if len(content) < 1024:
            return False
            
        # Check PDF header
        if not content.startswith(b'%PDF-'):
            return False
            
        # Additional validation could include virus scanning, etc.
        return True
    
    def _acquired_doc_to_dict(self, doc: AcquiredDocument) -> Dict[str, Any]:
        """Convert AcquiredDocument to specification-compliant dictionary.
        
        Args:
            doc: AcquiredDocument object
            
        Returns:
            Dictionary representation of the acquired document
        """
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

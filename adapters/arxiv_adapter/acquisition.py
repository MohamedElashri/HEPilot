"""
Acquisition module for downloading ArXiv papers with verification.

Downloads PDF files from arXiv with exponential backoff retry logic,
computes cryptographic hashes, and validates integrity.
"""

import hashlib
import time
import requests
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID
from models import DiscoveredDocument, AcquiredDocument


class ArxivAcquisition:
    """Downloads and verifies ArXiv papers."""
    
    def __init__(self, download_dir: Path, verbose: bool = False, delay_seconds: float = 3.0) -> None:
        """
        Initialize acquisition module.
        
        Args:
            download_dir: Directory to store downloaded PDFs
            verbose: Enable verbose output
            delay_seconds: Delay between downloads to avoid rate limiting (default: 3.0s)
        """
        self.download_dir: Path = download_dir
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.verbose: bool = verbose
        self.delay_seconds: float = delay_seconds
        self.last_request_time: float = 0.0  # Track last request time for rate limiting
        self.session: requests.Session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HEPilot-ArXiv-Adapter/1.0 (mohamed.elashri@cern.ch)'
        })
    
    def acquire(self, documents: List[DiscoveredDocument]) -> List[AcquiredDocument]:
        """
        Download all discovered documents.
        
        Args:
            documents: List of documents to acquire
            
        Returns:
            List of acquisition results
        """
        acquired: List[AcquiredDocument] = []
        try:
            from tqdm import tqdm
            docs_iter = tqdm(documents, desc="Acquiring", disable=self.verbose)
        except ImportError:
            docs_iter = documents
        
        for i, doc in enumerate(docs_iter):
            result: AcquiredDocument = self._download_document(doc)
            acquired.append(result)
        return acquired
    
    def _download_document(self, doc: DiscoveredDocument) -> AcquiredDocument:
        """
        Download single document with retry logic.
        
        Args:
            doc: Document to download
            
        Returns:
            Acquisition result
        """
        local_path: Path = self.download_dir / f"{doc.document_id}.pdf"
        
        # Check if file already exists (skip re-download)
        if local_path.exists():
            try:
                file_size: int = local_path.stat().st_size
                if file_size > 0:
                    sha256_hash: str = self._compute_hash(local_path, 'sha256')
                    sha512_hash: str = self._compute_hash(local_path, 'sha512')
                    validation_status: str = self._validate_file(local_path, file_size)
                    return AcquiredDocument(
                        document_id=doc.document_id,
                        local_path=str(local_path),
                        file_hash_sha256=sha256_hash,
                        file_hash_sha512=sha512_hash,
                        file_size=file_size,
                        download_timestamp=datetime.now(timezone.utc),
                        download_status="success",
                        retry_count=0,
                        validation_status=validation_status,
                        arxiv_id=doc.arxiv_id,
                        arxiv_version=doc.arxiv_version
                    )
            except Exception:
                pass  # If there's an error reading the file, re-download it
        
        retry_count: int = 0
        max_retries: int = 5
        start_time: datetime = datetime.now(timezone.utc)
        while retry_count < max_retries:
            try:
                self._download_with_backoff(doc.source_url, local_path, retry_count)
                file_size: int = local_path.stat().st_size
                
                # Validate file immediately after download - delete if HTML
                validation_status: str = self._validate_file(local_path, file_size)
                if validation_status == "failed":
                    # Delete corrupted file (HTML reCAPTCHA page)
                    if local_path.exists():
                        local_path.unlink()
                    raise ValueError(f"Downloaded HTML instead of PDF (rate limited or blocked)")
                
                sha256_hash: str = self._compute_hash(local_path, 'sha256')
                sha512_hash: str = self._compute_hash(local_path, 'sha512')
                return AcquiredDocument(
                    document_id=doc.document_id,
                    local_path=str(local_path),
                    file_hash_sha256=sha256_hash,
                    file_hash_sha512=sha512_hash,
                    file_size=file_size,
                    download_timestamp=datetime.now(timezone.utc),
                    download_status="success",
                    retry_count=retry_count,
                    validation_status=validation_status,
                    arxiv_id=doc.arxiv_id,
                    arxiv_version=doc.arxiv_version
                )
            except Exception as e:
                retry_count += 1
                if self.verbose:
                    print(f"[WARNING] Download attempt {retry_count} failed for {doc.arxiv_id}: {str(e)}")
                # Clean up any partial/corrupted file
                if local_path.exists():
                    try:
                        local_path.unlink()
                    except Exception:
                        pass
                if retry_count >= max_retries:
                    return AcquiredDocument(
                        document_id=doc.document_id,
                        local_path="",
                        file_hash_sha256="",
                        file_hash_sha512="",
                        file_size=0,
                        download_timestamp=datetime.now(timezone.utc),
                        download_status="failed",
                        retry_count=retry_count,
                        validation_status="failed",
                        arxiv_id=doc.arxiv_id,
                        arxiv_version=doc.arxiv_version
                    )
        return self._create_failed_acquisition(doc)
    
    def _download_with_backoff(self, url: str, local_path: Path, retry_count: int) -> None:
        """
        Download file with rate limiting - ensures minimum 3 seconds between requests.
        
        Args:
            url: URL to download from
            local_path: Local path to save file
            retry_count: Current retry attempt number
        """
        # Enforce minimum delay between ANY requests (initial or retry)
        current_time: float = time.time()
        time_since_last_request: float = current_time - self.last_request_time
        
        if self.delay_seconds > 0 and time_since_last_request < self.delay_seconds:
            sleep_time: float = self.delay_seconds - time_since_last_request
            if self.verbose:
                print(f"[RATE LIMIT] Waiting {sleep_time:.1f}s before request...")
            time.sleep(sleep_time)
        
        # Additional backoff for retries (on top of rate limit)
        if retry_count > 0:
            backoff_time: float = min(2 ** retry_count, 30)
            if self.verbose:
                print(f"[RETRY] Additional {backoff_time:.1f}s backoff for retry {retry_count}...")
            time.sleep(backoff_time)
        
        # Make the request and update timestamp
        self.last_request_time = time.time()
        response: requests.Response = self.session.get(url, timeout=300, stream=True)
        response.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=16 * 1024 * 1024):
                if chunk:
                    f.write(chunk)
    
    def _compute_hash(self, file_path: Path, algorithm: str) -> str:
        """
        Compute cryptographic hash of file.
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm ('sha256' or 'sha512')
            
        Returns:
            Hexadecimal hash string
        """
        hash_obj: Any = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            chunk: bytes = f.read(8192)
            while chunk:
                hash_obj.update(chunk)
                chunk = f.read(8192)
        return hash_obj.hexdigest()
    
    def _validate_file(self, file_path: Path, file_size: int) -> str:
        """
        Validate downloaded file.
        
        Args:
            file_path: Path to downloaded file
            file_size: Expected file size
            
        Returns:
            Validation status ('passed', 'warning', 'failed')
        """
        if not file_path.exists():
            return "failed"
        if file_size < 1000:
            return "warning"
        if not file_path.suffix == '.pdf':
            return "warning"
        with open(file_path, 'rb') as f:
            header: bytes = f.read(1024)
            # Check for PDF signature
            if not header.startswith(b'%PDF'):
                # Check if it's an HTML page (reCAPTCHA or error page)
                if b'<html' in header.lower() or b'<!DOCTYPE' in header.lower() or b'recaptcha' in header.lower():
                    if self.verbose:
                        print(f"[ERROR] Downloaded HTML instead of PDF (rate limited by ArXiv): {file_path.name}")
                    return "failed"
                # Unknown format
                return "failed"
        return "passed"
    
    def _create_failed_acquisition(self, doc: DiscoveredDocument) -> AcquiredDocument:
        """
        Create acquisition result for failed download.
        
        Args:
            doc: Document that failed to download
            
        Returns:
            Failed acquisition result
        """
        return AcquiredDocument(
            document_id=doc.document_id,
            local_path="",
            file_hash_sha256="",
            file_hash_sha512="",
            file_size=0,
            download_timestamp=datetime.now(timezone.utc),
            download_status="failed",
            retry_count=5,
            validation_status="failed",
            arxiv_id=doc.arxiv_id,
            arxiv_version=doc.arxiv_version
        )
    
    def save_acquisition_output(self, acquired: List[AcquiredDocument], output_path: Path) -> None:
        """
        Save acquisition results to JSON file.
        
        Args:
            acquired: List of acquisition results
            output_path: Path to output JSON file
        """
        output_data: Dict[str, Any] = {
            "acquired_documents": [
                {
                    k: v for k, v in {
                        "document_id": str(doc.document_id),
                        "local_path": doc.local_path,
                        "file_hash_sha256": doc.file_hash_sha256,
                        "file_hash_sha512": doc.file_hash_sha512,
                        "file_size": doc.file_size,
                        "download_timestamp": doc.download_timestamp.isoformat(),
                        "download_status": doc.download_status,
                        "retry_count": doc.retry_count,
                        "validation_status": doc.validation_status,
                        "arxiv_id": doc.arxiv_id,
                        "arxiv_version": doc.arxiv_version
                    }.items() if v is not None
                }
                for doc in acquired
            ]
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)

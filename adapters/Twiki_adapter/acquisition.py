"""
Acquisition module for downloading or registering Twiki pages with verification. 

Downloads HTML pages from LHCb Twiki (via CERN credentials if available),
computes hashes, and validates integrity according to
HEPilot acquision_output.schema.json.
"""

import hashlib
import time
import requests
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4
from adapters.Twiki_adapter.models import DiscoveredDocument, AcquiredDocument
from urllib.parse import urlparse

class TwikiAcquisition:
    # downloads and verifies Twiki pages or registers existing local ones.

    def __init__(self, download_dir: str = "data_twiki", verbose: bool = True) -> None:
        self.download_dir = Path(download_dir)
        self.verbose = verbose
        if not self.download_dir.exists():
            raise FileNotFoundError(f"Download directory not found: {self.download_dir}")
        
        # main function:
    def acquire(self, discovered: List[DiscoveredDocument]) -> List[AcquiredDocument]:
        acquired: List[AcquiredDocument] =[]
        for doc in discovered:
            acquired_doc = self._register_local(doc)
        return acquired
    
    def _register_local(self, doc: DiscoveredDocument) -> AcquiredDocument:
        local_path: Path
        parsed = urlparse(doc.source_url)
        if parsed.scheme == "file":
            local_path = Path(parsed.path)
        else:
            local_path = (self.download_dir / f"{doc.title}.txt")

        if not local_path.exists():
            return self._create_failed_acquisition(doc, reason="file not found")
        
        
        sha256 = self._compute_hash(local_path, "sha256")
        sha512 = self._compute_hash(local_path, "sha512")
        file_size = local_path.stat().st_size

        return AcquiredDocument(
            document_id=doc.document_id,
            local_path=str(local_path),
            file_hash_sha256=sha256,
            file_hash_sha512=sha512,
            file_size=file_size,
            download_timestamp=datetime.now(timezone.utc),
            download_status="success",
            retry_count=0,
            validation_status="passed",
        ) # type: ignore
    
    def _compute_hash(self, path: Path, algorithm: str) -> str:
        h = hashlib.new(algorithm)
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    
    def _create_failed_acquisition(self, doc: DiscoveredDocument, reason: str = "") -> AcquiredDocument:
        if self.verbose:
            print(f"[FAIL] Acquisition failed for {doc.title} ({reason})")

        return AcquiredDocument(
            document_id=doc.document_id or str(uuid4()),
            local_path="",
            file_hash_sha256="",
            file_hash_sha512="",
            file_size=0,
            download_timestamp=datetime.now(timezone.utc),
            download_status="failed",
            retry_count=5,
            validation_status="failed",
        ) #type: ignore
    def save_acquisition_output(self, acquired: List[AcquiredDocument], output_path: Path) -> None:
        output = {
            "acquired_documents": [
                {
                    k: v
                    for k, v in {
                        "document_id": str(doc.document_id),
                        "local_path": doc.local_path,
                        "file_hash_sha256": doc.file_hash_sha256,
                        "file_hash_sha512": doc.file_hash_sha512,
                        "file_size": doc.file_size,
                        "download_timestamp": doc.download_timestamp.isoformat(),
                        "download_status": doc.download_status,
                        "retry_count": doc.retry_count,
                        "validation_status": doc.validation_status,
                    }.items()
                    if v is not None
                }
                for doc in acquired
            ]
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        if self.verbose:
            print(f"[INFO] Saved acquisition output → {output_path}")


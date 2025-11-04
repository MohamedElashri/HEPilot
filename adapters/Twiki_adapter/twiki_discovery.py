"""
Discovery module for searching and identifying Twiki pages.

this discovery module will search the LHCb Twiki and identifies candidates
pages for acquisition.
It collects metadata such as title, URL and estimated size
"""

import uuid
import json
import time
import requests
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup
from models import DiscoveredDocument

class TwikiDiscovery:
    # Discovers candidates Twiki pages from CERN LHCb twiki.

    def __init__(
            self, 
            base_url: str = "https://twiki.cern.ch/twiki/bin/view/LHCb",
            max_pages: Optional[int] = None,
            include_authors: bool = False,
            delay_seconds: float = 1.5
    ) -> None:
        """
        Initializing the twiki discovery module
        """
        self.base_url = base_url.rstrip("/")
        self.max_pages = max_pages
        self.include_authors = include_authors
        self.delay_seconds = delay_seconds
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "HEPilot-TWiki-Adapter/1.0"})
        self.visited = set()

    def discovry(self) -> List[DiscoveredDocument]:
        discovered: List[DiscoveredDocument] = []
        local_dir = Path("data_twiki")

        for txt_path in sorted(local_dir.glob("*.txt")):
            title = txt_path.stem
            source_url = f"file://{txt_path.resolve()}"
            document_id = uuid.uuid5(uuid.NAMESPACE_URL, source_url)
            estimated_size = txt_path.stat().st_size

            doc = DiscoveredDocument(
                document_id=document_id,
                source_type="twiki",
                source_url=source_url,                 # key: file:// URL
                title=title,
                authors=None,
                discovery_timestamp=datetime.now(timezone.utc),
                estimated_size=estimated_size,
                content_type="text/plain",            # local txt
                priority_score=None
            )
        print(f"[INFO] Local discovery complete: {len(discovered)} Twiki pages found.")
        return discovered
    
    def save_discovery_output(self, documents: List[DiscoveredDocument], output_path: Path) -> None:
        """
        Save discovery results to JSON file compliant with HEPilot schema.

        Args:
            documents: List of discovered DiscoveredDocument objects
            output_path: Path to output file
        """
        output_data: Dict[str, Any] = {
            "discovered_documents": [
                {
                    k: v
                    for k, v in {
                        "document_id": str(doc.document_id),
                        "source_type": doc.source_type,
                        "source_url": doc.source_url,
                        "title": doc.title,
                        "authors": doc.authors,
                        "discovery_timestamp": doc.discovery_timestamp.isoformat(),
                        "estimated_size": doc.estimated_size,
                        "content_type": doc.content_type,
                        "priority_score": doc.priority_score,
                    }.items()
                    if v is not None
                }
                for doc in documents
            ]
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)

        print(f"[INFO] Saved TWiki discovery output → {output_path}")
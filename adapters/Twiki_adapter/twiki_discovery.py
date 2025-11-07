"""
Discovery module for searching and identifying Twiki pages.

this discovery module will search the LHCb Twiki and identifies candidates
pages for acquisition.
It collects metadata such as title, URL and estimated size
"""

import uuid
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pathlib import Path
from adapters.Twiki_adapter.models import DiscoveredDocument

class TwikiDiscovery:
    # Discovers candidates Twiki pages from CERN LHCb twiki.

    def __init__(
            self, 
            data_dir: Path = Path("data_twiki"),
            max_pages: Optional[int] = None
    ) -> None:
        # Initializing the Twiki discovery model

        self.data_dir = Path(data_dir)
        self.max_pages = max_pages
    
    def _extract_title(self, md_path: Path) -> str:
        try: 
            with open(md_path, "r", encoding="utf-8") as f:
                for line in f: 
                    if line.strip().startswith("#"):
                        return line.strip().lstrip("#").strip()
        except Exception:
            pass
        return md_path.stem
    
    def discover(self) -> List[DiscoveredDocument]: # type: ignore
        # Discover Twiki Markdown files from the local directory

        if not self.data_dir.exists():
            raise FileNotFoundError(f"[TwikiDiscovery] Data directory not found: {self.data_dir}")
        
        md_files = sorted(self.data_dir.glob("*.md"))
        discovered: List[DiscoveredDocument] = []

        for md_path in md_files: 
            if self.max_pages and len(discovered) >= self.max_pages:
                break

            document_id = uuid.uuid5(uuid.NAMESPACE_OID, str(md_path.resolve()))
            title = self._extract_title(md_path)
            estimated_size = md_path.stat().st_size

            doc = DiscoveredDocument(
                document_id=document_id, 
                source_type="twiki",
                source_url=str(md_path.resolve()),  
                title=title,
                authors=None,
                discovery_timestamp=datetime.now(timezone.utc),
                estimated_size=estimated_size,
                content_type="text/markdown",
                priority_score=None
            )
            discovered.append(doc)

        print(f"[INFO] Local discovery complete: {len(discovered)} Twiki Markdown pages found in '{self.data_dir}'")
        return discovered
    
    def save_directory_output(self, documents: List[DiscoveredDocument], output_path: Path) -> None:

        output_data: Dict[str, Any] = {
            "discovered_documents":[
                {
                    k: v
                    for k, v in {
                        "document_id": str(doc.document_id),
                        "source_type": doc.source_type,
                        "source_path": doc.source_url,  # renamed to reflect local path
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

        print(f"[INFO] Saved Twiki discovery output to {output_path}")


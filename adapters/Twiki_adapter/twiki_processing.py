"""
Processing module for Twiki markdown.
"""

import re
import json
import logging 
import time 
from typing import List, Dict, Any, Tuple 
from datetime import datetime, timezone
from pathlib import Path
from adapters.Twiki_adapter.models import AcquiredDocument, ProcessingMetadata

__version__ = "1.0.0"
PROCESSOR_NAME = f"twiki-cleaner/{__version__}"

class TwikiProcessor: 
    # Processes pre-downloaded twiki markdown files.

    def __init__(
            self, 
            exclude_edit_metadata: bool = True,
            exclude_raw_macros: bool = True, 
            preserve_equations: bool = True, 
            preserve_tables: bool = True, 
    ) -> None:
        # Initialize twiki processor
        self.logger = logging.getLogger(__name__)
        self.exclude_edit_metadata = exclude_edit_metadata
        self.exclude_raw_macros = exclude_raw_macros
        self.preserve_equations = preserve_equations
        self.preserve_tables = preserve_tables

    
    def process(self, acquired: AcquiredDocument, output_dir: Path) -> Tuple[Path, ProcessingMetadata]:

        # Normalizing a twiki markdown file.

        start_time = datetime.now(timezone.utc)
        warnings: List[str] = []

        input_path = Path(acquired.local_path)
        if not input_path.exists():
            raise FileNotFoundError(f"TWiki file not found: {input_path}")
        
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()

        cleaned = self._clean_content(content, warnings)

        doc_dir = output_dir / f"twiki_{acquired.document_id}"
        doc_dir.mkdir(parents=True, exist_ok=True)
        md_path = doc_dir / "normalized.md"

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(cleaned)
        
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        metadata = ProcessingMetadata(
            processor_used=PROCESSOR_NAME,
            processing_timestamp=start_time,
            processing_duration=duration,
            conversion_warnings=warnings
        ) #type: ignore

        self.logger.info(f"[TWikiProcessor] Cleaned {input_path.name} in {duration:.2f}s")
        return md_path, metadata
    
    def _clean_content(self, text:str, warnings: List[str]) -> str:

        lines = text.splitlines()
        cleaned: List[str] = []

        for line in lines:
            if self.exclude_raw_macros and re.search(r"%[A-Z]+(\{.*?\})?%", line):
                warnings.append(f"Removed TWiki macro line: {line.strip()[:40]}...")
                continue

            if self.exclude_edit_metadata and "r" in line and " - " in line and "Author" in line:
                warnings.append("Removed revision metadata line")
                continue

            cleaned.append(line)

        cleaned_text = "\n".join(cleaned)
        if self.preserve_equations:
            cleaned_text = self._normalize_equations(cleaned_text)
        else:
            cleaned_text = re.sub(r"\$[^$]+\$", "", cleaned_text)

        
        cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)
        cleaned_text = re.sub(r"^\s*---\+\+?\s*", "## ", cleaned_text, flags=re.MULTILINE)

        return cleaned_text.strip()
    
    def _normalize_equations(self, text: str) -> str:
        """Ensure LaTeX equations are enclosed in $...$ or $$...$$ properly."""
        text = re.sub(r"<latex>(.*?)</latex>", r"$$\1$$", text, flags=re.DOTALL)
        text = re.sub(r"\s*\$\s*(.*?)\s*\$\s*", r" $\1$ ", text)
        return text
    
    def save_processing_metadata(self, metadata: ProcessingMetadata, output_path: Path) -> None:
        #Save metadata JSON compliant with processing_metadata.schema.json.
        data: Dict[str, Any] = {
            "processor_used": metadata.processor_used,
            "processing_timestamp": metadata.processing_timestamp.isoformat(),
            "processing_duration": metadata.processing_duration,
            "conversion_warnings": metadata.conversion_warnings,
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


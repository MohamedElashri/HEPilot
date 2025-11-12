# Test script for Processor module

from adapters.Twiki_adapter.twiki_processing import TwikiProcessor, PROCESSOR_NAME
from adapters.Twiki_adapter.models import AcquiredDocument
from pathlib import Path
from datetime import datetime, timezone
import uuid
import json
import sys

def main():
    DATA_DIR = Path("data_twiki")
    OUTPUT_DIR = Path("test_output")

    if not DATA_DIR.exists():
        print(f"[ERROR] Directory not found: {DATA_DIR.resolve()}")
        sys.exit(1)
    
    md_files = sorted(DATA_DIR.glob("*.md"))
    if not md_files:
        print(f"[ERROR] No Markdown files found in {DATA_DIR.resolve()}")
        sys.exit(1)
    
    test_file = md_files[0]
    print(f"[INFO] Processing test file: {test_file.name}")

    file_url = test_file.resolve().as_uri()

    acquired_doc = AcquiredDocument(
        document_id=uuid.uuid4(),
        local_path=str(test_file.resolve()),
        source_url=file_url,
        file_hash_sha256="dummy_hash_sha256",
        file_hash_sha512="dummy_hash_sha512",
        file_size=test_file.stat().st_size,
        download_timestamp=datetime.now(timezone.utc),
        download_status="success",
        retry_count=0,
        validation_status="passed"
    ) #type:ignore

    processor = TwikiProcessor(
        exclude_edit_metadata=True, 
        exclude_raw_macros=True, 
        preserve_equations=True, 
        preserve_tables=True
    )
    normalized_path, metadata = processor.process(acquired_doc, OUTPUT_DIR)
    print(f"[INFO] Normalized markdown saved at: {normalized_path}")

    
    metadata_path = OUTPUT_DIR / f"{test_file.stem}_processing_metadata.json"
    processor.save_processing_metadata(metadata, metadata_path)
    print(f"[INFO] Processing metadata saved at: {metadata_path}")

   
    print(f"Processor Used: {metadata.processor_used}")
    print(f"Duration: {metadata.processing_duration:.2f}s")
    print(f"Warnings: {metadata.conversion_warnings if metadata.conversion_warnings else 'None'}")

    print(json.dumps({
        "processor_used": metadata.processor_used,
        "processing_timestamp": metadata.processing_timestamp.isoformat(),
        "processing_duration": metadata.processing_duration,
        "conversion_warnings": metadata.conversion_warnings
    }, indent=2))

if __name__ == "__main__":
    main()
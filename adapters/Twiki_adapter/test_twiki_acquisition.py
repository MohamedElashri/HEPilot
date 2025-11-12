
# Test script for the Twiki Acquisition module.


from adapters.Twiki_adapter.models import DiscoveredDocument
from adapters.Twiki_adapter.acquisition import TwikiAcquisition
from datetime import datetime, timezone
from pathlib import Path
import uuid
import json
import os
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data_twiki"

print(f"[DEBUG] Current working directory: {os.getcwd()}")
print(f"[DEBUG] Resolved data_twiki path: {DATA_DIR}")

if not DATA_DIR.exists():
    sys.exit(f"[ERROR] data_twiki directory not found: {DATA_DIR}")

md_files = sorted(DATA_DIR.glob("*.md"))
if not md_files:
    sys.exit(f"[ERROR] No .md files found in {DATA_DIR}")

print(f"[INFO] Found {len(md_files)} .md files in data_twiki.")
print(f"[INFO] Example file: {md_files[0].name}")

acquisition = TwikiAcquisition(download_dir=str(DATA_DIR), verbose=True)
acquired_docs = []

for md_file in md_files:
    print(f"\n[INFO] Processing: {md_file.name}")

    test_doc = DiscoveredDocument(
        document_id=uuid.uuid4(),
        source_type="twiki",
        source_url=md_file.resolve().as_uri(),
        title=md_file.stem,
        authors=None,
        discovery_timestamp=datetime.now(timezone.utc),
        estimated_size=md_file.stat().st_size,
        content_type="text/markdown",
        priority_score=None,
    )

    acquired = acquisition.acquire([test_doc])
    acquired_docs.extend(acquired)

output_dir = PROJECT_ROOT / "test_output"
output_dir.mkdir(exist_ok=True)
output_path = output_dir / "acquisition_output.json"

acquisition.save_acquisition_output(acquired_docs, output_path)


print(f"\n[SUCCESS] Acquisition completed for {len(acquired_docs)} documents.")
print(f" Results saved to: {output_path}")


print("\n Acquired document is")
print(json.dumps(acquired_docs[0].model_dump(mode="json"), indent=2))

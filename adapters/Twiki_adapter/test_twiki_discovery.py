# Test script for the twiki discovery module. 

from adapters.Twiki_adapter.twiki_discovery import TwikiDiscovery
from pathlib import Path 
import json
import sys

def main():
    DATA_DIR = Path("data_twiki")
    OUTPUT_DIR = Path("test_output")
    OUTPUT_PATH = OUTPUT_DIR / "discovery_output.json"

    print("[INFO] Initializing TwikiDiscovery")
    discovery = TwikiDiscovery(data_dir=DATA_DIR, max_pages=None)

    try:
        discovered_docs = discovery.discover()
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    if not discovered_docs:
        print(f"[WARN] No Markdown (.md) files found in data_twiki")
        sys.exit(0)

    discovery.save_directory_output(discovered_docs, OUTPUT_PATH)
    print(f"[INFO] Discovery results saved to {OUTPUT_PATH}")

    for i, doc in enumerate(discovered_docs[:5]):
        print(f"[{i+1}] Title: {doc.title}")
        print(f"    Path:  {doc.source_url}")
        print(f"    Size:  {doc.estimated_size} bytes")
        print(f"    Type:  {doc.content_type}")
        print("")

    print("[INFO] Ssample Json output:")
    print(json.dumps(discovered_docs[0].model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    main()
    

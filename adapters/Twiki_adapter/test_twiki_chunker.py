from adapters.Twiki_adapter.twiki_chunker import TWikiChunker
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
    print(f"[INFO] Chunking test file: {test_file.name}")

    chunker = TWikiChunker(
        chunk_size=256, 
        chunk_overlap=0.1, 
        use_model_tokenizer=False, # for local testing
        verbose=True
    )

    document_id = uuid.uuid4()
    chunks = chunker.chunk_document(test_file, document_id)

    # saving and metadata
    chunk_output_dir = OUTPUT_DIR / "chunk_test_ouput"
    chunker.save_chunks(chunks, chunk_output_dir)

    print(f"\n[INFO] Chunking complete. {len(chunks)} chunks generated.")
    print(f"[INFO] Chunks and metadata saved to: {chunk_output_dir.resolve()}")

    if chunks:
        sample = chunks[0]
        print(f"Chunk ID: {sample.chunk_id}")
        print(f"Token Count: {sample.token_count}")
        print(f"Chunk Type: {sample.chunk_type}")
        print(f"Section Path: {sample.section_path}")
        print(f"Content Preview: {sample.content[:200]}...")

    output_json = chunk_output_dir / "chunks" / "chunk_output.json"
    if output_json.exists():
        print(f"\n Aggregarte chunk_output.json")
        with open(output_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(json.dumps(data, indent=2)[:500])

if __name__ == "__main__":
    main()


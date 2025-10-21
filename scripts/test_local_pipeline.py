#!/usr/bin/env python3
"""
HEPilot Local Test Pipeline

A simplified end-to-end test that works without PostgreSQL.
Tests: arXiv download → processing → chunking → embeddings → vector storage

This script:
1. Uses ChromaDB for vector storage (works locally, no setup needed)
2. Stores embeddings only (skips PostgreSQL DocStore)
3. Demonstrates the complete flow for testing
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import argparse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.embedding.config import load_config
    from src.embedding.adapters.onnx_bge_encoder import ONNXBGEEncoder
    from src.embedding.adapters.chroma_vectordb import ChromaVectorDB
except ImportError as e:
    print(f"❌ Error importing embedding modules: {e}")
    print("Make sure you've installed requirements: pip install -r requirements-embedding.txt")
    sys.exit(1)


def discover_chunk_files(output_dir: Path) -> List[Path]:
    """
    Discover chunk files from arXiv adapter output.
    
    The new format has:
    - catalog.json with document list
    - documents/arxiv_{doc_id}/chunks/chunk_NNNN.md
    - documents/arxiv_{doc_id}/chunks/chunk_NNNN_metadata.json
    """
    if not output_dir.exists():
        return []
    
    catalog_file = output_dir / "catalog.json"
    
    if not catalog_file.exists():
        # Fallback to old format
        chunk_files = []
        for chunk_file in output_dir.rglob('*chunk_output.json'):
            chunk_files.append(chunk_file)
        return sorted(chunk_files)
    
    # New format: read catalog and collect all document directories
    with open(catalog_file, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    document_dirs = []
    for doc in catalog.get('documents', []):
        doc_id = doc['document_id']
        doc_dir = output_dir / "documents" / f"arxiv_{doc_id}"
        if doc_dir.exists():
            document_dirs.append(doc_dir)
    
    return sorted(document_dirs)


def parse_chunk_file(doc_dir: Path) -> Dict[str, Any]:
    """
    Parse chunks from a document directory.
    
    Reads:
    - document_metadata.json: Document-level metadata
    - chunks/chunk_NNNN.md: Chunk content
    - chunks/chunk_NNNN_metadata.json: Chunk-level metadata
    """
    # Load document metadata
    doc_metadata_file = doc_dir / "document_metadata.json"
    if not doc_metadata_file.exists():
        return {'chunks': [], 'metadata': {}}
    
    with open(doc_metadata_file, 'r', encoding='utf-8') as f:
        doc_metadata = json.load(f)
    
    # Load all chunks
    chunks_dir = doc_dir / "chunks"
    if not chunks_dir.exists():
        return {'chunks': [], 'metadata': doc_metadata}
    
    chunks = []
    # Find all chunk markdown files
    chunk_files = sorted(chunks_dir.glob('chunk_*.md'))
    
    for chunk_file in chunk_files:
        # Get chunk number from filename (e.g., chunk_0001.md -> 0001)
        chunk_num = chunk_file.stem.split('_')[1]
        metadata_file = chunks_dir / f"chunk_{chunk_num}_metadata.json"
        
        # Read chunk content
        with open(chunk_file, 'r', encoding='utf-8') as f:
            chunk_text = f.read().strip()
        
        # Read chunk metadata
        chunk_metadata = {}
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                chunk_metadata = json.load(f)
        
        # Combine into chunk object
        chunks.append({
            'text': chunk_text,
            'metadata': chunk_metadata
        })
    
    return {
        'chunks': chunks,
        'metadata': doc_metadata
    }


async def test_local_pipeline(arxiv_output_dir: Path, config_path: Path):
    """
    Test the local pipeline without PostgreSQL.
    
    Flow:
    1. Find chunk files from arXiv adapter
    2. Load encoder and vectordb
    3. Generate embeddings for chunks
    4. Store vectors in ChromaDB
    5. Test retrieval
    """
    
    print("=" * 70)
    print("🧪 HEPilot Local Pipeline Test")
    print("=" * 70)
    print()
    
    # Step 1: Discover chunk files
    print("📚 Step 1: Discovering chunk files...")
    chunk_files = discover_chunk_files(arxiv_output_dir)
    
    if not chunk_files:
        print(f"❌ No chunk files found in {arxiv_output_dir}")
        print(f"   Run the arXiv adapter first: cd {arxiv_output_dir.parent} && ./run.sh dev")
        return False
    
    print(f"✓ Found {len(chunk_files)} chunk files")
    print()
    
    # Step 2: Initialize components
    print("⚙️  Step 2: Initializing embedding components...")
    
    try:
        # Load config
        config = load_config(config_path)
        
        # Initialize encoder
        print("  - Loading encoder model (this may take a moment)...")
        encoder = ONNXBGEEncoder(
            model_name=config.encoder.model_name,
            cache_dir=Path(config.encoder.cache_dir),
            batch_size=config.encoder.batch_size,
            normalize=config.encoder.normalize,
            device=config.encoder.device
        )
        await encoder.load_model()
        print(f"    ✓ Encoder loaded: {config.encoder.model_name}")
        print(f"    ✓ Embedding dimension: {encoder.dimension}")
        
        # Initialize VectorDB
        print("  - Setting up ChromaDB...")
        vectordb = ChromaVectorDB(
            persist_directory=Path(config.vectordb.persist_directory),
            collection_name=config.vectordb.collection_name,
            distance_metric=config.vectordb.distance_metric
        )
        await vectordb.setup()
        
        # Clear existing data for fresh test
        existing_count = await vectordb.count()
        if existing_count > 0:
            print(f"    ⚠️  Found {existing_count} existing vectors, clearing...")
            await vectordb.clear()
        
        print(f"    ✓ ChromaDB ready at {config.vectordb.persist_directory}")
        print()
        
    except Exception as e:
        print(f"❌ Failed to initialize components: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Process chunks and generate embeddings
    print("🔄 Step 3: Processing chunks and generating embeddings...")
    
    total_chunks = 0
    total_vectors = 0
    documents_processed = 0
    
    for i, doc_dir in enumerate(chunk_files, 1):
        try:
            print(f"  [{i}/{len(chunk_files)}] Processing {doc_dir.name}...")
            
            # Parse document directory and load all chunks
            chunk_data = parse_chunk_file(doc_dir)
            chunks = chunk_data.get('chunks', [])
            metadata = chunk_data.get('metadata', {})
            
            if not chunks:
                print(f"    ⚠️  No chunks found, skipping")
                continue
            
            doc_title = metadata.get('title', 'Unknown')[:60]
            print(f"    📄 '{doc_title}...'")
            print(f"    📊 {len(chunks)} chunks")
            
            # Extract texts and prepare for embedding
            chunk_texts = []
            chunk_ids = []
            chunk_metadata_list = []
            
            for chunk in chunks:
                text = chunk.get('text', '')
                if not text:
                    continue
                
                chunk_meta = chunk.get('metadata', {})
                chunk_texts.append(text)
                # Use the UUID from chunk metadata, fallback to index-based ID
                chunk_id = chunk_meta.get('chunk_id', f"{metadata.get('document_id', 'unknown')}_{chunk_meta.get('chunk_index', total_chunks)}")
                chunk_ids.append(chunk_id)
                chunk_metadata_list.append({
                    'document_id': chunk_meta.get('document_id', metadata.get('document_id', '')),
                    'source_id': metadata.get('source_id', ''),
                    'title': metadata.get('title', '')[:100],
                    'chunk_index': chunk_meta.get('chunk_index', 0),
                    'position': chunk_meta.get('chunk_index', 0)
                })
            
            if not chunk_texts:
                print(f"    ⚠️  No valid text chunks, skipping")
                continue
            
            # Generate embeddings
            print(f"    🧠 Generating embeddings...")
            embeddings = await encoder.embed(chunk_texts)
            print(f"    ✓ Generated {len(embeddings)} embeddings")
            
            # Store in ChromaDB
            print(f"    💾 Storing vectors...")
            await vectordb.upsert(
                ids=chunk_ids,
                vectors=embeddings,
                metadata=chunk_metadata_list
            )
            
            total_chunks += len(chunk_texts)
            total_vectors += len(embeddings)
            documents_processed += 1
            
            print(f"    ✅ Complete")
            print()
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print()
    print("📈 Processing Summary:")
    print(f"  Documents processed: {documents_processed}")
    print(f"  Total chunks: {total_chunks}")
    print(f"  Total vectors stored: {total_vectors}")
    print()
    
    # Step 4: Test retrieval
    print("🔍 Step 4: Testing vector retrieval...")
    
    try:
        # Test query
        test_query = "quantum chromodynamics"
        print(f"  Query: '{test_query}'")
        
        # Encode query
        query_embedding = await encoder.embed([test_query])
        query_vector = query_embedding[0]
        
        # Search
        results = await vectordb.query(query_vector, top_k=3)
        
        print(f"  ✓ Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"    {i}. Score: {result.score:.4f}")
            print(f"       Title: {result.metadata.get('title', 'N/A')}")
            print(f"       Chunk ID: {result.chunk_id}")
        
        print()
        
    except Exception as e:
        print(f"  ❌ Retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 5: Final statistics
    print("📊 Final Statistics:")
    final_count = await vectordb.count()
    print(f"  Total vectors in ChromaDB: {final_count}")
    print()
    
    # Cleanup
    await encoder.close()
    await vectordb.close()
    
    print("=" * 70)
    print("✅ Local pipeline test complete!")
    print("=" * 70)
    
    return True


async def main():
    parser = argparse.ArgumentParser(
        description='Test HEPilot pipeline locally without PostgreSQL'
    )
    parser.add_argument(
        '--input',
        type=Path,
        default=Path('src/collector/adapters/arxiv/arxiv_output'),
        help='ArXiv adapter output directory'
    )
    parser.add_argument(
        '--config',
        type=Path,
        default=Path('config/embedding-local.toml'),
        help='Embedding configuration file'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.config.exists():
        print(f"❌ Config file not found: {args.config}")
        sys.exit(1)
    
    # Run test
    success = await test_local_pipeline(args.input, args.config)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    asyncio.run(main())

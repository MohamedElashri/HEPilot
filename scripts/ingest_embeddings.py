#!/usr/bin/env python3
"""
HEPilot Embedding Ingestion Script

Ingests chunk outputs from arXiv adapter into the embedding layer.
Reads JSON chunk files and feeds them to the IngestionPipeline.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime
import argparse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.embedding import create_ingestion_pipeline, IngestionResult


def parse_chunk_output(chunk_file: Path) -> Dict[str, Any]:
    """Parse a chunk JSON file."""
    with open(chunk_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_document_metadata(chunk_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract document metadata from chunk output.
    
    Args:
        chunk_data: Parsed chunk output JSON
    
    Returns:
        Document metadata dict for DocStore
    """
    metadata = chunk_data.get('metadata', {})
    
    # Parse publication date if present
    pub_date = None
    if 'publication_date' in metadata:
        try:
            pub_date = datetime.fromisoformat(metadata['publication_date'].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            pub_date = None
    
    return {
        'source_type': metadata.get('source_type', 'arxiv'),
        'source_id': metadata.get('source_id', ''),
        'title': metadata.get('title', ''),
        'authors': metadata.get('authors', []),
        'publication_date': pub_date,
        'source_url': metadata.get('source_url', ''),
        'metadata': {
            'categories': metadata.get('categories', []),
            'abstract': metadata.get('abstract', ''),
            'doi': metadata.get('doi', ''),
            'journal_ref': metadata.get('journal_ref', ''),
            'primary_category': metadata.get('primary_category', ''),
            'updated': metadata.get('updated', ''),
            'published': metadata.get('published', '')
        }
    }


def extract_chunks(chunk_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract chunk data from chunk output.
    
    Args:
        chunk_data: Parsed chunk output JSON
    
    Returns:
        List of chunk dicts for DocStore
    """
    chunks_list = []
    
    for chunk in chunk_data.get('chunks', []):
        chunks_list.append({
            'text': chunk.get('text', ''),
            'section_path': chunk.get('section_path', []),
            'position_in_doc': chunk.get('position_in_doc', 0),
            'token_count': chunk.get('token_count', 0),
            'overlap_start': chunk.get('overlap', {}).get('start', 0),
            'overlap_end': chunk.get('overlap', {}).get('end', 0),
            'metadata': {
                'chunk_id': chunk.get('chunk_id', ''),
                'checksum': chunk.get('checksum', ''),
                'page_numbers': chunk.get('page_numbers', [])
            }
        })
    
    return chunks_list


def discover_chunk_files(output_dir: Path) -> List[Path]:
    """
    Discover all chunk JSON files in the output directory.
    
    Args:
        output_dir: Path to arxiv_output directory
    
    Returns:
        List of chunk file paths
    """
    chunk_files = []
    
    # Look for chunk_output.json files
    for chunk_file in output_dir.rglob('*chunk_output.json'):
        chunk_files.append(chunk_file)
    
    return sorted(chunk_files)


async def ingest_documents(
    chunk_files: List[Path],
    config_path: Path,
    batch_size: int = 10,
    dry_run: bool = False
) -> IngestionResult:
    """
    Ingest all documents from chunk files.
    
    Args:
        chunk_files: List of chunk file paths
        config_path: Path to embedding config
        batch_size: Number of documents to process in parallel
        dry_run: If True, parse files but don't ingest
    
    Returns:
        Aggregated ingestion result
    """
    print(f"📚 Found {len(chunk_files)} chunk files to process")
    
    if dry_run:
        print("🔍 DRY RUN MODE - No data will be ingested")
    
    # Parse all chunk files
    documents: List[Tuple[Dict[str, Any], List[Dict[str, Any]]]] = []
    
    for i, chunk_file in enumerate(chunk_files, 1):
        try:
            print(f"  [{i}/{len(chunk_files)}] Parsing {chunk_file.name}...")
            
            chunk_data = parse_chunk_output(chunk_file)
            doc_metadata = extract_document_metadata(chunk_data)
            chunks = extract_chunks(chunk_data)
            
            print(f"    ✓ {len(chunks)} chunks from '{doc_metadata['title'][:60]}...'")
            
            documents.append((doc_metadata, chunks))
            
        except Exception as e:
            print(f"    ✗ Error parsing {chunk_file}: {e}")
            continue
    
    if dry_run:
        total_chunks = sum(len(chunks) for _, chunks in documents)
        print(f"\n📊 DRY RUN SUMMARY:")
        print(f"  Documents: {len(documents)}")
        print(f"  Total chunks: {total_chunks}")
        return IngestionResult(
            documents_processed=len(documents),
            chunks_processed=total_chunks,
            vectors_stored=0,
            errors=[]
        )
    
    # Ingest documents
    print(f"\n🚀 Starting ingestion of {len(documents)} documents...")
    
    async with create_ingestion_pipeline(config_path) as pipeline:
        # Check health first
        health = await pipeline.health_check()
        print(f"\n🏥 Component Health:")
        print(f"  DocStore:  {'✓' if health['docstore'] else '✗'}")
        print(f"  Encoder:   {'✓' if health['encoder'] else '✗'}")
        print(f"  VectorDB:  {'✓' if health['vectordb'] else '✗'}")
        
        if not all(health.values()):
            print("\n❌ Some components are unhealthy. Aborting ingestion.")
            return IngestionResult(
                documents_processed=0,
                chunks_processed=0,
                vectors_stored=0,
                errors=["Component health check failed"]
            )
        
        print(f"\n⚙️  Ingesting documents...")
        result = await pipeline.ingest_documents(documents)
        
        return result


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Ingest arXiv adapter outputs into HEPilot embedding layer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest from default location
  python scripts/ingest_embeddings.py
  
  # Ingest from specific directory
  python scripts/ingest_embeddings.py --input adapters/arxiv_adapter/arxiv_output
  
  # Dry run (parse only, no ingestion)
  python scripts/ingest_embeddings.py --dry-run
  
  # Use custom config
  python scripts/ingest_embeddings.py --config config/embedding.toml
        """
    )
    
    parser.add_argument(
        '--input',
        type=Path,
        default=Path('adapters/arxiv_adapter/arxiv_output'),
        help='Directory containing chunk outputs (default: adapters/arxiv_adapter/arxiv_output)'
    )
    
    parser.add_argument(
        '--config',
        type=Path,
        default=Path('config/embedding.toml'),
        help='Embedding configuration file (default: config/embedding.toml)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Number of documents to process in parallel (default: 10)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Parse files but do not ingest (useful for testing)'
    )
    
    args = parser.parse_args()
    
    # Validate paths
    if not args.input.exists():
        print(f"❌ Error: Input directory not found: {args.input}")
        print(f"   Please run the arXiv adapter first to generate chunk outputs.")
        sys.exit(1)
    
    if not args.config.exists():
        print(f"❌ Error: Config file not found: {args.config}")
        sys.exit(1)
    
    # Discover chunk files
    chunk_files = discover_chunk_files(args.input)
    
    if not chunk_files:
        print(f"❌ No chunk files found in {args.input}")
        print(f"   Expected files matching pattern: *chunk_output.json")
        sys.exit(1)
    
    # Run ingestion
    try:
        result = await ingest_documents(
            chunk_files=chunk_files,
            config_path=args.config,
            batch_size=args.batch_size,
            dry_run=args.dry_run
        )
        
        # Print results
        print(f"\n✨ INGESTION COMPLETE!")
        print(f"\n📊 Results:")
        print(f"  Documents processed: {result.documents_processed}")
        print(f"  Chunks processed:    {result.chunks_processed}")
        print(f"  Vectors stored:      {result.vectors_stored}")
        
        if result.errors:
            print(f"\n⚠️  Errors encountered:")
            for error in result.errors[:10]:  # Show first 10 errors
                print(f"    • {error}")
            if len(result.errors) > 10:
                print(f"    ... and {len(result.errors) - 10} more")
        
        sys.exit(0 if not result.errors else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())

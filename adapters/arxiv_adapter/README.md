# HEPilot ArXiv Adapter

**Version 1.0.0** - HEPilot-compliant adapter for discovering, acquiring, processing, and chunking High-Energy Physics papers from arXiv for RAG system ingestion.

---

## Overview

This adapter implements a complete pipeline for processing arXiv papers according to the [HEPilot Data Acquisition Specification v1.0](../../standards/README.md). It is built from scratch with a focus on modularity, type safety, and compliance with all schema requirements.

---

## Quick Start

### Prerequisites

- Python 3.10+
- Internet connection (arXiv API access)
- ~1GB disk space per 100 papers
- (Optional) [uv](https://github.com/astral-sh/uv) - Fast Python package manager (automatically used if available)

### Installation

```bash
cd adapters/arxiv_adapter
chmod +x run.sh
./run.sh dev
```

This will:
1. Detect and use `uv` if available (much faster), otherwise fall back to pip
2. Create a virtual environment
3. Install dependencies
4. Process 5 arXiv papers (dev mode)
5. Generate compliant output in `output/`

**Speed Tip**: Install `uv` for 10-100x faster dependency installation:
```bash
pip install uv
# or: curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Production Mode

```bash
./run.sh prod
```

Processes papers without limit (use `--max-results` flag in script for custom limits).

### Makefile Commands (Alternative Interface)

The adapter includes a Makefile for common tasks:

```bash
# Show all available commands
make help

# Run pipeline
make dev          # Development mode (5 papers)
make prod         # Production mode

# Cleanup
make clean        # Remove output files (keeps model cache)
make clean-cache  # Remove model cache files
make clean-all    # Remove output + cache
make clean-full   # Remove everything including venv

# Quick shortcuts
make reset        # Clean output + cache (alias for clean-all)
make nuke         # Nuclear option - remove everything (alias for clean-full)
```

**Note**: `run.sh` is the primary interface. The Makefile provides convenient shortcuts for cleanup and common tasks.

---

## Architecture

### Pipeline Stages

```
Discovery → Acquisition → Processing → Chunking → Metadata
```

| Stage | Module | Input | Output |
|-------|--------|-------|--------|
| **Discovery** | `discovery.py` | arXiv query | `discovery_output.json` |
| **Acquisition** | `acquisition.py` | Document URLs | PDFs + `acquisition_output.json` |
| **Processing** | `processing.py` | PDF files | `full_document.md` + `processing_metadata.json` |
| **Chunking** | `chunking.py` | Markdown files | `chunk_NNNN.md` + metadata |
| **Metadata** | `metadata.py` | All stages | `catalog.json`, `document_metadata.json` |

### Module Details

#### `config.py` - Configuration Manager
- Loads and validates `adapter_config.json`
- Computes SHA-256 config hash
- Provides typed configuration access

#### `discovery.py` - Discovery Module
- Searches arXiv API with configurable query
- Filters redacted/withdrawn papers
- Generates UUIDs for document tracking

#### `acquisition.py` - Acquisition Module
- Downloads PDFs with exponential backoff retry
- Computes SHA-256 and SHA-512 hashes
- Validates file integrity (PDF header, size)

#### `processing.py` - Processing Pipeline
- Uses docling's ML models for advanced PDF processing
- **Formula Enrichment**: ML-based LaTeX extraction from equations (resolves `<!-- formula-not-decoded -->` placeholders)
- Comprehensive LaTeX math environment support (equation, align, gather, multline, split, matrix variants)
- Intelligent content filtering (removes references, acknowledgments, author lists)
- Preserves LaTeX equations with enhanced detection
- Maintains section hierarchy and table structure
- Converts to CommonMark markdown

#### `chunking.py` - Chunking Engine
- **Uses actual embedding model's tokenizer** (BAAI/bge-large-en-v1.5)
- Token-aware semantic chunking matching target model
- Configurable overlap (fraction of chunk_size)
- Preserves equations, tables, code blocks
- Safe batched token counting (prevents memory issues with 161K+ token docs)
- Uses `add_special_tokens=False` for accurate counting
- Ensures chunks fit within model's max sequence length

#### `metadata.py` - Metadata Manager
- Generates document metadata
- Creates catalog entries
- Maintains structured processing log

#### `main.py` - Pipeline Orchestrator
- Coordinates all stages
- Handles errors gracefully
- Provides CLI interface

---

## Configuration

### `adapter_config.json`

```json
{
  "adapter_config": {
    "name": "arxiv_hep_adapter",
    "version": "1.0.0",
    "source_type": "arxiv",
    "processing_config": {
      "chunk_size": 512,
      "chunk_overlap": 0.1,
      "preserve_tables": true,
      "preserve_equations": true,
      "enrich_formulas": true
    },
    "profile": "core",
    "config_hash": "<computed>"
  }
}
```

### Configuration Parameters

#### Processing Configuration
- **chunk_size** (512-4096): Target tokens per chunk
- **chunk_overlap** (0.0-0.99): Overlap fraction between chunks
- **preserve_tables**: Convert tables to GFM format
- **preserve_equations**: Preserve LaTeX equations with ML-based extraction
- **enrich_formulas**: Enable ML-based formula enrichment to extract LaTeX from equations (default: true)
  - When enabled, replaces `<!-- formula-not-decoded -->` placeholders with actual LaTeX representations
  - Uses docling's CodeFormula model for advanced equation analysis
  - Significantly improves mathematical content quality in RAG applications
- **exclude_references**: Remove references/bibliography sections (default: true)
- **exclude_acknowledgments**: Remove acknowledgments sections (default: true)
- **exclude_author_lists**: Remove author lists and collaboration sections from content (default: true)
- **include_authors_metadata**: Include author lists in document_metadata.json (default: false)

#### Embedding Configuration
- **model_name**: Embedding model for token counting (default: "BAAI/bge-large-en-v1.5")
- **use_model_tokenizer**: Use actual model's tokenizer for accurate counts (default: true)
- **cache_dir**: Directory to cache downloaded models (default: ".model_cache")

**Note**: The model's `max_seq_length` is automatically detected from the loaded model. The `chunk_size` in processing_config must not exceed this value (validation enforced at runtime).

---

## Output Structure

```
output/
├── documents/
│   └── arxiv_{document_id}/
│       ├── chunks/
│       │   ├── chunk_0001.md              # Content (for embedding)
│       │   ├── chunk_0001_metadata.json   # Chunk metadata
│       │   ├── chunk_0002.md
│       │   ├── chunk_0002_metadata.json
│       │   └── ...
│       ├── full_document.md               # Complete document (provenance)
│       ├── document_metadata.json         # Document metadata
│       └── processing_metadata.json       # Processing details
├── downloads/                             # Downloaded PDFs
├── catalog.json                           # Master catalog
├── discovery_output.json                  # Discovery results
├── acquisition_output.json                # Acquisition results
└── processing_log.json                    # Structured logs
```

### Key Principles

✅ **Content in `.md` files** - Markdown text for RAG embedding  
✅ **Metadata in `.json` files** - Structured data about content  
❌ **Never embed content in JSON** - Maintains efficiency and compliance

---

## Usage Examples

### Basic Usage (Dev Mode)

```bash
./run.sh dev
```

### Production Mode

```bash
./run.sh prod
```

### Custom Python Invocation

```bash
python3 main.py \
    --config adapter_config.json \
    --output output \
    --query "cat:hep-ex AND LHCb" \
    --max-results 10
```

### Query Examples

```bash
# All HEP papers
--query "cat:hep-ex OR cat:hep-ph"

# LHCb-specific papers
--query "cat:hep-ex AND LHCb"

# Recent papers (2024+)
--query "cat:hep-ex AND submittedDate:[202401010000 TO 202412312359]"
```

---

## Schema Compliance

All outputs validate against HEPilot schemas:

| Output File | Schema |
|-------------|--------|
| `discovery_output.json` | `discovery_output.schema.json` |
| `acquisition_output.json` | `acquisition_output.schema.json` |
| `processing_metadata.json` | `processing_metadata.schema.json` |
| `chunk_NNNN_metadata.json` | `chunk_metadata.schema.json` |
| `document_metadata.json` | `document_metadata.schema.json` |
| `catalog.json` | `catalog.schema.json` |
| `processing_log.json` | `log_entry.schema.json` |

---

## Error Handling

### Recoverable Errors
- Network timeouts → Exponential backoff retry (max 5 attempts)
- Rate limiting → Automatic wait and retry
- Partial downloads → Resume from checkpoint

### Non-Recoverable Errors
- Redacted papers → Skipped during discovery
- Invalid PDFs → Marked as failed in acquisition
- Processing failures → Logged, document skipped

All errors are logged to `processing_log.json` with structured context.

---

## Performance

- **Processing Speed**: ~30-60 seconds per paper
- **Memory Usage**: <1GB per process
- **Disk Space**: ~500KB-2MB per paper (PDF + markdown + chunks)
- **Throughput**: ~50-100 papers/hour (depending on network)

---

## Development

### Project Structure

```
arxiv_adapter/
├── main.py              # Pipeline orchestrator
├── config.py            # Configuration manager
├── discovery.py         # Discovery module
├── acquisition.py       # Acquisition module
├── processing.py        # Processing pipeline
├── chunking.py          # Chunking engine
├── metadata.py          # Metadata manager
├── models.py            # Data models (Pydantic)
├── adapter_config.json  # Configuration
├── requirements.txt     # Dependencies
├── run.sh               # Control script (primary interface)
├── Makefile             # Make targets (cleanup, shortcuts)
├── README.md            # This file
├── Agent.md             # Agent context
└── plan.md              # Implementation plan
```

### Testing

```bash
# Validate configuration
python3 -c "from config import ConfigManager; ConfigManager(Path('adapter_config.json'))"

# Test discovery only
python3 -c "from discovery import ArxivDiscovery; d = ArxivDiscovery(max_results=1); print(len(d.search()))"

# Full pipeline test (1 paper)
python3 main.py --max-results 1
```

---

## Limitations & Future Work

### Current Limitations
- PDF-only processing (no LaTeX source support)
- No figure extraction (text only)
- Basic table detection (no complex table parsing)
- No citation graph extraction
- No version history tracking

### Planned Enhancements
- OAI-PMH feed integration for incremental discovery
- LaTeX source processing for better equation handling
- Figure extraction and OCR
- Citation network analysis
- Incremental updates (detect new versions)

---

## Dependencies

```
arxiv>=2.1.0                 # Official arXiv API client
docling>=1.0.0               # ML-powered PDF processing with LaTeX support
sentence-transformers>=2.2.0 # Embedding model for accurate token counting
transformers>=4.35.0         # Transformer models and tokenizers
tiktoken>=0.5.0              # Alternative token counting (fallback)
pydantic>=2.5.0              # Schema validation
requests>=2.31.0             # HTTP with retry logic
torch>=2.0.0                 # PyTorch for embedding models
```

**Key Points**:
- **Docling**: ML-based formula extraction and advanced PDF processing
- **sentence-transformers**: Uses BAAI/bge-large-en-v1.5 for accurate token counting that matches your RAG system's embedding model
- **Accurate Chunking**: Chunks are created using the same tokenizer as your target embedding model, ensuring no truncation issues

---

## Troubleshooting

### "No documents discovered"
- Check internet connection
- Verify arXiv API is accessible
- Try different query

### "Download failed"
- Network timeout → Will retry automatically
- Invalid URL → Check discovery output
- Rate limited → Wait and retry

### "Processing failed"
- Corrupted PDF → Check file integrity
- Unsupported format → Verify PDF header
- Memory error → Reduce batch size

### "Token count error"
- Install sentence-transformers: `pip install sentence-transformers` (or `uv pip install sentence-transformers`)
- Falls back to word-based counting if unavailable

### Slow installation
- Install `uv` for much faster dependency installation: `pip install uv`
- The script automatically detects and uses uv if available

---

## License

This adapter is part of the HEPilot project.

---

## Contact

**Maintainer**: Mohamed Elashri  
**Email**: mohamed.elashri@cern.ch  
**Repository**: https://github.com/MohamedElashri/HEPilot

---

## Changelog

### v1.0.0 (2025-10-08)
- Initial release with complete rewrite from scratch
- Full HEPilot v1.0 compliance with all schema validation
- **ML-Powered Processing**: Integrated docling for advanced PDF processing
- **Real Embedding Model Tokenization**: Uses BAAI/bge-large-en-v1.5 model's tokenizer for accurate chunking
- **Configurable Embedding Models**: Easy model switching via configuration
- **LaTeX Formula Support**: Comprehensive math environment detection (equation, align, gather, multline, split, matrix variants)
- **Content Filtering**: Intelligent removal of references, acknowledgments, and author lists
- **Safe Token Counting**: Batched processing prevents memory issues with 161K+ token documents
- Discovery, acquisition, processing, chunking, and metadata modules
- Dev/prod mode support via bash control script
- Comprehensive error handling with structured logging
- Type-safe implementation with full Pydantic models

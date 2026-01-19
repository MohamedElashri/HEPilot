# HEPilot ArXiv Adapter (HTML-Based)

**Version 1.0.0** - HEPilot-compliant adapter for discovering, acquiring, processing, and chunking High-Energy Physics papers from arXiv using their HTML format.

---

## Overview

This adapter implements a complete pipeline for processing arXiv papers according to the [HEPilot Data Acquisition Specification](../../standards/spec.json). Unlike legacy PDF-based approaches, this adapter leverages the ArXiv HTML format (via Ar5iv/ArXiv HTML) to provide:
*   **Cleaner Content**: Direct access to text without OCR errors.
*   **Semantic Structure**: Preserves document hierarchy, tables, and lists natively.
*   **Rich Math**: Preserves LaTeX equations (via MathJax/annotation tags) for high-fidelity RAG.
*   **Performance**: Significantly faster processing (no heavy VLM/OCR models required).

---

## Architecture

### Pipeline Stages

```
Discovery → Acquisition → Processing → Chunking → Metadata
```

| Stage | Module | Input | Output |
|-------|--------|-------|--------|
| **Discovery** | `discovery.py` | arXiv query | `discovery_output.json` |
| **Acquisition** | `acquisition.py` | Document URLs (HTML) | `.html` files + `acquisition_output.json` |
| **Processing** | `fast_html_processing.py` | HTML files | `full_document.md` + `processing_metadata.json` |
| **Chunking** | `chunking.py` | Markdown files | `chunk_NNNN.md` + metadata |
| **Metadata** | `metadata.py` | All stages | `catalog.json`, `document_metadata.json` |

### Module Details

#### `fast_html_processing.py` - HTML Core
*   **BeautifulSoup4**: Robust HTML parsing and DOM cleaning.
*   **Smart Cleaning**: Removes navigation bars, biblio/references (configurable), and footers.
*   **Table Serialization**: Grid-based table processor that handles `colspan`/`rowspan` to produce aligned Markdown tables.
*   **Math Handling**: Preserves LaTeX from MathJax scripts or annotation tags.

#### `chunking.py` - Semantic Chunking
*   **Tokenizer-Aware**: Uses the actual embedding model's tokenizer (e.g., `BAAI/bge-large-en-v1.5`) for precise token counting.
*   **Semantic Split**: Splits by section headers and sentences, preserving complete blocks.
*   **Overlap**: Configurable overlap to maintain context between chunks.

#### `cache_manager.py` - Incremental Processing
*   Tracks ArXiv versions (e.g., `v1` -> `v2`) to avoid reprocessing unchanged papers.
*   Stores SHA-256 hashes of HTML content.

---

## Usage

### Quick Start

Run the adapter for a specific paper:

```bash
python adapters/arxiv_adapter/main.py --query "id:2312.12451"
```

### Command Line Options

| Flag | Description | Default |
|------|-------------|---------|
| `--query` | ArXiv search query (e.g., `all:lhcb`, `id:1706.03762`) | `all:lhcb` |
| `--max-results` | Limit number of papers to process | `None` (All) |
| `--output` | Output directory | `output_html` |
| `--dev` | Development mode (Max 5 papers, verbose logs) | `False` |
| `--no-cache` | Force re-download and re-process | `False` |
| `--download-only`| Download HTMLs only (skip processing) | `False` |
| `--process-only` | Process downloaded HTMLs only | `False` |

---

## Configuration

Edit `adapters/arxiv_adapter/adapter_config.json` to customize the pipeline.

### Processing Configuration
*   **`chunk_size`**: Target size of chunks in tokens (default: `512`).
*   **`chunk_overlap`**: Overlap as a fraction (default: `0.1`).
*   **`preserve_tables`**: Keep tables in Markdown (default: `true`).
*   **`exclude_references`**: Remove bibliography sections (default: `true`).

### Embedding Configuration
Control the tokenizer used for chunking to ensure compatibility with your RAG model.

```json
"embedding_config": {
  "model_name": "BAAI/bge-large-en-v1.5",
  "use_model_tokenizer": true,
  "cache_dir": ".model_cache"
}
```

---

## Output Structure

Compliant with HEPilot spec:

```
output_html/
├── documents/
│   └── arxiv_{uuid}/
│       ├── chunks/
│       │   ├── chunk_0001.md              # Embeddable text
│       │   ├── chunk_0001_metadata.json   # Token count, type
│       │   └── ...
│       ├── full_document.md               # Complete Markdown
│       ├── document_metadata.json         # Biblio info
│       └── processing_metadata.json       # Log of processing
├── downloads/                             # Raw HTML files
├── catalog.json                           # Master index
└── processing_log.json                    # Execution logs
```

---

## Troubleshooting

### "No documents discovered"
*   Check your query.
*   Verify internet connection to `arxiv.org`.

### "Validation Failed" (Acquisition)
*   The downloaded file might be an error page or CAPTCHA from ArXiv.
*   Check `acquisition_output.json`.
*   Solution: Wait a few minutes and try again (automating throttling is built-in).

### "Token count error"
*   Ensure `sentence-transformers` is installed.
*   If missing, the adapter falls back to less accurate word-based counting.

### Ugly/Broken Tables
*   The adapter uses a custom grid serializer. If a table looks wrong, ensure `table_mode` is set to "fast" (default).
*   Complex nested tables may still be challenging to render in Markdown.

---

## Dependencies

*   `beautifulsoup4`: HTML parsing
*   `markdownify`: HTML to Markdown conversion
*   `sentence-transformers`: Tokenization and model handling
*   `requests`, `pydantic`, `tqdm`

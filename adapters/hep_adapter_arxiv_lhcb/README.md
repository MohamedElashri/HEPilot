# HEPilot arXiv LHCb Adapter

A comprehensive RAG (Retrieval-Augmented Generation) pipeline for discovering, acquiring, processing, and chunking scientific papers from arXiv, specifically focused on LHCb experiment publications. This adapter provides advanced mathematical content preservation, intelligent content filtering, and robust document processing capabilities.

## Overview

The HEPilot arXiv LHCb Adapter is designed to create high-quality, searchable document collections from arXiv papers. It excels at preserving complex mathematical notation, filtering out non-essential content, and creating properly chunked text suitable for RAG applications.

### Key Features

- **Dual Discovery Methods**: Uses both arXiv API and OAI-PMH for comprehensive paper discovery
- **Advanced Mathematical Preservation**: Comprehensive LaTeX environment support with AI-powered formula enrichment
- **Intelligent Content Filtering**: Configurable exclusion of authors, references, acknowledgments, and collaboration lists
- **Robust Processing**: Built-in retry logic, caching, and state management
- **Optimized Chunking**: Token-aware text segmentation with configurable overlap
- **Production Ready**: Comprehensive logging, error handling, and configuration management

## Architecture

The adapter follows a modular, pipeline-based architecture with six main components:

### 1. ArxivDiscovery
Discovers LHCb-related papers using:
- **arXiv API** (`http://export.arxiv.org/api/query`): Searches for "LHCb" in titles and abstracts
- **OAI-PMH Interface** (`http://export.arxiv.org/oai2`): Secondary discovery method with improved termination logic
- **Deduplication**: Removes duplicate papers before processing
- **Iteration Limits**: Prevents infinite loops with configurable max iterations and empty batch detection

### 2. DocumentAcquisition
Downloads PDF sources with:
- **Retry Logic**: Handles transient network issues
- **Parallel Downloads**: Configurable concurrent download limits
- **Validation**: Verifies PDF integrity before processing

### 3. DocumentProcessor
Converts PDFs to structured Markdown using `docling` with:
- **LaTeX Math Environments**: Support for `equation`, `align`, `gather`, `multline`, `split`, `matrix` and starred variants
- **Block Equations**: Preserves `$$...$$` and `\[...\]` formatting
- **Inline Equations**: Maintains `$...$` and `\(...\)` notation
- **Mathematical Symbols**: Comprehensive Greek letters, operators, and special symbols
- **LaTeX Commands**: Preserves formatting commands (`\textbf`, `\mathbf`, etc.)
- **Enhanced Tables**: Mathematical content handling within tables
- **Formula Enrichment**: AI-powered LaTeX extraction from visual formulas
- **Content Filtering**: Configurable removal of unwanted sections

### 4. ChunkingEngine
Segments documents into RAG-optimized chunks:
- **Token-Aware Splitting**: Uses configurable tokenizer models
- **Sentence Boundaries**: Respects natural text boundaries
- **Overlapping Chunks**: Configurable overlap for context preservation
- **Metadata Preservation**: Maintains document relationships

### 5. UnifiedCache
Provides intelligent caching and state management:
- **API Response Caching**: Avoids redundant API calls
- **Document State Tracking**: Tracks processing status
- **Content-Based Deduplication**: Prevents duplicate processing
- **Persistent State**: Maintains state across runs

### 6. HEPilotArxivAdapter
Orchestrates the entire pipeline:
- **Configuration Management**: Centralized configuration handling
- **Pipeline Coordination**: Manages data flow between components
- **Output Generation**: Creates structured catalog and metadata
- **Error Recovery**: Handles component failures gracefully

## Installation and Setup

### Prerequisites

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Configuration File

The adapter uses `adapter_config.json` for configuration. All options are controlled through this file rather than command-line arguments.

## Usage

### Basic Usage

Run the adapter with default configuration:

```bash
python run.py
```

This processes the number of documents specified in `adapter_config.json` (default: 5 documents).

### Custom Configuration

To use a different configuration file:

```bash
python run.py --config my_config.json
```

### Processing Examples

#### Example 1: Process a Few Recent Papers

For testing or limited processing, create a configuration file `small_batch_config.json`:

```json
{
  "adapter_config": {
    "name": "hepilot-arxiv-lhcb",
    "version": "1.0.0",
    "source_type": "arxiv",
    "processing_config": {
      "chunk_size": 512,
      "chunk_overlap": 0.1,
      "preserve_tables": true,
      "preserve_equations": true,
      "latex_environment_detection": true,
      "comprehensive_math_preservation": true,
      "equation_numbering_support": true,
      "enable_formula_enrichment": true
    },
    "profile": "core",
    "x_extension": {
      "max_documents": 3,
      "fetch_all": false,
      "output_dir": "./test_output",
      "cache_dir": "./test_output/cache",
      "state_file": "./test_output/state.json",
      "skip_processed": true,
      "exclude_authors": true,
      "exclude_acknowledgments": true,
      "exclude_references": true,
      "tokenizer_model": "BAAI/bge-large-en-v1.5"
    }
  }
}
```

Then run:

```bash
python run.py --config small_batch_config.json
```

#### Example 2: Process All Available LHCb Papers

For comprehensive processing, create `full_processing_config.json`:

```json
{
  "adapter_config": {
    "name": "hepilot-arxiv-lhcb",
    "version": "1.0.0",
    "source_type": "arxiv",
    "processing_config": {
      "chunk_size": 768,
      "chunk_overlap": 0.15,
      "preserve_tables": true,
      "preserve_equations": true,
      "latex_environment_detection": true,
      "comprehensive_math_preservation": true,
      "equation_numbering_support": true,
      "enable_formula_enrichment": true
    },
    "profile": "core",
    "x_extension": {
      "max_documents": null,
      "fetch_all": true,
      "output_dir": "./full_lhcb_corpus",
      "cache_dir": "./full_lhcb_corpus/cache",
      "state_file": "./full_lhcb_corpus/state.json",
      "skip_processed": true,
      "exclude_authors": true,
      "exclude_acknowledgments": true,
      "exclude_references": true,
      "tokenizer_model": "BAAI/bge-large-en-v1.5"
    }
  }
}
```

Then run:

```bash
python run.py --config full_processing_config.json
```

**Note**: Setting `"max_documents": null` and `"fetch_all": true` will process all available LHCb papers on arXiv. This can take considerable time and storage space.

#### Example 3: Research-Focused Configuration

For research applications requiring maximum mathematical content preservation:

```json
{
  "adapter_config": {
    "name": "hepilot-arxiv-lhcb",
    "version": "1.0.0",
    "source_type": "arxiv",
    "processing_config": {
      "chunk_size": 1024,
      "chunk_overlap": 0.2,
      "preserve_tables": true,
      "preserve_equations": true,
      "latex_environment_detection": true,
      "comprehensive_math_preservation": true,
      "equation_numbering_support": true,
      "enable_formula_enrichment": true
    },
    "profile": "core",
    "x_extension": {
      "max_documents": 50,
      "fetch_all": false,
      "output_dir": "./research_corpus",
      "cache_dir": "./research_corpus/cache",
      "state_file": "./research_corpus/state.json",
      "skip_processed": true,
      "exclude_authors": false,
      "exclude_acknowledgments": false,
      "exclude_references": false,
      "preserve_inline_equations": true,
      "mathematical_symbol_preservation": true,
      "latex_command_preservation": true,
      "enhanced_table_processing": true,
      "tokenizer_model": "BAAI/bge-large-en-v1.5"
    }
  }
}
```

## Configuration Reference

### Core Processing Configuration

#### `processing_config` Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `chunk_size` | integer | 512 | Target size of each text chunk in tokens |
| `chunk_overlap` | float | 0.1 | Percentage of overlap between consecutive chunks (0.0-1.0) |
| `preserve_tables` | boolean | true | Enable enhanced table processing and preservation |
| `preserve_equations` | boolean | true | Enable comprehensive equation preservation |
| `latex_environment_detection` | boolean | true | Detect and preserve LaTeX math environments |
| `comprehensive_math_preservation` | boolean | true | Enhanced mathematical notation handling |
| `equation_numbering_support` | boolean | true | Support for labeled equations and cross-references |
| `enable_formula_enrichment` | boolean | true | AI-powered formula understanding and LaTeX extraction |

#### `x_extension` Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_documents` | integer/null | 5 | Maximum number of documents to process (null = no limit) |
| `fetch_all` | boolean | false | Process all available LHCb papers when true |
| `output_dir` | string | "./hepilot_output" | Directory for processed files |
| `cache_dir` | string | "./hepilot_output/cache" | Directory for caching |
| `state_file` | string | "./hepilot_output/state.json" | File to track processing state |
| `skip_processed` | boolean | true | Skip already processed documents |
| `tokenizer_model` | string | "BAAI/bge-large-en-v1.5" | Tokenizer model for chunking |

### Content Filtering Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `exclude_authors` | boolean | true | Remove author sections, metadata blocks, and LHCb collaboration lists |
| `exclude_acknowledgments` | boolean | true | Filter out acknowledgment and funding sections |
| `exclude_references` | boolean | true | Remove reference sections, bibliography, and citations |

### Advanced Mathematical Processing Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `preserve_inline_equations` | boolean | true | Preserve inline mathematical expressions |
| `mathematical_symbol_preservation` | boolean | true | Protect individual mathematical symbols |
| `latex_command_preservation` | boolean | true | Maintain LaTeX formatting commands |
| `enhanced_table_processing` | boolean | true | Special handling for mathematical content in tables |

## Mathematical Content Preservation

### Supported LaTeX Environments

#### Standard Mathematical Environments
- `equation` / `equation*`: Single-line equations
- `align` / `align*`: Multi-line aligned equations
- `gather` / `gather*`: Multi-line centered equations
- `multline` / `multline*`: Multi-line equations with specific alignment
- `split`: Split equations within other environments

#### Matrix and Array Environments
- `matrix`: Basic matrix
- `pmatrix`: Matrix with parentheses
- `bmatrix`: Matrix with square brackets
- `vmatrix`: Matrix with vertical bars (determinant)
- `Vmatrix`: Matrix with double vertical bars
- `array`: General array environment
- `tabular`: Enhanced table processing with mathematical content

#### Mathematical Notation Support
- **Greek Letters**: Complete alphabet (α, β, γ, δ, Δ, Γ, etc.)
- **Operators**: Integrals (∫, ∮), summations (∑), products (∏), limits
- **Set Theory**: Union (∪), intersection (∩), subset (⊂), element (∈)
- **Logic Symbols**: Quantifiers (∀, ∃), implication (⇒), equivalence (⇔)
- **Special Symbols**: Infinity (∞), partial derivatives (∂), nabla (∇)
- **Formatting**: Bold (`\mathbf`), italic (`\mathit`), roman (`\mathrm`)

### Formula Enrichment Features

When `enable_formula_enrichment` is enabled:

- **ML-Powered Analysis**: Uses docling's specialized ML models for formula understanding
- **Automatic LaTeX Extraction**: Converts visual formulas in PDFs to LaTeX code
- **Formula Classification**: Identifies and categorizes different types of mathematical expressions
- **Spatial Information**: Preserves bounding box data for formula locations in documents
- **Metadata Enhancement**: Adds enriched formula data to processing metadata for analysis

### Content Filtering Details

#### Author Filtering (`exclude_authors: true`)
Removes:
- Author name sections and bylines
- Institutional affiliations
- Email addresses and contact information
- LHCb collaboration member lists (specifically filtered with pattern: `r'^#+ lhcb collaboration\s*$'`)
- Author metadata blocks

#### Reference Filtering (`exclude_references: true`) 
Removes:
- "References" sections
- "Bibliography" sections
- "Citations" sections
- "Works Cited" sections
- "Literature Cited" sections
- Individual citation entries

#### Acknowledgment Filtering (`exclude_acknowledgments: true`)
Removes:
- Acknowledgment sections
- Funding information
- Grant acknowledgments
- Thank you notes to collaborators

## Output Structure

The adapter creates a structured output directory:

```
output_directory/
├── cache/                    # Cached API responses and state
├── documents/               # Individual document folders
│   ├── arxiv_XXXX.YYYY/    # Document ID folder
│   │   ├── content.md       # Full processed markdown
│   │   ├── chunks/          # Individual chunk files
│   │   │   ├── chunk_001.md
│   │   │   ├── chunk_002.md
│   │   │   └── ...
│   │   └── metadata.json    # Document processing metadata
├── catalog.json             # Complete catalog of all documents
├── processing_log.txt       # Detailed processing log
└── state.json              # Processing state for resumption
```

## Troubleshooting

### Common Issues

2. **Memory Issues**: Reduce `chunk_size` or process smaller batches
3. **Network Timeouts**: Increase retry limits or check internet connection
4. **Missing Dependencies**: Ensure all packages in `requirements.txt` are installed

### Resume Processing

The adapter automatically resumes from the last successful state when `skip_processed` is enabled. Delete `state.json` to restart from the beginning.

# HEPilot arXiv LHCb Adapter

This adapter is a reference implementation for a RAG (Retrieval-Augmented Generation) pipeline that discovers, acquires, processes, and chunks scientific papers from arXiv, specifically focusing on those related to the LHCb experiment.

## Design

The adapter follows a modular, pipeline-based architecture. Each stage of the process is handled by a dedicated class:

1.  **`ArxivDiscovery`**: This module is responsible for finding relevant documents. It uses two methods:
    *   The official arXiv API (`http://export.arxiv.org/api/query`) to search for papers with "LHCb" in the title or abstract.
    *   The arXiv OAI-PMH interface (`http://export.arxiv.org/oai2`) as a secondary discovery method.
    It de-duplicates results before passing them to the next stage.

2.  **`DocumentAcquisition`**: This module takes the list of discovered documents and downloads the PDF source for each one. It includes retry logic to handle transient network issues.

3.  **`DocumentProcessor`**: Once a document is downloaded, this module uses the `docling` library to convert the PDF into clean, structured Markdown with comprehensive LaTeX and mathematical content preservation:
    *   **LaTeX Math Environments**: Comprehensive support for `equation`, `align`, `gather`, `multline`, `split`, `matrix` and their starred variants
    *   **Block Equations** (`$$...$$` or `\[...\]`) are wrapped in LaTeX-formatted code blocks
    *   **Inline Equations** (`$...$` or `\(...\)`) are preserved with backtick wrapping
    *   **Mathematical Symbols**: Greek letters, operators, and special symbols are preserved
    *   **LaTeX Commands**: Common formatting commands like `\textbf`, `\mathbf` are maintained
    *   **Enhanced Tables**: Special handling for mathematical content within tables and LaTeX table environments
    *   **Equation Numbering**: Support for labeled equations and cross-references
    *   **Formula Enrichment**: Advanced formula understanding using docling's AI-powered formula extraction to identify and preserve LaTeX representations

4.  **`ChunkingEngine`**: The processed Markdown is segmented into smaller, overlapping chunks suitable for ingestion by a large language model. This simple implementation splits the text by sentences and creates chunks based on a configurable token count.

5.  **`UnifiedCache`**: This module provides an intelligent caching system that unifies API response caching, document state tracking, and content-based deduplication. It avoids redundant storage and processing by detecting already downloaded and processed documents in the same working directory.

6.  **`HEPilotArxivAdapter`**: This is the main orchestrator class that initializes and runs the entire pipeline in sequence. It manages the flow of data from one component to the next and saves the final structured output.

The final output is stored in a structured directory, including the full processed Markdown, individual chunk files, and metadata for each document and chunk.

## Usage

The adapter is executed via the `run.py` script, which provides a command-line interface to control the pipeline.

### Prerequisites

Before running, install the necessary dependencies:

```bash
pip install -r requirements.txt
```

### Running the Adapter

You can run the adapter with various arguments to control its behavior.

**Basic Example:**

To run the pipeline and process the 10 most recent documents, using the default settings:

```bash
python run.py
```

**Customizing Execution:**

You can control several parameters, such as the number of documents to process and the output directory.

*   `--max-documents`: The maximum number of documents to process.
*   `--output-dir`: The directory where the processed files will be saved.
*   `--chunk-size`: The target size of each text chunk in tokens.
*   `--chunk-overlap`: The percentage of overlap between consecutive chunks.
*   `--tokenizer-model`: The tokenizer model to use (default: "BAAI/bge-large-en-v1.5").
*   `--include-authors`: Whether to include author information in documents and chunks (default: `false`).

**Example with Arguments:**

To process the 5 most recent documents and save the output to a directory named `my_arxiv_output`:

```bash
python run.py --max-documents 5 --output-dir my_arxiv_output
```

## LaTeX and Mathematical Content Features

### Comprehensive Mathematical Environment Support
- **Standard Environments**: `equation`, `align`, `gather`, `multline`, `split`
- **Matrix Environments**: `matrix`, `pmatrix`, `bmatrix`, `vmatrix`, `Vmatrix`
- **Array and Table Environments**: `array`, `tabular` with mathematical content
- **Starred Variants**: Support for unnumbered versions (`equation*`, `align*`, etc.)

### Symbol and Command Preservation
- **Greek Letters**: All standard Greek alphabet symbols (α, β, γ, Δ, etc.)
- **Mathematical Operators**: Integrals, summations, products, limits
- **Set Theory**: Union, intersection, subset, superset symbols
- **Logic Symbols**: Quantifiers, logical operators
- **Formatting Commands**: Bold, italic, roman text in math mode

### Enhanced Processing Configuration
- `latex_environment_detection`: Comprehensive LaTeX environment recognition
- `comprehensive_math_preservation`: Enhanced mathematical notation handling
- `mathematical_symbol_preservation`: Individual symbol protection
- `latex_command_preservation`: LaTeX command maintenance
- `enhanced_table_processing`: Mathematical table content handling
- `enable_formula_enrichment`: AI-powered formula understanding and LaTeX extraction

### Formula Enrichment Features
- **AI-Powered Analysis**: Uses docling's specialized formula understanding model
- **LaTeX Extraction**: Automatically extracts LaTeX representations from visual formulas in PDFs
- **Formula Classification**: Identifies and labels mathematical formulas in documents
- **Metadata Enhancement**: Adds enriched formula data to processing metadata
- **Bounding Box Detection**: Preserves spatial information about formula locations

## ToDo 

1. Handle withdrawn papers (because current code doesn't handle this case and gives error)
2. Add batch processing for documents
3. ~~Add `--enrich-formula` option to `docling` to improve formula understanding~~ ✅ Implemented comprehensive LaTeX processing with AI-powered formula enrichment
4. Add validation testing for mathematical content preservation
5. Implement equation cross-reference resolution
6. Add support for additional docling enrichment features (code understanding, picture classification)
# HEPilot arXiv LHCb Adapter

This adapter is a reference implementation for a RAG (Retrieval-Augmented Generation) pipeline that discovers, acquires, processes, and chunks scientific papers from arXiv, specifically focusing on those related to the LHCb experiment.

## Design

The adapter follows a modular, pipeline-based architecture. Each stage of the process is handled by a dedicated class:

1.  **`ArxivDiscovery`**: This module is responsible for finding relevant documents. It uses two methods:
    *   The official arXiv API (`http://export.arxiv.org/api/query`) to search for papers with "LHCb" in the title or abstract.
    *   The arXiv OAI-PMH interface (`http://export.arxiv.org/oai2`) as a secondary discovery method.
    It de-duplicates results before passing them to the next stage.

2.  **`DocumentAcquisition`**: This module takes the list of discovered documents and downloads the PDF source for each one. It includes retry logic to handle transient network issues.

3.  **`DocumentProcessor`**: Once a document is downloaded, this module uses the `docling` library to convert the PDF into clean, structured Markdown. It performs additional post-processing to ensure that mathematical content is preserved correctly:
    *   **Block Equations** (`$$...$$` or `\[...\]`) are wrapped in Markdown code blocks.
    *   **Inline Equations and Symbols** (`$...$`) are wrapped in backticks to preserve them as inline code.

4.  **`ChunkingEngine`**: The processed Markdown is segmented into smaller, overlapping chunks suitable for ingestion by a large language model. This simple implementation splits the text by sentences and creates chunks based on a configurable token count.

5.  **`HEPilotArxivAdapter`**: This is the main orchestrator class that initializes and runs the entire pipeline in sequence. It manages the flow of data from one component to the next and saves the final structured output.

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

**Example with Arguments:**

To process the 5 most recent documents and save the output to a directory named `my_arxiv_output`:

```bash
python run.py --max-documents 5 --output-dir my_arxiv_output
```

# HEPilot Data Acquisition and Preparation Specification for RAG

**Version 1.0** — Data Acquisition System Format for RAG

**Last Modified:** 2025-10-02 | **Next Review:** 2026-01

**Author:** Mohamed Elashri | **Contact:** [mohamed.elashri@cern.ch](mailto:mohamed.elashri@cern.ch)

**Repository:** [https://github.com/MohamedElashri/HEPilot/standards](https://github.com/MohamedElashri/HEPilot/standards)

---

## Machine-Readable Specifications

**Primary Specifications:**
- **[spec.json](./spec.json)** - Complete machine-readable specification in a single JSON file
- **[schemas/](./schemas/)** - Self-documenting JSON schemas with embedded requirements

All detailed technical specifications, requirements, and implementation rules are now embedded in the JSON schemas themselves, making them the authoritative source of truth and enabling programmatic access.

---

## Abstract

This specification defines the **data acquisition and preparation format** for RAG (Retrieval-Augmented Generation) systems processing High-Energy Physics literature. 

**Scope:** Document discovery, acquisition, processing, chunking, and metadata generation—preparing HEP documents for RAG system ingestion.

**Key Features:**
- Standardized pipeline from source documents to embedding-ready chunks
- Self-documenting JSON schemas with embedded requirements
- Support for multiple HEP sources (arXiv, Indico, TWiki, Internal Notes, Code repositories)
- Code documentation extraction (docstrings, comments) and full source code indexing
- Comprehensive metadata for retrieval and provenance
- Modular adapter architecture for extensibility
- Output format designed for RAG indexing systems

---

## Quick Start

### 1. Understanding the Architecture

The specification consists of six core components:

| Component | Responsibility | Schema Reference |
|-----------|---------------|------------------|
| **Configuration Manager** | Validates and persists adapter settings | [`adapter_config.schema.json`](./schemas/adapter_config.schema.json) |
| **Discovery Module** | Finds candidate documents | [`discovery_output.schema.json`](./schemas/discovery_output.schema.json) |
| **Acquisition Module** | Downloads and verifies files | [`acquisition_output.schema.json`](./schemas/acquisition_output.schema.json) |
| **Processing Pipeline** | Converts to CommonMark markdown | [`processing_metadata.schema.json`](./schemas/processing_metadata.schema.json) |
| **Chunking Engine** | Creates LLM-sized chunks with overlap | [`chunk_output.schema.json`](./schemas/chunk_output.schema.json) |
| **Metadata Manager** | Generates comprehensive metadata | [`document_metadata.schema.json`](./schemas/document_metadata.schema.json) |

### 2. Content Storage Model

**REQUIRED: Content and metadata MUST be stored separately.**

```
output/
├── documents/
│   └── {source_type}_{document_id}/
│       ├── chunks/
│       │   ├── chunk_0001.md              # ← CONTENT (for RAG embedding)
│       │   ├── chunk_0001_metadata.json   # ← METADATA (JSON only)
│       │   └── ...
│       ├── full_document.md               # ← CONTENT (provenance, NOT for retrieval)
│       ├── document_metadata.json         # ← METADATA (bibliographic info)
│       ├── processing_metadata.json       # ← METADATA (processing details)
│       └── references.json                # ← STRUCTURED DATA (CSL-JSON)
├── catalog.json                           # Master index
└── processing_log.json                    # Processing events log
```

**Critical Rules:**
- **MUST**: Content in `.md` files, metadata in `.json` files
- **MUST**: `chunk_NNNN.md` files are self-contained for RAG embedding
- **MUST**: `full_document.md` for provenance/archival, SHOULD NOT be used for retrieval
- **MUST NOT**: Embed document or chunk content in JSON metadata files

**Why Separate Content from Metadata?**
- **Efficiency:** Query metadata without loading large content files
- **Version Control:** Better git diffs for text vs. structured data  
- **Tool Support:** Specialized tools for markdown vs. JSON
- **Scalability:** Papers can be multi-MB; metadata is always small
- **RAG Optimization:** Embedding systems index markdown files directly

### 3. Working with Schemas

All schemas are self-documenting with comprehensive descriptions:

```bash
# Validate your adapter configuration
jsonschema -i adapter_config.json schemas/adapter_config.schema.json

# View schema with descriptions (any JSON schema viewer)
cat schemas/chunk_output.schema.json | jq '.properties.chunk_id.description'
```

**Each schema includes:**
- Field-level descriptions with MUST/SHOULD/MAY requirements
- Algorithm specifications and implementation guidance
- Cross-references to related schemas and concepts
- Validation rules and constraints

---

## Compliance & Normative Keywords

Per RFC 2119:
- **MUST** / **SHALL** / **REQUIRED**: Absolute requirements for compliance
- **SHOULD** / **RECOMMENDED**: Best practices (may be ignored with valid reason)
- **MAY** / **OPTIONAL**: Truly optional capabilities

An implementation claiming *HEPilot-Adapter-Compliant* status **MUST** satisfy all MUST/SHALL requirements for its supported source types.

---

## Key Specifications

### Configuration
See [`adapter_config.schema.json`](./schemas/adapter_config.schema.json) for complete configuration requirements.

**Key Rules:**
- `chunk_overlap` **SHALL** be interpreted as fraction (0 ≤ x < 1)
- `chunk_size` range: 512-4096 tokens
- `config_hash` **MUST** be recomputed after changes (SHA-256 of canonicalized JSON)

### Credentials
See [`credentials.schema.json`](./schemas/credentials.schema.json) for authentication.

** Security:** `credentials.json` **MUST NOT** be committed to version control.

Supported methods: API keys, bearer tokens, OAuth2 client credentials, x509 certificates.

### Discovery
See [`discovery_output.schema.json`](./schemas/discovery_output.schema.json) and [`rate_limit_status.schema.json`](./schemas/rate_limit_status.schema.json).

**Source-Specific Requirements:**

| Source | MUST Requirements | SHOULD Requirements |
|--------|-------------------|---------------------|
| **arXiv** | Query REST API + OAI-PMH feed<br>Extract version history & withdrawal notices | Category filtering<br>Relevance scoring |
| **Indico** | Traverse event hierarchies<br>Capture speaker metadata<br>Handle authentication | Date-range filtering |
| **Internal Notes** | Respect ACLs & classification flags | Content-based filtering |
| **TWiki** | Resolve internal links & page histories | Namespace filtering |
| **code_docs** | Authenticate with repository API<br>Traverse file tree<br>Extract docstrings (Python ast module)<br>Extract Doxygen comments (C++) | Respect .gitignore patterns<br>Filter by file extensions<br>Support specific paths (e.g., docs/) |
| **code** | Authenticate with repository API<br>Parse AST for functions/classes<br>Preserve imports & dependencies<br>Maintain file hierarchy in section_path | Language-specific optimizations<br>Support incremental updates (git diff)<br>Configurable depth limits |

### Acquisition
See [`acquisition_output.schema.json`](./schemas/acquisition_output.schema.json).

**Key Requirements:**
- **MUST** implement exponential-backoff retry logic
- **MUST** honour HTTP/HTTPS rate-limit headers
- **MUST** verify SHA-256 **and** SHA-512 hashes
- **SHOULD** use HTTP Range requests (16 MiB blocks) for files > 1 GiB

### Processing
See [`processing_metadata.schema.json`](./schemas/processing_metadata.schema.json).

**Text Extraction Requirements:**
- **MUST** preserve section hierarchy
- **MUST** convert tables to GitHub-Flavoured Markdown
- **MUST** preserve LaTeX equations (`$...$` and `$$...$$`)
- **MUST** handle multi-column layouts
- **SHOULD** maintain cross-references and citations

**Content Filtering:**
- Strip embedded images (unless figure extraction enabled)
- Remove navigation elements, headers, footers
- Exclude adverts and boilerplate

### Chunking
See [`chunk_output.schema.json`](./schemas/chunk_output.schema.json) and [`chunk_metadata.schema.json`](./schemas/chunk_metadata.schema.json).

**Algorithm:**
1. Prefer semantic boundaries (sections > paragraphs > sentences)
2. Pack tokens until `chunk_size`; if exceeded, split at sentence boundary
3. Apply overlap of `chunk_size × chunk_overlap` tokens
4. **MUST NOT** split inside equations, tables, or fenced code blocks

### Metadata
See [`document_metadata.schema.json`](./schemas/document_metadata.schema.json) and [`catalog.schema.json`](./schemas/catalog.schema.json).

**Output Files:**
- `document_metadata.json` - Provenance and bibliographic info
- `processing_metadata.json` - Processing execution details
- `chunk_NNNN_metadata.json` - Per-chunk metadata
- `catalog.json` - Master index of all documents
- `references.json` - Bibliography in CSL-JSON format

### Logging
See [`log_entry.schema.json`](./schemas/log_entry.schema.json).

All processing events logged to `processing_log.json` with structured entries including timestamp, trace_id, severity level, component, and context

---

## Compliance & Testing

### Testing Requirements
Adapters claiming *HEPilot-Adapter-Compliant* status **MUST** pass:

1. **JSON schema validation** for all output artifacts
2. **Format conversion tests** for supported source types
3. **Performance benchmark**: < 1 GiB RAM per process
4. **Interoperability**: Generated markdown embeddable without errors

### Reference Implementation
See: [reference_adapter](https://github.com/MohamedElashri/HEPilot/standards/reference_adapter)

---

## Versioning

This specification follows **Semantic Versioning** (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: Backward-compatible additions
- **PATCH**: Bug fixes and editorial corrections

Implementations declare supported features via `adapter_config.profile`.

---

## Resources

### Complete Machine-Readable Specification
📄 **[spec.json](./spec.json)** - All specification details in a single JSON file

### Self-Documenting Schemas
All schemas are in [`./schemas/`](./schemas/) with embedded requirements:

| Schema | Purpose |
|--------|---------|
| `adapter_config.schema.json` | Configuration and processing parameters |
| `credentials.schema.json` | Authentication credentials (⚠️ NOT for version control) |
| `discovery_output.schema.json` | Discovery results and candidate documents |
| `rate_limit_status.schema.json` | API rate limiting information |
| `acquisition_output.schema.json` | Download and validation results |
| `processing_metadata.schema.json` | Processing execution metadata |
| `chunk_output.schema.json` | Individual chunk content and metadata |
| `chunk_metadata.schema.json` | Detailed chunk metadata |
| `document_metadata.schema.json` | Document provenance and bibliographic info |
| `catalog.schema.json` | Master catalog of all processed documents |
| `log_entry.schema.json` | Structured processing log entries |

### Content Storage Answer
**Q: Where does document content live?**

**A: Content is stored as separate markdown (.md) files, NOT embedded in JSON.**

- **Content files**: `chunk_NNNN.md`, `full_document.md` (markdown format)
- **Metadata files**: `*.json` (structured data about the content)
- **Why separate?** Efficiency (query metadata without loading large content), better version control, specialized tooling, scalability

---

## Contact & Contributions

**Maintainer:** Mohamed Elashri  
**Email:** [mohamed.elashri@cern.ch](mailto:mohamed.elashri@cern.ch)  
**Repository:** [https://github.com/MohamedElashri/HEPilot/standards](https://github.com/MohamedElashri/HEPilot/standards)

Feedback, issues, and pull requests are welcome!

---

**HEPilot Data Acquisition and Preparation Specification for RAG v1.0**  
*Standardized data acquisition and preparation format for RAG systems.*

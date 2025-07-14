## HEP ilot RAG Adapter Framework Specification
**Version 1.0** — Initial Personal Release

**Last-modified** 14 July 2025 · Next-review January 2026

**Author** Mohamed Elashri · Contact [mohamed.elashri@cern.ch](mailto:mohamed.elashri@cern.ch)

**Repository** [https://github.com/MohamedElashri/HEPilot/standards](https://github.com/MohamedElashri/HEPilot/standards)

---

## Abstract

This document defines the **Retrieval-Augmented-Generation (RAG) Adapter Framework** used by the *HEPilot* project.  The framework delivers a reproducible pipeline for discovering, acquiring, processing, chunking and cataloguing High-Energy-Physics (HEP) documents so they can be indexed or embedded by large-language-model (LLM) systems.  Every adapter is responsible for one (or more) specific document source types; an implementation **is not required** to support all source classes.

---

## § 0 Glossary

| Term          | Definition                                                                                   |
| ------------- | -------------------------------------------------------------------------------------------- |
| **Document**  | A complete source artefact (PDF, LaTeX bundle, PPTX …) uniquely identified by `document_id`. |
| **Chunk**     | A semantically coherent subsequence of a Document produced by the Chunking Engine.           |
| **Token**     | The minimal text unit recognised by the downstream LLM tokenizer.                            |
| **Character** | A single Unicode scalar value.                                                               |
| **Byte**      | An 8-bit octet in the binary representation of a file.                                       |

---

## 1 Introduction

### 1.1 Purpose

LLM-based assistants and knowledge bases require well-structured scientific content.  The HEPilot RAG Adapter Framework specifies normative behaviour for:

* discovering and cataloguing scientific documents,
* acquiring artefacts while preserving provenance,
* converting diverse formats into CommonMark markdown,
* intelligently chunking content for transformer models, and
* emitting rich metadata for every processing stage.

### 1.2 Scope

The framework covers discovery, acquisition, validation, processing, chunking, metadata management, output layout, logging and compliance testing.  Security, privacy and quality-scoring are out of scope for this initial release.

### 1.3 Compliance

Normative keywords **MUST**, **SHALL** and **REQUIRED** denote mandatory behaviour.  **SHOULD** and **MAY** describe optional capabilities.  An implementation that advertises itself *HEPilot-Adapter-Compliant* **MUST** satisfy every mandatory clause herein for the source types it elects to support.

---

## 2 Architecture Overview

| # | Component                 | Responsibility                                                      |
| - | ------------------------- | ------------------------------------------------------------------- |
| 1 | **Configuration Manager** | Loads, validates and persists adapter settings.                     |
| 2 | **Discovery Module**      | Finds candidate documents, returns a registry.                      |
| 3 | **Acquisition Module**    | Downloads artefacts, verifies integrity, enforces quotas.           |
| 4 | **Processing Pipeline**   | Converts source files to CommonMark markdown.                       |
| 5 | **Chunking Engine**       | Segments markdown into LLM-sized chunks with overlap.               |
| 6 | **Metadata Manager**      | Creates and stores document-, chunk- and processing-level metadata. |

---

## 3 Configuration Management

### 3.1 Schema

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/MohamedElashri/HEPilot/standards/schemas/adapter_config.schema.json",
  "title": "Adapter Configuration",
  "type": "object",
  "required": ["adapter_config"],
  "properties": {
    "adapter_config": {
      "type": "object",
      "required": [
        "name",
        "version",
        "source_type",
        "processing_config",
        "config_hash"
      ],
      "properties": {
        "name":    { "type": "string" },
        "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },

        "source_type": {
          "description": "Key identifying the document class handled by this adapter",
          "enum": ["arxiv", "indico", "internal_notes", "twiki", "other"]
        },

        "processing_config": {
          "type": "object",
          "required": [
            "chunk_size",
            "chunk_overlap",
            "preserve_tables",
            "preserve_equations"
          ],
          "properties": {
            "chunk_size": {
              "type": "integer",
              "minimum": 512,
              "maximum": 4096
            },
            "chunk_overlap": {
              "type": "number",
              "minimum": 0.0,
              "exclusiveMaximum": 1.0,
              "default": 0.1
            },
            "preserve_tables":    { "type": "boolean", "default": true },
            "preserve_equations": { "type": "boolean", "default": true }
          },
          "additionalProperties": false
        },

        "profile": {
          "type": "string",
          "description": "Feature profile, e.g. \"core+figures\""
        },

        "config_hash": {
          "type": "string",
          "pattern": "^[A-Fa-f0-9]{64}$",
          "description": "SHA-256 of the canonicalised configuration JSON"
        },

        "x_extension": {
          "type": "object",
          "description": "Forward-compatible vendor extensions",
          "additionalProperties": true
        }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

### 3.2 Rules

* `chunk_overlap` **SHALL** be interpreted as a fraction (`0 ≤ x < 1`).
* `config_hash` **SHALL** be recomputed and committed after each change.

---

## 4 Discovery Module

### 4.1 Security Hooks

A Discovery implementation **SHALL** accept an opaque credential object (token, certificate, API key …).  The adapter passes it unchanged to the target service; public endpoints ignore it.

### 4.2 Global Rate-Limit Status

Discovery output **MUST** include:

```json
"rate_limit_status": {
  "limit": 1000,
  "remaining": 745,
  "reset_timestamp": "2025-07-14T12:00:00Z"
}
```

### 4.3 Source-Specific Requirements

#### arXiv

* **MUST** query both the REST API and the OAI-PMH feed `https://export.arxiv.org/oai2`.
* **MUST** extract version history and withdrawal notices.
* **SHOULD** expose category filtering and relevance scoring.

#### Indico

* **MUST** traverse event hierarchies, capture speaker metadata.
* **MUST** handle authentication when required.
* **SHOULD** support date-range filtering.

#### Internal Notes

* **MUST** respect repository-specific ACLs and classification flags.
* **SHOULD** allow content-based filtering.

#### TWiki

* **MUST** resolve internal links and page histories.
* **SHOULD** provide namespace filtering.

### 4.4 Discovery Output Schema

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/MohamedElashri/HEPilot/standards/schemas/discovery_output.schema.json",
  "title": "Discovery Output",
  "type": "object",
  "required": ["discovered_documents"],
  "properties": {
    "rate_limit_status": {
      "$ref": "https://github.com/MohamedElashri/HEPilot/standards/schemas/rate_limit_status.schema.json"
    },
    "discovered_documents": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "document_id",
          "source_type",
          "source_url",
          "title",
          "discovery_timestamp",
          "estimated_size"
        ],
        "properties": {
          "document_id":         { "type": "string", "format": "uuid" },
          "source_type":         { "type": "string" },
          "source_url":          { "type": "string", "format": "uri" },
          "title":               { "type": "string" },
          "authors":             { "type": "array", "items": { "type": "string" } },
          "discovery_timestamp": { "type": "string", "format": "date-time" },
          "estimated_size":      { "type": "integer" },
          "content_type":        { "type": "string" },
          "priority_score":      { "type": "number" }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

---

## 5 Acquisition Module

### 5.1 Download Requirements

* **MUST** implement exponential-backoff retry logic.
* **MUST** honour HTTP/HTTPS rate-limit headers.
* **SHOULD** use HTTP Range requests with 16 MiB blocks for artefacts > 1 GiB.

### 5.2 Validation

Every file **MUST** pass:

1. SHA-256 **and** SHA-512 hash verification.
2. Format/extension consistency.
3. Minimum size threshold.
4. Virus scan for external sources.

### 5.3 Acquisition Output Schema

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/MohamedElashri/HEPilot/standards/schemas/acquisition_output.schema.json",
  "title": "Acquisition Output",
  "type": "object",
  "required": ["acquired_documents"],
  "properties": {
    "acquired_documents": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "document_id",
          "local_path",
          "file_hash_sha256",
          "file_hash_sha512",
          "file_size",
          "download_timestamp",
          "download_status",
          "validation_status"
        ],
        "properties": {
          "document_id":        { "type": "string", "format": "uuid" },
          "local_path":         { "type": "string" },
          "file_hash_sha256":   { "type": "string", "pattern": "^[A-Fa-f0-9]{64}$" },
          "file_hash_sha512":   { "type": "string", "pattern": "^[A-Fa-f0-9]{128}$" },
          "file_size":          { "type": "integer" },
          "download_timestamp": { "type": "string", "format": "date-time" },
          "download_status":    {
            "enum": ["success", "failed", "partial", "abandoned"]
          },
          "retry_count":        { "type": "integer", "minimum": 0 },
          "validation_status":  {
            "enum": ["passed", "failed", "warning"]
          }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

---

## 6 Processing Pipeline

### 6.1 Adapter Processor Interface

```text
interface AdapterProcessor {
  process(input_file: File) -> ProcessingResult
  validate_input(input_file: File) -> boolean
  get_supported_formats() -> List<string>
}
```

### 6.2 Text Extraction

| Requirement                                 | Status     |
| ------------------------------------------- | ---------- |
| Preserve section hierarchy                  | **MUST**   |
| Convert tables to GitHub-Flavoured Markdown | **MUST**   |
| Preserve LaTeX equations (`$…$`, `$$…$$`)   | **MUST**   |
| Maintain cross-references and citations     | **SHOULD** |
| Handle multi-column layouts                 | **MUST**   |

### 6.3 Content Filtering

* Strip embedded images (unless optional figure extraction enabled).
* Remove navigation elements, headers, footers.
* Exclude adverts or boiler-plate.
* Eliminate duplicate content blocks.

### 6.4 Optional Figure Extraction

A processor **MAY** extract figures as SVG or PNG and insert placeholders:

```
![Figure n](fig_<sha256>.png){#fig:n}
Caption text …
```

`<sha256>` is the SHA-256 of the binary.

### 6.5 Reference Handling

Bibliographies **MUST** be serialised in CSL-JSON (`references.json`).
`full_document.md` **SHALL** include `<!--references-->`.

### 6.6 Processor-Specific Rules

| Source             | Mandatory Behaviour                                                                   |
| ------------------ | ------------------------------------------------------------------------------------- |
| **arXiv**          | Support PDF & LaTeX, preserve references, convert tables, maintain section numbering. |
| **Indico**         | Extract slide text & notes, preserve order, capture media descriptions.               |
| **Internal Notes** | Handle PDF, DOCX, LaTeX; respect revision markers & classification flags.             |
| **TWiki**          | Convert wiki markup, resolve links, keep page hierarchy.                              |

### 6.7 Processing Metadata Schema

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/MohamedElashri/HEPilot/standards/schemas/processing_metadata.schema.json",
  "title": "Processing Metadata",
  "type": "object",
  "required": [
    "processor_used",
    "processing_timestamp",
    "processing_duration"
  ],
  "properties": {
    "processor_used":      { "type": "string" },
    "processing_timestamp":{ "type": "string", "format": "date-time" },
    "processing_duration": { "type": "number" },
    "conversion_warnings": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "additionalProperties": false
}
```

---

## 7 Chunking Engine

### 7.1 Strategy

*Prefer semantic boundaries* (sections > paragraphs > sentences).
If that fails within `chunk_size`, use greedy token packing.

### 7.2 Algorithm

1. Locate section headers.
2. Pack tokens until reaching `chunk_size`; if exceeded, split at the preceding sentence boundary.
3. Apply overlap of `chunk_size × chunk_overlap`.
4. **MUST NOT** split inside equations, tables or fenced code.

### 7.3 Streaming Interface

```python
def chunk_generator(document: Document) -> Iterator[Chunk]:
    ...
```

### 7.4 Chunk Output Schema

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/MohamedElashri/HEPilot/standards/schemas/chunk_output.schema.json",
  "title": "Chunk Output",
  "type": "object",
  "required": [
    "chunk_id",
    "document_id",
    "chunk_index",
    "total_chunks",
    "content",
    "token_count"
  ],
  "properties": {
    "chunk_id":       { "type": "string", "format": "uuid" },
    "document_id":    { "type": "string", "format": "uuid" },
    "chunk_index":    { "type": "integer" },
    "total_chunks":   { "type": "integer" },
    "content":        { "type": "string" },
    "token_count":    { "type": "integer" },
    "chunk_type":     { "enum": ["text", "table", "equation", "mixed"] },
    "section_path":   { "type": "array", "items": { "type": "string" } },
    "has_overlap_previous": { "type": "boolean" },
    "has_overlap_next":     { "type": "boolean" },
    "content_features": {
      "type": "object",
      "properties": {
        "heading_count":  { "type": "integer" },
        "list_count":     { "type": "integer" },
        "table_count":    { "type": "integer" },
        "equation_count": { "type": "integer" }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

---

## 8 Metadata Management

### 8.1 Document-Level Metadata

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/MohamedElashri/HEPilot/standards/schemas/document_metadata.schema.json",
  "title": "Document Metadata",
  "type": "object",
  "required": [
    "document_id",
    "source_type",
    "original_url",
    "title",
    "file_hash",
    "file_size",
    "processing_timestamp",
    "adapter_version"
  ],
  "properties": {
    "document_id":        { "type": "string", "format": "uuid" },
    "source_type":        { "type": "string" },
    "original_url":       { "type": "string", "format": "uri" },
    "local_path":         { "type": "string" },
    "title":              { "type": "string" },
    "authors":            { "type": "array", "items": { "type": "string" } },
    "publication_date":   { "type": "string", "format": "date" },
    "subject_categories": { "type": "array", "items": { "type": "string" } },
    "language":           { "type": "string" },
    "file_hash":          { "type": "string" },
    "file_size":          { "type": "integer" },
    "processing_timestamp":{ "type": "string", "format": "date-time" },
    "adapter_version":    { "type": "string" },
    "experiment_tags":    { "type": "array", "items": { "type": "string" } },
    "collaboration":      { "type": "string" },
    "license":            { "type": "string" }
  },
  "additionalProperties": false
}
```

### 8.2 Chunk-Level Metadata

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/MohamedElashri/HEPilot/standards/schemas/chunk_metadata.schema.json",
  "title": "Chunk Metadata",
  "type": "object",
  "required": [
    "chunk_id",
    "document_id",
    "chunk_index",
    "total_chunks",
    "token_count"
  ],
  "properties": {
    "chunk_id":     { "type": "string", "format": "uuid" },
    "document_id":  { "type": "string", "format": "uuid" },
    "chunk_index":  { "type": "integer" },
    "total_chunks": { "type": "integer" },
    "section_hierarchy": {
      "type": "array",
      "items": { "type": "string" }
    },
    "token_count":      { "type": "integer" },
    "character_count":  { "type": "integer" },
    "chunk_type":       { "type": "string" },
    "contains_equations":{ "type": "boolean" },
    "contains_tables":   { "type": "boolean" },
    "overlap_info": {
      "type": "object",
      "required": [
        "has_previous_overlap",
        "has_next_overlap",
        "overlap_token_count"
      ],
      "properties": {
        "has_previous_overlap": { "type": "boolean" },
        "has_next_overlap":     { "type": "boolean" },
        "overlap_token_count":  { "type": "integer" }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

### 8.3 Processing Metadata

*(See § 6.7.)*

---

## 9 Output Format

### 9.1 Directory Layout

```
output/
├── documents/
│   └── {source_type}_{document_id}/
│       ├── chunks/
│       │   ├── chunk_0001.md
│       │   ├── chunk_0001_metadata.json
│       │   ├── …
│       ├── document_metadata.json
│       ├── processing_metadata.json
│       ├── references.json
│       ├── full_document.md
│       └── (optional) document_{id}.tar.zst
├── catalog.json
└── processing_log.json
```

If a document produces more than 128 chunks, the adapter **MAY** bundle the entire sub-tree into `document_{id}.tar.zst` and reference that tarball inside the catalog.

### 9.2 Naming & Encoding Rules

* All file names lower-case; words separated by underscores.
* Chunk indices zero-padded.
* Markdown files UTF-8; JSON files valid against schemas in Appendix A.

### 9.3 Virtual URI Scheme

`file_path` **SHOULD** adopt `adp://{bucket}/{key}` to abstract local v. object storage.

### 9.4 Catalog Schema

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/MohamedElashri/HEPilot/standards/schemas/catalog.schema.json",
  "title": "Processing Catalog",
  "type": "object",
  "required": [
    "creation_timestamp",
    "adapter_version",
    "total_documents",
    "total_chunks",
    "documents"
  ],
  "properties": {
    "creation_timestamp": { "type": "string", "format": "date-time" },
    "adapter_version":    { "type": "string" },
    "total_documents":    { "type": "integer" },
    "total_chunks":       { "type": "integer" },

    "source_distribution": {
      "type": "object",
      "properties": {
        "arxiv":          { "type": "integer" },
        "indico":         { "type": "integer" },
        "internal_notes": { "type": "integer" },
        "twiki":          { "type": "integer" },
        "other":          { "type": "integer" }
      },
      "additionalProperties": false
    },

    "documents": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "document_id",
          "source_type",
          "title",
          "chunk_count",
          "file_path"
        ],
        "properties": {
          "document_id": { "type": "string", "format": "uuid" },
          "source_type": { "type": "string" },
          "title":       { "type": "string" },
          "chunk_count": { "type": "integer" },
          "file_path":   { "type": "string" }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

---

## 10 Error Handling & Logging

### 10.1 Categories

| Category    | Examples                             |
| ----------- | ------------------------------------ |
| Discovery   | API failure, credential mismatch     |
| Acquisition | Network timeout, checksum error      |
| Processing  | Parser exception, unsupported format |
| Output      | I/O error, JSON schema violation     |

### 10.2 Log Entry Schema

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/MohamedElashri/HEPilot/standards/schemas/log_entry.schema.json",
  "title": "Processing Log Entry",
  "type": "object",
  "required": [
    "timestamp",
    "trace_id",
    "level",
    "component",
    "message"
  ],
  "properties": {
    "timestamp":  { "type": "string", "format": "date-time" },
    "trace_id":   { "type": "string", "format": "uuid" },
    "level":      { "enum": ["debug", "info", "warning", "error", "critical"] },
    "component":  { "type": "string" },
    "document_id":{ "type": "string", "format": "uuid" },
    "message":    { "type": "string" },
    "error_code": { "type": "string" },
    "recovery_action": { "type": "string" },
    "context":    { "type": "object" }
  },
  "additionalProperties": false
}
```

When retries apply, `context.retry_policy` **SHOULD** appear:

```json
"retry_policy": {
  "strategy": "exponential_backoff",
  "initial_backoff_ms": 2000,
  "max_retry_attempts": 5
}
```

---

## 11 Compliance & Testing

### 11.1 Test Suite

The *HEPilot* repository hosts a reference corpus and an automated test harness.  Conforming adapters **MUST** pass:

* JSON-schema validation for every output artefact.
* Format-conversion tests for the source types they support.
* Basic performance benchmark (< 1 GiB RAM per process).
* Interoperability check: generated markdown can be embedded by the reference embedding pipeline without error.

### 11.2 Reference Implementation

An illustrative adapter resides at
[https://github.com/MohamedElashri/HEPilot/standards/reference\_adapter](https://github.com/MohamedElashri/HEPilot/standards/reference_adapter).

---

## 12 Versioning & Governance

* The specification follows **Semantic Versioning** (`MAJOR.MINOR.PATCH`).
* Breaking changes increment **MAJOR**.
* Minor, backward-compatible additions increment **MINOR**.
* Typographic or editorial fixes increment **PATCH**.

Implementations declare supported feature sets via `adapter_config.profile`.

---

## Conclusion

The HEPilot RAG Adapter Framework supplies a concise but extensible contract for turning heterogeneous HEP documents into LLM-ready knowledge. 
Feedback and pull-requests are welcome at the GitHub repository or by contacting [mohamed.elashri@cern.ch](mailto:mohamed.elashri@cern.ch).

---

## Document Control

| Field          | Value                                                                                                      |
| -------------- | ---------------------------------------------------------------------------------------------------------- |
| Version        | **1.0**                                                                                                    |
| Classification | Public                                                                                                     |
| Repository     | [https://github.com/MohamedElashri/HEPilot/standards](https://github.com/MohamedElashri/HEPilot/standards) |

---

## Appendix A Machine-Readable JSON Schemas

All schemas conform to JSON-Schema Draft 2020-12 and disable unspecified properties (`"additionalProperties": false"`) unless otherwise noted.  File paths under `$id` correspond to:

```
https://github.com/MohamedElashri/HEPilot/standards/schemas/
```

---

### A.1  rate\_limit\_status.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/MohamedElashri/HEPilot/standards/schemas/rate_limit_status.schema.json",
  "title": "Rate-Limit Status",
  "type": "object",
  "required": ["limit", "remaining", "reset_timestamp"],
  "properties": {
    "limit":           { "type": "integer", "minimum": 0 },
    "remaining":       { "type": "integer", "minimum": 0 },
    "reset_timestamp": { "type": "string", "format": "date-time" }
  },
  "additionalProperties": false
}
```

---

### A.2  adapter\_config.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/MohamedElashri/HEPilot/standards/schemas/adapter_config.schema.json",
  "title": "Adapter Configuration",
  "type": "object",
  "required": ["adapter_config"],
  "properties": {
    "adapter_config": {
      "type": "object",
      "required": [
        "name",
        "version",
        "source_type",
        "processing_config",
        "config_hash"
      ],
      "properties": {
        "name":    { "type": "string" },
        "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
        "source_type": {
          "description": "Document class handled by this adapter",
          "enum": ["arxiv", "indico", "internal_notes", "twiki", "other"]
        },
        "processing_config": {
          "type": "object",
          "required": [
            "chunk_size",
            "chunk_overlap",
            "preserve_tables",
            "preserve_equations"
          ],
          "properties": {
            "chunk_size": {
              "type": "integer",
              "minimum": 512,
              "maximum": 4096
            },
            "chunk_overlap": {
              "type": "number",
              "minimum": 0.0,
              "exclusiveMaximum": 1.0,
              "default": 0.1
            },
            "preserve_tables":    { "type": "boolean", "default": true },
            "preserve_equations": { "type": "boolean", "default": true }
          },
          "additionalProperties": false
        },
        "profile": {
          "type": "string",
          "description": "Feature profile (e.g. \"core+figures\")"
        },
        "config_hash": {
          "type": "string",
          "pattern": "^[A-Fa-f0-9]{64}$",
          "description": "SHA-256 of the canonicalised configuration JSON"
        },
        "x_extension": {
          "type": "object",
          "description": "Forward-compatible extensions",
          "additionalProperties": true
        }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

---

### A.3  discovery\_output.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/MohamedElashri/HEPilot/standards/schemas/discovery_output.schema.json",
  "title": "Discovery Output",
  "type": "object",
  "required": ["discovered_documents"],
  "properties": {
    "rate_limit_status": {
      "$ref": "rate_limit_status.schema.json"
    },
    "discovered_documents": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "document_id",
          "source_type",
          "source_url",
          "title",
          "discovery_timestamp",
          "estimated_size"
        ],
        "properties": {
          "document_id":         { "type": "string", "format": "uuid" },
          "source_type":         { "type": "string" },
          "source_url":          { "type": "string", "format": "uri" },
          "title":               { "type": "string" },
          "authors":             { "type": "array", "items": { "type": "string" } },
          "discovery_timestamp": { "type": "string", "format": "date-time" },
          "estimated_size":      { "type": "integer" },
          "content_type":        { "type": "string" },
          "priority_score":      { "type": "number" }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

---

### A.4  acquisition\_output.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/MohamedElashri/HEPilot/standards/schemas/acquisition_output.schema.json",
  "title": "Acquisition Output",
  "type": "object",
  "required": ["acquired_documents"],
  "properties": {
    "acquired_documents": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "document_id",
          "local_path",
          "file_hash_sha256",
          "file_hash_sha512",
          "file_size",
          "download_timestamp",
          "download_status",
          "validation_status"
        ],
        "properties": {
          "document_id":        { "type": "string", "format": "uuid" },
          "local_path":         { "type": "string" },
          "file_hash_sha256":   { "type": "string", "pattern": "^[A-Fa-f0-9]{64}$" },
          "file_hash_sha512":   { "type": "string", "pattern": "^[A-Fa-f0-9]{128}$" },
          "file_size":          { "type": "integer" },
          "download_timestamp": { "type": "string", "format": "date-time" },
          "download_status":    { "enum": ["success", "failed", "partial", "abandoned"] },
          "retry_count":        { "type": "integer", "minimum": 0 },
          "validation_status":  { "enum": ["passed", "failed", "warning"] }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

---

### A.5  chunk\_output.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/MohamedElashri/HEPilot/standards/schemas/chunk_output.schema.json",
  "title": "Chunk Output",
  "type": "object",
  "required": [
    "chunk_id",
    "document_id",
    "chunk_index",
    "total_chunks",
    "content",
    "token_count"
  ],
  "properties": {
    "chunk_id":       { "type": "string", "format": "uuid" },
    "document_id":    { "type": "string", "format": "uuid" },
    "chunk_index":    { "type": "integer" },
    "total_chunks":   { "type": "integer" },
    "content":        { "type": "string" },
    "token_count":    { "type": "integer" },
    "chunk_type":     { "enum": ["text", "table", "equation", "mixed"] },
    "section_path":   { "type": "array", "items": { "type": "string" } },
    "has_overlap_previous": { "type": "boolean" },
    "has_overlap_next":     { "type": "boolean" },
    "content_features": {
      "type": "object",
      "properties": {
        "heading_count":  { "type": "integer" },
        "list_count":     { "type": "integer" },
        "table_count":    { "type": "integer" },
        "equation_count": { "type": "integer" }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

---

### A.6  document\_metadata.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/MohamedElashri/HEPilot/standards/schemas/document_metadata.schema.json",
  "title": "Document Metadata",
  "type": "object",
  "required": [
    "document_id",
    "source_type",
    "original_url",
    "title",
    "file_hash",
    "file_size",
    "processing_timestamp",
    "adapter_version"
  ],
  "properties": {
    "document_id":        { "type": "string", "format": "uuid" },
    "source_type":        { "type": "string" },
    "original_url":       { "type": "string", "format": "uri" },
    "local_path":         { "type": "string" },
    "title":              { "type": "string" },
    "authors":            { "type": "array", "items": { "type": "string" } },
    "publication_date":   { "type": "string", "format": "date" },
    "subject_categories": { "type": "array", "items": { "type": "string" } },
    "language":           { "type": "string" },
    "file_hash":          { "type": "string" },
    "file_size":          { "type": "integer" },
    "processing_timestamp":{ "type": "string", "format": "date-time" },
    "adapter_version":    { "type": "string" },
    "experiment_tags":    { "type": "array", "items": { "type": "string" } },
    "collaboration":      { "type": "string" },
    "license":            { "type": "string" }
  },
  "additionalProperties": false
}
```

---

### A.7  chunk\_metadata.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/MohamedElashri/HEPilot/standards/schemas/chunk_metadata.schema.json",
  "title": "Chunk Metadata",
  "type": "object",
  "required": [
    "chunk_id",
    "document_id",
    "chunk_index",
    "total_chunks",
    "token_count"
  ],
  "properties": {
    "chunk_id":     { "type": "string", "format": "uuid" },
    "document_id":  { "type": "string", "format": "uuid" },
    "chunk_index":  { "type": "integer" },
    "total_chunks": { "type": "integer" },
    "section_hierarchy": {
      "type": "array",
      "items": { "type": "string" }
    },
    "token_count":      { "type": "integer" },
    "character_count":  { "type": "integer" },
    "chunk_type":       { "type": "string" },
    "contains_equations":{ "type": "boolean" },
    "contains_tables":   { "type": "boolean" },
    "overlap_info": {
      "type": "object",
      "required": [
        "has_previous_overlap",
        "has_next_overlap",
        "overlap_token_count"
      ],
      "properties": {
        "has_previous_overlap": { "type": "boolean" },
        "has_next_overlap":     { "type": "boolean" },
        "overlap_token_count":  { "type": "integer" }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

---

### A.8  processing\_metadata.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/MohamedElashri/HEPilot/standards/schemas/processing_metadata.schema.json",
  "title": "Processing Metadata",
  "type": "object",
  "required": [
    "processor_used",
    "processing_timestamp",
    "processing_duration"
  ],
  "properties": {
    "processor_used":      { "type": "string" },
    "processing_timestamp":{ "type": "string", "format": "date-time" },
    "processing_duration": { "type": "number" },
    "conversion_warnings": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "additionalProperties": false
}
```

---

### A.9  catalog.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/MohamedElashri/HEPilot/standards/schemas/catalog.schema.json",
  "title": "Processing Catalog",
  "type": "object",
  "required": [
    "creation_timestamp",
    "adapter_version",
    "total_documents",
    "total_chunks",
    "documents"
  ],
  "properties": {
    "creation_timestamp": { "type": "string", "format": "date-time" },
    "adapter_version":    { "type": "string" },
    "total_documents":    { "type": "integer" },
    "total_chunks":       { "type": "integer" },
    "source_distribution": {
      "type": "object",
      "properties": {
        "arxiv":          { "type": "integer" },
        "indico":         { "type": "integer" },
        "internal_notes": { "type": "integer" },
        "twiki":          { "type": "integer" },
        "other":          { "type": "integer" }
      },
      "additionalProperties": false
    },
    "documents": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "document_id",
          "source_type",
          "title",
          "chunk_count",
          "file_path"
        ],
        "properties": {
          "document_id": { "type": "string", "format": "uuid" },
          "source_type": { "type": "string" },
          "title":       { "type": "string" },
          "chunk_count": { "type": "integer" },
          "file_path":   { "type": "string" }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

---

### A.10  log\_entry.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/MohamedElashri/HEPilot/standards/schemas/log_entry.schema.json",
  "title": "Processing Log Entry",
  "type": "object",
  "required": [
    "timestamp",
    "trace_id",
    "level",
    "component",
    "message"
  ],
  "properties": {
    "timestamp":  { "type": "string", "format": "date-time" },
    "trace_id":   { "type": "string", "format": "uuid" },
    "level":      { "enum": ["debug", "info", "warning", "error", "critical"] },
    "component":  { "type": "string" },
    "document_id":{ "type": "string", "format": "uuid" },
    "message":    { "type": "string" },
    "error_code": { "type": "string" },
    "recovery_action": { "type": "string" },
    "context":    { "type": "object" }
  },
  "additionalProperties": false
}
```



**End of Specification**

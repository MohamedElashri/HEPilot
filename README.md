# HEPilot

**High-Energy Physics Literature Pilot** - A modular RAG framework for HEP documentation.

## Overview

HEPilot is a Retrieval-Augmented Generation (RAG) system designed for High-Energy Physics literature and documentation. It provides:

- **Modular Architecture**: Pluggable adapters for data sources, embeddings, and vector stores
- **Multi-Source Support**: arXiv, Indico, TWiki, internal notes, and code repositories
- **Semantic Search**: Fast similarity search over HEP literature
- **Full Traceability**: Every result maps back to original source
- **OpenAI-Compatible API**: Standard REST interface for LLM integration
- **Web Interface**: Ready-to-use chat UI with inline citations

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                      User Interface (UI)                  │
│           Chatbot-UI → /v1/chat | /rag/search             │
└──────────────┬────────────────────────────────────────────┘
               │  REST + SSE (OpenAI spec)                  
┌──────────────┴────────────────────────────────────────────┐
│                        API Layer                          │
│ FastAPI · Auth · Throttling · Metrics · Health Probes     │
└──────────────┬────────────────────────────────────────────┘
     ingest    │                                    retrieve
┌──────────────┴──────────────┐      ┌────────────────────────┴──────────────┐
│        Source Collector      │      │            Embedding Engine           │
│ scrape → clean → chunk → DB  │      │ encode → upsert/query → decode ↩text │
└──────────────────────────────┘      └───────────────────────────────────────┘
```

### Components

1. **Source Collector** (`src/collector/`)
   - Adapters for various HEP data sources
   - Document processing and chunking
   - Currently implemented: arXiv

2. **Embedding Engine** (`src/embedding/`)
   - Text-to-vector encoding
   - Vector storage and similarity search
   - Content retrieval with full metadata

3. **API Layer** (`src/api/`) - *WIP*
   - OpenAI-compatible endpoints
   - LLM backend integration
   - Authentication and rate limiting

4. **User Interface** (`ui/`) - *WIP*
   - Web-based chat interface
   - Document browsing
   - Citation tracking

## Project Structure

```
hepilot/
├── src/
│   ├── collector/          # Data acquisition layer
│   │   ├── ports.py        # Abstract interfaces
│   │   ├── registry.py     # Adapter discovery
│   │   └── adapters/       # Source-specific implementations
│   │       └── arxiv/      # arXiv adapter
│   ├── embedding/          # Embedding layer (in development)
│   │   ├── ports.py        # Encoder/VectorDB/Decoder interfaces
│   │   ├── registry.py     # Adapter registry
│   │   └── adapters/       # Encoder/VectorDB implementations
│   └── api/                # API layer (planned)
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contracts/
├── docker/                 # Docker configurations
├── scripts/                # Utility scripts
├── alembic/               # Database migrations
├── config/                # Configuration files
├── docs/                  # Documentation
│   ├── reference.md       # Architecture reference
│   ├── plan.md           # Implementation plan
│   └── embedding_quickstart.md
└── standards/             # Data format specifications
```

## Current Status

### Completed
- **Source Collector Framework**: Port interfaces and adapter pattern
- **arXiv Adapter**: Full pipeline (discovery → acquisition → processing → chunking)
- **Data Standards**: JSON schemas for all pipeline stages
- **Documentation**: Architecture reference and implementation plans

### In Progress
- **Embedding Engine**: Text encoding, vector storage, retrieval (see `docs/plan.md`)
  - Port interfaces defined
  - Adapters in development
- **API Layer**: REST endpoints, LLM integration
- **User Interface**: Web chat interface
- **Additional Adapters**: Indico, TWiki, internal notes, code repositories

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- uv (for dependency management)

### Installation

```bash
# Clone the repository
git clone https://github.com/MohamedElashri/HEPilot.git
cd HEPilot

# Install dependencies (when available)
uv pip install -r requirements.txt 
```

## Documentation

- **[Reference Architecture](docs/reference.md)**: Complete system design
- **[Data Standards](standards/README.md)**: Format specifications

## Contributing

Contributions are welcome! Please see our development branches:

- `main`: Stable releases
- Feature branches: `feature/*`

## Contact

**Maintainer**: Mohamed Elashri  
**Email**: mohamed.elashri@cern.ch  
**Repository**: https://github.com/MohamedElashri/HEPilot


**Status**: Active Development | **Version**: 0.1.0-dev | **Last Updated**: October 2025

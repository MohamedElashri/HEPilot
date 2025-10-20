# HEPilot Implementation Plan: Modular Embedding Layer

**Version:** 0.1  
**Date:** October 20, 2025  
**Status:** Planning Phase  
**Previous Milestone:** ✅ arXiv Adapter (Data Acquisition Layer)  
**Current Milestone:** 🎯 Embedding Engine (Embedding Layer)  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Component Specifications](#3-component-specifications)
4. [Implementation Phases](#4-implementation-phases)
5. [Directory Structure](#5-directory-structure)
6. [Technical Specifications](#6-technical-specifications)
7. [Integration Points](#7-integration-points)
8. [Testing Strategy](#8-testing-strategy)
9. [Success Criteria](#9-success-criteria)
10. [Timeline & Dependencies](#10-timeline--dependencies)

---

## 1. Executive Summary

### Context
The arXiv adapter (Data Acquisition Layer) is now functional and producing standardized outputs:
- Discovery → Acquisition → Processing → Chunking pipeline complete
- Output: Markdown chunks with comprehensive metadata
- Ready for embedding and vector storage

### Objective
Build the **Modular Embedding Engine** that transforms processed document chunks into searchable vector representations while maintaining full traceability back to source content.

### Key Design Principles
1. **Adapter Pattern**: Pluggable encoders and vector stores
2. **Separation of Concerns**: Content retrieval independent of vector storage
3. **Full Traceability**: Every vector maps to exact source chunk
4. **Performance**: Batch processing, async operations, caching
5. **Observability**: Metrics, logging, health checks

---

## 2. Architecture Overview

### 2.1 High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     Source Collector                            │
│          (arXiv Adapter + Future Adapters)                      │
│                                                                  │
│  Output: chunk_NNNN.md + chunk_NNNN_metadata.json              │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Embedding Engine                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Encoder    │  │  Vector DB   │  │   Decoder    │         │
│  │  (Adapter)   │  │  (Adapter)   │  │  (Adapter)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         │                  │                  │                 │
│         │                  │                  │                 │
│  Text → Vector      Store + Index      Vector ID → Text        │
└─────────┴──────────────────┴──────────────────┴─────────────────┘
                 │                  │                  │
                 ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Storage Layer                                │
│  ┌─────────────────────┐      ┌──────────────────────┐         │
│  │   PostgreSQL        │      │   Vector Store       │         │
│  │   (DocStore)        │      │   (Chroma/Qdrant)    │         │
│  │                     │      │                      │         │
│  │ • doc_segments      │      │ • vectors            │         │
│  │ • documents         │      │ • metadata refs      │         │
│  │ • processing_meta   │      │ • similarity index   │         │
│  └─────────────────────┘      └──────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Layer                                  │
│           (Future Phase - Not in Current Scope)                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Responsibilities

| Component | Role | Input | Output |
|-----------|------|-------|--------|
| **Encoder** | Text → Vector transformation | List of text strings | numpy.ndarray of vectors |
| **VectorDB** | Vector storage & similarity search | Vectors + IDs | Query results (IDs + scores) |
| **DocStore** | Plain text persistence & retrieval | Chunks + metadata | Original text chunks |
| **Decoder** | Vector ID → Original text | Vector IDs from query | Full chunk content + metadata |
| **Registry** | Adapter discovery & instantiation | Adapter name + config | Initialized adapter instance |

### 2.3 Data Flow

**Ingestion Pipeline:**
```
1. Read chunk files from adapter output
2. Extract text content from .md files
3. Load metadata from .json files
4. Store chunks in PostgreSQL (DocStore)
5. Generate embeddings via Encoder
6. Upsert vectors to VectorDB with chunk IDs
7. Log processing metrics
```

**Retrieval Pipeline:**
```
1. User query (text string)
2. Encode query via Encoder
3. Similarity search in VectorDB (top-k)
4. Get vector IDs + similarity scores
5. Lookup full chunks via Decoder → PostgreSQL
6. Return ranked results with content + metadata
```

---

## 3. Component Specifications

### 3.1 Port Interfaces (Abstract Protocols)

#### 3.1.1 Encoder Protocol

**File:** `src/embedding/ports.py`

```python
from typing import Protocol, List
import numpy as np
from numpy.typing import NDArray

class Encoder(Protocol):
    """
    Text-to-vector encoding interface.
    
    Implementations MUST:
    - Return normalized vectors (unit length)
    - Support batch processing
    - Be deterministic (same text → same vector)
    - Handle long texts gracefully (truncate or error)
    """
    
    async def embed(self, texts: List[str]) -> NDArray[np.float32]:
        """
        Encode text strings to vectors.
        
        Args:
            texts: List of text strings to encode
            
        Returns:
            2D array of shape (len(texts), embedding_dim)
            
        Raises:
            EncoderError: If encoding fails
        """
        ...
    
    @property
    def dimension(self) -> int:
        """Vector dimensionality (e.g., 384, 768, 1024)."""
        ...
    
    @property
    def max_tokens(self) -> int:
        """Maximum token length supported."""
        ...
    
    async def health_check(self) -> bool:
        """Verify encoder is operational."""
        ...
```

#### 3.1.2 VectorDB Protocol

**File:** `src/embedding/ports.py`

```python
from typing import Protocol, List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray

@dataclass
class QueryResult:
    """Single similarity search result."""
    chunk_id: str
    score: float
    metadata: Dict[str, Any]

class VectorDB(Protocol):
    """
    Vector storage and similarity search interface.
    
    Implementations MUST:
    - Store vectors with associated IDs
    - Support similarity search (cosine or dot-product)
    - Handle batch upserts efficiently
    - Maintain index consistency
    """
    
    async def upsert(
        self,
        ids: List[str],
        vectors: NDArray[np.float32],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Insert or update vectors.
        
        Args:
            ids: Unique identifiers (chunk UUIDs)
            vectors: 2D array of shape (len(ids), dimension)
            metadata: Optional metadata dicts (NOT content!)
        """
        ...
    
    async def query(
        self,
        vector: NDArray[np.float32],
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[QueryResult]:
        """
        Find most similar vectors.
        
        Args:
            vector: Query vector (1D array)
            top_k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            Ranked list of QueryResult objects
        """
        ...
    
    async def delete(self, ids: List[str]) -> None:
        """Remove vectors by ID."""
        ...
    
    async def count(self) -> int:
        """Total number of vectors in store."""
        ...
    
    async def health_check(self) -> bool:
        """Verify vector store is operational."""
        ...
```

#### 3.1.3 Decoder Protocol

**File:** `src/embedding/ports.py`

```python
from typing import Protocol, List, Optional
from dataclasses import dataclass

@dataclass
class ChunkContent:
    """Decoded chunk with full content and metadata."""
    chunk_id: str
    text: str
    document_id: str
    source_type: str
    section_path: List[str]
    position_in_doc: int
    token_count: int
    overlap_start: int
    overlap_end: int
    source_url: str
    created_at: str
    additional_metadata: Dict[str, Any]

class Decoder(Protocol):
    """
    Vector ID to original content retrieval.
    
    CRITICAL: Decoder MUST fetch content from PostgreSQL,
    NOT from vector store payloads. This ensures traceability.
    """
    
    async def lookup(self, chunk_ids: List[str]) -> List[ChunkContent]:
        """
        Retrieve full chunk content by IDs.
        
        Args:
            chunk_ids: List of chunk UUIDs
            
        Returns:
            List of ChunkContent objects in same order
            Missing IDs return None in that position
        """
        ...
    
    async def get_document_chunks(
        self,
        document_id: str,
        limit: Optional[int] = None
    ) -> List[ChunkContent]:
        """Get all chunks for a document."""
        ...
    
    async def health_check(self) -> bool:
        """Verify database connection."""
        ...
```

### 3.2 Default Adapter Implementations

#### 3.2.1 ONNXBGEEncoder

**File:** `src/embedding/adapters/onnx_bge_encoder.py`

**Technology:**
- ONNX Runtime (CPU optimized)
- BGE-base-en-v1.5 model (384 dimensions)
- Sentence transformers tokenizer

**Features:**
- ✅ No GPU required (runs on CPU)
- ✅ Fast inference (~50-100 chunks/sec on CPU)
- ✅ Normalized embeddings
- ✅ Batch processing support
- ✅ Model caching

**Configuration:**
```toml
[embedding.encoder]
type = "onnx_bge"
model_name = "BAAI/bge-base-en-v1.5"
batch_size = 32
device = "cpu"
normalize = true
cache_dir = ".cache/models"
```

#### 3.2.2 ChromaDB Adapter

**File:** `src/embedding/adapters/chroma_vectordb.py`

**Technology:**
- ChromaDB (embedded mode)
- HNSW index for similarity search
- Persistent storage

**Features:**
- ✅ No external service required
- ✅ Fast similarity search
- ✅ Metadata filtering
- ✅ Persistent storage on disk
- ✅ Collection management

**Configuration:**
```toml
[embedding.vectordb]
type = "chroma"
persist_directory = ".data/chroma"
collection_name = "hepilot"
distance_metric = "cosine"
```

#### 3.2.3 PostgreSQL DocStore

**File:** `src/embedding/adapters/postgres_docstore.py`

**Schema:**
```sql
-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    source_type VARCHAR(50) NOT NULL,
    source_id VARCHAR(500) NOT NULL,
    title TEXT,
    authors JSONB,
    publication_date TIMESTAMP,
    source_url TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(source_type, source_id)
);

-- Document segments (chunks) table
CREATE TABLE doc_segments (
    id UUID PRIMARY KEY,
    doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    section_path JSONB,  -- ["Introduction", "Methods", ...]
    position_in_doc INTEGER NOT NULL,
    token_count INTEGER NOT NULL,
    overlap_start INTEGER NOT NULL,
    overlap_end INTEGER NOT NULL,
    meta JSONB,  -- chunk-specific metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_document FOREIGN KEY (doc_id) REFERENCES documents(id)
);

-- Indexes for performance
CREATE INDEX idx_segments_doc_id ON doc_segments(doc_id);
CREATE INDEX idx_segments_position ON doc_segments(doc_id, position_in_doc);
CREATE INDEX idx_documents_source ON documents(source_type, source_id);
CREATE INDEX idx_segments_text_trgm ON doc_segments USING gin(text gin_trgm_ops);

-- Processing metadata table
CREATE TABLE processing_runs (
    id UUID PRIMARY KEY,
    doc_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    adapter_type VARCHAR(50),
    adapter_version VARCHAR(20),
    config_hash VARCHAR(64),
    status VARCHAR(20),  -- pending, processing, completed, failed
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    metrics JSONB
);
```

**Features:**
- ✅ Full text search (pg_trgm)
- ✅ Document hierarchy preservation
- ✅ Efficient chunk retrieval
- ✅ Processing audit trail

#### 3.2.4 PostgreSQL Decoder

**File:** `src/embedding/adapters/postgres_decoder.py`

**Features:**
- ✅ Async database queries (asyncpg)
- ✅ Batch retrieval optimization
- ✅ Connection pooling
- ✅ Full metadata reconstruction

---

## 4. Implementation Phases

### Phase 1: Core Infrastructure (Week 1)

**Deliverables:**
- [ ] Port interfaces defined (`src/embedding/ports.py`)
- [ ] Adapter registry implementation (`src/embedding/registry.py`)
- [ ] Database schema and migrations (Alembic)
- [ ] Base configuration management
- [ ] Unit tests for protocols

**Files to Create:**
```
src/embedding/
├── __init__.py
├── ports.py              # Protocol definitions
├── registry.py           # Adapter discovery & registration
├── exceptions.py         # Custom exceptions
└── config.py             # Configuration models
```

### Phase 2: PostgreSQL Layer (Week 1-2)

**Deliverables:**
- [ ] DocStore implementation
- [ ] Decoder implementation
- [ ] Database migrations
- [ ] Integration tests with test database
- [ ] Fixture data for testing

**Files to Create:**
```
src/embedding/adapters/
├── __init__.py
├── postgres_docstore.py
├── postgres_decoder.py
└── db_models.py

alembic/
└── versions/
    └── 001_initial_schema.py
```

### Phase 3: Encoder Implementation (Week 2)

**Deliverables:**
- [ ] ONNX BGE encoder adapter
- [ ] Model download and caching
- [ ] Batch processing logic
- [ ] Performance benchmarks
- [ ] Unit tests

**Files to Create:**
```
src/embedding/adapters/
├── onnx_bge_encoder.py
└── base_encoder.py        # Shared encoder utilities
```

### Phase 4: Vector Store Implementation (Week 2-3)

**Deliverables:**
- [ ] ChromaDB adapter
- [ ] Collection management
- [ ] Similarity search implementation
- [ ] Integration tests
- [ ] Performance benchmarks

**Files to Create:**
```
src/embedding/adapters/
└── chroma_vectordb.py
```

### Phase 5: Ingestion Pipeline (Week 3)

**Deliverables:**
- [ ] Pipeline orchestrator
- [ ] Batch processing logic
- [ ] Progress tracking
- [ ] Error handling and retry logic
- [ ] CLI tool for ingestion

**Files to Create:**
```
src/embedding/
├── pipeline.py           # Ingestion orchestration
├── ingestion.py          # Chunk reading and processing
└── cli.py                # Command-line interface

scripts/
└── ingest_adapter_output.py
```

### Phase 6: Retrieval Pipeline (Week 3-4)

**Deliverables:**
- [ ] Query processing
- [ ] Retrieval implementation
- [ ] Result ranking
- [ ] Integration tests
- [ ] CLI tool for search

**Files to Create:**
```
src/embedding/
├── retrieval.py          # Query and retrieval logic
└── ranking.py            # Result scoring and reranking

scripts/
└── search.py
```

### Phase 7: Integration & Testing (Week 4)

**Deliverables:**
- [ ] End-to-end integration tests
- [ ] Performance benchmarks
- [ ] Documentation
- [ ] Example workflows
- [ ] CI/CD pipeline updates

**Files to Create:**
```
tests/
├── unit/
│   └── embedding/
│       ├── test_encoders.py
│       ├── test_vectordb.py
│       └── test_decoder.py
├── integration/
│   └── embedding/
│       ├── test_pipeline.py
│       └── test_retrieval.py
└── fixtures/
    └── sample_chunks/

docs/
└── embedding_guide.md
```

---

## 5. Directory Structure

### 5.1 Complete Source Layout

```
src/
└── embedding/
    ├── __init__.py
    ├── ports.py                    # Protocol definitions
    ├── registry.py                 # Adapter registry
    ├── config.py                   # Configuration models
    ├── exceptions.py               # Custom exceptions
    ├── pipeline.py                 # Ingestion orchestration
    ├── ingestion.py                # Chunk reading
    ├── retrieval.py                # Query processing
    ├── ranking.py                  # Result scoring
    ├── cli.py                      # CLI interface
    └── adapters/
        ├── __init__.py
        ├── postgres_docstore.py
        ├── postgres_decoder.py
        ├── db_models.py
        ├── onnx_bge_encoder.py
        ├── base_encoder.py
        └── chroma_vectordb.py
```

### 5.2 Configuration Structure

```
config/
└── embedding.toml

[embedding.encoder]
type = "onnx_bge"
model_name = "BAAI/bge-base-en-v1.5"
batch_size = 32
device = "cpu"
normalize = true
cache_dir = ".cache/models"

[embedding.vectordb]
type = "chroma"
persist_directory = ".data/chroma"
collection_name = "hepilot"
distance_metric = "cosine"

[embedding.docstore]
type = "postgres"
database_url = "postgresql+asyncpg://hep:hep@localhost/hepilot"
pool_size = 10
max_overflow = 20

[embedding.pipeline]
batch_size = 100
max_workers = 4
checkpoint_interval = 1000
```

---

## 6. Technical Specifications

### 6.1 Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Encoding Speed** | > 50 chunks/sec (CPU) | Batch of 1000 chunks |
| **Ingestion Throughput** | > 1000 chunks/min | Full pipeline |
| **Query Latency** | < 100ms (p95) | Top-10 similarity search |
| **Memory Usage** | < 2GB RAM | 100K chunks indexed |
| **Storage Efficiency** | < 1KB/chunk overhead | Metadata + indexes |

### 6.2 Quality Requirements

| Aspect | Requirement | Validation |
|--------|-------------|------------|
| **Determinism** | Same text → same vector | Unit test |
| **Traceability** | 100% vector → source mapping | Integration test |
| **Consistency** | Vector count = chunk count | Health check |
| **Reliability** | < 0.1% ingestion failure rate | Monitoring |
| **Reproducibility** | Config hash tracks parameters | Metadata check |

### 6.3 Technology Stack

**Core Dependencies:**
```toml
[tool.poetry.dependencies]
python = "^3.11"
numpy = "^1.26.0"
asyncpg = "^0.29.0"
psycopg2-binary = "^2.9.9"
chromadb = "^0.4.24"
onnxruntime = "^1.17.0"
transformers = "^4.38.0"
sentence-transformers = "^2.5.0"
alembic = "^1.13.0"
pydantic = "^2.6.0"
pydantic-settings = "^2.2.0"
rich = "^13.7.0"          # CLI formatting
typer = "^0.9.0"          # CLI framework
tqdm = "^4.66.0"          # Progress bars
```

**Dev Dependencies:**
```toml
[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
pytest-asyncio = "^0.23.0"
pytest-cov = "^4.1.0"
mypy = "^1.8.0"
ruff = "^0.2.0"
```

---

## 7. Integration Points

### 7.1 Adapter Output Integration

**Input:** Adapter output directory structure
```
adapters/arxiv_adapter/arxiv_output/
├── documents/
│   └── arxiv_2301.12345/
│       ├── chunks/
│       │   ├── chunk_0001.md
│       │   ├── chunk_0001_metadata.json
│       │   ├── chunk_0002.md
│       │   └── chunk_0002_metadata.json
│       ├── full_document.md
│       ├── document_metadata.json
│       └── processing_metadata.json
└── catalog.json
```

**Processing Flow:**
1. Read `catalog.json` to get document list
2. For each document:
   - Read `document_metadata.json` → Insert into `documents` table
   - Read `processing_metadata.json` → Insert into `processing_runs` table
   - For each chunk:
     - Read `chunk_NNNN.md` → Extract text
     - Read `chunk_NNNN_metadata.json` → Extract metadata
     - Insert into `doc_segments` table
     - Generate embedding
     - Upsert to vector store

### 7.2 API Layer Integration (Future)

**Embedding Engine Exposes:**
```python
class EmbeddingService:
    async def ingest_adapter_output(self, output_dir: Path) -> IngestResult
    async def query(self, text: str, top_k: int = 10) -> List[ChunkContent]
    async def get_chunk(self, chunk_id: str) -> ChunkContent
    async def health_check() -> HealthStatus
```

**API Layer Will Use:**
- `query()` for `/rag/search` endpoint
- `get_chunk()` for chunk detail retrieval
- `health_check()` for `/healthz` endpoint

### 7.3 Configuration Integration

**Global Config:**
```toml
# config/hepilot.toml
[project]
name = "hepilot"
version = "0.1.0"

[database]
url = "postgresql+asyncpg://hep:hep@localhost/hepilot"

[embedding]
config_file = "config/embedding.toml"

[adapters]
output_dir = "adapters/*/*/output"
```

---

## 8. Testing Strategy

### 8.1 Unit Tests

**Coverage Requirements:** > 90%

**Test Categories:**
- Protocol compliance tests
- Adapter initialization tests
- Configuration validation tests
- Error handling tests
- Edge case tests

**Example Test Structure:**
```python
# tests/unit/embedding/test_encoder.py
@pytest.mark.asyncio
async def test_onnx_encoder_batch():
    encoder = ONNXBGEEncoder(config)
    texts = ["test1", "test2", "test3"]
    vectors = await encoder.embed(texts)
    assert vectors.shape == (3, 384)
    assert np.allclose(np.linalg.norm(vectors, axis=1), 1.0)

@pytest.mark.asyncio
async def test_encoder_determinism():
    encoder = ONNXBGEEncoder(config)
    text = "reproducible test"
    v1 = await encoder.embed([text])
    v2 = await encoder.embed([text])
    assert np.allclose(v1, v2)
```

### 8.2 Integration Tests

**Test Scenarios:**
1. **End-to-End Ingestion:**
   - Load sample adapter output
   - Process through pipeline
   - Verify database state
   - Verify vector store state
   - Check chunk count consistency

2. **Retrieval Accuracy:**
   - Ingest known chunks
   - Query with expected matches
   - Verify result ranking
   - Check metadata completeness

3. **Error Recovery:**
   - Simulate failures at each stage
   - Verify retry logic
   - Check partial completion handling
   - Validate rollback behavior

### 8.3 Performance Tests

**Benchmarks:**
```python
# tests/performance/test_throughput.py
def test_ingestion_throughput():
    # Measure chunks/second for 1000 chunks
    assert throughput > 1000  # chunks/minute

def test_query_latency():
    # Measure p95 latency for 100 queries
    assert p95_latency < 0.1  # seconds
```

### 8.4 Contract Tests

**Vector Store Contract:**
- Verify CRUD operations
- Check consistency guarantees
- Validate search results

**Decoder Contract:**
- Verify ID → content mapping
- Check metadata completeness
- Validate ordering preservation

---

## 9. Success Criteria

### 9.1 Functional Requirements

- [x] **F1:** All port interfaces defined and documented
- [ ] **F2:** At least one working adapter per component type
- [ ] **F3:** Full ingestion pipeline functional
- [ ] **F4:** Retrieval pipeline returns correct results
- [ ] **F5:** 100% traceability: every vector maps to source chunk
- [ ] **F6:** Database schema supports all required metadata
- [ ] **F7:** CLI tools for ingestion and search
- [ ] **F8:** Configuration-based adapter selection

### 9.2 Non-Functional Requirements

- [ ] **NF1:** > 90% test coverage
- [ ] **NF2:** < 100ms p95 query latency
- [ ] **NF3:** > 1000 chunks/minute ingestion rate
- [ ] **NF4:** < 2GB memory usage for 100K chunks
- [ ] **NF5:** Comprehensive logging and error messages
- [ ] **NF6:** Type hints and mypy compliance
- [ ] **NF7:** Documentation for all public APIs

### 9.3 Integration Requirements

- [ ] **I1:** Successfully ingest arxiv adapter output
- [ ] **I2:** Database migrations run cleanly
- [ ] **I3:** Health checks for all components
- [ ] **I4:** Graceful degradation on component failure
- [ ] **I5:** Configuration validation and error messages

### 9.4 Demonstration Scenarios

**Scenario 1: Ingest ArXiv Papers**
```bash
# Ingest adapter output
python -m hepilot.embedding ingest \
    --input adapters/arxiv_adapter/arxiv_output \
    --config config/embedding.toml

# Expected: All chunks in database and vector store
```

**Scenario 2: Semantic Search**
```bash
# Search for relevant chunks
python -m hepilot.embedding search \
    --query "quantum chromodynamics lattice calculations" \
    --top-k 10

# Expected: Ranked results with scores and full content
```

**Scenario 3: Health Check**
```bash
# Check system health
python -m hepilot.embedding health

# Expected: Status of encoder, vectordb, database
```

---

## 10. Timeline & Dependencies

### 10.1 Milestone Schedule

| Phase | Duration | Start | End | Dependencies |
|-------|----------|-------|-----|--------------|
| **Phase 1: Core Infrastructure** | 5 days | Day 1 | Day 5 | None |
| **Phase 2: PostgreSQL Layer** | 5 days | Day 3 | Day 7 | Phase 1 (partial) |
| **Phase 3: Encoder** | 5 days | Day 6 | Day 10 | Phase 1 |
| **Phase 4: Vector Store** | 5 days | Day 8 | Day 12 | Phase 1 |
| **Phase 5: Ingestion** | 5 days | Day 11 | Day 15 | Phases 2, 3, 4 |
| **Phase 6: Retrieval** | 5 days | Day 13 | Day 17 | Phases 2, 4 |
| **Phase 7: Integration** | 5 days | Day 16 | Day 20 | All phases |

**Total Duration:** ~4 weeks (20 working days)

### 10.2 Critical Path

1. Port definitions (Phase 1) → Blocks all adapter development
2. Database schema (Phase 2) → Blocks ingestion and retrieval
3. Encoder + VectorDB (Phases 3-4) → Blocks pipeline testing
4. Integration testing (Phase 7) → Validates entire system

### 10.3 Parallel Workstreams

**Week 1:**
- Stream A: Port interfaces + Registry
- Stream B: Database schema + Migrations

**Week 2:**
- Stream A: Encoder implementation
- Stream B: VectorDB implementation
- Stream C: DocStore + Decoder

**Week 3:**
- Stream A: Ingestion pipeline
- Stream B: Retrieval pipeline

**Week 4:**
- Integration testing
- Documentation
- Performance tuning

### 10.4 External Dependencies

| Dependency | Status | Impact | Mitigation |
|------------|--------|--------|------------|
| **PostgreSQL** | Available | CRITICAL | Use Docker for dev |
| **ONNX Runtime** | Available | HIGH | Pre-download models |
| **ChromaDB** | Available | HIGH | Fallback to Qdrant |
| **ArXiv Adapter** | ✅ Complete | HIGH | Already functional |
| **Future Adapters** | In Progress | MEDIUM | Design for compatibility |

---

## Next Steps

### Immediate Actions (This Week)

1. **Set up development environment:**
   ```bash
   # Create src directory structure
   mkdir -p src/embedding/adapters
   
   # Initialize poetry project
   cd src
   poetry init
   poetry add asyncpg chromadb onnxruntime transformers
   ```

2. **Create port definitions:**
   - Define Encoder, VectorDB, Decoder protocols
   - Document interface contracts
   - Add type hints

3. **Set up database:**
   - Create PostgreSQL database
   - Write Alembic migrations
   - Test schema creation

4. **Begin encoder implementation:**
   - Download BGE model
   - Implement ONNX wrapper
   - Write unit tests

### Review Points

- **End of Week 1:** Core interfaces + database schema review
- **End of Week 2:** Adapter implementations code review
- **End of Week 3:** Pipeline integration review
- **End of Week 4:** Final system demonstration

---

## Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| **Chunk** | Fixed-size text segment from document (512-4096 tokens) |
| **Embedding** | Dense vector representation of text (typically 384-1024 dimensions) |
| **Vector Store** | Database optimized for similarity search over embeddings |
| **DocStore** | Relational database storing original text content |
| **Encoder** | Model that transforms text to embeddings |
| **Decoder** | Component that retrieves original text from IDs |
| **Port** | Abstract interface (Python Protocol) |
| **Adapter** | Concrete implementation of a port |
| **Registry** | System for discovering and instantiating adapters |

### B. References

- [HEPilot Reference Architecture](./reference.md)
- [Data Acquisition Specification](../standards/README.md)
- [BGE Embeddings](https://huggingface.co/BAAI/bge-base-en-v1.5)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [ONNX Runtime](https://onnxruntime.ai/)

### C. Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-20 | 0.1 | Initial plan created |

---

**Status:** 📋 Planning Complete — Ready for Implementation  
**Next Milestone:** Phase 1 - Core Infrastructure  
**Owner:** Development Team  
**Reviewers:** Architecture Team

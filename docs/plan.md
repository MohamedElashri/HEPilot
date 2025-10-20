# HEPilot Embedding Layer Implementation Plan

**Version:** 1.4.0  
**Date:** October 20, 2025  
**Branch:** `embedding-dev`  
**Status:** 🚀 Steps 1-4 Complete - Encoder Implementation Next  
**Note:** Migration infrastructure moved to `src/embedding/` for better modularity

---

## Quick Navigation

- [What We Have](#what-we-have) - Current state
- [What We're Building](#what-were-building) - Goals and components
- [Step-by-Step Implementation](#step-by-step-implementation) - Detailed guide
- [Testing](#testing-strategy) - How to verify everything works
- [Progress Tracking](#progress-tracking) - Current status

---

## What We Have

### ✅ Completed Foundation

**Project Structure:**
```
src/embedding/
├── __init__.py               # ✅ Module exports with config classes
├── config.py                 # ✅ Configuration system
├── ports.py                  # ✅ Protocol interfaces defined
├── registry.py               # ✅ Adapter discovery system  
├── exceptions.py             # ✅ Custom exceptions (with DocStoreError)
├── README.md                 # ✅ Configuration documentation
├── alembic.ini               # ✅ Database migration config
├── alembic/                  # ✅ Database migrations
│   ├── env.py                # ✅ Migration environment
│   ├── README.md             # ✅ Migration documentation
│   └── versions/
│       └── 67906781f81e_*.py # ✅ Initial schema migration
├── adapters/
│   ├── db_models.py          # ✅ SQLAlchemy models
│   ├── postgres_docstore.py  # ✅ PostgreSQL DocStore
│   ├── postgres_decoder.py   # ✅ PostgreSQL Decoder (NEW)
│   └── __init__.py
└── examples/
    └── load_config.py        # ✅ Config usage example
```

**Configuration System:** ✅ COMPLETED
- `EncoderConfig` - Text encoder settings with validation
- `VectorDBConfig` - Vector database settings with validation
- `DocStoreConfig` - PostgreSQL settings with validation
- `PipelineConfig` - Ingestion pipeline settings
- `load_config()` - TOML configuration loader
- All validated with Pydantic (21 passing unit tests)

**Database Schema:** ✅ COMPLETED
- `documents` table - Paper/source metadata with JSONB fields
- `doc_segments` table - Text chunks with position tracking
- Alembic migrations with async support
- Self-contained in `src/embedding/alembic/`
- Complete upgrade/downgrade paths

**PostgreSQL DocStore:** ✅ COMPLETED
- Async PostgreSQL connection pooling with asyncpg
- Document CRUD operations with UPSERT support
- Chunk CRUD operations with batch insertion
- Transaction support for batch operations
- Health check and connection management
- Async context manager support
- 25 passing unit tests with comprehensive coverage

**PostgreSQL Decoder:** ✅ COMPLETED
- Async chunk retrieval by vector IDs
- Batch lookup with order preservation
- Document chunk retrieval with ordering
- JOIN queries for complete chunk metadata
- UUID validation and error handling
- Health check and connection management
- Async context manager support
- 22 passing unit tests with comprehensive coverage

**Port Interfaces Defined:**
- `Encoder` - Text → Vector transformation
- `VectorDB` - Vector storage and similarity search
- `Decoder` - Vector ID → Original text retrieval ✅ IMPLEMENTED

**Prerequisites Ready:**
- arXiv adapter producing chunk outputs
- Data format standards defined (JSON schemas)
- Architecture documented (reference.md)
- Dependencies identified (requirements*.txt)

---

## What We're Building

### The 7 Components

| Step | Component | Purpose | Complexity | Status |
|------|-----------|---------|------------|--------|
| 1 | **Configuration System** | Load/validate settings from TOML | Low | ✅ **DONE** |
| 2 | **Database Schema** | PostgreSQL tables for chunks/docs | Medium | ✅ **DONE** |
| 3 | **PostgreSQL DocStore** | Store original text chunks | Medium | ✅ **DONE** |
| 4 | **PostgreSQL Decoder** | Retrieve chunks by ID | Medium | ✅ **DONE** |
| 5 | **ONNX BGE Encoder** | Convert text to vectors | High | ⏭️ Next |
| 6 | **ChromaDB Adapter** | Store and search vectors | Medium | 📋 Pending |
| 7 | **Pipeline Orchestrator** | Coordinate ingestion/retrieval | High | 📋 Pending |

**Completed:** 4/7 steps (57%)  
**Estimated Remaining:** ~4 days

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  Adapter Output (chunks/*.md + metadata.json files)    │
└───────────────────┬─────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────────────┐
│  INGESTION PIPELINE                                       │
│  1. Read chunks from files                                │
│  2. Store in PostgreSQL (DocStore)                        │
│  3. Generate embeddings (Encoder)                         │
│  4. Store vectors in ChromaDB (VectorDB)                  │
└───────────────────────────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────────────┐
│  STORAGE LAYER                                            │
│  ┌──────────────────┐     ┌──────────────────┐           │
│  │  PostgreSQL      │     │  ChromaDB         │           │
│  │  • documents     │     │  • vectors (384d) │           │
│  │  • doc_segments  │     │  • chunk_id refs  │           │
│  └──────────────────┘     └──────────────────┘           │
└───────────────────────────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────────────┐
│  RETRIEVAL PIPELINE                                       │
│  1. Encode query (Encoder)                                │
│  2. Search vectors (VectorDB)                             │
│  3. Get chunk IDs + scores                                │
│  4. Lookup content (Decoder → PostgreSQL)                 │
│  5. Return ranked results                                 │
└───────────────────────────────────────────────────────────┘
```

### Database Schema

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
    UNIQUE(source_type, source_id)
);

-- Chunks table
CREATE TABLE doc_segments (
    id UUID PRIMARY KEY,
    doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    section_path JSONB,
    position_in_doc INTEGER NOT NULL,
    token_count INTEGER NOT NULL,
    overlap_start INTEGER NOT NULL,
    overlap_end INTEGER NOT NULL,
    meta JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_segments_doc_id ON doc_segments(doc_id);
CREATE INDEX idx_segments_position ON doc_segments(doc_id, position_in_doc);
CREATE INDEX idx_documents_source ON documents(source_type, source_id);
```

---

## Step-by-Step Implementation

### Step 1: Configuration System ⚙️ ✅ COMPLETED

**Goal:** Load and validate configuration from TOML files

**Status:** ✅ **COMPLETED** (October 20, 2025)

**Files Created:**
- ✅ `src/embedding/config.py` - Configuration classes with Pydantic validation
- ✅ `config/embedding.toml` - Default configuration file
- ✅ `tests/unit/embedding/test_config.py` - 21 passing unit tests
- ✅ `src/embedding/__init__.py` - Updated with exports
- ✅ `src/embedding/README.md` - Configuration documentation
- ✅ `src/embedding/examples/load_config.py` - Usage example

**What Was Implemented:**
- `EncoderConfig` - Text encoder settings (batch_size: 1-256, device: cpu/cuda)
- `VectorDBConfig` - Vector database settings (metric: cosine/l2/ip)
- `DocStoreConfig` - PostgreSQL settings with URL validation
- `PipelineConfig` - Pipeline settings (batch_size: 1-1000, workers: 1-32)
- `EmbeddingConfig` - Main configuration container
- `load_config()` - TOML loader with comprehensive validation

**Test Results:**
```
21 passed in 0.13s
```

**Usage Example:**
```python
from pathlib import Path
from src.embedding import load_config

config = load_config(Path("config/embedding.toml"))
print(f"Model: {config.encoder.model_name}")
print(f"Database: {config.docstore.database_url}")
```

**✅ Validation Checklist:**
- [x] Configuration loads without errors
- [x] Invalid values raise ValidationError
- [x] Default values work correctly
- [x] Unit tests pass (21/21)
- [x] No linting errors
- [x] Documentation complete

---

### Step 1 Implementation Details (Reference)

<details>
<summary><b>src/embedding/config.py</b> (click to view)</summary>

```python
"""Configuration management for embedding layer."""

from pydantic import BaseModel, Field, field_validator
from pathlib import Path
import tomllib
from typing import Optional


class EncoderConfig(BaseModel):
    """Text encoder configuration."""
    type: str = "onnx_bge"
    model_name: str = "BAAI/bge-base-en-v1.5"
    batch_size: int = Field(default=32, ge=1, le=256)
    device: str = Field(default="cpu", pattern="^(cpu|cuda)$")
    normalize: bool = True
    cache_dir: Path = Path(".cache/models")


class VectorDBConfig(BaseModel):
    """Vector database configuration."""
    type: str = "chroma"
    persist_directory: Path = Path(".data/chroma")
    collection_name: str = "hepilot"
    distance_metric: str = Field(default="cosine", pattern="^(cosine|l2|ip)$")


class DocStoreConfig(BaseModel):
    """Document storage configuration."""
    type: str = "postgres"
    database_url: str
    pool_size: int = Field(default=10, ge=1, le=100)
    max_overflow: int = Field(default=20, ge=0, le=100)
    
    @field_validator('database_url')
    @classmethod
    def validate_db_url(cls, v: str) -> str:
        """Ensure valid PostgreSQL URL."""
        if not v.startswith(('postgresql://', 'postgresql+asyncpg://')):
            raise ValueError("Database URL must start with postgresql:// or postgresql+asyncpg://")
        return v


class PipelineConfig(BaseModel):
    """Ingestion pipeline configuration."""
    batch_size: int = Field(default=100, ge=1, le=1000)
    max_workers: int = Field(default=4, ge=1, le=32)
    checkpoint_interval: int = Field(default=1000, ge=100)


class EmbeddingConfig(BaseModel):
    """Main embedding engine configuration."""
    encoder: EncoderConfig
    vectordb: VectorDBConfig
    docstore: DocStoreConfig
    pipeline: PipelineConfig


def load_config(config_path: Path) -> EmbeddingConfig:
    """Load configuration from TOML file."""
    with open(config_path, 'rb') as f:
        data = tomllib.load(f)
    return EmbeddingConfig(**data)
```
</details>

<details>
<summary><b>config/embedding.toml</b> (click to expand)</summary>

```toml
[encoder]
type = "onnx_bge"
model_name = "BAAI/bge-base-en-v1.5"
batch_size = 32
device = "cpu"
normalize = true
cache_dir = ".cache/models"

[vectordb]
type = "chroma"
persist_directory = ".data/chroma"
collection_name = "hepilot"
distance_metric = "cosine"

[docstore]
type = "postgres"
database_url = "postgresql+asyncpg://hep:hep@localhost/hepilot"
pool_size = 10
max_overflow = 20

[pipeline]
batch_size = 100
max_workers = 4
checkpoint_interval = 1000
```
</details>

---

### Step 2: Database Schema & Migrations 🗄️ ✅ COMPLETED

**Goal:** Create PostgreSQL schema with Alembic

**Status:** ✅ **COMPLETED** (October 20, 2025)

**Files Created:**
- ✅ `src/embedding/alembic.ini` - Alembic configuration
- ✅ `src/embedding/alembic/env.py` - Migration environment (configured with async support)
- ✅ `src/embedding/alembic/versions/67906781f81e_initial_schema_for_embedding_layer.py` - Initial migration
- ✅ `src/embedding/adapters/db_models.py` - SQLAlchemy models
- ✅ `src/embedding/alembic/README.md` - Migration documentation
- ✅ `tests/unit/embedding/test_migration.py` - Migration validation tests

**Migration Location:**
All migration infrastructure is self-contained within `src/embedding/` for better modularity and portability.

**What Was Implemented:**

**Database Tables:**
1. **`documents`** - Document metadata
   - Stores paper/source information
   - UUID primary key
   - Unique constraint on (source_type, source_id)
   - Index on source fields

2. **`doc_segments`** - Text chunks
   - Stores segmented text from documents
   - Foreign key to documents with CASCADE delete
   - Indexes on doc_id and (doc_id, position_in_doc)
   - JSONB columns for flexible metadata

**Migration Features:**
- Async-compatible (uses asyncpg driver)
- Loads database URL from `config/embedding.toml`
- Auto-imports models for autogenerate support
- Complete upgrade/downgrade paths

**Test Results:**
```
✅ All tests passed!
✓ Alembic imports successful
✓ Migration file syntax is valid
✓ upgrade() and downgrade() functions exist
✓ Database models imported successfully
  Tables: documents, doc_segments
```

**Usage:**
```bash
# When PostgreSQL is available (run from project root):
alembic -c src/embedding/alembic.ini upgrade head    # Apply migrations
alembic -c src/embedding/alembic.ini current         # Show current version
alembic -c src/embedding/alembic.ini downgrade -1    # Rollback one version
```

**✅ Validation Checklist:**
- [x] Alembic initialized with async template
- [x] Migration file created with complete schema
- [x] SQLAlchemy models defined
- [x] Migration syntax validated
- [x] Documentation complete
- [x] Ready for database application (when PostgreSQL available)

---

### Step 2 Implementation Details (Reference)

<details>
<summary><b>Database Schema SQL</b> (click to view)</summary>

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
    meta JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_documents_source UNIQUE (source_type, source_id)
);

-- Doc segments table
CREATE TABLE doc_segments (
    id UUID PRIMARY KEY,
    doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    section_path JSONB,
    position_in_doc INTEGER NOT NULL,
    token_count INTEGER NOT NULL,
    overlap_start INTEGER NOT NULL,
    overlap_end INTEGER NOT NULL,
    meta JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_segments_doc_id ON doc_segments(doc_id);
CREATE INDEX idx_segments_position ON doc_segments(doc_id, position_in_doc);
CREATE INDEX idx_documents_source ON documents(source_type, source_id);
```
</details>

---

### Step 3: PostgreSQL DocStore 💾 ✅ COMPLETED

**Goal:** Implement document and chunk storage

**Status:** ✅ **COMPLETED** (October 20, 2025)

**Files Created:**
- ✅ `src/embedding/adapters/postgres_docstore.py` - PostgreSQL DocStore implementation
- ✅ `tests/unit/embedding/test_docstore.py` - 25 passing unit tests
- ✅ `src/embedding/exceptions.py` - Updated with DocStoreError exception

**What Was Implemented:**
- `PostgresDocStore` class with async connection pooling using asyncpg
- Document operations:
  - `add_document()` - UPSERT document with optional metadata
  - `get_document()` - Retrieve document by ID with JSON parsing
  - `delete_document()` - Delete document and cascading chunks
  - `count_documents()` - Get total document count
- Chunk operations:
  - `add_chunk()` - Insert single chunk with position tracking
  - `add_chunks_batch()` - Batch insert with transactions
  - `get_chunk()` - Retrieve chunk by ID
  - `get_document_chunks()` - Get all chunks for a document
  - `count_chunks()` - Get total chunk count
- Connection management:
  - `connect()` - Initialize connection pool
  - `close()` - Close connection pool
  - `health_check()` - Verify database connectivity
  - Async context manager support (`async with`)

**Test Results:**
```
25 passed in 0.18s
```

**Test Coverage:**
- Initialization and configuration
- Connection lifecycle management
- Document CRUD operations (add, get, delete)
- Chunk CRUD operations (add, batch add, get, get all)
- Error handling (not connected, database errors)
- Health checks (healthy, unhealthy, not connected)
- Async context manager protocol
- Count operations (documents and chunks)

**✅ Validation Checklist:**
- [x] PostgresDocStore class implemented
- [x] All CRUD methods working
- [x] Batch operations with transactions
- [x] Connection pooling configured
- [x] Health check functionality
- [x] Async context manager support
- [x] Unit tests pass (25/25)
- [x] No linting errors
- [x] Comprehensive error handling

---

### Step 3 Implementation Reference (COMPLETED)

<details>
<summary><b>Key Implementation Details</b> (click to view)</summary>

**Connection Management:**
```python
async def connect(self) -> None:
    """Initialize connection pool."""
    if self.pool:
        return
    self.pool = await asyncpg.create_pool(
        dsn=self.database_url,
        min_size=self.pool_size // 2,
        max_size=self.pool_size
    )
```

**UPSERT Document:**
```python
async def add_document(self, doc_id: UUID, source_type: str, source_id: str, ...) -> UUID:
    """Add or update document with ON CONFLICT DO UPDATE."""
    query = """
    INSERT INTO documents (id, source_type, source_id, ...)
    VALUES ($1, $2, $3, ...)
    ON CONFLICT (source_type, source_id)
    DO UPDATE SET ...
    RETURNING id
    """
    return await conn.fetchval(query, ...)
```

**Batch Insert with Transaction:**
```python
async def add_chunks_batch(self, chunks: List[Dict[str, Any]]) -> int:
    """Insert multiple chunks in a transaction."""
    async with self.pool.acquire() as conn:
        async with conn.transaction():
            for chunk in chunks:
                await conn.execute(query, ...)
    return len(chunks)
```

**Async Context Manager:**
```python
async def __aenter__(self):
    await self.connect()
    return self

async def __aexit__(self, exc_type, exc_val, exc_tb):
    await self.close()
```

</details>

---

### Step 3: PostgreSQL DocStore 💾 (OLD - FOR REFERENCE)

**Goal:** Implement document and chunk storage

**Files to create:**
- `alembic.ini`
- `alembic/env.py`
- `alembic/versions/001_initial_schema.py`
- `src/embedding/adapters/db_models.py`

**Setup Instructions:**

```bash
# Initialize Alembic
cd /data/home/melashri/LLM/HEPilot
alembic init alembic

# Edit alembic.ini to set database URL
# sqlalchemy.url = postgresql+asyncpg://hep:hep@localhost/hepilot
```

<details>
<summary><b>alembic/versions/001_initial_schema.py</b> (click to expand)</summary>

```python
"""Initial schema for embedding layer

Revision ID: 001
Create Date: 2025-10-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('source_id', sa.String(500), nullable=False),
        sa.Column('title', sa.Text),
        sa.Column('authors', postgresql.JSONB),
        sa.Column('publication_date', sa.TIMESTAMP),
        sa.Column('source_url', sa.Text),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now())
    )
    
    # Create doc_segments table
    op.create_table(
        'doc_segments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('doc_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('section_path', postgresql.JSONB),
        sa.Column('position_in_doc', sa.Integer, nullable=False),
        sa.Column('token_count', sa.Integer, nullable=False),
        sa.Column('overlap_start', sa.Integer, nullable=False),
        sa.Column('overlap_end', sa.Integer, nullable=False),
        sa.Column('meta', postgresql.JSONB),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['doc_id'], ['documents.id'], ondelete='CASCADE')
    )
    
    # Create indexes
    op.create_index('idx_segments_doc_id', 'doc_segments', ['doc_id'])
    op.create_index('idx_segments_position', 'doc_segments', ['doc_id', 'position_in_doc'])
    op.create_index('idx_documents_source', 'documents', ['source_type', 'source_id'])
    
    # Create unique constraint
    op.create_unique_constraint('uq_documents_source', 'documents', ['source_type', 'source_id'])


def downgrade():
    op.drop_table('doc_segments')
    op.drop_table('documents')
```
</details>

**Run Migration:**
```bash
# Apply migration
alembic upgrade head

# Verify tables created
psql -h localhost -U hep hepilot -c "\dt"
```

**✅ Validation Checklist:**
- [ ] `alembic upgrade head` succeeds
- [ ] Tables `documents` and `doc_segments` exist
- [ ] Indexes created
- [ ] `alembic downgrade base` works

---

### Step 3: PostgreSQL DocStore 💾

**Goal:** Implement document and chunk storage

**File to create:**
- `src/embedding/adapters/postgres_docstore.py`
- `tests/unit/embedding/test_docstore.py`

<details>
<summary><b>src/embedding/adapters/postgres_docstore.py</b> (click to expand)</summary>

```python
"""PostgreSQL-based document storage."""

import asyncpg
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
import json

from src.embedding.exceptions import DocStoreError


class PostgresDocStore:
    """Store documents and chunks in PostgreSQL."""
    
    def __init__(self, database_url: str, pool_size: int = 10):
        self.database_url = database_url
        self.pool_size = pool_size
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Establish database connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=self.pool_size
            )
        except Exception as e:
            raise DocStoreError(f"Failed to connect to database: {e}")
    
    async def close(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
    
    async def add_document(
        self,
        doc_id: UUID,
        source_type: str,
        source_id: str,
        title: Optional[str] = None,
        authors: Optional[List[Dict]] = None,
        publication_date: Optional[datetime] = None,
        source_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """Insert or update a document."""
        query = """
        INSERT INTO documents (id, source_type, source_id, title, authors, 
                              publication_date, source_url, metadata)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (source_type, source_id) 
        DO UPDATE SET 
            title = EXCLUDED.title,
            authors = EXCLUDED.authors,
            publication_date = EXCLUDED.publication_date,
            source_url = EXCLUDED.source_url,
            metadata = EXCLUDED.metadata
        RETURNING id
        """
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval(
                    query,
                    doc_id,
                    source_type,
                    source_id,
                    title,
                    json.dumps(authors) if authors else None,
                    publication_date,
                    source_url,
                    json.dumps(metadata) if metadata else None
                )
            return result
        except Exception as e:
            raise DocStoreError(f"Failed to add document: {e}")
    
    async def add_chunk(
        self,
        chunk_id: UUID,
        doc_id: UUID,
        text: str,
        position: int,
        token_count: int,
        section_path: Optional[List[str]] = None,
        overlap_start: int = 0,
        overlap_end: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """Insert a text chunk."""
        query = """
        INSERT INTO doc_segments (id, doc_id, text, section_path, position_in_doc,
                                 token_count, overlap_start, overlap_end, meta)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING id
        """
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval(
                    query,
                    chunk_id,
                    doc_id,
                    text,
                    json.dumps(section_path) if section_path else None,
                    position,
                    token_count,
                    overlap_start,
                    overlap_end,
                    json.dumps(metadata) if metadata else None
                )
            return result
        except Exception as e:
            raise DocStoreError(f"Failed to add chunk: {e}")
    
    async def health_check(self) -> bool:
        """Check if database connection is healthy."""
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception:
            return False
```
</details>

**✅ Validation Checklist:**
- [ ] Can connect to PostgreSQL
- [ ] Can insert documents
- [ ] Can insert chunks
- [ ] Upsert works (ON CONFLICT)
- [ ] Health check works
- [ ] Unit tests pass

---

---

### Step 4: PostgreSQL Decoder 🔍 ✅ COMPLETED

**Goal:** Retrieve chunks by ID from database

**Status:** ✅ **COMPLETED** (October 20, 2025)

**Files Created:**
- ✅ `src/embedding/adapters/postgres_decoder.py` - PostgreSQL Decoder implementation
- ✅ `tests/unit/embedding/test_decoder.py` - 22 passing unit tests

**What Was Implemented:**
- `PostgresDecoder` class with async connection pooling using asyncpg
- Chunk lookup operations:
  - `lookup()` - Batch retrieve chunks by UUIDs with order preservation
  - Returns List[Optional[ChunkContent]] maintaining input order
  - Handles missing chunks gracefully (returns None in position)
  - Validates UUID format with clear error messages
- Document operations:
  - `get_document_chunks()` - Retrieve all chunks for a document
  - Returns chunks ordered by position_in_doc
  - Optional limit parameter for pagination
- Connection management:
  - `connect()` - Initialize connection pool
  - `close()` - Close connection pool
  - `health_check()` - Verify database connectivity
  - Async context manager support (`async with`)
- Data transformation:
  - `_row_to_chunk_content()` - Convert DB rows to ChunkContent dataclass
  - JOIN queries combining doc_segments + documents tables
  - JSON parsing for section_path and metadata
  - Complete metadata inclusion (chunk + document metadata)

**Test Results:**
```
22 passed in 0.64s
```

**Test Coverage:**
- Initialization and configuration
- Connection lifecycle management
- Lookup operations (single, multiple, missing chunks)
- Empty list and invalid UUID handling
- get_document_chunks (success, with limit, empty results)
- Error handling (not connected, database errors, invalid UUIDs)
- Health checks (healthy, unhealthy, not connected)
- Async context manager protocol

**Key Features:**
- **Order Preservation**: lookup() maintains input chunk_ids order
- **Graceful Degradation**: Missing chunks return None (not error)
- **Complete Metadata**: JOINs documents table for full context
- **UUID Validation**: Clear errors for malformed IDs
- **Efficient Batching**: Uses PostgreSQL ANY() for batch lookups

**✅ Validation Checklist:**
- [x] PostgresDecoder class implemented
- [x] lookup() method with order preservation
- [x] get_document_chunks() with sorting
- [x] Connection pooling configured
- [x] Health check functionality
- [x] Async context manager support
- [x] Unit tests pass (22/22)
- [x] No linting errors
- [x] Comprehensive error handling
- [x] UUID validation
- [x] JSON metadata parsing

---

### Step 4 Implementation Reference (COMPLETED)

<details>
<summary><b>Key Implementation Details</b> (click to view)</summary>

**Batch Lookup with Order Preservation:**
```python
async def lookup(self, chunk_ids: List[str]) -> List[Optional[ChunkContent]]:
    """Retrieve chunks maintaining input order."""
    # Query with ANY for efficiency
    query = "SELECT ... FROM doc_segments s JOIN documents d ... WHERE s.id = ANY($1::uuid[])"
    
    async with self.pool.acquire() as conn:
        rows = await conn.fetch(query, uuid_ids)
        
        # Create mapping for quick lookup
        row_map = {str(row['id']): row for row in rows}
        
        # Build result maintaining input order
        results = []
        for chunk_id in chunk_ids:
            row = row_map.get(chunk_id)
            if row is None:
                results.append(None)  # Missing chunk
            else:
                results.append(self._row_to_chunk_content(row))
    
    return results
```

**Document Chunks with Ordering:**
```python
async def get_document_chunks(self, document_id: str, limit: Optional[int] = None):
    """Get all chunks for a document, ordered by position."""
    query = """
    SELECT ... FROM doc_segments s
    JOIN documents d ON s.doc_id = d.id
    WHERE s.doc_id = $1
    ORDER BY s.position_in_doc ASC
    """
    if limit:
        query += f" LIMIT {int(limit)}"
    
    async with self.pool.acquire() as conn:
        rows = await conn.fetch(query, doc_uuid)
        return [self._row_to_chunk_content(row) for row in rows]
```

**ChunkContent Transformation:**
```python
def _row_to_chunk_content(self, row: asyncpg.Record) -> ChunkContent:
    """Convert DB row to ChunkContent with full metadata."""
    section_path = json.loads(row['section_path']) if row['section_path'] else []
    chunk_meta = json.loads(row['meta']) if row['meta'] else {}
    doc_meta = json.loads(row['doc_meta']) if row['doc_meta'] else {}
    
    additional_metadata = {
        'chunk_metadata': chunk_meta,
        'document_metadata': doc_meta,
        'title': row['title'],
        'authors': json.loads(row['authors']) if row['authors'] else [],
        # ... more fields
    }
    
    return ChunkContent(chunk_id=str(row['id']), text=row['text'], ...)
```

</details>

---

### Step 4: PostgreSQL Decoder 🔍 (OLD - FOR REFERENCE)

**Goal:** Retrieve chunks by ID from database

**File to create:**
- `src/embedding/adapters/postgres_decoder.py`
- `tests/unit/embedding/test_decoder.py`

<details>
<summary><b>src/embedding/adapters/postgres_decoder.py</b> (click to expand)</summary>

```python
"""Retrieve original content from PostgreSQL."""

import asyncpg
from typing import List, Optional
from uuid import UUID
import json

from src.embedding.ports import ChunkContent
from src.embedding.exceptions import DecoderError


class PostgresDecoder:
    """Decode vector IDs to original text content."""
    
    def __init__(self, database_url: str, pool_size: int = 10):
        self.database_url = database_url
        self.pool_size = pool_size
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Establish database connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=self.pool_size
            )
        except Exception as e:
            raise DecoderError(f"Failed to connect to database: {e}")
    
    async def lookup(self, chunk_ids: List[str]) -> List[Optional[ChunkContent]]:
        """Retrieve chunks by IDs, maintaining order."""
        query = """
        SELECT 
            s.id::text as chunk_id,
            s.text,
            s.doc_id::text as document_id,
            d.source_type,
            s.section_path,
            s.position_in_doc,
            s.token_count,
            s.overlap_start,
            s.overlap_end,
            d.source_url,
            s.created_at,
            s.meta
        FROM doc_segments s
        JOIN documents d ON s.doc_id = d.id
        WHERE s.id = ANY($1::uuid[])
        """
        
        try:
            # Convert string IDs to UUIDs
            uuids = [UUID(cid) for cid in chunk_ids]
            
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, uuids)
            
            # Create lookup map
            results_map = {}
            for row in rows:
                section_path = json.loads(row['section_path']) if row['section_path'] else []
                meta = json.loads(row['meta']) if row['meta'] else {}
                
                chunk_content = ChunkContent(
                    chunk_id=row['chunk_id'],
                    text=row['text'],
                    document_id=row['document_id'],
                    source_type=row['source_type'],
                    section_path=section_path,
                    position_in_doc=row['position_in_doc'],
                    token_count=row['token_count'],
                    overlap_start=row['overlap_start'],
                    overlap_end=row['overlap_end'],
                    source_url=row['source_url'] or "",
                    created_at=str(row['created_at']),
                    additional_metadata=meta
                )
                results_map[row['chunk_id']] = chunk_content
            
            # Return in same order as input, None for missing
            return [results_map.get(cid) for cid in chunk_ids]
            
        except Exception as e:
            raise DecoderError(f"Failed to lookup chunks: {e}")
    
    async def get_document_chunks(
        self,
        document_id: str,
        limit: Optional[int] = None
    ) -> List[ChunkContent]:
        """Get all chunks for a document."""
        query = """
        SELECT 
            s.id::text as chunk_id,
            s.text,
            s.doc_id::text as document_id,
            d.source_type,
            s.section_path,
            s.position_in_doc,
            s.token_count,
            s.overlap_start,
            s.overlap_end,
            d.source_url,
            s.created_at,
            s.meta
        FROM doc_segments s
        JOIN documents d ON s.doc_id = d.id
        WHERE s.doc_id = $1
        ORDER BY s.position_in_doc
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, UUID(document_id))
            
            return [
                ChunkContent(
                    chunk_id=row['chunk_id'],
                    text=row['text'],
                    document_id=row['document_id'],
                    source_type=row['source_type'],
                    section_path=json.loads(row['section_path']) if row['section_path'] else [],
                    position_in_doc=row['position_in_doc'],
                    token_count=row['token_count'],
                    overlap_start=row['overlap_start'],
                    overlap_end=row['overlap_end'],
                    source_url=row['source_url'] or "",
                    created_at=str(row['created_at']),
                    additional_metadata=json.loads(row['meta']) if row['meta'] else {}
                )
                for row in rows
            ]
            
        except Exception as e:
            raise DecoderError(f"Failed to get document chunks: {e}")
    
    async def health_check(self) -> bool:
        """Check database connection."""
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception:
            return False
```
</details>

**✅ Validation Checklist:**
- [ ] Can retrieve chunks by ID
- [ ] Batch retrieval works
- [ ] Returns None for missing IDs
- [ ] Order preserved
- [ ] Document chunks retrieval works
- [ ] Tests pass

---

### Step 5: ONNX BGE Encoder 🧮

**Goal:** Convert text to embeddings using BGE model

**File to create:**
- `src/embedding/adapters/onnx_bge_encoder.py`
- `tests/unit/embedding/test_encoder.py`

<details>
<summary><b>src/embedding/adapters/onnx_bge_encoder.py</b> (click to expand)</summary>

```python
"""ONNX-based BGE encoder for text embeddings."""

import numpy as np
from numpy.typing import NDArray
from typing import List
from pathlib import Path
from sentence_transformers import SentenceTransformer

from src.embedding.exceptions import EncoderError


class ONNXBGEEncoder:
    """BGE encoder using SentenceTransformers."""
    
    def __init__(
        self,
        model_name: str = "BAAI/bge-base-en-v1.5",
        cache_dir: Path = Path(".cache/models"),
        batch_size: int = 32,
        normalize: bool = True
    ):
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.batch_size = batch_size
        self.normalize = normalize
        
        self.model = None
        self._dimension = 384  # BGE-base dimension
        self._max_tokens = 512
    
    async def setup(self):
        """Initialize model."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
            self.model = SentenceTransformer(
                self.model_name,
                cache_folder=str(self.cache_dir)
            )
            
        except Exception as e:
            raise EncoderError(f"Failed to load encoder: {e}")
    
    async def embed(self, texts: List[str]) -> NDArray[np.float32]:
        """Encode texts to vectors."""
        if not self.model:
            await self.setup()
        
        try:
            # Encode in batches
            all_embeddings = []
            for i in range(0, len(texts), self.batch_size):
                batch = texts[i:i + self.batch_size]
                embeddings = self.model.encode(
                    batch,
                    normalize_embeddings=self.normalize,
                    show_progress_bar=False,
                    convert_to_numpy=True
                )
                all_embeddings.append(embeddings)
            
            # Combine batches
            result = np.vstack(all_embeddings).astype(np.float32)
            return result
            
        except Exception as e:
            raise EncoderError(f"Encoding failed: {e}")
    
    @property
    def dimension(self) -> int:
        """Embedding dimension."""
        return self._dimension
    
    @property
    def max_tokens(self) -> int:
        """Maximum token length."""
        return self._max_tokens
    
    async def health_check(self) -> bool:
        """Verify encoder is operational."""
        try:
            if not self.model:
                await self.setup()
            test_vec = await self.embed(["test"])
            return test_vec.shape == (1, self._dimension)
        except Exception:
            return False
```
</details>

**✅ Validation Checklist:**
- [ ] Model downloads successfully
- [ ] Can encode single text
- [ ] Can encode batch
- [ ] Vectors are normalized (if enabled)
- [ ] Dimension is correct (384)
- [ ] Health check works
- [ ] Tests pass

---

### Step 6: ChromaDB Adapter 🗂️

**Goal:** Store and search vectors in ChromaDB

**File to create:**
- `src/embedding/adapters/chroma_vectordb.py`
- `tests/unit/embedding/test_vectordb.py`

<details>
<summary><b>src/embedding/adapters/chroma_vectordb.py</b> (click to expand)</summary>

```python
"""ChromaDB-based vector storage."""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import numpy as np
from numpy.typing import NDArray
from pathlib import Path

from src.embedding.ports import QueryResult
from src.embedding.exceptions import VectorDBError


class ChromaVectorDB:
    """Vector storage using ChromaDB."""
    
    def __init__(
        self,
        persist_directory: Path = Path(".data/chroma"),
        collection_name: str = "hepilot",
        distance_metric: str = "cosine"
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.distance_metric = distance_metric
        
        self.client = None
        self.collection = None
    
    async def setup(self):
        """Initialize ChromaDB client and collection."""
        try:
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=False
                )
            )
            
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": self.distance_metric}
            )
            
        except Exception as e:
            raise VectorDBError(f"Failed to initialize ChromaDB: {e}")
    
    async def upsert(
        self,
        ids: List[str],
        vectors: NDArray[np.float32],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Insert or update vectors."""
        if not self.collection:
            await self.setup()
        
        try:
            embeddings = vectors.tolist()
            
            if metadata is None:
                metadata = [{} for _ in ids]
            
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadata
            )
            
        except Exception as e:
            raise VectorDBError(f"Upsert failed: {e}")
    
    async def query(
        self,
        vector: NDArray[np.float32],
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[QueryResult]:
        """Find most similar vectors."""
        if not self.collection:
            await self.setup()
        
        try:
            results = self.collection.query(
                query_embeddings=[vector.tolist()],
                n_results=top_k,
                where=filter_dict
            )
            
            query_results = []
            if results['ids'] and results['ids'][0]:
                for i, chunk_id in enumerate(results['ids'][0]):
                    # Convert distance to similarity score
                    distance = results['distances'][0][i] if results['distances'] else 0
                    score = 1.0 - distance if self.distance_metric == "cosine" else distance
                    
                    query_results.append(QueryResult(
                        chunk_id=chunk_id,
                        score=score,
                        metadata=results['metadatas'][0][i] if results['metadatas'] else {}
                    ))
            
            return query_results
            
        except Exception as e:
            raise VectorDBError(f"Query failed: {e}")
    
    async def delete(self, ids: List[str]) -> None:
        """Remove vectors by ID."""
        if not self.collection:
            await self.setup()
        
        try:
            self.collection.delete(ids=ids)
        except Exception as e:
            raise VectorDBError(f"Delete failed: {e}")
    
    async def count(self) -> int:
        """Total number of vectors."""
        if not self.collection:
            await self.setup()
        
        try:
            return self.collection.count()
        except Exception as e:
            raise VectorDBError(f"Count failed: {e}")
    
    async def health_check(self) -> bool:
        """Verify vector store is operational."""
        try:
            if not self.collection:
                await self.setup()
            await self.count()
            return True
        except Exception:
            return False
```
</details>

**✅ Validation Checklist:**
- [ ] ChromaDB initializes
- [ ] Collection created
- [ ] Can upsert vectors
- [ ] Can query vectors
- [ ] Can delete vectors
- [ ] Count works
- [ ] Tests pass

---

### Step 7: Pipeline & CLI 🔄

**Goal:** Tie everything together with ingestion/retrieval pipelines

**Files to create:**
- `src/embedding/pipeline.py`
- `src/embedding/cli.py`
- `tests/integration/embedding/test_pipeline.py`

<details>
<summary><b>src/embedding/pipeline.py</b> (basic structure)</summary>

```python
"""Ingestion and retrieval pipelines."""

from pathlib import Path
from typing import Dict, Any, List
import json
from uuid import UUID
from tqdm import tqdm

from src.embedding.config import EmbeddingConfig
from src.embedding.adapters.postgres_docstore import PostgresDocStore
from src.embedding.adapters.postgres_decoder import PostgresDecoder
from src.embedding.adapters.onnx_bge_encoder import ONNXBGEEncoder
from src.embedding.adapters.chroma_vectordb import ChromaVectorDB


class IngestionPipeline:
    """Ingest documents from adapter output."""
    
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.docstore = PostgresDocStore(
            config.docstore.database_url,
            config.docstore.pool_size
        )
        self.encoder = ONNXBGEEncoder(
            model_name=config.encoder.model_name,
            cache_dir=config.encoder.cache_dir,
            batch_size=config.encoder.batch_size,
            normalize=config.encoder.normalize
        )
        self.vectordb = ChromaVectorDB(
            persist_directory=config.vectordb.persist_directory,
            collection_name=config.vectordb.collection_name,
            distance_metric=config.vectordb.distance_metric
        )
    
    async def setup(self):
        """Initialize all components."""
        await self.docstore.connect()
        await self.encoder.setup()
        await self.vectordb.setup()
    
    async def ingest_directory(self, output_dir: Path) -> Dict[str, Any]:
        """Ingest all documents from adapter output."""
        await self.setup()
        
        # Read catalog
        catalog_path = output_dir / "catalog.json"
        with open(catalog_path) as f:
            catalog = json.load(f)
        
        stats = {
            'documents_processed': 0,
            'chunks_processed': 0,
            'vectors_created': 0
        }
        
        # Process each document
        for doc_entry in tqdm(catalog.get('documents', []), desc="Processing documents"):
            # Implementation continues...
            # (Read chunks, store in DB, generate embeddings, etc.)
            pass
        
        return stats


class RetrievalPipeline:
    """Search and retrieve documents."""
    
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.encoder = ONNXBGEEncoder(
            model_name=config.encoder.model_name,
            cache_dir=config.encoder.cache_dir
        )
        self.vectordb = ChromaVectorDB(
            persist_directory=config.vectordb.persist_directory,
            collection_name=config.vectordb.collection_name
        )
        self.decoder = PostgresDecoder(
            database_url=config.docstore.database_url,
            pool_size=config.docstore.pool_size
        )
    
    async def setup(self):
        """Initialize components."""
        await self.encoder.setup()
        await self.vectordb.setup()
        await self.decoder.connect()
    
    async def search(self, query: str, top_k: int = 10):
        """Semantic search."""
        await self.setup()
        
        # Encode query
        query_vector = await self.encoder.embed([query])
        
        # Search vectors
        results = await self.vectordb.query(query_vector[0], top_k)
        
        # Retrieve full content
        chunk_ids = [r.chunk_id for r in results]
        chunks = await self.decoder.lookup(chunk_ids)
        
        # Combine results
        return [(chunk, result.score) for chunk, result in zip(chunks, results) if chunk]
```
</details>

<details>
<summary><b>src/embedding/cli.py</b> (basic structure)</summary>

```python
"""Command-line interface for embedding engine."""

import typer
import asyncio
from pathlib import Path
from rich.console import Console

from src.embedding.config import load_config
from src.embedding.pipeline import IngestionPipeline, RetrievalPipeline

app = typer.Typer()
console = Console()


@app.command()
def ingest(
    input_dir: Path = typer.Argument(..., help="Adapter output directory"),
    config_file: Path = typer.Option("config/embedding.toml", help="Config file")
):
    """Ingest documents from adapter output."""
    console.print(f"[bold]Loading config from {config_file}...[/bold]")
    config = load_config(config_file)
    
    console.print(f"[bold]Ingesting from {input_dir}...[/bold]")
    pipeline = IngestionPipeline(config)
    
    stats = asyncio.run(pipeline.ingest_directory(input_dir))
    
    console.print("\n[bold green]✓ Complete![/bold green]")
    console.print(f"Documents: {stats['documents_processed']}")
    console.print(f"Chunks: {stats['chunks_processed']}")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    top_k: int = typer.Option(10, help="Number of results"),
    config_file: Path = typer.Option("config/embedding.toml")
):
    """Search for relevant chunks."""
    config = load_config(config_file)
    pipeline = RetrievalPipeline(config)
    
    results = asyncio.run(pipeline.search(query, top_k))
    
    console.print(f"\n[bold]Results for: {query}[/bold]\n")
    for i, (chunk, score) in enumerate(results, 1):
        console.print(f"{i}. [cyan]Score: {score:.3f}[/cyan]")
        console.print(f"   {chunk.text[:200]}...")
        console.print()


if __name__ == "__main__":
    app()
```
</details>

**Usage:**
```bash
# Ingest
python -m src.embedding.cli ingest src/collector/adapters/arxiv/arxiv_output

# Search
python -m src.embedding.cli search "quantum chromodynamics" --top-k 5
```

**✅ Validation Checklist:**
- [ ] Can read adapter output
- [ ] Ingestion works end-to-end
- [ ] Retrieval works end-to-end
- [ ] CLI commands work
- [ ] Integration tests pass

---

## Testing Strategy

### Unit Tests

**Test each component in isolation:**

```
tests/unit/embedding/
├── test_config.py          # Config loading/validation
├── test_docstore.py        # Database operations (mocked DB)
├── test_decoder.py         # Chunk retrieval (mocked DB)
├── test_encoder.py         # Embedding generation
├── test_vectordb.py        # Vector operations (mocked ChromaDB)
└── test_pipeline.py        # Pipeline logic (all mocked)
```

**Run unit tests:**
```bash
pytest tests/unit/embedding/ -v
```

### Integration Tests

**Test with real databases:**

```bash
# Start test database
docker run -d --name hepilot-test-db \
  -e POSTGRES_PASSWORD=test \
  -e POSTGRES_DB=hepilot_test \
  -p 5433:5432 \
  postgres:15

# Run integration tests
pytest tests/integration/embedding/ -v
```

### Performance Tests

**Benchmark key operations:**
- Encoding speed (chunks/second)
- Ingestion throughput
- Query latency (p50, p95, p99)

---

## Progress Tracking

### Current Status

**Phase 0: Foundation** ✅ COMPLETED
- [x] Project structure
- [x] Port interfaces
- [x] Registry system
- [x] Exception classes
- [x] Documentation

**Phase 1: Core Components** 🚧 IN PROGRESS (This Week)
- [x] **Step 1: Configuration system** ✅ COMPLETED (Oct 20, 2025)
  - [x] Created `src/embedding/config.py` with Pydantic models
  - [x] Created `config/embedding.toml` with defaults
  - [x] Wrote 21 passing unit tests
  - [x] Updated module exports and documentation
- [x] **Step 2: Database schema** ✅ COMPLETED (Oct 20, 2025)
  - [x] Initialized Alembic with async support
  - [x] Created SQLAlchemy models for documents and doc_segments
  - [x] Generated initial migration script
  - [x] Validated migration syntax and structure
  - [x] Created migration documentation
- [x] **Step 3: PostgreSQL DocStore** ✅ COMPLETED (Oct 20, 2025)
  - [x] Implemented `PostgresDocStore` with async connection pooling
  - [x] Created document CRUD operations (add, get, delete, count)
  - [x] Created chunk CRUD operations (add, batch add, get, get all, count)
  - [x] Implemented connection management and health checks
  - [x] Added async context manager support
  - [x] Wrote 25 passing unit tests with comprehensive coverage
- [x] **Step 4: PostgreSQL Decoder** ✅ COMPLETED (Oct 20, 2025)
  - [x] Implemented `PostgresDecoder` with async connection pooling
  - [x] Created lookup() method with order preservation
  - [x] Created get_document_chunks() method with sorting
  - [x] Implemented JOIN queries for complete metadata
  - [x] Added UUID validation and error handling
  - [x] Wrote 22 passing unit tests with comprehensive coverage

**Phase 2: ML Components** 📋 PENDING (Next Week)
- [ ] Step 5: ONNX BGE Encoder ⏭️ NEXT
- [ ] Step 6: ChromaDB Adapter

**Phase 3: Integration** 📋 PENDING (Week After)
- [ ] Step 7: Pipeline Orchestrator
- [ ] Step 8: CLI Interface
- [ ] Integration testing

**Progress:** 2/7 steps complete (29%)

### Next Immediate Actions

**Next (Step 3):**
1. Create `src/embedding/adapters/postgres_docstore.py`
2. Implement document and chunk storage methods
3. Write unit tests for DocStore
4. Test with real database connection

**Today's Accomplishments:**
- ✅ Completed Step 2: Database Schema & Migrations
- ✅ Created Alembic migrations with async support
- ✅ Defined SQLAlchemy models for documents and segments
- ✅ Validated migration syntax
- ✅ Created comprehensive documentation

**This Week Goal:**
1. Complete Steps 2-4 (Database + DocStore + Decoder)
2. Full database integration tested
3. Ready for ML components next week

**Blockers:** None currently

---

## Quick Commands Reference

```bash
# Setup environment
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uv pip install -r requirements-embedding.txt
uv pip install -r requirements-dev.txt

# Database migrations
alembic upgrade head
alembic downgrade -1

# Run tests
pytest tests/unit/embedding/ -v
pytest tests/integration/embedding/ -v

# Ingest documents
python -m src.embedding.cli ingest <output_dir>

# Search
python -m src.embedding.cli search "query" --top-k 10

# Format code
ruff format src/
ruff check src/

# Type checking
mypy src/embedding/
```

---

## Summary

This plan provides:
- ✅ Clear **7-step implementation path**
- ✅ **Complete code examples** for each step
- ✅ **Validation checklists** to verify progress
- ✅ **Testing strategy** for quality assurance
- ✅ **Progress tracking** to stay on schedule

**Current Progress:**
- ✅ **Step 1 COMPLETED** - Configuration system fully implemented and tested (21 tests passing)
- ✅ **Step 2 COMPLETED** - Database schema and migrations with async support
- ✅ **Step 3 COMPLETED** - PostgreSQL DocStore with async operations (25 tests passing)
- ✅ **Step 4 COMPLETED** - PostgreSQL Decoder for chunk retrieval (22 tests passing)
- ⏭️ **Step 5 NEXT** - ONNX BGE Encoder for text-to-vector transformation

**Recent Updates (Oct 20, 2025):**
- ✅ Implemented configuration system with Pydantic validation
- ✅ Created 21 passing unit tests for configuration
- ✅ Set up Alembic database migrations with async support
- ✅ Created database schema (documents and doc_segments tables)
- ✅ Implemented PostgresDocStore with async connection pooling
- ✅ Created comprehensive CRUD operations for documents and chunks
- ✅ Wrote 25 passing unit tests for DocStore
- ✅ Implemented PostgresDecoder with batch lookup and order preservation
- ✅ Created JOIN queries for complete chunk metadata
- ✅ Wrote 22 passing unit tests for Decoder
- ✅ Added async context manager support to both DocStore and Decoder
- ✅ All 70 embedding tests passing (21 config + 22 decoder + 25 docstore + 2 migration)

**Ready to continue?** → **Proceed to Step 5: ONNX BGE Encoder**

---

**Questions?** Check `docs/DEVELOPMENT.md` for workflow or `docs/reference.md` for architecture details.

**Ready to continue?** → **Proceed to Step 3: PostgreSQL DocStore** �

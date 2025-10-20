# Embedding Layer Quick Start Guide

**Date:** October 20, 2025  
**Status:** Ready to Begin Implementation  

---

## What We're Building

The **Modular Embedding Layer** transforms processed document chunks from adapters (like arXiv) into searchable vector representations. This enables semantic search across HEP literature.

## Architecture at a Glance

```
Adapter Output (Chunks) → Encoder (Text→Vector) → VectorDB (Storage)
                              ↓                        ↓
                         PostgreSQL (Original Text) ← Decoder (Vector→Text)
```

**Key Principle:** Vectors stored in VectorDB, original text in PostgreSQL for full traceability.

---

## Implementation Phases (4 Weeks)

### Week 1: Foundation
- **Phase 1:** Port interfaces (Encoder, VectorDB, Decoder protocols)
- **Phase 2:** PostgreSQL schema + migrations

### Week 2: Adapters
- **Phase 3:** ONNX BGE Encoder (text → embeddings)
- **Phase 4:** ChromaDB adapter (vector storage)

### Week 3: Pipelines
- **Phase 5:** Ingestion pipeline (adapter output → database)
- **Phase 6:** Retrieval pipeline (query → ranked results)

### Week 4: Integration
- **Phase 7:** End-to-end testing + documentation

---

## Quick Setup

### 1. Create Project Structure

```bash
# From HEPilot root
mkdir -p src/embedding/adapters
mkdir -p config
mkdir -p tests/{unit,integration}/embedding
mkdir -p alembic/versions
```

### 2. Initialize Python Environment

```bash
# Create pyproject.toml
cd src
poetry init --name hepilot-embedding --python "^3.11"

# Add dependencies
poetry add asyncpg chromadb onnxruntime transformers sentence-transformers
poetry add alembic pydantic pydantic-settings rich typer tqdm numpy

# Add dev dependencies
poetry add --group dev pytest pytest-asyncio pytest-cov mypy ruff
```

### 3. First Files to Create

**Priority 1 (This Week):**
1. `src/embedding/ports.py` - Protocol definitions
2. `src/embedding/registry.py` - Adapter discovery
3. `src/embedding/config.py` - Configuration models
4. `alembic/versions/001_initial_schema.py` - Database schema

**Priority 2 (Next Week):**
5. `src/embedding/adapters/postgres_docstore.py`
6. `src/embedding/adapters/onnx_bge_encoder.py`
7. `src/embedding/adapters/chroma_vectordb.py`

---

## Database Schema Quick Reference

```sql
-- Core tables
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    source_type VARCHAR(50),
    title TEXT,
    authors JSONB,
    metadata JSONB
);

CREATE TABLE doc_segments (
    id UUID PRIMARY KEY,
    doc_id UUID REFERENCES documents(id),
    text TEXT NOT NULL,
    section_path JSONB,
    position_in_doc INTEGER,
    meta JSONB
);
```

See full schema in `plan.md` Section 3.2.3.

---

## Key Design Decisions

### 1. Adapter Pattern
- **Why:** Swap encoders/vector stores without changing core logic
- **How:** Define Protocol interfaces, implement concrete adapters

### 2. Content Separation
- **Why:** Efficiency, traceability, scalability
- **What:** Vectors in ChromaDB, text in PostgreSQL

### 3. Default Technology Stack
- **Encoder:** ONNX BGE (CPU-friendly, no GPU needed)
- **VectorDB:** ChromaDB (embedded mode, simple setup)
- **DocStore:** PostgreSQL (robust, ACID guarantees)

---

## Success Metrics

After 4 weeks, we should have:

✅ **Functional:**
- Ingest arxiv adapter output
- Semantic search working
- Full chunk traceability

✅ **Performance:**
- >1000 chunks/minute ingestion
- <100ms query latency (p95)
- <2GB memory for 100K chunks

✅ **Quality:**
- >90% test coverage
- Type-safe (mypy compliant)
- Comprehensive documentation

---

## Example Usage (Target API)

### Ingestion
```bash
python -m hepilot.embedding ingest \
    --input adapters/arxiv_adapter/arxiv_output \
    --config config/embedding.toml
```

### Search
```bash
python -m hepilot.embedding search \
    --query "quantum chromodynamics lattice" \
    --top-k 10
```

### Health Check
```bash
python -m hepilot.embedding health
# Encoder: ✓ Ready (384d, ONNX)
# VectorDB: ✓ Connected (12,543 vectors)
# DocStore: ✓ Connected (12,543 chunks)
```

---

## Integration with Existing Work

### ArXiv Adapter (Complete ✅)
- **Output:** `adapters/arxiv_adapter/arxiv_output/`
- **Format:** Chunks as `.md` + metadata as `.json`
- **Compatibility:** Embedding layer reads this directly

### Future Adapters (In Progress)
- Design ensures compatibility
- Same chunk format expected
- Metadata schema extensible

### API Layer (Future)
- Will consume embedding layer as service
- REST endpoints use retrieval pipeline
- OpenAI-compatible interface

---

## Next Actions

### Today
1. ✅ Review `plan.md` (you're here!)
2. Create `src/embedding/ports.py`
3. Define Encoder, VectorDB, Decoder protocols
4. Set up PostgreSQL database

### This Week
1. Implement database schema
2. Write Alembic migrations
3. Create adapter registry
4. Begin encoder implementation

### This Month
Complete all 7 phases per timeline in `plan.md`

---

## Getting Help

**Documentation:**
- Full plan: `docs/plan.md`
- Architecture: `docs/reference.md`
- Standards: `standards/README.md`

**Questions to Consider:**
- Which vector store? (ChromaDB recommended, Qdrant alternative)
- Which encoder? (BGE-base recommended, others configurable)
- Local vs. remote PostgreSQL? (Docker for dev)

---

## File Locations Summary

| What | Where |
|------|-------|
| **Full Plan** | `docs/plan.md` |
| **This Guide** | `docs/embedding_quickstart.md` |
| **Source Code** | `src/embedding/` |
| **Tests** | `tests/unit/embedding/`, `tests/integration/embedding/` |
| **Config** | `config/embedding.toml` |
| **Migrations** | `alembic/versions/` |

---

**Ready to start? Begin with Phase 1 in `plan.md` Section 4!** 🚀

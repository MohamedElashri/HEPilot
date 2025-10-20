# HEPilot Development Guide

## Project Organization

HEPilot follows a **layered architecture** with clear separation of concerns:

```
hepilot/
├── src/                    # Source code (organized by layer)
│   ├── collector/          # Layer 1: Data acquisition
│   ├── embedding/          # Layer 2: Embeddings and search
│   └── api/                # Layer 3: REST API
├── tests/                  # Test suite
├── docs/                   # Documentation
├── standards/              # Data format specifications
├── config/                 # Configuration files
├── docker/                 # Container configurations
├── scripts/                # Utility scripts
└── alembic/               # Database migrations
```

## Current Development Branch: `embedding-dev`

This branch focuses on implementing the **Embedding Engine** (Layer 2).

### What Changed from Main

1. **Project Structure**: Reorganized to match reference architecture
   - `adapters/` → `src/collector/adapters/`
   - Added `src/embedding/` for the embedding layer
   - Added proper Python package structure

2. **New Files**:
   - Port interfaces: `src/embedding/ports.py`, `src/collector/ports.py`
   - Registries: `src/embedding/registry.py`, `src/collector/registry.py`
   - Project configuration: `pyproject.toml`
   - Documentation: `README.md`, implementation plans

3. **Old Structure Preserved**:
   - `adapters/arxiv_adapter/` kept for reference (see deprecation notice)
   - Copy available at `src/collector/adapters/arxiv/`

## Development Workflow

### 1. Branch Strategy

- `main`: Stable releases and completed features
- `embedding-dev`: Active development of embedding layer
- `feature/*`: Individual feature branches

### 2. Getting Started

```bash
# Ensure you're on the embedding-dev branch
git checkout embedding-dev

# Create a virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install core dependencies
uv pip install -r requirements.txt

# Install embedding layer dependencies (when working on embedding)
uv pip install -r requirements-embedding.txt

# Install development dependencies
uv pip install -r requirements-dev.txt

# Run tests
pytest
```

### 3. Development Phases

See `docs/plan.md` for detailed implementation plan:

**Current Phase**: Phase 1 - Core Infrastructure
- Defining port interfaces (done)
- Setting up registries (done)
- Database schema (next)
- Configuration management (next)

### 4. Code Organization

#### Port-Adapter Pattern

Each layer uses **Ports and Adapters** (Hexagonal Architecture):

- **Port**: Abstract interface (Python `Protocol`)
- **Adapter**: Concrete implementation

Example:
```python
# Port (interface)
class Encoder(Protocol):
    async def embed(self, texts: List[str]) -> NDArray:
        ...

# Adapter (implementation)
class ONNXBGEEncoder:
    async def embed(self, texts: List[str]) -> NDArray:
        # Actual implementation
        ...
```

#### Registry Pattern

Adapters are discovered and instantiated via registries:

```python
from hepilot.embedding.registry import encoder_registry

# Register an encoder
encoder_registry.register("onnx_bge", ONNXBGEEncoder)

# Get encoder class
EncoderClass = encoder_registry.get("onnx_bge")
encoder = EncoderClass(config)
```

### 5. Testing Strategy

Tests are organized by type:

- `tests/unit/`: Fast, isolated unit tests
- `tests/integration/`: Tests with external dependencies
- `tests/contracts/`: API contract tests

Run tests by category:
```bash
# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# All tests
pytest
```

### 6. Code Style

We use:
- **Ruff**: Linting and formatting
- **MyPy**: Type checking

```bash
# Format code
ruff format src/

# Check linting
ruff check src/

# Type checking
mypy src/
```

## Layer-Specific Guidelines

### Source Collector (`src/collector/`)

**Purpose**: Fetch and process documents from various sources

**Key Components**:
- `ports.py`: Scraper, Cleaner, Chunker, DocStore interfaces
- `registry.py`: Adapter discovery
- `adapters/`: Source-specific implementations

**Adding a New Adapter**:
1. Create directory: `src/collector/adapters/my_source/`
2. Implement the port interfaces
3. Register in entry points (pyproject.toml)
4. Add tests

### Embedding Engine (`src/embedding/`)

**Purpose**: Transform text to vectors and enable similarity search

**Key Components**:
- `ports.py`: Encoder, VectorDB, Decoder interfaces
- `registry.py`: Adapter discovery
- `adapters/`: Encoder/VectorDB implementations
- `pipeline.py`: Ingestion orchestration
- `retrieval.py`: Query processing

**Current Work** (see `docs/plan.md`):
1.  Port interfaces defined
2.  Registry implementation
3.  Database schema (in progress)
4.  Adapter implementations (planned)

### API Layer (`src/api/`)

**Status**: Planned for future phase

**Purpose**: REST API for LLM integration

**Planned Components**:
- OpenAI-compatible endpoints
- Authentication and rate limiting
- LLM backend adapters
- Metrics and health checks

## Configuration Management

Configuration uses **TOML files** and **Pydantic**:

```toml
# config/embedding.toml
[encoder]
type = "onnx_bge"
model_name = "BAAI/bge-base-en-v1.5"
batch_size = 32

[vectordb]
type = "chroma"
persist_directory = ".data/chroma"
```

Configuration models with validation:
```python
from pydantic import BaseModel

class EncoderConfig(BaseModel):
    type: str
    model_name: str
    batch_size: int = 32
```

## Database Migrations

We use **Alembic** for database schema management:

```bash
# Create a new migration
alembic revision -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Documentation

### Code Documentation

- Use **docstrings** for all public functions and classes
- Follow **Google style** docstrings
- Include type hints

Example:
```python
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
```

### Project Documentation

- Architecture: `docs/reference.md`
- Implementation plans: `docs/plan.md`
- Quick starts: `docs/*_quickstart.md`
- Standards: `standards/README.md`

## Common Tasks

### Adding a New Encoder

1. Create file: `src/embedding/adapters/my_encoder.py`
2. Implement `Encoder` protocol
3. Register in `encoder_registry`
4. Add configuration model
5. Write tests

### Adding a New Vector Store

1. Create file: `src/embedding/adapters/my_vectordb.py`
2. Implement `VectorDB` protocol
3. Register in `vectordb_registry`
4. Add configuration model
5. Write tests

### Running the Ingestion Pipeline

```bash
# (When implemented)
python -m hepilot.embedding ingest \
    --input src/collector/adapters/arxiv/arxiv_output \
    --config config/embedding.toml
```

### Querying the System

```bash
# (When implemented)
python -m hepilot.embedding search \
    --query "your search query" \
    --top-k 10
```

## Troubleshooting

### Import Errors

Make sure you're in the project root with the virtual environment activated:
```bash
cd /path/to/HEPilot
source .venv/bin/activate
```

### Database Connection Issues

Check PostgreSQL is running:
```bash
# With Docker
docker ps | grep postgres

# Local installation
pg_isready
```

### Module Not Found

Reinstall dependencies:
```bash
uv pip install -r requirements.txt
uv pip install -r requirements-embedding.txt
uv pip install -r requirements-dev.txt
```

## Contributing

1. Create a feature branch from `embedding-dev`
2. Make your changes
3. Add tests
4. Run linting and tests
5. Create a pull request to `embedding-dev`

## Resources

- [Reference Architecture](docs/reference.md)
- [Embedding Layer Plan](docs/plan.md)
- [Data Standards](standards/README.md)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

---

**Questions?** Contact: mohamed.elashri@cern.ch

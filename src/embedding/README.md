# Embedding Layer - Configuration System

## Overview

The configuration system provides type-safe, validated configuration management for the HEPilot embedding layer using Pydantic models and TOML files.

## Components

### Configuration Classes

#### `EncoderConfig`
Configures the text-to-vector encoder.

**Fields:**
- `type` (str): Encoder type (default: "onnx_bge")
- `model_name` (str): HuggingFace model identifier (default: "BAAI/bge-base-en-v1.5")
- `batch_size` (int): Batch size for encoding (range: 1-256, default: 32)
- `device` (str): Device to use - "cpu" or "cuda" (default: "cpu")
- `normalize` (bool): Whether to normalize embeddings (default: True)
- `cache_dir` (Path): Model cache directory (default: ".cache/models")

#### `VectorDBConfig`
Configures the vector database.

**Fields:**
- `type` (str): Vector DB type (default: "chroma")
- `persist_directory` (Path): Storage directory (default: ".data/chroma")
- `collection_name` (str): Collection name (default: "hepilot")
- `distance_metric` (str): Distance metric - "cosine", "l2", or "ip" (default: "cosine")

#### `DocStoreConfig`
Configures the document storage backend.

**Fields:**
- `type` (str): Storage type (default: "postgres")
- `database_url` (str): PostgreSQL connection URL (required, must start with "postgresql://" or "postgresql+asyncpg://")
- `pool_size` (int): Connection pool size (range: 1-100, default: 10)
- `max_overflow` (int): Max overflow connections (range: 0-100, default: 20)

#### `PipelineConfig`
Configures the ingestion pipeline.

**Fields:**
- `batch_size` (int): Processing batch size (range: 1-1000, default: 100)
- `max_workers` (int): Parallel workers (range: 1-32, default: 4)
- `checkpoint_interval` (int): Checkpoint frequency (minimum: 100, default: 1000)

#### `EmbeddingConfig`
Main configuration container combining all components.

**Fields:**
- `encoder` (EncoderConfig): Encoder configuration
- `vectordb` (VectorDBConfig): Vector database configuration
- `docstore` (DocStoreConfig): Document store configuration
- `pipeline` (PipelineConfig): Pipeline configuration

## Usage

### Loading Configuration

```python
from pathlib import Path
from src.embedding import load_config

# Load from default location
config = load_config(Path("config/embedding.toml"))

# Access nested configurations
print(f"Model: {config.encoder.model_name}")
print(f"Batch size: {config.encoder.batch_size}")
print(f"Database: {config.docstore.database_url}")
```

### Creating Configuration Programmatically

```python
from src.embedding import (
    EmbeddingConfig,
    EncoderConfig,
    VectorDBConfig,
    DocStoreConfig,
    PipelineConfig,
)

config = EmbeddingConfig(
    encoder=EncoderConfig(
        model_name="BAAI/bge-base-en-v1.5",
        batch_size=64,
        device="cuda"
    ),
    vectordb=VectorDBConfig(
        collection_name="my_collection",
        distance_metric="l2"
    ),
    docstore=DocStoreConfig(
        database_url="postgresql://localhost/mydb"
    ),
    pipeline=PipelineConfig(
        batch_size=200,
        max_workers=8
    )
)
```

### Validation

All configurations are automatically validated using Pydantic:

```python
from pydantic import ValidationError
from src.embedding import EncoderConfig

# This will raise ValidationError - batch_size too large
try:
    config = EncoderConfig(
        model_name="test",
        batch_size=999  # Max is 256
    )
except ValidationError as e:
    print(f"Invalid configuration: {e}")
```

## Configuration File Format

The configuration uses TOML format for readability and ease of editing:

```toml
# config/embedding.toml

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

## Environment-Specific Configurations

You can create multiple configuration files for different environments:

```bash
config/
├── embedding.toml          # Default/development
├── embedding.prod.toml     # Production
└── embedding.test.toml     # Testing
```

Then load the appropriate one:

```python
import os
from pathlib import Path
from src.embedding import load_config

env = os.getenv("HEPILOT_ENV", "default")
config_file = f"config/embedding.{env}.toml" if env != "default" else "config/embedding.toml"
config = load_config(Path(config_file))
```

## Validation Rules

### EncoderConfig
- `batch_size`: Must be between 1 and 256
- `device`: Must be "cpu" or "cuda"

### VectorDBConfig
- `distance_metric`: Must be "cosine", "l2", or "ip"

### DocStoreConfig
- `database_url`: Must start with "postgresql://" or "postgresql+asyncpg://"
- `pool_size`: Must be between 1 and 100
- `max_overflow`: Must be between 0 and 100

### PipelineConfig
- `batch_size`: Must be between 1 and 1000
- `max_workers`: Must be between 1 and 32
- `checkpoint_interval`: Must be at least 100

## Testing

Run the configuration tests:

```bash
pytest tests/unit/embedding/test_config.py -v
```

See example usage:

```bash
PYTHONPATH=/data/home/melashri/LLM/HEPilot python src/embedding/examples/load_config.py
```

## Next Steps

This configuration system is the foundation for:
1. Database schema and migrations (Step 2)
2. PostgreSQL DocStore implementation (Step 3)
3. ONNX BGE Encoder implementation (Step 5)
4. ChromaDB adapter implementation (Step 6)
5. Pipeline orchestrator (Step 7)

All subsequent components will use these configuration classes to load their settings.

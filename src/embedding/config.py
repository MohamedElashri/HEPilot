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
    """Load configuration from TOML file.
    
    Args:
        config_path: Path to TOML configuration file
        
    Returns:
        Validated EmbeddingConfig instance
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        tomllib.TOMLDecodeError: If TOML is malformed
        pydantic.ValidationError: If config values are invalid
    """
    with open(config_path, 'rb') as f:
        data = tomllib.load(f)
    return EmbeddingConfig(**data)

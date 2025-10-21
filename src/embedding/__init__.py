"""Embedding layer for HEPilot.

This module provides the embedding infrastructure for converting text chunks
into vector representations and managing their storage and retrieval.
"""

from src.embedding.config import (
    EncoderConfig,
    VectorDBConfig,
    DocStoreConfig,
    PipelineConfig,
    EmbeddingConfig,
    load_config,
)

from src.embedding.pipeline import (
    IngestionPipeline,
    RetrievalPipeline,
    IngestionResult,
    RetrievalResult,
    create_ingestion_pipeline,
    create_retrieval_pipeline,
)

__all__ = [
    # Configuration
    "EncoderConfig",
    "VectorDBConfig",
    "DocStoreConfig",
    "PipelineConfig",
    "EmbeddingConfig",
    "load_config",
    # Pipelines
    "IngestionPipeline",
    "RetrievalPipeline",
    "IngestionResult",
    "RetrievalResult",
    "create_ingestion_pipeline",
    "create_retrieval_pipeline",
]

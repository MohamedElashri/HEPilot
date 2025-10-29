"""Factory for instantiating embedding adapters from configuration."""

from pathlib import Path
from typing import Any

from src.embedding.config import (
    EmbeddingConfig,
    EncoderConfig,
    VectorDBConfig,
    DocStoreConfig,
)
from src.embedding.registry import encoder_registry, vectordb_registry, decoder_registry
from src.embedding.ports import Encoder, VectorDB, Decoder
from src.embedding.adapters.postgres_docstore import PostgresDocStore
from src.embedding.exceptions import ConfigurationError


def _normalize_db_url(url: str) -> str:
    """
    Normalize database URL for asyncpg.
    
    asyncpg expects 'postgresql://' but SQLAlchemy uses 'postgresql+asyncpg://'.
    This function converts between the formats.
    
    Args:
        url: Database URL (can be postgresql:// or postgresql+asyncpg://)
    
    Returns:
        Normalized URL for asyncpg
    """
    if url.startswith('postgresql+asyncpg://'):
        return url.replace('postgresql+asyncpg://', 'postgresql://')
    return url


def create_encoder(config: EncoderConfig) -> Encoder:
    """
    Create encoder instance from configuration.
    
    Args:
        config: Encoder configuration
        
    Returns:
        Encoder instance
        
    Raises:
        ConfigurationError: If encoder type not registered
    """
    encoder_type = config.type
    
    if encoder_type not in encoder_registry.list():
        raise ConfigurationError(
            f"Encoder type '{encoder_type}' not registered. "
            f"Available: {encoder_registry.list()}"
        )
    
    encoder_class = encoder_registry.get(encoder_type)
    
    # Map config to constructor arguments based on encoder type
    if encoder_type == "onnx_bge":
        return encoder_class(
            model_name=config.model_name,
            cache_dir=Path(config.cache_dir),
            batch_size=config.batch_size,
            normalize=config.normalize,
            device=config.device,
        )
    else:
        # Generic fallback - pass all config fields as kwargs
        return encoder_class(**config.model_dump())


def create_vectordb(config: VectorDBConfig) -> VectorDB:
    """
    Create vector database instance from configuration.
    
    Args:
        config: VectorDB configuration
        
    Returns:
        VectorDB instance
        
    Raises:
        ConfigurationError: If vectordb type not registered
    """
    vectordb_type = config.type
    
    if vectordb_type not in vectordb_registry.list():
        raise ConfigurationError(
            f"VectorDB type '{vectordb_type}' not registered. "
            f"Available: {vectordb_registry.list()}"
        )
    
    vectordb_class = vectordb_registry.get(vectordb_type)
    
    # Map config to constructor arguments based on vectordb type
    if vectordb_type == "chroma":
        return vectordb_class(
            persist_directory=Path(config.persist_directory),
            collection_name=config.collection_name,
            distance_metric=config.distance_metric,
        )
    else:
        # Generic fallback
        return vectordb_class(**config.model_dump())


def create_decoder(config: DocStoreConfig) -> Decoder:
    """
    Create decoder instance from configuration.
    
    Args:
        config: DocStore configuration (decoder uses same DB)
        
    Returns:
        Decoder instance
        
    Raises:
        ConfigurationError: If decoder type not registered
    """
    # Decoder type matches docstore type
    decoder_type = config.type
    
    if decoder_type not in decoder_registry.list():
        raise ConfigurationError(
            f"Decoder type '{decoder_type}' not registered. "
            f"Available: {decoder_registry.list()}"
        )
    
    decoder_class = decoder_registry.get(decoder_type)
    
    # Normalize database URL
    db_url = _normalize_db_url(config.database_url)
    
    # Map config to constructor arguments based on decoder type
    if decoder_type == "postgres":
        return decoder_class(
            database_url=db_url,
            pool_size=config.pool_size,
        )
    else:
        # Generic fallback
        return decoder_class(database_url=db_url, **config.model_dump(exclude={'database_url', 'type'}))


def create_docstore(config: DocStoreConfig) -> PostgresDocStore:
    """
    Create docstore instance from configuration.
    
    Args:
        config: DocStore configuration
        
    Returns:
        DocStore instance
        
    Raises:
        ConfigurationError: If docstore type not supported
    """
    docstore_type = config.type
    
    # Currently only postgres is supported for docstore
    if docstore_type != "postgres":
        raise ConfigurationError(
            f"DocStore type '{docstore_type}' not supported. "
            f"Only 'postgres' is available."
        )
    
    # Normalize database URL
    db_url = _normalize_db_url(config.database_url)
    
    return PostgresDocStore(
        database_url=db_url,
        pool_size=config.pool_size,
    )


def create_all_adapters(config: EmbeddingConfig) -> tuple[Encoder, VectorDB, Decoder, PostgresDocStore]:
    """
    Create all embedding adapters from configuration.
    
    Args:
        config: Complete embedding configuration
        
    Returns:
        Tuple of (encoder, vectordb, decoder, docstore)
        
    Raises:
        ConfigurationError: If any adapter creation fails
    """
    encoder = create_encoder(config.encoder)
    vectordb = create_vectordb(config.vectordb)
    decoder = create_decoder(config.docstore)
    docstore = create_docstore(config.docstore)
    
    return encoder, vectordb, decoder, docstore

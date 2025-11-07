"""Tests for embedding factory and registry."""

import pytest
from pathlib import Path

from src.embedding.factory import (
    create_encoder,
    create_vectordb,
    create_decoder,
    create_docstore,
    create_all_adapters,
)
from src.embedding.config import (
    EmbeddingConfig,
    EncoderConfig,
    VectorDBConfig,
    DocStoreConfig,
    PipelineConfig,
)
from src.embedding.registry import encoder_registry, vectordb_registry, decoder_registry
from src.embedding.exceptions import ConfigurationError
from src.embedding.adapters import ONNXBGEEncoder, ChromaVectorDB, PostgresDecoder


@pytest.fixture
def encoder_config():
    """Create encoder configuration."""
    return EncoderConfig(
        type="onnx_bge",
        model_name="BAAI/bge-base-en-v1.5",
        batch_size=32,
        device="cpu",
        normalize=True,
        cache_dir=Path(".cache/models"),
    )


@pytest.fixture
def vectordb_config():
    """Create vectordb configuration."""
    return VectorDBConfig(
        type="chroma",
        persist_directory=Path(".data/chroma"),
        collection_name="test_collection",
        distance_metric="cosine",
    )


@pytest.fixture
def docstore_config():
    """Create docstore configuration."""
    return DocStoreConfig(
        type="postgres",
        database_url="postgresql://user:pass@localhost/testdb",
        pool_size=10,
        max_overflow=20,
    )


@pytest.fixture
def embedding_config(encoder_config, vectordb_config, docstore_config):
    """Create complete embedding configuration."""
    return EmbeddingConfig(
        encoder=encoder_config,
        vectordb=vectordb_config,
        docstore=docstore_config,
        pipeline=PipelineConfig(),
    )


class TestEncoderRegistry:
    """Test encoder registry functionality."""

    def test_encoder_registry_has_onnx_bge(self):
        """Test that onnx_bge encoder is registered."""
        assert "onnx_bge" in encoder_registry.list()

    def test_encoder_registry_get_onnx_bge(self):
        """Test getting onnx_bge encoder from registry."""
        encoder_class = encoder_registry.get("onnx_bge")
        assert encoder_class == ONNXBGEEncoder

    def test_encoder_registry_get_nonexistent_raises(self):
        """Test that getting non-existent encoder raises KeyError."""
        with pytest.raises(KeyError):
            encoder_registry.get("nonexistent_encoder")


class TestVectorDBRegistry:
    """Test vectordb registry functionality."""

    def test_vectordb_registry_has_chroma(self):
        """Test that chroma vectordb is registered."""
        assert "chroma" in vectordb_registry.list()

    def test_vectordb_registry_get_chroma(self):
        """Test getting chroma vectordb from registry."""
        vectordb_class = vectordb_registry.get("chroma")
        assert vectordb_class == ChromaVectorDB

    def test_vectordb_registry_get_nonexistent_raises(self):
        """Test that getting non-existent vectordb raises KeyError."""
        with pytest.raises(KeyError):
            vectordb_registry.get("nonexistent_vectordb")


class TestDecoderRegistry:
    """Test decoder registry functionality."""

    def test_decoder_registry_has_postgres(self):
        """Test that postgres decoder is registered."""
        assert "postgres" in decoder_registry.list()

    def test_decoder_registry_get_postgres(self):
        """Test getting postgres decoder from registry."""
        decoder_class = decoder_registry.get("postgres")
        assert decoder_class == PostgresDecoder

    def test_decoder_registry_get_nonexistent_raises(self):
        """Test that getting non-existent decoder raises KeyError."""
        with pytest.raises(KeyError):
            decoder_registry.get("nonexistent_decoder")


class TestCreateEncoder:
    """Test encoder factory function."""

    def test_create_encoder_onnx_bge(self, encoder_config):
        """Test creating onnx_bge encoder from config."""
        encoder = create_encoder(encoder_config)
        assert isinstance(encoder, ONNXBGEEncoder)
        assert encoder.model_name == "BAAI/bge-base-en-v1.5"
        assert encoder.batch_size == 32
        assert encoder.device == "cpu"

    def test_create_encoder_unregistered_type_raises(self):
        """Test that creating encoder with unregistered type raises ConfigurationError."""
        config = EncoderConfig(
            type="nonexistent_encoder",
            model_name="test",
            batch_size=32,
            device="cpu",
            normalize=True,
            cache_dir=Path(".cache"),
        )
        with pytest.raises(ConfigurationError) as exc_info:
            create_encoder(config)
        assert "not registered" in str(exc_info.value).lower()


class TestCreateVectorDB:
    """Test vectordb factory function."""

    def test_create_vectordb_chroma(self, vectordb_config):
        """Test creating chroma vectordb from config."""
        vectordb = create_vectordb(vectordb_config)
        assert isinstance(vectordb, ChromaVectorDB)
        assert vectordb.persist_directory == Path(".data/chroma")
        assert vectordb.collection_name == "test_collection"

    def test_create_vectordb_unregistered_type_raises(self):
        """Test that creating vectordb with unregistered type raises ConfigurationError."""
        config = VectorDBConfig(
            type="nonexistent_vectordb",
            persist_directory=Path(".data"),
            collection_name="test",
            distance_metric="cosine",
        )
        with pytest.raises(ConfigurationError) as exc_info:
            create_vectordb(config)
        assert "not registered" in str(exc_info.value).lower()


class TestCreateDecoder:
    """Test decoder factory function."""

    def test_create_decoder_postgres(self, docstore_config):
        """Test creating postgres decoder from config."""
        decoder = create_decoder(docstore_config)
        assert isinstance(decoder, PostgresDecoder)
        # URL should be normalized (postgresql:// not postgresql+asyncpg://)
        assert decoder.database_url.startswith("postgresql://")
        assert not decoder.database_url.startswith("postgresql+asyncpg://")

    def test_create_decoder_normalizes_asyncpg_url(self):
        """Test that decoder factory normalizes asyncpg URL format."""
        config = DocStoreConfig(
            type="postgres",
            database_url="postgresql+asyncpg://user:pass@localhost/testdb",
            pool_size=10,
        )
        decoder = create_decoder(config)
        assert decoder.database_url == "postgresql://user:pass@localhost/testdb"

    def test_create_decoder_unregistered_type_raises(self):
        """Test that creating decoder with unregistered type raises ConfigurationError."""
        config = DocStoreConfig(
            type="nonexistent_decoder",
            database_url="postgresql://localhost/test",
            pool_size=10,
        )
        with pytest.raises(ConfigurationError) as exc_info:
            create_decoder(config)
        assert "not registered" in str(exc_info.value).lower()


class TestCreateDocStore:
    """Test docstore factory function."""

    def test_create_docstore_postgres(self, docstore_config):
        """Test creating postgres docstore from config."""
        docstore = create_docstore(docstore_config)
        # URL should be normalized
        assert docstore.database_url.startswith("postgresql://")
        assert docstore.pool_size == 10

    def test_create_docstore_normalizes_asyncpg_url(self):
        """Test that docstore factory normalizes asyncpg URL format."""
        config = DocStoreConfig(
            type="postgres",
            database_url="postgresql+asyncpg://user:pass@localhost/testdb",
            pool_size=10,
        )
        docstore = create_docstore(config)
        assert docstore.database_url == "postgresql://user:pass@localhost/testdb"

    def test_create_docstore_unsupported_type_raises(self):
        """Test that creating docstore with unsupported type raises ConfigurationError."""
        # Create config with valid URL but wrong type
        config = DocStoreConfig(
            type="mysql",  # Changed type but kept valid postgres URL
            database_url="postgresql://localhost/test",
            pool_size=10,
        )
        with pytest.raises(ConfigurationError) as exc_info:
            create_docstore(config)
        assert "not supported" in str(exc_info.value).lower()


class TestCreateAllAdapters:
    """Test creating all adapters at once."""

    def test_create_all_adapters(self, embedding_config):
        """Test creating all adapters from complete config."""
        encoder, vectordb, decoder, docstore = create_all_adapters(embedding_config)

        assert isinstance(encoder, ONNXBGEEncoder)
        assert isinstance(vectordb, ChromaVectorDB)
        assert isinstance(decoder, PostgresDecoder)
        assert docstore is not None

    def test_create_all_adapters_types(self, embedding_config):
        """Test that created adapters have correct types."""
        encoder, vectordb, decoder, docstore = create_all_adapters(embedding_config)

        # Verify encoder properties
        assert encoder.model_name == "BAAI/bge-base-en-v1.5"
        assert encoder.batch_size == 32

        # Verify vectordb properties
        assert vectordb.collection_name == "test_collection"

        # Verify decoder has normalized URL
        assert decoder.database_url.startswith("postgresql://")

        # Verify docstore has normalized URL
        assert docstore.database_url.startswith("postgresql://")


class TestURLNormalization:
    """Test database URL normalization."""

    def test_normalize_standard_url(self):
        """Test that standard postgresql:// URL is unchanged."""
        config = DocStoreConfig(
            type="postgres",
            database_url="postgresql://user:pass@localhost/testdb",
            pool_size=10,
        )
        decoder = create_decoder(config)
        assert decoder.database_url == "postgresql://user:pass@localhost/testdb"

    def test_normalize_asyncpg_url(self):
        """Test that postgresql+asyncpg:// URL is converted."""
        config = DocStoreConfig(
            type="postgres",
            database_url="postgresql+asyncpg://user:pass@localhost/testdb",
            pool_size=10,
        )
        decoder = create_decoder(config)
        assert decoder.database_url == "postgresql://user:pass@localhost/testdb"

    def test_normalize_complex_url(self):
        """Test normalization with complex URL (query params, etc)."""
        config = DocStoreConfig(
            type="postgres",
            database_url="postgresql+asyncpg://user:pass@localhost:5432/testdb?sslmode=require",
            pool_size=10,
        )
        decoder = create_decoder(config)
        assert decoder.database_url == "postgresql://user:pass@localhost:5432/testdb?sslmode=require"

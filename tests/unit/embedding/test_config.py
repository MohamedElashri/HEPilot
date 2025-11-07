"""Unit tests for embedding configuration."""

import pytest
from pathlib import Path
from pydantic import ValidationError
import tempfile
import tomllib

from src.embedding.config import (
    EncoderConfig,
    VectorDBConfig,
    DocStoreConfig,
    PipelineConfig,
    EmbeddingConfig,
    load_config,
)


class TestEncoderConfig:
    """Test encoder configuration validation."""
    
    def test_default_values(self):
        """Test encoder config with default values."""
        config = EncoderConfig(model_name="test-model")
        assert config.type == "onnx_bge"
        assert config.batch_size == 32
        assert config.device == "cpu"
        assert config.normalize is True
        assert config.cache_dir == Path(".cache/models")
    
    def test_custom_values(self):
        """Test encoder config with custom values."""
        config = EncoderConfig(
            type="custom",
            model_name="custom-model",
            batch_size=64,
            device="cuda",
            normalize=False,
            cache_dir=Path("/tmp/models")
        )
        assert config.type == "custom"
        assert config.batch_size == 64
        assert config.device == "cuda"
        assert config.normalize is False
        assert config.cache_dir == Path("/tmp/models")
    
    def test_batch_size_validation(self):
        """Test batch size must be in valid range."""
        # Too small
        with pytest.raises(ValidationError):
            EncoderConfig(model_name="test", batch_size=0)
        
        # Too large
        with pytest.raises(ValidationError):
            EncoderConfig(model_name="test", batch_size=257)
        
        # Valid boundaries
        config = EncoderConfig(model_name="test", batch_size=1)
        assert config.batch_size == 1
        
        config = EncoderConfig(model_name="test", batch_size=256)
        assert config.batch_size == 256
    
    def test_device_validation(self):
        """Test device must be cpu or cuda."""
        # Invalid device
        with pytest.raises(ValidationError):
            EncoderConfig(model_name="test", device="tpu")
        
        # Valid devices
        config = EncoderConfig(model_name="test", device="cpu")
        assert config.device == "cpu"
        
        config = EncoderConfig(model_name="test", device="cuda")
        assert config.device == "cuda"


class TestVectorDBConfig:
    """Test vector database configuration validation."""
    
    def test_default_values(self):
        """Test vectordb config with default values."""
        config = VectorDBConfig()
        assert config.type == "chroma"
        assert config.persist_directory == Path(".data/chroma")
        assert config.collection_name == "hepilot"
        assert config.distance_metric == "cosine"
    
    def test_custom_values(self):
        """Test vectordb config with custom values."""
        config = VectorDBConfig(
            type="milvus",
            persist_directory=Path("/data/vectors"),
            collection_name="custom_collection",
            distance_metric="l2"
        )
        assert config.type == "milvus"
        assert config.persist_directory == Path("/data/vectors")
        assert config.collection_name == "custom_collection"
        assert config.distance_metric == "l2"
    
    def test_distance_metric_validation(self):
        """Test distance metric must be cosine, l2, or ip."""
        # Invalid metric
        with pytest.raises(ValidationError):
            VectorDBConfig(distance_metric="euclidean")
        
        # Valid metrics
        for metric in ["cosine", "l2", "ip"]:
            config = VectorDBConfig(distance_metric=metric)
            assert config.distance_metric == metric


class TestDocStoreConfig:
    """Test document store configuration validation."""
    
    def test_valid_postgres_url(self):
        """Test valid PostgreSQL URLs."""
        urls = [
            "postgresql://user:pass@localhost/db",
            "postgresql+asyncpg://user:pass@localhost:5432/db",
        ]
        for url in urls:
            config = DocStoreConfig(database_url=url)
            assert config.database_url == url
    
    def test_invalid_database_url(self):
        """Test invalid database URLs are rejected."""
        invalid_urls = [
            "mysql://user:pass@localhost/db",
            "sqlite:///database.db",
            "mongodb://localhost/db",
            "http://localhost/db",
        ]
        for url in invalid_urls:
            with pytest.raises(ValidationError):
                DocStoreConfig(database_url=url)
    
    def test_pool_size_validation(self):
        """Test pool size must be in valid range."""
        db_url = "postgresql://user:pass@localhost/db"
        
        # Too small
        with pytest.raises(ValidationError):
            DocStoreConfig(database_url=db_url, pool_size=0)
        
        # Too large
        with pytest.raises(ValidationError):
            DocStoreConfig(database_url=db_url, pool_size=101)
        
        # Valid boundaries
        config = DocStoreConfig(database_url=db_url, pool_size=1)
        assert config.pool_size == 1
        
        config = DocStoreConfig(database_url=db_url, pool_size=100)
        assert config.pool_size == 100
    
    def test_default_values(self):
        """Test default pool configuration."""
        config = DocStoreConfig(database_url="postgresql://localhost/db")
        assert config.pool_size == 10
        assert config.max_overflow == 20


class TestPipelineConfig:
    """Test pipeline configuration validation."""
    
    def test_default_values(self):
        """Test pipeline config with default values."""
        config = PipelineConfig()
        assert config.batch_size == 100
        assert config.max_workers == 4
        assert config.checkpoint_interval == 1000
    
    def test_batch_size_validation(self):
        """Test batch size must be in valid range."""
        # Too small
        with pytest.raises(ValidationError):
            PipelineConfig(batch_size=0)
        
        # Too large
        with pytest.raises(ValidationError):
            PipelineConfig(batch_size=1001)
        
        # Valid boundaries
        config = PipelineConfig(batch_size=1)
        assert config.batch_size == 1
        
        config = PipelineConfig(batch_size=1000)
        assert config.batch_size == 1000
    
    def test_max_workers_validation(self):
        """Test max workers must be in valid range."""
        # Too small
        with pytest.raises(ValidationError):
            PipelineConfig(max_workers=0)
        
        # Too large
        with pytest.raises(ValidationError):
            PipelineConfig(max_workers=33)
        
        # Valid boundaries
        config = PipelineConfig(max_workers=1)
        assert config.max_workers == 1
        
        config = PipelineConfig(max_workers=32)
        assert config.max_workers == 32
    
    def test_checkpoint_interval_validation(self):
        """Test checkpoint interval must be >= 100."""
        # Too small
        with pytest.raises(ValidationError):
            PipelineConfig(checkpoint_interval=99)
        
        # Valid boundary
        config = PipelineConfig(checkpoint_interval=100)
        assert config.checkpoint_interval == 100


class TestEmbeddingConfig:
    """Test main embedding configuration."""
    
    def test_full_config(self):
        """Test complete embedding configuration."""
        config = EmbeddingConfig(
            encoder=EncoderConfig(model_name="test-model"),
            vectordb=VectorDBConfig(),
            docstore=DocStoreConfig(database_url="postgresql://localhost/db"),
            pipeline=PipelineConfig()
        )
        assert config.encoder.model_name == "test-model"
        assert config.vectordb.type == "chroma"
        assert config.docstore.database_url == "postgresql://localhost/db"
        assert config.pipeline.batch_size == 100


class TestLoadConfig:
    """Test configuration loading from TOML."""
    
    def test_load_valid_config(self, tmp_path):
        """Test loading a valid TOML configuration."""
        config_file = tmp_path / "config.toml"
        config_file.write_text("""
[encoder]
type = "onnx_bge"
model_name = "BAAI/bge-base-en-v1.5"
batch_size = 64
device = "cuda"
normalize = true
cache_dir = ".cache/models"

[vectordb]
type = "chroma"
persist_directory = ".data/chroma"
collection_name = "test_collection"
distance_metric = "l2"

[docstore]
type = "postgres"
database_url = "postgresql+asyncpg://user:pass@localhost/testdb"
pool_size = 5
max_overflow = 10

[pipeline]
batch_size = 50
max_workers = 8
checkpoint_interval = 500
        """)
        
        config = load_config(config_file)
        
        # Verify encoder
        assert config.encoder.batch_size == 64
        assert config.encoder.device == "cuda"
        
        # Verify vectordb
        assert config.vectordb.collection_name == "test_collection"
        assert config.vectordb.distance_metric == "l2"
        
        # Verify docstore
        assert config.docstore.pool_size == 5
        assert config.docstore.max_overflow == 10
        
        # Verify pipeline
        assert config.pipeline.batch_size == 50
        assert config.pipeline.max_workers == 8
        assert config.pipeline.checkpoint_interval == 500
    
    def test_load_missing_file(self):
        """Test loading non-existent config file."""
        with pytest.raises(FileNotFoundError):
            load_config(Path("/nonexistent/config.toml"))
    
    def test_load_invalid_toml(self, tmp_path):
        """Test loading malformed TOML."""
        config_file = tmp_path / "bad_config.toml"
        config_file.write_text("this is not valid TOML [[[")
        
        with pytest.raises(tomllib.TOMLDecodeError):
            load_config(config_file)
    
    def test_load_invalid_values(self, tmp_path):
        """Test loading TOML with invalid configuration values."""
        config_file = tmp_path / "invalid_config.toml"
        config_file.write_text("""
[encoder]
model_name = "test"
batch_size = 999  # Too large
device = "cpu"

[vectordb]
type = "chroma"

[docstore]
database_url = "mysql://wrong/db"  # Wrong DB type

[pipeline]
batch_size = 100
        """)
        
        with pytest.raises(ValidationError):
            load_config(config_file)
    
    def test_load_default_config(self):
        """Test loading the actual default config file."""
        config_path = Path("/data/home/melashri/LLM/HEPilot/config/embedding.toml")
        
        # Only test if file exists
        if config_path.exists():
            config = load_config(config_path)
            
            # Verify structure
            assert config.encoder.model_name == "BAAI/bge-base-en-v1.5"
            assert config.vectordb.collection_name == "hepilot"
            assert config.pipeline.batch_size == 100

"""Tests for collector configuration loading and validation."""

import json
import pytest
from pathlib import Path
from src.collector.config import (
    AdapterConfig,
    ProcessingConfig,
    AdapterConfigError,
    load_adapter_config,
)


@pytest.fixture
def tmp_config_dir(tmp_path):
    """Create temporary config directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def valid_config():
    """Create valid adapter configuration."""
    return {
        "adapter_config": {
            "name": "test_adapter",
            "version": "1.0.0",
            "source_type": "arxiv",
            "processing_config": {
                "chunk_size": 512,
                "chunk_overlap": 0.1,
                "preserve_tables": True,
                "preserve_equations": True,
            },
            "profile": "core",
            "config_hash": "0" * 64,
        }
    }


@pytest.fixture
def config_with_extensions():
    """Create config with extensions."""
    return {
        "adapter_config": {
            "name": "test_adapter",
            "version": "1.0.0",
            "source_type": "arxiv",
            "processing_config": {
                "chunk_size": 512,
                "chunk_overlap": 0.1,
                "preserve_tables": True,
                "preserve_equations": True,
            },
            "x_extension": {
                "processing": {
                    "enrich_formulas": True,
                    "table_mode": "fast",
                    "exclude_references": True,
                }
            },
            "config_hash": "0" * 64,
        }
    }


class TestAdapterConfigDataclass:
    """Test AdapterConfig dataclass."""

    def test_adapter_config_creation(self):
        """Test basic AdapterConfig creation."""
        processing = ProcessingConfig(
            chunk_size=512,
            chunk_overlap=0.1,
            preserve_tables=True,
            preserve_equations=True,
        )
        config = AdapterConfig(
            name="test",
            version="1.0.0",
            source_type="arxiv",
            processing=processing,
            config_hash="abc123",
        )

        assert config.name == "test"
        assert config.version == "1.0.0"
        assert config.source_type == "arxiv"
        assert config.config_hash == "abc123"

    def test_adapter_config_raw_property(self):
        """Test raw property returns dict representation."""
        processing = ProcessingConfig(
            chunk_size=512,
            chunk_overlap=0.1,
            preserve_tables=True,
            preserve_equations=True,
        )
        config = AdapterConfig(
            name="test",
            version="1.0.0",
            source_type="arxiv",
            processing=processing,
            config_hash="abc123",
            profile="core",
        )

        raw = config.raw
        assert "adapter_config" in raw
        assert raw["adapter_config"]["name"] == "test"
        assert raw["adapter_config"]["profile"] == "core"
        assert "processing_config" in raw["adapter_config"]


class TestLoadAdapterConfig:
    """Test adapter config loading."""

    def test_load_valid_config(self, tmp_config_dir, valid_config):
        """Test loading valid configuration."""
        config_path = tmp_config_dir / "adapter_config.json"
        with open(config_path, "w") as f:
            json.dump(valid_config, f)

        config = load_adapter_config(config_path, auto_update_hash=True)

        assert config.name == "test_adapter"
        assert config.version == "1.0.0"
        assert config.source_type == "arxiv"
        assert config.processing.chunk_size == 512

    def test_load_config_file_not_found(self, tmp_config_dir):
        """Test error when config file doesn't exist."""
        config_path = tmp_config_dir / "nonexistent.json"

        with pytest.raises(AdapterConfigError) as exc_info:
            load_adapter_config(config_path)

        assert "not found" in str(exc_info.value).lower()

    def test_load_config_auto_update_hash(self, tmp_config_dir, valid_config):
        """Test hash auto-update when enabled."""
        config_path = tmp_config_dir / "adapter_config.json"
        with open(config_path, "w") as f:
            json.dump(valid_config, f)

        config = load_adapter_config(config_path, auto_update_hash=True)

        # Re-read file to check hash was updated
        with open(config_path, "r") as f:
            updated_config = json.load(f)

        # Hash should no longer be all zeros
        assert updated_config["adapter_config"]["config_hash"] != "0" * 64
        assert len(updated_config["adapter_config"]["config_hash"]) == 64

    def test_load_config_hash_mismatch_without_auto_update(
        self, tmp_config_dir, valid_config
    ):
        """Test error on hash mismatch without auto-update."""
        # First create with correct hash
        config_path = tmp_config_dir / "adapter_config.json"
        with open(config_path, "w") as f:
            json.dump(valid_config, f)

        # Load once to compute correct hash
        load_adapter_config(config_path, auto_update_hash=True)

        # Modify config but keep old hash
        with open(config_path, "r") as f:
            config_data = json.load(f)

        old_hash = config_data["adapter_config"]["config_hash"]
        config_data["adapter_config"]["name"] = "modified_name"
        config_data["adapter_config"]["config_hash"] = old_hash

        with open(config_path, "w") as f:
            json.dump(config_data, f)

        # Should raise error without auto_update
        with pytest.raises(AdapterConfigError) as exc_info:
            load_adapter_config(config_path, auto_update_hash=False)

        assert "hash mismatch" in str(exc_info.value).lower()

    def test_load_config_with_extensions(self, tmp_config_dir, config_with_extensions):
        """Test loading config with x_extension."""
        config_path = tmp_config_dir / "adapter_config.json"
        with open(config_path, "w") as f:
            json.dump(config_with_extensions, f)

        config = load_adapter_config(config_path, auto_update_hash=True)

        assert "processing" in config.extensions
        assert config.extensions["processing"]["enrich_formulas"] is True
        assert config.extensions["processing"]["table_mode"] == "fast"

    def test_load_config_extras_in_processing(
        self, tmp_config_dir, config_with_extensions
    ):
        """Test that extension processing fields are merged into extras."""
        config_path = tmp_config_dir / "adapter_config.json"
        with open(config_path, "w") as f:
            json.dump(config_with_extensions, f)

        config = load_adapter_config(config_path, auto_update_hash=True)

        # Extension processing fields should be in extras
        assert config.processing.extras["enrich_formulas"] is True
        assert config.processing.extras["table_mode"] == "fast"
        assert config.processing.extras["exclude_references"] is True

    def test_load_config_optional_fields(self, tmp_config_dir, valid_config):
        """Test loading config with optional fields."""
        valid_config["adapter_config"]["credential_id"] = "cred-123"
        valid_config["adapter_config"]["profile"] = "production"

        config_path = tmp_config_dir / "adapter_config.json"
        with open(config_path, "w") as f:
            json.dump(valid_config, f)

        config = load_adapter_config(config_path, auto_update_hash=True)

        assert config.credential_id == "cred-123"
        assert config.profile == "production"


class TestProcessingConfig:
    """Test ProcessingConfig dataclass."""

    def test_processing_config_creation(self):
        """Test basic ProcessingConfig creation."""
        config = ProcessingConfig(
            chunk_size=512,
            chunk_overlap=0.1,
            preserve_tables=True,
            preserve_equations=True,
        )

        assert config.chunk_size == 512
        assert config.chunk_overlap == 0.1
        assert config.preserve_tables is True
        assert config.preserve_equations is True
        assert config.extras == {}

    def test_processing_config_with_extras(self):
        """Test ProcessingConfig with extra fields."""
        config = ProcessingConfig(
            chunk_size=512,
            chunk_overlap=0.1,
            preserve_tables=True,
            preserve_equations=True,
            extras={
                "enrich_formulas": True,
                "table_mode": "accurate",
            },
        )

        assert config.extras["enrich_formulas"] is True
        assert config.extras["table_mode"] == "accurate"


class TestConfigHashComputation:
    """Test configuration hash computation."""

    def test_hash_consistent(self, tmp_config_dir, valid_config):
        """Test hash is consistent for same config."""
        config_path = tmp_config_dir / "adapter_config.json"
        with open(config_path, "w") as f:
            json.dump(valid_config, f)

        config1 = load_adapter_config(config_path, auto_update_hash=True)
        hash1 = config1.config_hash

        # Load again
        config2 = load_adapter_config(config_path, auto_update_hash=True)
        hash2 = config2.config_hash

        assert hash1 == hash2

    def test_hash_changes_with_config(self, tmp_config_dir, valid_config):
        """Test hash changes when config changes."""
        config_path = tmp_config_dir / "adapter_config.json"

        # Load first config
        with open(config_path, "w") as f:
            json.dump(valid_config, f)
        config1 = load_adapter_config(config_path, auto_update_hash=True)
        hash1 = config1.config_hash

        # Modify and reload
        valid_config["adapter_config"]["processing_config"]["chunk_size"] = 1024
        valid_config["adapter_config"]["config_hash"] = "0" * 64
        with open(config_path, "w") as f:
            json.dump(valid_config, f)
        config2 = load_adapter_config(config_path, auto_update_hash=True)
        hash2 = config2.config_hash

        assert hash1 != hash2

    def test_hash_excludes_hash_field(self, tmp_config_dir, valid_config):
        """Test that hash is computed without the hash field itself."""
        config_path = tmp_config_dir / "adapter_config.json"

        # Load with auto_update_hash to get consistent hash
        with open(config_path, "w") as f:
            json.dump(valid_config, f)
        config1 = load_adapter_config(config_path, auto_update_hash=True)
        computed_hash = config1.config_hash

        # Now load again with auto_update to confirm hash is stable
        config2 = load_adapter_config(config_path, auto_update_hash=True)

        # Hash should be same since content is same
        assert config1.config_hash == config2.config_hash == computed_hash

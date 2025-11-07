"""Configuration accessors for the ArXiv collector adapter."""

from pathlib import Path
from typing import Any, Dict

from src.collector.config import AdapterConfig, load_adapter_config


class ConfigManager:
    """Wrapper around the shared adapter configuration loader."""

    def __init__(
        self,
        config_path: Path,
        *,
        auto_update_hash: bool = True,
    ) -> None:
        self.config_path = config_path
        self.auto_update_hash = auto_update_hash
        self.config: AdapterConfig = load_adapter_config(
            config_path,
            auto_update_hash=auto_update_hash,
        )

    def reload(self) -> None:
        """Reload configuration from disk."""

        self.config = load_adapter_config(
            self.config_path,
            auto_update_hash=self.auto_update_hash,
        )

    # ------------------------------------------------------------------
    # Processing configuration helpers
    # ------------------------------------------------------------------
    def get_chunk_size(self) -> int:
        return self.config.processing.chunk_size

    def get_chunk_overlap(self) -> float:
        return self.config.processing.chunk_overlap

    def get_preserve_tables(self) -> bool:
        return self.config.processing.preserve_tables

    def get_preserve_equations(self) -> bool:
        return self.config.processing.preserve_equations

    def get_enrich_formulas(self) -> bool:
        return self._processing_extra("enrich_formulas", True)

    def get_exclude_references(self) -> bool:
        return self._processing_extra("exclude_references", True)

    def get_exclude_acknowledgments(self) -> bool:
        return self._processing_extra("exclude_acknowledgments", True)

    def get_exclude_author_lists(self) -> bool:
        return self._processing_extra("exclude_author_lists", True)

    def get_include_authors_metadata(self) -> bool:
        return self._processing_extra("include_authors_metadata", False)

    def get_processing_timeout(self) -> int:
        return self._processing_extra("processing_timeout", 0)

    def get_table_mode(self) -> str:
        return self._processing_extra("table_mode", "fast")

    # ------------------------------------------------------------------
    # Embedding convenience accessors (legacy support)
    # ------------------------------------------------------------------
    def get_embedding_model_name(self) -> str:
        embedding_cfg = self._extension_section("embedding")
        return embedding_cfg.get("model_name", "BAAI/bge-large-en-v1.5")

    def get_use_model_tokenizer(self) -> bool:
        embedding_cfg = self._extension_section("embedding")
        return embedding_cfg.get("use_model_tokenizer", True)

    def get_model_cache_dir(self) -> str:
        embedding_cfg = self._extension_section("embedding")
        return embedding_cfg.get("cache_dir", ".model_cache")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _processing_extra(self, key: str, default: Any) -> Any:
        return self.config.processing.extras.get(key, default)

    def _extension_section(self, section: str) -> Dict[str, Any]:
        return self.config.extensions.get(section, {})

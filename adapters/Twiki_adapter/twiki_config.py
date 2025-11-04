"""
Configuration manager for Twiki adapter.

Loads and validates adapter configuration, computes config hash, 
and provides typed access to processing and embedding settings.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any
from models import AdapterConfig

class TwikiConfigManager:
    # manages twiki adapter configuration with validation and hash tracking.

    def __init__(self, config_path: Path) -> None:
        """
        Initializes Twiki configuration manager.

        Args:
            config_path: Path to adapter_config.json file
        """
        self.config_path: Path = config_path
        self.config: AdapterConfig = self._load_config()


    # Core I/O methods
    def _load_config(self) -> AdapterConfig:
        """
        Load and validate configuration from JSON.

        Returns: 
            Validated AdapterConfig instance.
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"[TWikiConfig] Config file not found: {self.config_path}")
        
        with open(self.config_path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)

        config_data: Dict[str, Any] = data.get("adapter_config", {})
        config: AdapterConfig = AdapterConfig(**config_data)

        # compute and inject hash if not yet set
        computed_hash = self._compute_config_hash(config_data)
        if config.config_hash == "0" * 64 or config.config_hash != computed_hash:
            config.config_hash = computed_hash
            self._save_config(config)

        if config.source_type.lower() != "twiki":
            raise ValueError(
                f"[TWikiConfig] Invalid source_type '{config.source_type}', expected 'twiki'."
            )

        return config
    

    def _compute_config_hash(self, config_data: Dict[str, Any]) -> str:
        # Compute stable SHA-256 hash for configuration contents.
        
        config_copy = dict(config_data)
        config_copy.pop("config_hash", None)
        canonical_json = json.dumps(config_copy, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    def _save_config(self, config: AdapterConfig) -> None:
        # Save updated configuration with computed hash.
        data = {"adapter_config": config.model_dump()}
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def get_chunk_size(self) -> int:
        # get target chunk size in tokens.
        return self.config.processing_config.get("chunk_size", 512)
    
    def get_chunk_overlap(self) -> float:
        # get chunk overlap fraction.
        return self.config.processing_config.get("chunk_overlap", 0.1)
    
    def get_preserve_tables(self) -> bool:
        # Return True if TWiki tables should be preserved in Markdown.
        return self.config.processing_config.get("preserve_tables", True)
    
    def get_preserve_equations(self) -> bool:
        # Return True if LaTeX math in TWiki pages should be preserved.
        return self.config.processing_config.get("preserve_equations", True)

    def get_enrich_links(self) -> bool:
        # Return True if TWiki internal/external links should be enriched
        # with metadata annotations.
        return self.config.processing_config.get("enrich_links", True)

    def get_exclude_edit_metadata(self) -> bool:
        # Return True if page edit-history metadata should be excluded.
        return self.config.processing_config.get("exclude_edit_metadata", True)

    def get_exclude_raw_macros(self) -> bool:
        # Return True if TWiki macros (e.g., %SEARCH%, %TOC%) should be removed.
        return self.config.processing_config.get("exclude_raw_macros", True)

    def get_include_section_hierarchy(self) -> bool:
        # Return True if section hierarchy should be stored in metadata.
        return self.config.processing_config.get("include_section_hierarchy", True)

    def get_table_mode(self) -> str:
        # Return TWiki table parsing mode ('fast' or 'accurate').
        return self.config.processing_config.get("table_mode", "fast")

    def get_processing_timeout(self) -> int:
        # Return processing timeout in seconds.
        return self.config.processing_config.get("processing_timeout", 120)
    
    def get_embedding_model_name(self) -> str:
        # Return embedding model name
        emb_cfg = self.config.model_dump().get("embedding_config", {})
        return emb_cfg.get("model_name", "BAAI/bge-large-en-v1.5")

    def get_use_model_tokenizer(self) -> bool:
        # Return True if tokenizer from embedding model should be used.
        emb_cfg = self.config.model_dump().get("embedding_config", {})
        return emb_cfg.get("use_model_tokenizer", True)

    def get_model_cache_dir(self) -> str:
        # Return local directory for cached embedding model.
        emb_cfg = self.config.model_dump().get("embedding_config", {})
        return emb_cfg.get("cache_dir", ".model_cache")
    
    def get_config_hash(self) -> str:
        # Return computed SHA-256 configuration hash.
        return self.config.config_hash

    def get_adapter_name(self) -> str:
        # Return human-readable adapter name.
        return self.config.name

    def get_adapter_version(self) -> str:
        # Return adapter version string.
        return self.config.version
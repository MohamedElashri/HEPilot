"""
Configuration manager for ArXiv adapter.

Loads and validates adapter configuration, computes config hash,
and provides typed configuration objects.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any
from models import AdapterConfig


class ConfigManager:
    """Manages adapter configuration with validation and hashing."""
    
    def __init__(self, config_path: Path) -> None:
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to adapter_config.json file
        """
        self.config_path: Path = config_path
        self.config: AdapterConfig = self._load_config()
    
    def _load_config(self) -> AdapterConfig:
        """
        Load and validate configuration from JSON file.
        
        Returns:
            Validated adapter configuration
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, 'r', encoding='utf-8') as f:
            data: Dict[str, Any] = json.load(f)
        config_data: Dict[str, Any] = data.get('adapter_config', {})
        config: AdapterConfig = AdapterConfig(**config_data)
        computed_hash: str = self._compute_config_hash(config_data)
        if config.config_hash == "0" * 64:
            config.config_hash = computed_hash
            self._save_config(config)
        return config
    
    def _compute_config_hash(self, config_data: Dict[str, Any]) -> str:
        """
        Compute SHA-256 hash of canonicalized config JSON.
        
        Args:
            config_data: Configuration dictionary
            
        Returns:
            64-character hexadecimal hash string
        """
        config_copy: Dict[str, Any] = config_data.copy()
        config_copy.pop('config_hash', None)
        canonical_json: str = json.dumps(config_copy, sort_keys=True, separators=(',', ':'))
        hash_obj: hashlib._Hash = hashlib.sha256(canonical_json.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def _save_config(self, config: AdapterConfig) -> None:
        """
        Save updated configuration back to file.
        
        Args:
            config: Configuration to save
        """
        data: Dict[str, Any] = {"adapter_config": config.model_dump()}
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def get_chunk_size(self) -> int:
        """Get configured chunk size in tokens."""
        return self.config.processing_config['chunk_size']
    
    def get_chunk_overlap(self) -> float:
        """Get configured chunk overlap as fraction."""
        return self.config.processing_config['chunk_overlap']
    
    def get_preserve_tables(self) -> bool:
        """Get table preservation setting."""
        return self.config.processing_config['preserve_tables']
    
    def get_preserve_equations(self) -> bool:
        """Get equation preservation setting."""
        return self.config.processing_config['preserve_equations']
    
    def get_enrich_formulas(self) -> bool:
        """Get formula enrichment setting."""
        return self.config.processing_config.get('enrich_formulas', True)
    
    def get_exclude_references(self) -> bool:
        """Get reference exclusion setting."""
        return self.config.processing_config.get('exclude_references', True)
    
    def get_exclude_acknowledgments(self) -> bool:
        """Get acknowledgments exclusion setting."""
        return self.config.processing_config.get('exclude_acknowledgments', True)
    
    def get_exclude_author_lists(self) -> bool:
        """Get author list exclusion setting."""
        return self.config.processing_config.get('exclude_author_lists', True)
    
    def get_include_authors_metadata(self) -> bool:
        """Get whether to include authors in metadata."""
        return self.config.processing_config.get('include_authors_metadata', False)
    
    def get_embedding_model_name(self) -> str:
        """Get embedding model name."""
        embedding_config: Dict[str, Any] = self.config.model_dump().get('embedding_config', {})
        return embedding_config.get('model_name', 'BAAI/bge-large-en-v1.5')
    
    def get_use_model_tokenizer(self) -> bool:
        """Get whether to use the embedding model's tokenizer."""
        embedding_config: Dict[str, Any] = self.config.model_dump().get('embedding_config', {})
        return embedding_config.get('use_model_tokenizer', True)
    
    def get_model_cache_dir(self) -> str:
        """Get model cache directory."""
        embedding_config: Dict[str, Any] = self.config.model_dump().get('embedding_config', {})
        return embedding_config.get('cache_dir', '.model_cache')
    
    def get_processing_timeout(self) -> int:
        """Get processing timeout in seconds (0 = no timeout)."""
        return self.config.processing_config.get('processing_timeout', 600)
    
    def get_table_mode(self) -> str:
        """Get table processing mode ('fast' or 'accurate')."""
        return self.config.processing_config.get('table_mode', 'fast')

"""
Adapter Registry

Discovers and instantiates adapters based on configuration.
Uses Python entry points for plugin discovery.
"""

from typing import Dict, Type, Any, Protocol
import importlib.metadata


class AdapterRegistry:
    """Registry for discovering and loading adapters."""
    
    def __init__(self):
        self._adapters: Dict[str, Type] = {}
    
    def register(self, name: str, adapter_class: Type) -> None:
        """Register an adapter implementation."""
        self._adapters[name] = adapter_class
    
    def get(self, name: str) -> Type:
        """Get adapter class by name."""
        if name not in self._adapters:
            raise KeyError(f"Adapter '{name}' not registered")
        return self._adapters[name]
    
    def discover(self, entry_point_group: str) -> None:
        """
        Discover adapters via entry points.
        
        Args:
            entry_point_group: Entry point group name (e.g., 'hepilot.scrapers')
        """
        for entry_point in importlib.metadata.entry_points().get(entry_point_group, []):
            adapter_class = entry_point.load()
            self.register(entry_point.name, adapter_class)


# Global registries
scraper_registry = AdapterRegistry()
cleaner_registry = AdapterRegistry()
chunker_registry = AdapterRegistry()
docstore_registry = AdapterRegistry()

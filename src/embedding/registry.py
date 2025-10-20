"""
Embedding Engine Adapter Registry

Discovers and instantiates embedding adapters based on configuration.
"""

from typing import Dict, Type, Any, List
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
    
    def list(self) -> List[str]:
        """List all registered adapter names."""
        return list(self._adapters.keys())
    
    def discover(self, entry_point_group: str) -> None:
        """
        Discover adapters via entry points.
        
        Args:
            entry_point_group: Entry point group name (e.g., 'hepilot.encoders')
        """
        for entry_point in importlib.metadata.entry_points().get(entry_point_group, []):
            adapter_class = entry_point.load()
            self.register(entry_point.name, adapter_class)


# Global registries for embedding components
encoder_registry = AdapterRegistry()
vectordb_registry = AdapterRegistry()
decoder_registry = AdapterRegistry()

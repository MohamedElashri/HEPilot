"""Tests for collector registry system."""

import pytest
from src.collector.registry import AdapterRegistry


class TestAdapterRegistry:
    """Test adapter registry functionality."""

    def test_registry_creation(self):
        """Test creating a new registry."""
        registry = AdapterRegistry()
        assert registry is not None
        assert len(registry._adapters) == 0

    def test_register_adapter(self):
        """Test registering an adapter."""
        registry = AdapterRegistry()

        class DummyAdapter:
            pass

        registry.register("test_adapter", DummyAdapter)
        assert "test_adapter" in registry._adapters
        assert registry.get("test_adapter") == DummyAdapter

    def test_register_duplicate_adapter_overwrites(self):
        """Test registering duplicate adapter overwrites."""
        registry = AdapterRegistry()

        class Adapter1:
            pass

        class Adapter2:
            pass

        registry.register("test", Adapter1)
        registry.register("test", Adapter2)

        assert registry.get("test") == Adapter2

    def test_get_adapter(self):
        """Test retrieving registered adapter."""
        registry = AdapterRegistry()

        class DummyAdapter:
            pass

        registry.register("test_adapter", DummyAdapter)
        adapter = registry.get("test_adapter")

        assert adapter == DummyAdapter

    def test_get_nonexistent_adapter_raises(self):
        """Test getting nonexistent adapter raises KeyError."""
        registry = AdapterRegistry()

        with pytest.raises(KeyError) as exc_info:
            registry.get("nonexistent")

        assert "nonexistent" in str(exc_info.value)

    def test_list_adapters(self):
        """Test listing all registered adapters."""
        registry = AdapterRegistry()

        class Adapter1:
            pass

        class Adapter2:
            pass

        registry.register("adapter1", Adapter1)
        registry.register("adapter2", Adapter2)

        adapters = registry.list()
        assert "adapter1" in adapters
        assert "adapter2" in adapters
        assert len(adapters) == 2

    def test_list_empty_registry(self):
        """Test listing empty registry."""
        registry = AdapterRegistry()
        adapters = registry.list()

        assert adapters == []

    def test_contains_adapter(self):
        """Test checking if adapter exists."""
        registry = AdapterRegistry()

        class DummyAdapter:
            pass

        registry.register("test", DummyAdapter)

        assert registry.contains("test")
        assert not registry.contains("nonexistent")

    def test_registry_isolation(self):
        """Test that different registries are isolated."""
        registry1 = AdapterRegistry()
        registry2 = AdapterRegistry()

        class Adapter1:
            pass

        registry1.register("test", Adapter1)

        assert registry1.contains("test")
        assert not registry2.contains("test")


class TestGlobalRegistries:
    """Test global registry instances."""

    def test_scraper_registry_exists(self):
        """Test scraper registry is available."""
        from src.collector.registry import scraper_registry

        assert scraper_registry is not None

    def test_cleaner_registry_exists(self):
        """Test cleaner registry is available."""
        from src.collector.registry import cleaner_registry

        assert cleaner_registry is not None

    def test_chunker_registry_exists(self):
        """Test chunker registry is available."""
        from src.collector.registry import chunker_registry

        assert chunker_registry is not None

    def test_docstore_registry_exists(self):
        """Test docstore registry is available."""
        from src.collector.registry import docstore_registry

        assert docstore_registry is not None

    def test_arxiv_adapters_registered(self):
        """Test ArXiv adapters are auto-registered."""
        from src.collector.registry import (
            scraper_registry,
            cleaner_registry,
            chunker_registry,
            docstore_registry,
        )

        # These should be registered by the adapters __init__.py
        assert scraper_registry.contains("arxiv_pdf")
        assert cleaner_registry.contains("arxiv_docling")
        assert chunker_registry.contains("arxiv_chunker")
        assert docstore_registry.contains("arxiv_docstore")

    def test_arxiv_adapter_classes(self):
        """Test ArXiv adapter classes can be retrieved."""
        from src.collector.registry import (
            scraper_registry,
            cleaner_registry,
            chunker_registry,
            docstore_registry,
        )
        from src.collector.adapters.arxiv.ports_impl import (
            ArxivScraper,
            ArxivCleaner,
            ArxivChunkerAdapter,
            ArxivInMemoryDocStore,
        )

        assert scraper_registry.get("arxiv_pdf") == ArxivScraper
        assert cleaner_registry.get("arxiv_docling") == ArxivCleaner
        assert chunker_registry.get("arxiv_chunker") == ArxivChunkerAdapter
        assert docstore_registry.get("arxiv_docstore") == ArxivInMemoryDocStore

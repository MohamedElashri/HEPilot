"""Adapter registrations for the collector layer."""

from src.collector.registry import (
	chunker_registry,
	cleaner_registry,
	docstore_registry,
	scraper_registry,
)

from .arxiv.ports_impl import (
	ArxivChunkerAdapter,
	ArxivCleaner,
	ArxivInMemoryDocStore,
	ArxivScraper,
)

scraper_registry.register("arxiv_pdf", ArxivScraper)
cleaner_registry.register("arxiv_docling", ArxivCleaner)
chunker_registry.register("arxiv_chunker", ArxivChunkerAdapter)
docstore_registry.register("arxiv_docstore", ArxivInMemoryDocStore)

__all__ = [
	"ArxivScraper",
	"ArxivCleaner",
	"ArxivChunkerAdapter",
	"ArxivInMemoryDocStore",
]

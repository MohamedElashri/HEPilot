"""Collector package public interface."""

# Ensure adapter registrations execute on import.
from . import adapters as _collector_adapters  # noqa: F401

from .pipeline import (
    CollectorError,
    CollectorPipeline,
    CollectorRequest,
    CollectorResult,
    ProcessedDocument,
)

__all__ = [
    "CollectorPipeline",
    "CollectorRequest",
    "CollectorResult",
    "ProcessedDocument",
    "CollectorError",
]


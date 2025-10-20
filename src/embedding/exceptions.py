"""
Embedding Engine Exceptions

Custom exception types for the embedding pipeline.
"""


class EmbeddingError(Exception):
    """Base exception for embedding engine errors."""
    pass


class EncoderError(EmbeddingError):
    """Error during text encoding."""
    pass


class VectorDBError(EmbeddingError):
    """Error during vector database operations."""
    pass


class DecoderError(EmbeddingError):
    """Error during content decoding/retrieval."""
    pass


class ConfigurationError(EmbeddingError):
    """Error in configuration or setup."""
    pass


class PipelineError(EmbeddingError):
    """Error during pipeline execution."""
    pass

"""Embedding layer adapters with auto-registration."""

from src.embedding.adapters.postgres_docstore import PostgresDocStore
from src.embedding.adapters.postgres_decoder import PostgresDecoder
from src.embedding.adapters.onnx_bge_encoder import ONNXBGEEncoder
from src.embedding.adapters.chroma_vectordb import ChromaVectorDB

# Import registries for auto-registration
from src.embedding.registry import encoder_registry, vectordb_registry, decoder_registry

# Auto-register available adapters
encoder_registry.register("onnx_bge", ONNXBGEEncoder)
vectordb_registry.register("chroma", ChromaVectorDB)
decoder_registry.register("postgres", PostgresDecoder)

__all__ = [
    "PostgresDocStore",
    "PostgresDecoder",
    "ONNXBGEEncoder",
    "ChromaVectorDB",
]

"""
Embedding Engine Port Interfaces

Defines abstract protocols for the embedding pipeline:
- Encoder: Text to vector transformation
- VectorDB: Vector storage and similarity search
- Decoder: Vector ID to original text retrieval
"""

from typing import Protocol, List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray


@dataclass
class QueryResult:
    """Single similarity search result."""
    chunk_id: str
    score: float
    metadata: Dict[str, Any]


@dataclass
class ChunkContent:
    """Decoded chunk with full content and metadata."""
    chunk_id: str
    text: str
    document_id: str
    source_type: str
    section_path: List[str]
    position_in_doc: int
    token_count: int
    overlap_start: int
    overlap_end: int
    source_url: str
    created_at: str
    additional_metadata: Dict[str, Any]


class Encoder(Protocol):
    """
    Text-to-vector encoding interface.
    
    Implementations MUST:
    - Return normalized vectors (unit length)
    - Support batch processing
    - Be deterministic (same text → same vector)
    - Handle long texts gracefully (truncate or error)
    """
    
    async def embed(self, texts: List[str]) -> NDArray[np.float32]:
        """
        Encode text strings to vectors.
        
        Args:
            texts: List of text strings to encode
            
        Returns:
            2D array of shape (len(texts), embedding_dim)
            
        Raises:
            EncoderError: If encoding fails
        """
        ...
    
    @property
    def dimension(self) -> int:
        """Vector dimensionality (e.g., 384, 768, 1024)."""
        ...
    
    @property
    def max_tokens(self) -> int:
        """Maximum token length supported."""
        ...
    
    async def health_check(self) -> bool:
        """Verify encoder is operational."""
        ...


class VectorDB(Protocol):
    """
    Vector storage and similarity search interface.
    
    Implementations MUST:
    - Store vectors with associated IDs
    - Support similarity search (cosine or dot-product)
    - Handle batch upserts efficiently
    - Maintain index consistency
    """
    
    async def upsert(
        self,
        ids: List[str],
        vectors: NDArray[np.float32],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Insert or update vectors.
        
        Args:
            ids: Unique identifiers (chunk UUIDs)
            vectors: 2D array of shape (len(ids), dimension)
            metadata: Optional metadata dicts (NOT content!)
            
        Raises:
            VectorDBError: If upsert fails
        """
        ...
    
    async def query(
        self,
        vector: NDArray[np.float32],
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[QueryResult]:
        """
        Find most similar vectors.
        
        Args:
            vector: Query vector (1D array)
            top_k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            Ranked list of QueryResult objects
            
        Raises:
            VectorDBError: If query fails
        """
        ...
    
    async def delete(self, ids: List[str]) -> None:
        """
        Remove vectors by ID.
        
        Args:
            ids: List of chunk IDs to remove
            
        Raises:
            VectorDBError: If deletion fails
        """
        ...
    
    async def count(self) -> int:
        """
        Total number of vectors in store.
        
        Returns:
            Count of stored vectors
        """
        ...
    
    async def health_check(self) -> bool:
        """Verify vector store is operational."""
        ...


class Decoder(Protocol):
    """
    Vector ID to original content retrieval.
    
    CRITICAL: Decoder MUST fetch content from PostgreSQL,
    NOT from vector store payloads. This ensures traceability.
    """
    
    async def lookup(self, chunk_ids: List[str]) -> List[Optional[ChunkContent]]:
        """
        Retrieve full chunk content by IDs.
        
        Args:
            chunk_ids: List of chunk UUIDs
            
        Returns:
            List of ChunkContent objects in same order.
            Missing IDs return None in that position.
            
        Raises:
            DecoderError: If database query fails
        """
        ...
    
    async def get_document_chunks(
        self,
        document_id: str,
        limit: Optional[int] = None
    ) -> List[ChunkContent]:
        """
        Get all chunks for a document.
        
        Args:
            document_id: Document UUID
            limit: Optional limit on number of chunks
            
        Returns:
            List of chunks ordered by position
            
        Raises:
            DecoderError: If database query fails
        """
        ...
    
    async def health_check(self) -> bool:
        """Verify database connection."""
        ...

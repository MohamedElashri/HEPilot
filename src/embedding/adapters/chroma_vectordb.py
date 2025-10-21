"""ChromaDB-based vector storage adapter.

Implements VectorDB protocol for storing and searching embeddings using ChromaDB.
"""

import asyncio
import chromadb
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection
from typing import List, Dict, Any, Optional
import numpy as np
from numpy.typing import NDArray
from pathlib import Path

from src.embedding.ports import QueryResult
from src.embedding.exceptions import VectorDBError


class ChromaVectorDB:
    """
    Vector storage using ChromaDB.
    
    Provides persistent vector storage with similarity search capabilities.
    Supports batch operations and metadata filtering.
    """
    
    def __init__(
        self,
        persist_directory: Path = Path(".data/chroma"),
        collection_name: str = "hepilot",
        distance_metric: str = "cosine"
    ):
        """
        Initialize ChromaDB adapter.
        
        Args:
            persist_directory: Directory for ChromaDB storage
            collection_name: Name of the collection to use
            distance_metric: Distance metric ("cosine", "l2", or "ip")
        """
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self.distance_metric = distance_metric
        
        self.client: Optional[chromadb.ClientAPI] = None
        self.collection: Optional[Collection] = None
    
    async def setup(self) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._setup_sync)
        except Exception as e:
            raise VectorDBError(f"Failed to initialize ChromaDB: {e}")
    
    def _setup_sync(self) -> None:
        """Synchronous setup (runs in executor)."""
        # Create persist directory
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=False
            )
        )
        
        # Get or create collection with distance metric
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": self.distance_metric}
        )
    
    async def upsert(
        self,
        ids: List[str],
        vectors: NDArray[np.float32],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Insert or update vectors in the collection.
        
        Args:
            ids: Unique chunk IDs (UUIDs)
            vectors: 2D array of embeddings (len(ids), dimension)
            metadata: Optional metadata dicts (without content)
            
        Raises:
            VectorDBError: If upsert fails
        """
        if not self.collection:
            await self.setup()
        
        if len(ids) == 0:
            return
        
        if len(ids) != len(vectors):
            raise VectorDBError(
                f"Mismatch: {len(ids)} IDs but {len(vectors)} vectors"
            )
        
        if metadata and len(metadata) != len(ids):
            raise VectorDBError(
                f"Mismatch: {len(ids)} IDs but {len(metadata)} metadata dicts"
            )
        
        try:
            # Convert numpy array to list of lists for ChromaDB
            embeddings_list = vectors.tolist()
            
            # Prepare metadata (ensure all values are JSON-serializable)
            metadatas = None
            if metadata:
                metadatas = [self._sanitize_metadata(m) for m in metadata]
            
            # Run upsert in executor to avoid blocking
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None,
                lambda: self.collection.upsert(
                    ids=ids,
                    embeddings=embeddings_list,
                    metadatas=metadatas
                )
            )
        except Exception as e:
            raise VectorDBError(f"Failed to upsert vectors: {e}")
    
    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize metadata for ChromaDB storage.
        
        ChromaDB requires metadata values to be strings, ints, floats, or bools.
        """
        sanitized = {}
        for key, value in metadata.items():
            if value is None:
                sanitized[key] = ""
            elif isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, (list, dict)):
                # Convert complex types to strings
                sanitized[key] = str(value)
            else:
                sanitized[key] = str(value)
        return sanitized
    
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
            filter_dict: Optional metadata filters (ChromaDB where clause)
            
        Returns:
            Ranked list of QueryResult objects
            
        Raises:
            VectorDBError: If query fails
        """
        if not self.collection:
            await self.setup()
        
        if vector.ndim != 1:
            raise VectorDBError(
                f"Query vector must be 1D, got shape {vector.shape}"
            )
        
        try:
            # Convert to list for ChromaDB
            query_embedding = vector.tolist()
            
            # Run query in executor
            loop = asyncio.get_running_loop()
            results = await loop.run_in_executor(
                None,
                lambda: self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=filter_dict
                )
            )
            
            # Parse results
            query_results = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i, chunk_id in enumerate(results['ids'][0]):
                    score = results['distances'][0][i] if results.get('distances') else 0.0
                    metadata = results['metadatas'][0][i] if results.get('metadatas') else {}
                    
                    query_results.append(QueryResult(
                        chunk_id=chunk_id,
                        score=float(score),
                        metadata=metadata
                    ))
            
            return query_results
            
        except Exception as e:
            raise VectorDBError(f"Failed to query vectors: {e}")
    
    async def delete(self, ids: List[str]) -> None:
        """
        Remove vectors by ID.
        
        Args:
            ids: List of chunk IDs to remove
            
        Raises:
            VectorDBError: If deletion fails
        """
        if not self.collection:
            await self.setup()
        
        if len(ids) == 0:
            return
        
        try:
            # Run delete in executor
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None,
                lambda: self.collection.delete(ids=ids)
            )
        except Exception as e:
            raise VectorDBError(f"Failed to delete vectors: {e}")
    
    async def count(self) -> int:
        """
        Get total number of vectors in collection.
        
        Returns:
            Count of stored vectors
            
        Raises:
            VectorDBError: If count fails
        """
        if not self.collection:
            await self.setup()
        
        try:
            # Run count in executor
            loop = asyncio.get_running_loop()
            count = await loop.run_in_executor(
                None,
                lambda: self.collection.count()
            )
            return count
        except Exception as e:
            raise VectorDBError(f"Failed to count vectors: {e}")
    
    async def clear(self) -> None:
        """
        Remove all vectors from collection.
        
        Raises:
            VectorDBError: If clear fails
        """
        if not self.collection:
            await self.setup()
        
        try:
            # Get all IDs and delete them
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.collection.get(include=[])
            )
            
            if result['ids']:
                await self.delete(result['ids'])
                
        except Exception as e:
            raise VectorDBError(f"Failed to clear collection: {e}")
    
    async def health_check(self) -> bool:
        """
        Verify ChromaDB is operational.
        
        Returns:
            True if operational, False otherwise
        """
        try:
            if not self.collection:
                await self.setup()
            
            # Try to count - this verifies connection
            await self.count()
            return True
            
        except Exception:
            return False
    
    async def close(self) -> None:
        """
        Close ChromaDB connection.
        
        Note: ChromaDB's PersistentClient doesn't require explicit closing,
        but this is here for protocol compliance and future-proofing.
        """
        # ChromaDB handles cleanup automatically
        self.collection = None
        self.client = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.setup()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

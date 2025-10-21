"""Pipeline orchestrators for ingestion and retrieval.

Coordinates the embedding layer components to provide complete workflows:
- IngestionPipeline: Store documents and generate embeddings
- RetrievalPipeline: Search and retrieve relevant content
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from uuid import UUID
import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass
import json

from src.embedding.config import EmbeddingConfig, load_config
from src.embedding.adapters import (
    PostgresDocStore,
    PostgresDecoder,
    ONNXBGEEncoder,
    ChromaVectorDB
)
from src.embedding.ports import QueryResult, ChunkContent
from src.embedding.exceptions import (
    DocStoreError,
    EncoderError,
    VectorDBError,
    DecoderError
)


def _normalize_db_url(url: str) -> str:
    """
    Normalize database URL for asyncpg.
    
    asyncpg expects 'postgresql://' but SQLAlchemy uses 'postgresql+asyncpg://'.
    This function converts between the formats.
    
    Args:
        url: Database URL (can be postgresql:// or postgresql+asyncpg://)
    
    Returns:
        Normalized URL for asyncpg
    """
    if url.startswith('postgresql+asyncpg://'):
        return url.replace('postgresql+asyncpg://', 'postgresql://')
    return url


@dataclass
class IngestionResult:
    """Result of ingestion pipeline."""
    documents_processed: int
    chunks_processed: int
    vectors_stored: int
    errors: List[str]


@dataclass
class RetrievalResult:
    """Result of retrieval pipeline with ranked chunks."""
    chunks: List[ChunkContent]
    scores: List[float]
    query_time_ms: float


class IngestionPipeline:
    """
    Orchestrates document ingestion and embedding generation.
    
    Flow:
    1. Store documents in PostgreSQL (DocStore)
    2. Store chunks in PostgreSQL (DocStore)
    3. Generate embeddings (Encoder)
    4. Store vectors in ChromaDB (VectorDB)
    
    All components are initialized from configuration with no hardcoding.
    """
    
    def __init__(self, config: EmbeddingConfig):
        """
        Initialize ingestion pipeline from configuration.
        
        Args:
            config: Validated embedding configuration
        """
        self.config = config
        
        # Initialize components (will be set up later)
        self.docstore: Optional[PostgresDocStore] = None
        self.encoder: Optional[ONNXBGEEncoder] = None
        self.vectordb: Optional[ChromaVectorDB] = None
        
        # Pipeline settings from config
        self.batch_size = config.pipeline.batch_size
        self.max_workers = config.pipeline.max_workers
        self.checkpoint_interval = config.pipeline.checkpoint_interval
    
    async def setup(self) -> None:
        """Initialize all pipeline components."""
        # Normalize database URL for asyncpg
        db_url = _normalize_db_url(self.config.docstore.database_url)
        
        # Initialize DocStore from config
        self.docstore = PostgresDocStore(
            database_url=db_url,
            pool_size=self.config.docstore.pool_size
        )
        await self.docstore.connect()
        
        # Initialize Encoder from config
        self.encoder = ONNXBGEEncoder(
            model_name=self.config.encoder.model_name,
            cache_dir=Path(self.config.encoder.cache_dir),
            batch_size=self.config.encoder.batch_size,
            normalize=self.config.encoder.normalize,
            device=self.config.encoder.device
        )
        await self.encoder.load_model()
        
        # Initialize VectorDB from config
        self.vectordb = ChromaVectorDB(
            persist_directory=Path(self.config.vectordb.persist_directory),
            collection_name=self.config.vectordb.collection_name,
            distance_metric=self.config.vectordb.distance_metric
        )
        await self.vectordb.setup()
    
    async def ingest_document(
        self,
        document_metadata: Dict[str, Any],
        chunks: List[Dict[str, Any]]
    ) -> IngestionResult:
        """
        Ingest a single document with its chunks.
        
        Args:
            document_metadata: Document metadata dict with keys:
                - source_type, source_id, title, authors, publication_date,
                  source_url, metadata
            chunks: List of chunk dicts with keys:
                - text, section_path, position_in_doc, token_count,
                  overlap_start, overlap_end, metadata
        
        Returns:
            IngestionResult with statistics
        """
        if not self.docstore or not self.encoder or not self.vectordb:
            await self.setup()
        
        errors = []
        chunks_processed = 0
        vectors_stored = 0
        
        try:
            # 1. Store document in PostgreSQL
            doc_id = await self.docstore.add_document(
                source_type=document_metadata['source_type'],
                source_id=document_metadata['source_id'],
                title=document_metadata.get('title'),
                authors=document_metadata.get('authors'),
                publication_date=document_metadata.get('publication_date'),
                source_url=document_metadata.get('source_url'),
                metadata=document_metadata.get('metadata', {})
            )
            
            # 2. Store chunks in batches
            chunk_ids = []
            chunk_texts = []
            
            for i in range(0, len(chunks), self.batch_size):
                batch = chunks[i:i + self.batch_size]
                
                # Prepare batch data
                batch_data = []
                for chunk in batch:
                    batch_data.append({
                        'doc_id': doc_id,
                        'text': chunk['text'],
                        'section_path': chunk.get('section_path', []),
                        'position_in_doc': chunk['position_in_doc'],
                        'token_count': chunk['token_count'],
                        'overlap_start': chunk.get('overlap_start', 0),
                        'overlap_end': chunk.get('overlap_end', 0),
                        'metadata': chunk.get('metadata', {})
                    })
                
                # Store batch in DocStore
                batch_ids = await self.docstore.add_chunks(batch_data)
                chunk_ids.extend(batch_ids)
                chunk_texts.extend([chunk['text'] for chunk in batch])
                chunks_processed += len(batch)
            
            # 3. Generate embeddings in batches
            for i in range(0, len(chunk_texts), self.batch_size):
                batch_texts = chunk_texts[i:i + self.batch_size]
                batch_ids = chunk_ids[i:i + self.batch_size]
                
                # Encode batch
                embeddings = await self.encoder.embed(batch_texts)
                
                # 4. Store vectors in ChromaDB
                # Prepare minimal metadata (no content)
                metadata_batch = [
                    {
                        'doc_id': str(doc_id),
                        'position': chunks[i + j]['position_in_doc']
                    }
                    for j in range(len(batch_texts))
                ]
                
                await self.vectordb.upsert(
                    ids=batch_ids,
                    vectors=embeddings,
                    metadata=metadata_batch
                )
                vectors_stored += len(batch_ids)
            
            return IngestionResult(
                documents_processed=1,
                chunks_processed=chunks_processed,
                vectors_stored=vectors_stored,
                errors=errors
            )
            
        except (DocStoreError, EncoderError, VectorDBError) as e:
            errors.append(f"Ingestion failed: {e}")
            return IngestionResult(
                documents_processed=0,
                chunks_processed=chunks_processed,
                vectors_stored=vectors_stored,
                errors=errors
            )
    
    async def ingest_documents(
        self,
        documents: List[Tuple[Dict[str, Any], List[Dict[str, Any]]]]
    ) -> IngestionResult:
        """
        Ingest multiple documents.
        
        Args:
            documents: List of (document_metadata, chunks) tuples
        
        Returns:
            Aggregated IngestionResult
        """
        total_docs = 0
        total_chunks = 0
        total_vectors = 0
        all_errors = []
        
        for doc_metadata, chunks in documents:
            result = await self.ingest_document(doc_metadata, chunks)
            total_docs += result.documents_processed
            total_chunks += result.chunks_processed
            total_vectors += result.vectors_stored
            all_errors.extend(result.errors)
        
        return IngestionResult(
            documents_processed=total_docs,
            chunks_processed=total_chunks,
            vectors_stored=total_vectors,
            errors=all_errors
        )
    
    async def health_check(self) -> Dict[str, bool]:
        """
        Check health of all pipeline components.
        
        Returns:
            Dict with component health status
        """
        if not self.docstore or not self.encoder or not self.vectordb:
            await self.setup()
        
        return {
            'docstore': await self.docstore.health_check(),
            'encoder': await self.encoder.health_check(),
            'vectordb': await self.vectordb.health_check()
        }
    
    async def close(self) -> None:
        """Close all pipeline components."""
        if self.docstore:
            await self.docstore.close()
        if self.encoder:
            await self.encoder.close()
        if self.vectordb:
            await self.vectordb.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.setup()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


class RetrievalPipeline:
    """
    Orchestrates query processing and content retrieval.
    
    Flow:
    1. Encode query text (Encoder)
    2. Search similar vectors (VectorDB)
    3. Decode chunk IDs to content (Decoder)
    4. Return ranked results
    
    All components are initialized from configuration with no hardcoding.
    """
    
    def __init__(self, config: EmbeddingConfig):
        """
        Initialize retrieval pipeline from configuration.
        
        Args:
            config: Validated embedding configuration
        """
        self.config = config
        
        # Initialize components (will be set up later)
        self.encoder: Optional[ONNXBGEEncoder] = None
        self.vectordb: Optional[ChromaVectorDB] = None
        self.decoder: Optional[PostgresDecoder] = None
    
    async def setup(self) -> None:
        """Initialize all pipeline components."""
        # Initialize Encoder from config
        self.encoder = ONNXBGEEncoder(
            model_name=self.config.encoder.model_name,
            cache_dir=Path(self.config.encoder.cache_dir),
            batch_size=self.config.encoder.batch_size,
            normalize=self.config.encoder.normalize,
            device=self.config.encoder.device
        )
        await self.encoder.load_model()
        
        # Initialize VectorDB from config
        self.vectordb = ChromaVectorDB(
            persist_directory=Path(self.config.vectordb.persist_directory),
            collection_name=self.config.vectordb.collection_name,
            distance_metric=self.config.vectordb.distance_metric
        )
        await self.vectordb.setup()
        
        # Normalize database URL for asyncpg
        db_url = _normalize_db_url(self.config.docstore.database_url)
        
        # Initialize Decoder from config
        self.decoder = PostgresDecoder(
            database_url=db_url,
            pool_size=self.config.docstore.pool_size
        )
        await self.decoder.connect()
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> RetrievalResult:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: Query text
            top_k: Number of results to return
            filter_dict: Optional metadata filters for VectorDB
        
        Returns:
            RetrievalResult with ranked chunks
        """
        if not self.encoder or not self.vectordb or not self.decoder:
            await self.setup()
        
        import time
        start_time = time.time()
        
        try:
            # 1. Encode query
            query_embeddings = await self.encoder.embed([query])
            query_vector = query_embeddings[0]
            
            # 2. Search similar vectors
            search_results = await self.vectordb.query(
                vector=query_vector,
                top_k=top_k,
                filter_dict=filter_dict
            )
            
            # 3. Decode chunk IDs to content
            chunk_ids = [result.chunk_id for result in search_results]
            scores = [result.score for result in search_results]
            
            chunks = await self.decoder.lookup(chunk_ids)
            
            # Filter out None results (missing chunks)
            valid_results = [
                (chunk, score)
                for chunk, score in zip(chunks, scores)
                if chunk is not None
            ]
            
            valid_chunks = [chunk for chunk, _ in valid_results]
            valid_scores = [score for _, score in valid_results]
            
            query_time = (time.time() - start_time) * 1000
            
            return RetrievalResult(
                chunks=valid_chunks,
                scores=valid_scores,
                query_time_ms=query_time
            )
            
        except (EncoderError, VectorDBError, DecoderError) as e:
            # Return empty result on error
            query_time = (time.time() - start_time) * 1000
            return RetrievalResult(
                chunks=[],
                scores=[],
                query_time_ms=query_time
            )
    
    async def retrieve_by_document(
        self,
        document_id: str,
        limit: Optional[int] = None
    ) -> List[ChunkContent]:
        """
        Retrieve all chunks for a specific document.
        
        Args:
            document_id: Document UUID
            limit: Optional limit on number of chunks
        
        Returns:
            List of chunks ordered by position
        """
        if not self.decoder:
            await self.setup()
        
        return await self.decoder.get_document_chunks(document_id, limit)
    
    async def health_check(self) -> Dict[str, bool]:
        """
        Check health of all pipeline components.
        
        Returns:
            Dict with component health status
        """
        if not self.encoder or not self.vectordb or not self.decoder:
            await self.setup()
        
        return {
            'encoder': await self.encoder.health_check(),
            'vectordb': await self.vectordb.health_check(),
            'decoder': await self.decoder.health_check()
        }
    
    async def close(self) -> None:
        """Close all pipeline components."""
        if self.encoder:
            await self.encoder.close()
        if self.vectordb:
            await self.vectordb.close()
        if self.decoder:
            await self.decoder.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.setup()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


def create_ingestion_pipeline(config_path: Optional[Path] = None) -> IngestionPipeline:
    """
    Factory function to create ingestion pipeline from config file.
    
    Args:
        config_path: Path to config file (default: config/embedding.toml)
    
    Returns:
        Configured IngestionPipeline instance
    """
    if config_path is None:
        config_path = Path("config/embedding.toml")
    
    config = load_config(config_path)
    return IngestionPipeline(config)


def create_retrieval_pipeline(config_path: Optional[Path] = None) -> RetrievalPipeline:
    """
    Factory function to create retrieval pipeline from config file.
    
    Args:
        config_path: Path to config file (default: config/embedding.toml)
    
    Returns:
        Configured RetrievalPipeline instance
    """
    if config_path is None:
        config_path = Path("config/embedding.toml")
    
    config = load_config(config_path)
    return RetrievalPipeline(config)

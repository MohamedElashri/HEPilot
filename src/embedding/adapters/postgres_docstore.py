"""PostgreSQL-based document storage for embedding layer."""

import asyncpg
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
import json

from src.embedding.exceptions import DocStoreError


class PostgresDocStore:
    """Store documents and chunks in PostgreSQL.
    
    This class provides async methods to store and manage:
    - Documents (papers, articles, etc.)
    - Document segments/chunks (text snippets from documents)
    
    Uses asyncpg for efficient async database operations.
    """
    
    def __init__(self, database_url: str, pool_size: int = 10, max_overflow: int = 20):
        """Initialize DocStore.
        
        Args:
            database_url: PostgreSQL connection URL (asyncpg format)
            pool_size: Size of connection pool
            max_overflow: Maximum overflow connections
        """
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Establish database connection pool.
        
        Raises:
            DocStoreError: If connection fails
        """
        if self.pool is not None:
            # Already connected
            return
            
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=self.pool_size
            )
        except Exception as e:
            raise DocStoreError(f"Failed to connect to database: {e}")
    
    async def close(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    async def add_document(
        self,
        doc_id: UUID,
        source_type: str,
        source_id: str,
        title: Optional[str] = None,
        authors: Optional[List[Dict]] = None,
        publication_date: Optional[datetime] = None,
        source_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """Insert or update a document.
        
        Uses UPSERT (ON CONFLICT) to handle duplicate (source_type, source_id).
        
        Args:
            doc_id: Unique document identifier
            source_type: Source type (e.g., "arxiv", "pubmed")
            source_id: External identifier (e.g., arXiv ID)
            title: Document title
            authors: List of author information
            publication_date: Publication date
            source_url: URL to source
            metadata: Additional metadata as dict
            
        Returns:
            UUID of inserted/updated document
            
        Raises:
            DocStoreError: If operation fails
        """
        if not self.pool:
            raise DocStoreError("Not connected to database. Call connect() first.")
            
        query = """
        INSERT INTO documents (id, source_type, source_id, title, authors, 
                              publication_date, source_url, meta)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (source_type, source_id) 
        DO UPDATE SET 
            title = EXCLUDED.title,
            authors = EXCLUDED.authors,
            publication_date = EXCLUDED.publication_date,
            source_url = EXCLUDED.source_url,
            meta = EXCLUDED.meta
        RETURNING id
        """
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval(
                    query,
                    doc_id,
                    source_type,
                    source_id,
                    title,
                    json.dumps(authors) if authors else None,
                    publication_date,
                    source_url,
                    json.dumps(metadata) if metadata else None
                )
            return result
        except Exception as e:
            raise DocStoreError(f"Failed to add document: {e}")
    
    async def add_chunk(
        self,
        chunk_id: UUID,
        doc_id: UUID,
        text: str,
        position: int,
        token_count: int,
        section_path: Optional[List[str]] = None,
        overlap_start: int = 0,
        overlap_end: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """Insert a text chunk/segment.
        
        Args:
            chunk_id: Unique chunk identifier
            doc_id: Parent document ID
            text: The actual text content
            position: Position in document (0-indexed)
            token_count: Number of tokens in chunk
            section_path: Hierarchical section path (e.g., ["intro", "background"])
            overlap_start: Number of overlapping tokens at start
            overlap_end: Number of overlapping tokens at end
            metadata: Additional metadata as dict
            
        Returns:
            UUID of inserted chunk
            
        Raises:
            DocStoreError: If operation fails
        """
        if not self.pool:
            raise DocStoreError("Not connected to database. Call connect() first.")
            
        query = """
        INSERT INTO doc_segments (id, doc_id, text, section_path, position_in_doc,
                                 token_count, overlap_start, overlap_end, meta)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING id
        """
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval(
                    query,
                    chunk_id,
                    doc_id,
                    text,
                    json.dumps(section_path) if section_path else None,
                    position,
                    token_count,
                    overlap_start,
                    overlap_end,
                    json.dumps(metadata) if metadata else None
                )
            return result
        except Exception as e:
            raise DocStoreError(f"Failed to add chunk: {e}")
    
    async def add_chunks_batch(
        self,
        chunks: List[Dict[str, Any]]
    ) -> int:
        """Insert multiple chunks in a single transaction.
        
        Args:
            chunks: List of chunk dictionaries with keys:
                - chunk_id: UUID
                - doc_id: UUID
                - text: str
                - position: int
                - token_count: int
                - section_path: Optional[List[str]]
                - overlap_start: int (default: 0)
                - overlap_end: int (default: 0)
                - metadata: Optional[Dict]
                
        Returns:
            Number of chunks inserted
            
        Raises:
            DocStoreError: If operation fails
        """
        if not self.pool:
            raise DocStoreError("Not connected to database. Call connect() first.")
            
        if not chunks:
            return 0
            
        query = """
        INSERT INTO doc_segments (id, doc_id, text, section_path, position_in_doc,
                                 token_count, overlap_start, overlap_end, meta)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """
        
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    for chunk in chunks:
                        await conn.execute(
                            query,
                            chunk['chunk_id'],
                            chunk['doc_id'],
                            chunk['text'],
                            json.dumps(chunk.get('section_path')) if chunk.get('section_path') else None,
                            chunk['position'],
                            chunk['token_count'],
                            chunk.get('overlap_start', 0),
                            chunk.get('overlap_end', 0),
                            json.dumps(chunk.get('metadata')) if chunk.get('metadata') else None
                        )
            return len(chunks)
        except Exception as e:
            raise DocStoreError(f"Failed to add chunks in batch: {e}")
    
    async def get_document(self, doc_id: UUID) -> Optional[Dict[str, Any]]:
        """Retrieve a document by ID.
        
        Args:
            doc_id: Document UUID
            
        Returns:
            Document dict or None if not found
            
        Raises:
            DocStoreError: If operation fails
        """
        if not self.pool:
            raise DocStoreError("Not connected to database. Call connect() first.")
            
        query = """
        SELECT id, source_type, source_id, title, authors, publication_date,
               source_url, meta, created_at
        FROM documents
        WHERE id = $1
        """
        
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, doc_id)
                
            if not row:
                return None
                
            return {
                'id': str(row['id']),
                'source_type': row['source_type'],
                'source_id': row['source_id'],
                'title': row['title'],
                'authors': json.loads(row['authors']) if row['authors'] else None,
                'publication_date': row['publication_date'],
                'source_url': row['source_url'],
                'metadata': json.loads(row['meta']) if row['meta'] else None,
                'created_at': row['created_at']
            }
        except Exception as e:
            raise DocStoreError(f"Failed to get document: {e}")
    
    async def get_chunk(self, chunk_id: UUID) -> Optional[Dict[str, Any]]:
        """Retrieve a chunk by ID.
        
        Args:
            chunk_id: Chunk UUID
            
        Returns:
            Chunk dict or None if not found
            
        Raises:
            DocStoreError: If operation fails
        """
        if not self.pool:
            raise DocStoreError("Not connected to database. Call connect() first.")
            
        query = """
        SELECT id, doc_id, text, section_path, position_in_doc,
               token_count, overlap_start, overlap_end, meta, created_at
        FROM doc_segments
        WHERE id = $1
        """
        
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, chunk_id)
                
            if not row:
                return None
                
            return {
                'id': str(row['id']),
                'doc_id': str(row['doc_id']),
                'text': row['text'],
                'section_path': json.loads(row['section_path']) if row['section_path'] else None,
                'position': row['position_in_doc'],
                'token_count': row['token_count'],
                'overlap_start': row['overlap_start'],
                'overlap_end': row['overlap_end'],
                'metadata': json.loads(row['meta']) if row['meta'] else None,
                'created_at': row['created_at']
            }
        except Exception as e:
            raise DocStoreError(f"Failed to get chunk: {e}")
    
    async def get_document_chunks(self, doc_id: UUID) -> List[Dict[str, Any]]:
        """Retrieve all chunks for a document, ordered by position.
        
        Args:
            doc_id: Document UUID
            
        Returns:
            List of chunk dicts
            
        Raises:
            DocStoreError: If operation fails
        """
        if not self.pool:
            raise DocStoreError("Not connected to database. Call connect() first.")
            
        query = """
        SELECT id, doc_id, text, section_path, position_in_doc,
               token_count, overlap_start, overlap_end, meta, created_at
        FROM doc_segments
        WHERE doc_id = $1
        ORDER BY position_in_doc
        """
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, doc_id)
                
            return [
                {
                    'id': str(row['id']),
                    'doc_id': str(row['doc_id']),
                    'text': row['text'],
                    'section_path': json.loads(row['section_path']) if row['section_path'] else None,
                    'position': row['position_in_doc'],
                    'token_count': row['token_count'],
                    'overlap_start': row['overlap_start'],
                    'overlap_end': row['overlap_end'],
                    'metadata': json.loads(row['meta']) if row['meta'] else None,
                    'created_at': row['created_at']
                }
                for row in rows
            ]
        except Exception as e:
            raise DocStoreError(f"Failed to get document chunks: {e}")
    
    async def delete_document(self, doc_id: UUID) -> bool:
        """Delete a document and all its chunks (CASCADE).
        
        Args:
            doc_id: Document UUID
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            DocStoreError: If operation fails
        """
        if not self.pool:
            raise DocStoreError("Not connected to database. Call connect() first.")
            
        query = "DELETE FROM documents WHERE id = $1"
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(query, doc_id)
                
            # result is like "DELETE 1" or "DELETE 0"
            deleted_count = int(result.split()[-1])
            return deleted_count > 0
        except Exception as e:
            raise DocStoreError(f"Failed to delete document: {e}")
    
    async def count_documents(self) -> int:
        """Count total documents in database.
        
        Returns:
            Number of documents
            
        Raises:
            DocStoreError: If operation fails
        """
        if not self.pool:
            raise DocStoreError("Not connected to database. Call connect() first.")
            
        query = "SELECT COUNT(*) FROM documents"
        
        try:
            async with self.pool.acquire() as conn:
                count = await conn.fetchval(query)
            return count
        except Exception as e:
            raise DocStoreError(f"Failed to count documents: {e}")
    
    async def count_chunks(self) -> int:
        """Count total chunks in database.
        
        Returns:
            Number of chunks
            
        Raises:
            DocStoreError: If operation fails
        """
        if not self.pool:
            raise DocStoreError("Not connected to database. Call connect() first.")
            
        query = "SELECT COUNT(*) FROM doc_segments"
        
        try:
            async with self.pool.acquire() as conn:
                count = await conn.fetchval(query)
            return count
        except Exception as e:
            raise DocStoreError(f"Failed to count chunks: {e}")
    
    async def health_check(self) -> bool:
        """Check if database connection is healthy.
        
        Returns:
            True if connection is healthy, False otherwise
        """
        if not self.pool:
            return False
            
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception:
            return False
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

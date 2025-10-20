"""PostgreSQL-based decoder for retrieving chunk content by vector IDs."""

import asyncpg
from typing import List, Optional, Dict, Any
from uuid import UUID
import json

from src.embedding.ports import ChunkContent
from src.embedding.exceptions import DecoderError


class PostgresDecoder:
    """Retrieve chunk content from PostgreSQL by vector IDs.
    
    This class implements the Decoder protocol to fetch original text chunks
    from the database using their UUIDs (returned by vector similarity search).
    
    CRITICAL: This retrieves content from PostgreSQL, NOT from vector store
    payloads, ensuring complete traceability and data consistency.
    """
    
    def __init__(self, database_url: str, pool_size: int = 10):
        """Initialize Decoder.
        
        Args:
            database_url: PostgreSQL connection URL (asyncpg format)
            pool_size: Size of connection pool
        """
        self.database_url = database_url
        self.pool_size = pool_size
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Establish database connection pool.
        
        Raises:
            DecoderError: If connection fails
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
            raise DecoderError(f"Failed to connect to database: {e}")
    
    async def close(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    async def lookup(self, chunk_ids: List[str]) -> List[Optional[ChunkContent]]:
        """Retrieve full chunk content by IDs.
        
        This is the primary method used after vector similarity search.
        It fetches complete chunk data including text, metadata, and
        document information.
        
        Args:
            chunk_ids: List of chunk UUIDs (as strings)
            
        Returns:
            List of ChunkContent objects in same order as chunk_ids.
            Missing IDs return None in that position.
            
        Raises:
            DecoderError: If database query fails
        """
        if not self.pool:
            raise DecoderError("Not connected to database. Call connect() first.")
        
        if not chunk_ids:
            return []
        
        # Convert string IDs to UUIDs
        try:
            uuid_ids = [UUID(cid) for cid in chunk_ids]
        except (ValueError, AttributeError) as e:
            raise DecoderError(f"Invalid chunk ID format: {e}")
        
        query = """
        SELECT 
            s.id,
            s.text,
            s.doc_id,
            s.section_path,
            s.position_in_doc,
            s.token_count,
            s.overlap_start,
            s.overlap_end,
            s.meta,
            s.created_at,
            d.source_type,
            d.source_id,
            d.title,
            d.source_url,
            d.authors,
            d.publication_date,
            d.meta as doc_meta
        FROM doc_segments s
        JOIN documents d ON s.doc_id = d.id
        WHERE s.id = ANY($1::uuid[])
        """
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, uuid_ids)
                
                # Create a mapping of chunk_id -> row for quick lookup
                row_map = {str(row['id']): row for row in rows}
                
                # Build result list maintaining input order
                results = []
                for chunk_id in chunk_ids:
                    row = row_map.get(chunk_id)
                    if row is None:
                        results.append(None)
                    else:
                        results.append(self._row_to_chunk_content(row))
                
                return results
                
        except Exception as e:
            raise DecoderError(f"Failed to lookup chunks: {e}")
    
    async def get_document_chunks(
        self,
        document_id: str,
        limit: Optional[int] = None
    ) -> List[ChunkContent]:
        """Get all chunks for a document.
        
        Useful for viewing entire document content or debugging.
        
        Args:
            document_id: Document UUID (as string)
            limit: Optional limit on number of chunks returned
            
        Returns:
            List of chunks ordered by position_in_doc
            
        Raises:
            DecoderError: If database query fails
        """
        if not self.pool:
            raise DecoderError("Not connected to database. Call connect() first.")
        
        try:
            doc_uuid = UUID(document_id)
        except (ValueError, AttributeError) as e:
            raise DecoderError(f"Invalid document ID format: {e}")
        
        query = """
        SELECT 
            s.id,
            s.text,
            s.doc_id,
            s.section_path,
            s.position_in_doc,
            s.token_count,
            s.overlap_start,
            s.overlap_end,
            s.meta,
            s.created_at,
            d.source_type,
            d.source_id,
            d.title,
            d.source_url,
            d.authors,
            d.publication_date,
            d.meta as doc_meta
        FROM doc_segments s
        JOIN documents d ON s.doc_id = d.id
        WHERE s.doc_id = $1
        ORDER BY s.position_in_doc ASC
        """
        
        if limit:
            query += f" LIMIT {int(limit)}"
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, doc_uuid)
                return [self._row_to_chunk_content(row) for row in rows]
                
        except Exception as e:
            raise DecoderError(f"Failed to get document chunks: {e}")
    
    async def health_check(self) -> bool:
        """Verify database connection is healthy.
        
        Returns:
            True if database is accessible, False otherwise
        """
        if not self.pool:
            return False
        
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval('SELECT 1')
            return True
        except Exception:
            return False
    
    def _row_to_chunk_content(self, row: asyncpg.Record) -> ChunkContent:
        """Convert database row to ChunkContent dataclass.
        
        Args:
            row: Database record from query
            
        Returns:
            ChunkContent object with all fields populated
        """
        # Parse JSON fields
        section_path = json.loads(row['section_path']) if row['section_path'] else []
        chunk_meta = json.loads(row['meta']) if row['meta'] else {}
        doc_meta = json.loads(row['doc_meta']) if row['doc_meta'] else {}
        
        # Combine chunk and document metadata
        additional_metadata = {
            'chunk_metadata': chunk_meta,
            'document_metadata': doc_meta,
            'title': row['title'],
            'authors': json.loads(row['authors']) if row['authors'] else [],
            'publication_date': row['publication_date'].isoformat() if row['publication_date'] else None,
            'source_id': row['source_id']
        }
        
        return ChunkContent(
            chunk_id=str(row['id']),
            text=row['text'],
            document_id=str(row['doc_id']),
            source_type=row['source_type'],
            section_path=section_path,
            position_in_doc=row['position_in_doc'],
            token_count=row['token_count'],
            overlap_start=row['overlap_start'],
            overlap_end=row['overlap_end'],
            source_url=row['source_url'] or '',
            created_at=row['created_at'].isoformat(),
            additional_metadata=additional_metadata
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

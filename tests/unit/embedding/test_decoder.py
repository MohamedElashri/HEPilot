"""Unit tests for PostgreSQL Decoder."""

import pytest
from uuid import uuid4, UUID
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch
import json

from src.embedding.adapters.postgres_decoder import PostgresDecoder
from src.embedding.ports import ChunkContent
from src.embedding.exceptions import DecoderError


class AsyncContextManager:
    """Helper class to create async context manager for mocks."""
    
    def __init__(self, return_value):
        self.return_value = return_value
    
    async def __aenter__(self):
        return self.return_value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def decoder():
    """Create a Decoder instance."""
    return PostgresDecoder(
        database_url="postgresql+asyncpg://test:test@localhost/test",
        pool_size=5
    )


class TestDecoderInit:
    """Test initialization and configuration."""
    
    def test_init(self):
        """Test Decoder initialization."""
        decoder = PostgresDecoder(
            database_url="postgresql+asyncpg://user:pass@localhost/db",
            pool_size=10
        )
        assert decoder.database_url == "postgresql+asyncpg://user:pass@localhost/db"
        assert decoder.pool_size == 10
        assert decoder.pool is None


class TestConnection:
    """Test connection management."""
    
    @pytest.mark.asyncio
    async def test_connect_success(self, decoder):
        """Test successful connection."""
        with patch('asyncpg.create_pool', new=AsyncMock()) as mock_create_pool:
            mock_pool = AsyncMock()
            mock_create_pool.return_value = mock_pool
            
            await decoder.connect()
            
            assert decoder.pool == mock_pool
            mock_create_pool.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connect_already_connected(self, decoder):
        """Test connecting when already connected."""
        with patch('asyncpg.create_pool', new=AsyncMock()) as mock_create_pool:
            mock_pool = AsyncMock()
            mock_create_pool.return_value = mock_pool
            
            await decoder.connect()
            await decoder.connect()  # Call again
            
            # Should only create pool once
            assert mock_create_pool.call_count == 1
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, decoder):
        """Test connection failure."""
        with patch('asyncpg.create_pool', new=AsyncMock()) as mock_create_pool:
            mock_create_pool.side_effect = Exception("Connection refused")
            
            with pytest.raises(DecoderError, match="Failed to connect"):
                await decoder.connect()
    
    @pytest.mark.asyncio
    async def test_close(self, decoder):
        """Test closing connection."""
        mock_pool = AsyncMock()
        decoder.pool = mock_pool
        
        await decoder.close()
        
        mock_pool.close.assert_called_once()
        assert decoder.pool is None
    
    @pytest.mark.asyncio
    async def test_close_when_not_connected(self, decoder):
        """Test closing when not connected."""
        await decoder.close()  # Should not raise
        assert decoder.pool is None


class TestLookup:
    """Test lookup operations."""
    
    @pytest.mark.asyncio
    async def test_lookup_success(self, decoder):
        """Test looking up chunks by IDs."""
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        decoder.pool = mock_pool
        
        chunk_id = uuid4()
        doc_id = uuid4()
        
        mock_row = {
            'id': chunk_id,
            'text': 'Test chunk content',
            'doc_id': doc_id,
            'section_path': json.dumps(['section1', 'subsection1']),
            'position_in_doc': 0,
            'token_count': 50,
            'overlap_start': 0,
            'overlap_end': 10,
            'meta': json.dumps({'key': 'value'}),
            'created_at': datetime(2024, 1, 15, 10, 30, 0),
            'source_type': 'arxiv',
            'source_id': '2401.12345',
            'title': 'Test Paper',
            'source_url': 'https://arxiv.org/abs/2401.12345',
            'authors': json.dumps([{'name': 'John Doe'}]),
            'publication_date': datetime(2024, 1, 15),
            'doc_meta': json.dumps({'category': 'cs.AI'})
        }
        
        mock_conn.fetch.return_value = [mock_row]
        
        result = await decoder.lookup([str(chunk_id)])
        
        assert len(result) == 1
        assert result[0] is not None
        assert result[0].chunk_id == str(chunk_id)
        assert result[0].text == 'Test chunk content'
        assert result[0].document_id == str(doc_id)
        assert result[0].source_type == 'arxiv'
        assert result[0].section_path == ['section1', 'subsection1']
        assert result[0].position_in_doc == 0
        assert result[0].token_count == 50
    
    @pytest.mark.asyncio
    async def test_lookup_multiple_chunks(self, decoder):
        """Test looking up multiple chunks."""
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        decoder.pool = mock_pool
        
        chunk_ids = [uuid4(), uuid4(), uuid4()]
        doc_id = uuid4()
        
        mock_rows = [
            {
                'id': chunk_ids[i],
                'text': f'Chunk {i}',
                'doc_id': doc_id,
                'section_path': None,
                'position_in_doc': i,
                'token_count': 50,
                'overlap_start': 0,
                'overlap_end': 0,
                'meta': None,
                'created_at': datetime(2024, 1, 15),
                'source_type': 'arxiv',
                'source_id': '2401.12345',
                'title': 'Test Paper',
                'source_url': 'https://arxiv.org/abs/2401.12345',
                'authors': None,
                'publication_date': None,
                'doc_meta': None
            }
            for i in range(3)
        ]
        
        mock_conn.fetch.return_value = mock_rows
        
        result = await decoder.lookup([str(cid) for cid in chunk_ids])
        
        assert len(result) == 3
        assert all(r is not None for r in result)
        assert result[0].text == 'Chunk 0'
        assert result[1].text == 'Chunk 1'
        assert result[2].text == 'Chunk 2'
    
    @pytest.mark.asyncio
    async def test_lookup_missing_chunks(self, decoder):
        """Test looking up chunks that don't exist."""
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        decoder.pool = mock_pool
        
        chunk_id1 = uuid4()
        chunk_id2 = uuid4()
        chunk_id3 = uuid4()
        doc_id = uuid4()
        
        # Only return row for chunk_id2
        mock_row = {
            'id': chunk_id2,
            'text': 'Chunk 2',
            'doc_id': doc_id,
            'section_path': None,
            'position_in_doc': 1,
            'token_count': 50,
            'overlap_start': 0,
            'overlap_end': 0,
            'meta': None,
            'created_at': datetime(2024, 1, 15),
            'source_type': 'arxiv',
            'source_id': '2401.12345',
            'title': 'Test Paper',
            'source_url': 'https://arxiv.org/abs/2401.12345',
            'authors': None,
            'publication_date': None,
            'doc_meta': None
        }
        
        mock_conn.fetch.return_value = [mock_row]
        
        result = await decoder.lookup([str(chunk_id1), str(chunk_id2), str(chunk_id3)])
        
        assert len(result) == 3
        assert result[0] is None  # chunk_id1 not found
        assert result[1] is not None  # chunk_id2 found
        assert result[2] is None  # chunk_id3 not found
        assert result[1].text == 'Chunk 2'
    
    @pytest.mark.asyncio
    async def test_lookup_empty_list(self, decoder):
        """Test lookup with empty list."""
        mock_pool = MagicMock()
        decoder.pool = mock_pool
        
        result = await decoder.lookup([])
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_lookup_not_connected(self, decoder):
        """Test lookup when not connected."""
        with pytest.raises(DecoderError, match="Not connected"):
            await decoder.lookup([str(uuid4())])
    
    @pytest.mark.asyncio
    async def test_lookup_invalid_uuid(self, decoder):
        """Test lookup with invalid UUID format."""
        mock_pool = MagicMock()
        decoder.pool = mock_pool
        
        with pytest.raises(DecoderError, match="Invalid chunk ID format"):
            await decoder.lookup(['not-a-uuid'])
    
    @pytest.mark.asyncio
    async def test_lookup_database_error(self, decoder):
        """Test lookup with database error."""
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        decoder.pool = mock_pool
        
        mock_conn.fetch.side_effect = Exception("Database error")
        
        with pytest.raises(DecoderError, match="Failed to lookup chunks"):
            await decoder.lookup([str(uuid4())])


class TestGetDocumentChunks:
    """Test get_document_chunks operations."""
    
    @pytest.mark.asyncio
    async def test_get_document_chunks_success(self, decoder):
        """Test getting all chunks for a document."""
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        decoder.pool = mock_pool
        
        doc_id = uuid4()
        chunk_ids = [uuid4(), uuid4(), uuid4()]
        
        mock_rows = [
            {
                'id': chunk_ids[i],
                'text': f'Chunk {i}',
                'doc_id': doc_id,
                'section_path': json.dumps(['section']),
                'position_in_doc': i,
                'token_count': 50,
                'overlap_start': 0,
                'overlap_end': 5,
                'meta': None,
                'created_at': datetime(2024, 1, 15),
                'source_type': 'arxiv',
                'source_id': '2401.12345',
                'title': 'Test Paper',
                'source_url': 'https://arxiv.org/abs/2401.12345',
                'authors': json.dumps([{'name': 'John Doe'}]),
                'publication_date': datetime(2024, 1, 15),
                'doc_meta': json.dumps({'key': 'value'})
            }
            for i in range(3)
        ]
        
        mock_conn.fetch.return_value = mock_rows
        
        result = await decoder.get_document_chunks(str(doc_id))
        
        assert len(result) == 3
        assert result[0].position_in_doc == 0
        assert result[1].position_in_doc == 1
        assert result[2].position_in_doc == 2
        assert all(r.document_id == str(doc_id) for r in result)
    
    @pytest.mark.asyncio
    async def test_get_document_chunks_with_limit(self, decoder):
        """Test getting chunks with limit."""
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        decoder.pool = mock_pool
        
        doc_id = uuid4()
        
        mock_conn.fetch.return_value = []
        
        result = await decoder.get_document_chunks(str(doc_id), limit=10)
        
        # Verify limit was included in query
        call_args = mock_conn.fetch.call_args
        assert 'LIMIT 10' in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_get_document_chunks_empty(self, decoder):
        """Test getting chunks for document with no chunks."""
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        decoder.pool = mock_pool
        
        mock_conn.fetch.return_value = []
        
        result = await decoder.get_document_chunks(str(uuid4()))
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_get_document_chunks_not_connected(self, decoder):
        """Test get_document_chunks when not connected."""
        with pytest.raises(DecoderError, match="Not connected"):
            await decoder.get_document_chunks(str(uuid4()))
    
    @pytest.mark.asyncio
    async def test_get_document_chunks_invalid_uuid(self, decoder):
        """Test get_document_chunks with invalid UUID."""
        mock_pool = MagicMock()
        decoder.pool = mock_pool
        
        with pytest.raises(DecoderError, match="Invalid document ID format"):
            await decoder.get_document_chunks('not-a-uuid')


class TestHealthCheck:
    """Test health check functionality."""
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, decoder):
        """Test health check when database is healthy."""
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        decoder.pool = mock_pool
        
        mock_conn.fetchval.return_value = 1
        
        result = await decoder.health_check()
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, decoder):
        """Test health check when database is unhealthy."""
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        decoder.pool = mock_pool
        
        mock_conn.fetchval.side_effect = Exception("Connection lost")
        
        result = await decoder.health_check()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_health_check_not_connected(self, decoder):
        """Test health check when not connected."""
        result = await decoder.health_check()
        
        assert result is False


class TestContextManager:
    """Test async context manager support."""
    
    @pytest.mark.asyncio
    async def test_context_manager(self, decoder):
        """Test using decoder as async context manager."""
        with patch('asyncpg.create_pool', new=AsyncMock()) as mock_create_pool:
            mock_pool = AsyncMock()
            mock_create_pool.return_value = mock_pool
            
            async with decoder as d:
                assert d.pool == mock_pool
                assert d is decoder
            
            # Pool should be closed after exit
            mock_pool.close.assert_called_once()
            assert decoder.pool is None

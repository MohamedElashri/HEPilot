"""Unit tests for PostgreSQL DocStore."""

import pytest
import asyncio
from uuid import uuid4, UUID
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import json

from src.embedding.adapters.postgres_docstore import PostgresDocStore
from src.embedding.exceptions import DocStoreError


class AsyncContextManager:
    """Helper class to create async context manager for mocks."""
    
    def __init__(self, return_value):
        self.return_value = return_value
    
    async def __aenter__(self):
        return self.return_value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def mock_pool():
    """Create a mock asyncpg connection pool."""
    pool = AsyncMock()
    conn = AsyncMock()
    pool.acquire.return_value = AsyncContextManager(conn)
    return pool, conn


@pytest.fixture
def docstore():
    """Create a DocStore instance."""
    return PostgresDocStore(
        database_url="postgresql+asyncpg://test:test@localhost/test",
        pool_size=5
    )


class TestDocStoreInit:
    """Test initialization and configuration."""
    
    def test_init(self):
        """Test DocStore initialization."""
        store = PostgresDocStore(
            database_url="postgresql+asyncpg://user:pass@localhost/db",
            pool_size=10,
            max_overflow=20
        )
        assert store.database_url == "postgresql+asyncpg://user:pass@localhost/db"
        assert store.pool_size == 10
        assert store.max_overflow == 20
        assert store.pool is None


class TestConnection:
    """Test connection management."""
    
    @pytest.mark.asyncio
    async def test_connect_success(self, docstore):
        """Test successful connection."""
        with patch('asyncpg.create_pool', new=AsyncMock()) as mock_create_pool:
            mock_pool = AsyncMock()
            mock_create_pool.return_value = mock_pool
            
            await docstore.connect()
            
            assert docstore.pool == mock_pool
            mock_create_pool.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connect_already_connected(self, docstore):
        """Test connecting when already connected."""
        with patch('asyncpg.create_pool', new=AsyncMock()) as mock_create_pool:
            mock_pool = AsyncMock()
            mock_create_pool.return_value = mock_pool
            
            await docstore.connect()
            await docstore.connect()  # Call again
            
            # Should only create pool once
            assert mock_create_pool.call_count == 1
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, docstore):
        """Test connection failure."""
        with patch('asyncpg.create_pool', new=AsyncMock()) as mock_create_pool:
            mock_create_pool.side_effect = Exception("Connection failed")
            
            with pytest.raises(DocStoreError, match="Failed to connect"):
                await docstore.connect()
    
    @pytest.mark.asyncio
    async def test_close(self, docstore):
        """Test closing connection."""
        mock_pool = AsyncMock()
        docstore.pool = mock_pool
        
        await docstore.close()
        
        mock_pool.close.assert_called_once()
        assert docstore.pool is None
    
    @pytest.mark.asyncio
    async def test_close_when_not_connected(self, docstore):
        """Test closing when not connected."""
        await docstore.close()  # Should not raise
        assert docstore.pool is None


class TestAddDocument:
    """Test adding documents."""
    
    @pytest.mark.asyncio
    async def test_add_document_success(self, docstore):
        """Test adding a document successfully."""
        mock_pool, mock_conn = MagicMock(), AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        docstore.pool = mock_pool
        
        doc_id = uuid4()
        mock_conn.fetchval.return_value = doc_id
        
        result = await docstore.add_document(
            doc_id=doc_id,
            source_type="arxiv",
            source_id="2401.12345",
            title="Test Paper",
            authors=[{"name": "John Doe"}],
            publication_date=datetime(2024, 1, 15),
            source_url="https://arxiv.org/abs/2401.12345",
            metadata={"category": "cs.AI"}
        )
        
        assert result == doc_id
        mock_conn.fetchval.assert_called_once()
        
        # Check query parameters
        call_args = mock_conn.fetchval.call_args[0]
        assert call_args[1] == doc_id
        assert call_args[2] == "arxiv"
        assert call_args[3] == "2401.12345"
    
    @pytest.mark.asyncio
    async def test_add_document_not_connected(self, docstore):
        """Test adding document when not connected."""
        with pytest.raises(DocStoreError, match="Not connected"):
            await docstore.add_document(
                doc_id=uuid4(),
                source_type="arxiv",
                source_id="test"
            )
    
    @pytest.mark.asyncio
    async def test_add_document_minimal(self, docstore):
        """Test adding document with minimal fields."""
        mock_pool, mock_conn = MagicMock(), AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        docstore.pool = mock_pool
        
        doc_id = uuid4()
        mock_conn.fetchval.return_value = doc_id
        
        result = await docstore.add_document(
            doc_id=doc_id,
            source_type="arxiv",
            source_id="2401.12345"
        )
        
        assert result == doc_id


class TestAddChunk:
    """Test adding chunks."""
    
    @pytest.mark.asyncio
    async def test_add_chunk_success(self, docstore):
        """Test adding a chunk successfully."""
        mock_pool, mock_conn = MagicMock(), AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        docstore.pool = mock_pool
        
        chunk_id = uuid4()
        doc_id = uuid4()
        mock_conn.fetchval.return_value = chunk_id
        
        result = await docstore.add_chunk(
            chunk_id=chunk_id,
            doc_id=doc_id,
            text="This is a test chunk.",
            position=0,
            token_count=5,
            section_path=["introduction"],
            overlap_start=0,
            overlap_end=2,
            metadata={"source": "page_1"}
        )
        
        assert result == chunk_id
        mock_conn.fetchval.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_chunk_not_connected(self, docstore):
        """Test adding chunk when not connected."""
        with pytest.raises(DocStoreError, match="Not connected"):
            await docstore.add_chunk(
                chunk_id=uuid4(),
                doc_id=uuid4(),
                text="test",
                position=0,
                token_count=1
            )


class TestBatchOperations:
    """Test batch operations."""
    
    @pytest.mark.asyncio
    async def test_add_chunks_batch(self, docstore):
        """Test adding multiple chunks in batch."""
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        docstore.pool = mock_pool
        
        # Mock transaction - use MagicMock instead of relying on AsyncMock
        mock_conn.transaction = MagicMock(return_value=AsyncContextManager(None))
        
        doc_id = uuid4()
        chunks = [
            {
                'chunk_id': uuid4(),
                'doc_id': doc_id,
                'text': f'Chunk {i}',
                'position': i,
                'token_count': 10
            }
            for i in range(3)
        ]
        
        result = await docstore.add_chunks_batch(chunks)
        
        assert result == 3
        assert mock_conn.execute.call_count == 3
    
    @pytest.mark.asyncio
    async def test_add_chunks_batch_empty(self, docstore):
        """Test adding empty batch."""
        mock_pool = AsyncMock()
        docstore.pool = mock_pool
        
        result = await docstore.add_chunks_batch([])
        
        assert result == 0


class TestGetOperations:
    """Test retrieval operations."""
    
    @pytest.mark.asyncio
    async def test_get_document(self, docstore):
        """Test retrieving a document."""
        mock_pool, mock_conn = MagicMock(), AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        docstore.pool = mock_pool
        
        doc_id = uuid4()
        mock_row = {
            'id': doc_id,
            'source_type': 'arxiv',
            'source_id': '2401.12345',
            'title': 'Test Paper',
            'authors': json.dumps([{'name': 'John Doe'}]),
            'publication_date': datetime(2024, 1, 15),
            'source_url': 'https://arxiv.org/abs/2401.12345',
            'meta': json.dumps({'category': 'cs.AI'}),
            'created_at': datetime(2024, 1, 15)
        }
        mock_conn.fetchrow.return_value = mock_row
        
        result = await docstore.get_document(doc_id)
        
        assert result['id'] == str(doc_id)
        assert result['source_type'] == 'arxiv'
        assert result['title'] == 'Test Paper'
        assert result['authors'] == [{'name': 'John Doe'}]
    
    @pytest.mark.asyncio
    async def test_get_document_not_found(self, docstore):
        """Test retrieving non-existent document."""
        mock_pool, mock_conn = MagicMock(), AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        docstore.pool = mock_pool
        
        mock_conn.fetchrow.return_value = None
        
        result = await docstore.get_document(uuid4())
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_chunk(self, docstore):
        """Test retrieving a chunk."""
        mock_pool, mock_conn = MagicMock(), AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        docstore.pool = mock_pool
        
        chunk_id = uuid4()
        doc_id = uuid4()
        mock_row = {
            'id': chunk_id,
            'doc_id': doc_id,
            'text': 'Test chunk',
            'section_path': json.dumps(['intro']),
            'position_in_doc': 0,
            'token_count': 10,
            'overlap_start': 0,
            'overlap_end': 2,
            'meta': None,
            'created_at': datetime(2024, 1, 15)
        }
        mock_conn.fetchrow.return_value = mock_row
        
        result = await docstore.get_chunk(chunk_id)
        
        assert result['id'] == str(chunk_id)
        assert result['text'] == 'Test chunk'
        assert result['section_path'] == ['intro']
    
    @pytest.mark.asyncio
    async def test_get_document_chunks(self, docstore):
        """Test retrieving all chunks for a document."""
        mock_pool, mock_conn = MagicMock(), AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        docstore.pool = mock_pool
        
        doc_id = uuid4()
        mock_rows = [
            {
                'id': uuid4(),
                'doc_id': doc_id,
                'text': f'Chunk {i}',
                'section_path': None,
                'position_in_doc': i,
                'token_count': 10,
                'overlap_start': 0,
                'overlap_end': 0,
                'meta': None,
                'created_at': datetime(2024, 1, 15)
            }
            for i in range(3)
        ]
        mock_conn.fetch.return_value = mock_rows
        
        result = await docstore.get_document_chunks(doc_id)
        
        assert len(result) == 3
        assert result[0]['position'] == 0
        assert result[1]['position'] == 1


class TestDeleteOperations:
    """Test delete operations."""
    
    @pytest.mark.asyncio
    async def test_delete_document_success(self, docstore):
        """Test deleting a document."""
        mock_pool, mock_conn = MagicMock(), AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        docstore.pool = mock_pool
        
        mock_conn.execute.return_value = "DELETE 1"
        
        result = await docstore.delete_document(uuid4())
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_delete_document_not_found(self, docstore):
        """Test deleting non-existent document."""
        mock_pool, mock_conn = MagicMock(), AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        docstore.pool = mock_pool
        
        mock_conn.execute.return_value = "DELETE 0"
        
        result = await docstore.delete_document(uuid4())
        
        assert result is False


class TestCountOperations:
    """Test count operations."""
    
    @pytest.mark.asyncio
    async def test_count_documents(self, docstore):
        """Test counting documents."""
        mock_pool, mock_conn = MagicMock(), AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        docstore.pool = mock_pool
        
        mock_conn.fetchval.return_value = 42
        
        result = await docstore.count_documents()
        
        assert result == 42
    
    @pytest.mark.asyncio
    async def test_count_chunks(self, docstore):
        """Test counting chunks."""
        mock_pool, mock_conn = MagicMock(), AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        docstore.pool = mock_pool
        
        mock_conn.fetchval.return_value = 156
        
        result = await docstore.count_chunks()
        
        assert result == 156


class TestHealthCheck:
    """Test health check functionality."""
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, docstore):
        """Test health check when database is healthy."""
        mock_pool, mock_conn = MagicMock(), AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        docstore.pool = mock_pool
        
        mock_conn.fetchval.return_value = 1
        
        result = await docstore.health_check()
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, docstore):
        """Test health check when database is unhealthy."""
        mock_pool, mock_conn = MagicMock(), AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManager(mock_conn)
        docstore.pool = mock_pool
        
        mock_conn.fetchval.side_effect = Exception("Connection lost")
        
        result = await docstore.health_check()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_health_check_not_connected(self, docstore):
        """Test health check when not connected."""
        result = await docstore.health_check()
        
        assert result is False


class TestContextManager:
    """Test async context manager support."""
    
    @pytest.mark.asyncio
    async def test_context_manager(self, docstore):
        """Test using DocStore as async context manager."""
        with patch('asyncpg.create_pool', new=AsyncMock()) as mock_create_pool:
            mock_pool = AsyncMock()
            mock_create_pool.return_value = mock_pool
            
            async with docstore as store:
                assert store.pool == mock_pool
            
            mock_pool.close.assert_called_once()
            assert docstore.pool is None

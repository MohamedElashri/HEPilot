"""Tests for ChromaDB vector database adapter."""

import pytest
import numpy as np
from unittest.mock import MagicMock, AsyncMock, patch, call
from pathlib import Path

from src.embedding.adapters.chroma_vectordb import ChromaVectorDB
from src.embedding.ports import QueryResult
from src.embedding.exceptions import VectorDBError


# Test Fixtures

@pytest.fixture
def vectordb():
    """Create ChromaVectorDB instance."""
    return ChromaVectorDB(
        persist_directory=Path(".test_chroma"),
        collection_name="test_collection",
        distance_metric="cosine"
    )


@pytest.fixture
def vectordb_custom():
    """Create ChromaVectorDB with custom settings."""
    return ChromaVectorDB(
        persist_directory=Path("/tmp/custom_chroma"),
        collection_name="custom_collection",
        distance_metric="l2"
    )


@pytest.fixture
def sample_vectors():
    """Sample embedding vectors."""
    return np.array([
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
        [0.7, 0.8, 0.9]
    ], dtype=np.float32)


@pytest.fixture
def sample_ids():
    """Sample chunk IDs."""
    return ["chunk-1", "chunk-2", "chunk-3"]


@pytest.fixture
def sample_metadata():
    """Sample metadata dicts."""
    return [
        {"doc_id": "doc-1", "position": 0},
        {"doc_id": "doc-1", "position": 1},
        {"doc_id": "doc-2", "position": 0}
    ]


# Test Initialization

class TestVectorDBInit:
    """Test ChromaVectorDB initialization."""
    
    def test_init_default(self):
        """Test initialization with default parameters."""
        db = ChromaVectorDB()
        assert db.persist_directory == Path(".data/chroma")
        assert db.collection_name == "hepilot"
        assert db.distance_metric == "cosine"
        assert db.client is None
        assert db.collection is None
    
    def test_init_custom(self, vectordb_custom):
        """Test initialization with custom parameters."""
        assert vectordb_custom.persist_directory == Path("/tmp/custom_chroma")
        assert vectordb_custom.collection_name == "custom_collection"
        assert vectordb_custom.distance_metric == "l2"


# Test Setup

class TestSetup:
    """Test ChromaDB setup and initialization."""
    
    @pytest.mark.asyncio
    async def test_setup_success(self, vectordb):
        """Test successful setup."""
        with patch('chromadb.PersistentClient') as mock_client_class:
            mock_client = MagicMock()
            mock_collection = MagicMock()
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_client_class.return_value = mock_client
            
            await vectordb.setup()
            
            assert vectordb.client is not None
            assert vectordb.collection is not None
            mock_client.get_or_create_collection.assert_called_once_with(
                name="test_collection",
                metadata={"hnsw:space": "cosine"}
            )
    
    @pytest.mark.asyncio
    async def test_setup_creates_directory(self, vectordb, tmp_path):
        """Test that setup creates persist directory."""
        test_dir = tmp_path / "test_chroma"
        vectordb.persist_directory = test_dir
        
        with patch('chromadb.PersistentClient') as mock_client_class:
            mock_client = MagicMock()
            mock_collection = MagicMock()
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_client_class.return_value = mock_client
            
            await vectordb.setup()
            
            assert test_dir.exists()
    
    @pytest.mark.asyncio
    async def test_setup_failure(self, vectordb):
        """Test setup failure handling."""
        with patch('chromadb.PersistentClient', side_effect=Exception("Connection failed")):
            with pytest.raises(VectorDBError, match="Failed to initialize ChromaDB"):
                await vectordb.setup()


# Test Upsert

class TestUpsert:
    """Test vector insertion and updates."""
    
    @pytest.mark.asyncio
    async def test_upsert_success(self, vectordb, sample_ids, sample_vectors):
        """Test successful vector upsert."""
        mock_collection = MagicMock()
        vectordb.collection = mock_collection
        
        await vectordb.upsert(sample_ids, sample_vectors)
        
        mock_collection.upsert.assert_called_once()
        call_args = mock_collection.upsert.call_args[1]
        assert call_args['ids'] == sample_ids
        assert len(call_args['embeddings']) == 3
    
    @pytest.mark.asyncio
    async def test_upsert_with_metadata(self, vectordb, sample_ids, sample_vectors, sample_metadata):
        """Test upsert with metadata."""
        mock_collection = MagicMock()
        vectordb.collection = mock_collection
        
        await vectordb.upsert(sample_ids, sample_vectors, sample_metadata)
        
        mock_collection.upsert.assert_called_once()
        call_args = mock_collection.upsert.call_args[1]
        assert call_args['metadatas'] is not None
        assert len(call_args['metadatas']) == 3
    
    @pytest.mark.asyncio
    async def test_upsert_empty_list(self, vectordb):
        """Test upsert with empty lists."""
        mock_collection = MagicMock()
        vectordb.collection = mock_collection
        
        await vectordb.upsert([], np.array([]).reshape(0, 3))
        
        mock_collection.upsert.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_upsert_auto_setup(self, vectordb, sample_ids, sample_vectors):
        """Test that upsert calls setup if not initialized."""
        with patch.object(vectordb, 'setup', new_callable=AsyncMock) as mock_setup:
            mock_collection = MagicMock()
            vectordb.collection = None
            
            # After setup is called, set the collection
            async def setup_side_effect():
                vectordb.collection = mock_collection
            mock_setup.side_effect = setup_side_effect
            
            await vectordb.upsert(sample_ids, sample_vectors)
            
            mock_setup.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_upsert_ids_vectors_mismatch(self, vectordb, sample_ids, sample_vectors):
        """Test error when IDs and vectors count mismatch."""
        vectordb.collection = MagicMock()
        
        with pytest.raises(VectorDBError, match="Mismatch"):
            await vectordb.upsert(sample_ids[:2], sample_vectors)
    
    @pytest.mark.asyncio
    async def test_upsert_ids_metadata_mismatch(self, vectordb, sample_ids, sample_vectors, sample_metadata):
        """Test error when IDs and metadata count mismatch."""
        vectordb.collection = MagicMock()
        
        with pytest.raises(VectorDBError, match="Mismatch"):
            await vectordb.upsert(sample_ids, sample_vectors, sample_metadata[:2])
    
    @pytest.mark.asyncio
    async def test_upsert_sanitizes_metadata(self, vectordb):
        """Test that metadata is sanitized for ChromaDB."""
        mock_collection = MagicMock()
        vectordb.collection = mock_collection
        
        ids = ["chunk-1"]
        vectors = np.array([[0.1, 0.2, 0.3]], dtype=np.float32)
        metadata = [{
            "string": "value",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "none": None,
            "list": [1, 2, 3],
            "dict": {"key": "value"}
        }]
        
        await vectordb.upsert(ids, vectors, metadata)
        
        call_args = mock_collection.upsert.call_args[1]
        sanitized = call_args['metadatas'][0]
        assert sanitized['string'] == "value"
        assert sanitized['int'] == 42
        assert sanitized['float'] == 3.14
        assert sanitized['bool'] is True
        assert sanitized['none'] == ""
        assert isinstance(sanitized['list'], str)
        assert isinstance(sanitized['dict'], str)
    
    @pytest.mark.asyncio
    async def test_upsert_exception(self, vectordb, sample_ids, sample_vectors):
        """Test upsert exception handling."""
        mock_collection = MagicMock()
        mock_collection.upsert.side_effect = Exception("Database error")
        vectordb.collection = mock_collection
        
        with pytest.raises(VectorDBError, match="Failed to upsert vectors"):
            await vectordb.upsert(sample_ids, sample_vectors)


# Test Query

class TestQuery:
    """Test similarity search."""
    
    @pytest.mark.asyncio
    async def test_query_success(self, vectordb):
        """Test successful query."""
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            'ids': [['chunk-1', 'chunk-2']],
            'distances': [[0.1, 0.2]],
            'metadatas': [[{'doc_id': 'doc-1'}, {'doc_id': 'doc-2'}]]
        }
        vectordb.collection = mock_collection
        
        query_vector = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        results = await vectordb.query(query_vector, top_k=2)
        
        assert len(results) == 2
        assert results[0].chunk_id == 'chunk-1'
        assert results[0].score == 0.1
        assert results[0].metadata == {'doc_id': 'doc-1'}
        assert results[1].chunk_id == 'chunk-2'
        assert results[1].score == 0.2
    
    @pytest.mark.asyncio
    async def test_query_with_filter(self, vectordb):
        """Test query with metadata filter."""
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            'ids': [['chunk-1']],
            'distances': [[0.1]],
            'metadatas': [[{'doc_id': 'doc-1'}]]
        }
        vectordb.collection = mock_collection
        
        query_vector = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        filter_dict = {'doc_id': 'doc-1'}
        results = await vectordb.query(query_vector, top_k=5, filter_dict=filter_dict)
        
        mock_collection.query.assert_called_once()
        call_args = mock_collection.query.call_args[1]
        assert call_args['where'] == filter_dict
    
    @pytest.mark.asyncio
    async def test_query_empty_results(self, vectordb):
        """Test query with no results."""
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            'ids': [[]],
            'distances': [[]],
            'metadatas': [[]]
        }
        vectordb.collection = mock_collection
        
        query_vector = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        results = await vectordb.query(query_vector)
        
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_query_auto_setup(self, vectordb):
        """Test that query calls setup if not initialized."""
        with patch.object(vectordb, 'setup', new_callable=AsyncMock) as mock_setup:
            mock_collection = MagicMock()
            mock_collection.query.return_value = {'ids': [[]], 'distances': [[]], 'metadatas': [[]]}
            vectordb.collection = None
            
            async def setup_side_effect():
                vectordb.collection = mock_collection
            mock_setup.side_effect = setup_side_effect
            
            query_vector = np.array([0.1, 0.2, 0.3], dtype=np.float32)
            await vectordb.query(query_vector)
            
            mock_setup.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_query_wrong_dimensions(self, vectordb):
        """Test query with wrong vector dimensions."""
        vectordb.collection = MagicMock()
        
        # 2D vector instead of 1D
        query_vector = np.array([[0.1, 0.2, 0.3]], dtype=np.float32)
        
        with pytest.raises(VectorDBError, match="Query vector must be 1D"):
            await vectordb.query(query_vector)
    
    @pytest.mark.asyncio
    async def test_query_exception(self, vectordb):
        """Test query exception handling."""
        mock_collection = MagicMock()
        mock_collection.query.side_effect = Exception("Query failed")
        vectordb.collection = mock_collection
        
        query_vector = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        
        with pytest.raises(VectorDBError, match="Failed to query vectors"):
            await vectordb.query(query_vector)


# Test Delete

class TestDelete:
    """Test vector deletion."""
    
    @pytest.mark.asyncio
    async def test_delete_success(self, vectordb, sample_ids):
        """Test successful deletion."""
        mock_collection = MagicMock()
        vectordb.collection = mock_collection
        
        await vectordb.delete(sample_ids)
        
        mock_collection.delete.assert_called_once_with(ids=sample_ids)
    
    @pytest.mark.asyncio
    async def test_delete_empty_list(self, vectordb):
        """Test delete with empty list."""
        mock_collection = MagicMock()
        vectordb.collection = mock_collection
        
        await vectordb.delete([])
        
        mock_collection.delete.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_delete_auto_setup(self, vectordb, sample_ids):
        """Test that delete calls setup if not initialized."""
        with patch.object(vectordb, 'setup', new_callable=AsyncMock) as mock_setup:
            mock_collection = MagicMock()
            vectordb.collection = None
            
            async def setup_side_effect():
                vectordb.collection = mock_collection
            mock_setup.side_effect = setup_side_effect
            
            await vectordb.delete(sample_ids)
            
            mock_setup.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_exception(self, vectordb, sample_ids):
        """Test delete exception handling."""
        mock_collection = MagicMock()
        mock_collection.delete.side_effect = Exception("Delete failed")
        vectordb.collection = mock_collection
        
        with pytest.raises(VectorDBError, match="Failed to delete vectors"):
            await vectordb.delete(sample_ids)


# Test Count

class TestCount:
    """Test vector counting."""
    
    @pytest.mark.asyncio
    async def test_count_success(self, vectordb):
        """Test successful count."""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 42
        vectordb.collection = mock_collection
        
        count = await vectordb.count()
        
        assert count == 42
        mock_collection.count.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_count_empty_collection(self, vectordb):
        """Test count with empty collection."""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        vectordb.collection = mock_collection
        
        count = await vectordb.count()
        
        assert count == 0
    
    @pytest.mark.asyncio
    async def test_count_auto_setup(self, vectordb):
        """Test that count calls setup if not initialized."""
        with patch.object(vectordb, 'setup', new_callable=AsyncMock) as mock_setup:
            mock_collection = MagicMock()
            mock_collection.count.return_value = 0
            vectordb.collection = None
            
            async def setup_side_effect():
                vectordb.collection = mock_collection
            mock_setup.side_effect = setup_side_effect
            
            await vectordb.count()
            
            mock_setup.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_count_exception(self, vectordb):
        """Test count exception handling."""
        mock_collection = MagicMock()
        mock_collection.count.side_effect = Exception("Count failed")
        vectordb.collection = mock_collection
        
        with pytest.raises(VectorDBError, match="Failed to count vectors"):
            await vectordb.count()


# Test Clear

class TestClear:
    """Test collection clearing."""
    
    @pytest.mark.asyncio
    async def test_clear_success(self, vectordb):
        """Test successful clear."""
        mock_collection = MagicMock()
        mock_collection.get.return_value = {'ids': ['chunk-1', 'chunk-2', 'chunk-3']}
        vectordb.collection = mock_collection
        
        with patch.object(vectordb, 'delete', new_callable=AsyncMock) as mock_delete:
            await vectordb.clear()
            
            mock_delete.assert_called_once_with(['chunk-1', 'chunk-2', 'chunk-3'])
    
    @pytest.mark.asyncio
    async def test_clear_empty_collection(self, vectordb):
        """Test clear on empty collection."""
        mock_collection = MagicMock()
        mock_collection.get.return_value = {'ids': []}
        vectordb.collection = mock_collection
        
        with patch.object(vectordb, 'delete', new_callable=AsyncMock) as mock_delete:
            await vectordb.clear()
            
            mock_delete.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_clear_auto_setup(self, vectordb):
        """Test that clear calls setup if not initialized."""
        with patch.object(vectordb, 'setup', new_callable=AsyncMock) as mock_setup:
            mock_collection = MagicMock()
            mock_collection.get.return_value = {'ids': []}
            vectordb.collection = None
            
            async def setup_side_effect():
                vectordb.collection = mock_collection
            mock_setup.side_effect = setup_side_effect
            
            await vectordb.clear()
            
            mock_setup.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_clear_exception(self, vectordb):
        """Test clear exception handling."""
        mock_collection = MagicMock()
        mock_collection.get.side_effect = Exception("Get failed")
        vectordb.collection = mock_collection
        
        with pytest.raises(VectorDBError, match="Failed to clear collection"):
            await vectordb.clear()


# Test Health Check

class TestHealthCheck:
    """Test health check functionality."""
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, vectordb):
        """Test successful health check."""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        vectordb.collection = mock_collection
        
        result = await vectordb.health_check()
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_auto_setup(self, vectordb):
        """Test health check calls setup if needed."""
        with patch.object(vectordb, 'setup', new_callable=AsyncMock) as mock_setup:
            mock_collection = MagicMock()
            mock_collection.count.return_value = 0
            vectordb.collection = None
            
            async def setup_side_effect():
                vectordb.collection = mock_collection
            mock_setup.side_effect = setup_side_effect
            
            result = await vectordb.health_check()
            
            assert result is True
            mock_setup.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, vectordb):
        """Test health check failure."""
        mock_collection = MagicMock()
        mock_collection.count.side_effect = Exception("Connection lost")
        vectordb.collection = mock_collection
        
        result = await vectordb.health_check()
        
        assert result is False


# Test Cleanup

class TestCleanup:
    """Test resource cleanup."""
    
    @pytest.mark.asyncio
    async def test_close(self, vectordb):
        """Test close method."""
        mock_collection = MagicMock()
        mock_client = MagicMock()
        vectordb.collection = mock_collection
        vectordb.client = mock_client
        
        await vectordb.close()
        
        assert vectordb.collection is None
        assert vectordb.client is None


# Test Context Manager

class TestContextManager:
    """Test async context manager."""
    
    @pytest.mark.asyncio
    async def test_context_manager(self, vectordb):
        """Test using ChromaVectorDB as context manager."""
        with patch.object(vectordb, 'setup', new_callable=AsyncMock) as mock_setup:
            with patch.object(vectordb, 'close', new_callable=AsyncMock) as mock_close:
                async with vectordb as db:
                    assert db is vectordb
                
                mock_setup.assert_called_once()
                mock_close.assert_called_once()

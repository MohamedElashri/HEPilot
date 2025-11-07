"""Tests for pipeline orchestrators."""

import pytest
import numpy as np
from unittest.mock import MagicMock, AsyncMock, patch, call
from pathlib import Path
from datetime import datetime
from uuid import UUID

from src.embedding.pipeline import (
    IngestionPipeline,
    RetrievalPipeline,
    IngestionResult,
    RetrievalResult,
    create_ingestion_pipeline,
    create_retrieval_pipeline
)
from src.embedding.config import EmbeddingConfig, load_config
from src.embedding.ports import ChunkContent, QueryResult
from src.embedding.exceptions import DocStoreError, EncoderError, VectorDBError


# Test Fixtures

@pytest.fixture
def mock_config():
    """Create mock configuration."""
    return load_config(Path("config/embedding.toml"))


@pytest.fixture
def sample_document_metadata():
    """Sample document metadata."""
    return {
        'source_type': 'arxiv',
        'source_id': '2401.12345',
        'title': 'Test Paper',
        'authors': ['Author One', 'Author Two'],
        'publication_date': datetime(2024, 1, 1),
        'source_url': 'https://arxiv.org/abs/2401.12345',
        'metadata': {'category': 'hep-ph'}
    }


@pytest.fixture
def sample_chunks():
    """Sample chunk data."""
    return [
        {
            'text': 'This is chunk one.',
            'section_path': ['Abstract'],
            'position_in_doc': 0,
            'token_count': 5,
            'overlap_start': 0,
            'overlap_end': 0,
            'metadata': {}
        },
        {
            'text': 'This is chunk two.',
            'section_path': ['Introduction'],
            'position_in_doc': 1,
            'token_count': 5,
            'overlap_start': 0,
            'overlap_end': 0,
            'metadata': {}
        }
    ]


@pytest.fixture
def sample_embeddings():
    """Sample embeddings."""
    return np.array([
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6]
    ], dtype=np.float32)


@pytest.fixture
def sample_chunk_content():
    """Sample ChunkContent objects."""
    return [
        ChunkContent(
            chunk_id='chunk-1',
            text='This is chunk one.',
            document_id='doc-1',
            source_type='arxiv',
            section_path=['Abstract'],
            position_in_doc=0,
            token_count=5,
            overlap_start=0,
            overlap_end=0,
            source_url='https://arxiv.org/abs/2401.12345',
            created_at='2024-01-01T00:00:00',
            additional_metadata={}
        ),
        ChunkContent(
            chunk_id='chunk-2',
            text='This is chunk two.',
            document_id='doc-1',
            source_type='arxiv',
            section_path=['Introduction'],
            position_in_doc=1,
            token_count=5,
            overlap_start=0,
            overlap_end=0,
            source_url='https://arxiv.org/abs/2401.12345',
            created_at='2024-01-01T00:00:00',
            additional_metadata={}
        )
    ]


# Test Ingestion Pipeline

class TestIngestionPipelineInit:
    """Test IngestionPipeline initialization."""
    
    def test_init_from_config(self, mock_config):
        """Test initialization from configuration."""
        pipeline = IngestionPipeline(mock_config)
        
        assert pipeline.config == mock_config
        assert pipeline.batch_size == mock_config.pipeline.batch_size
        assert pipeline.max_workers == mock_config.pipeline.max_workers
        assert pipeline.checkpoint_interval == mock_config.pipeline.checkpoint_interval
        assert pipeline.docstore is None
        assert pipeline.encoder is None
        assert pipeline.vectordb is None
    
    def test_factory_function(self):
        """Test factory function."""
        with patch('src.embedding.pipeline.load_config') as mock_load:
            mock_load.return_value = MagicMock()
            
            pipeline = create_ingestion_pipeline(Path("config/embedding.toml"))
            
            assert isinstance(pipeline, IngestionPipeline)
            mock_load.assert_called_once()


class TestIngestionPipelineSetup:
    """Test IngestionPipeline setup."""
    
    @pytest.mark.asyncio
    async def test_setup_components(self, mock_config):
        """Test component setup."""
        pipeline = IngestionPipeline(mock_config)
        
        with patch('src.embedding.pipeline.PostgresDocStore') as mock_docstore_class, \
             patch('src.embedding.pipeline.ONNXBGEEncoder') as mock_encoder_class, \
             patch('src.embedding.pipeline.ChromaVectorDB') as mock_vectordb_class:
            
            # Create mock instances
            mock_docstore = AsyncMock()
            mock_encoder = AsyncMock()
            mock_vectordb = AsyncMock()
            
            mock_docstore_class.return_value = mock_docstore
            mock_encoder_class.return_value = mock_encoder
            mock_vectordb_class.return_value = mock_vectordb
            
            await pipeline.setup()
            
            # Verify components initialized
            assert pipeline.docstore == mock_docstore
            assert pipeline.encoder == mock_encoder
            assert pipeline.vectordb == mock_vectordb
            
            # Verify setup methods called
            mock_docstore.connect.assert_called_once()
            mock_encoder.load_model.assert_called_once()
            mock_vectordb.setup.assert_called_once()


class TestIngestionPipelineIngest:
    """Test document ingestion."""
    
    @pytest.mark.asyncio
    async def test_ingest_single_document(
        self, mock_config, sample_document_metadata, sample_chunks, sample_embeddings
    ):
        """Test ingesting a single document."""
        pipeline = IngestionPipeline(mock_config)
        
        # Mock components
        mock_docstore = AsyncMock()
        mock_encoder = AsyncMock()
        mock_vectordb = AsyncMock()
        
        mock_docstore.add_document.return_value = 'doc-uuid'
        mock_docstore.add_chunks.return_value = ['chunk-1', 'chunk-2']
        mock_encoder.embed.return_value = sample_embeddings
        
        pipeline.docstore = mock_docstore
        pipeline.encoder = mock_encoder
        pipeline.vectordb = mock_vectordb
        
        result = await pipeline.ingest_document(sample_document_metadata, sample_chunks)
        
        assert result.documents_processed == 1
        assert result.chunks_processed == 2
        assert result.vectors_stored == 2
        assert len(result.errors) == 0
        
        # Verify components called
        mock_docstore.add_document.assert_called_once()
        mock_docstore.add_chunks.assert_called_once()
        mock_encoder.embed.assert_called_once()
        mock_vectordb.upsert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ingest_auto_setup(
        self, mock_config, sample_document_metadata, sample_chunks
    ):
        """Test that ingest calls setup if not initialized."""
        pipeline = IngestionPipeline(mock_config)
        
        with patch.object(pipeline, 'setup', new_callable=AsyncMock) as mock_setup:
            # Set up mock components after setup
            async def setup_side_effect():
                pipeline.docstore = AsyncMock()
                pipeline.encoder = AsyncMock()
                pipeline.vectordb = AsyncMock()
                pipeline.docstore.add_document.return_value = 'doc-uuid'
                pipeline.docstore.add_chunks.return_value = []
                pipeline.encoder.embed.return_value = np.array([]).reshape(0, 3)
            
            mock_setup.side_effect = setup_side_effect
            
            await pipeline.ingest_document(sample_document_metadata, [])
            
            mock_setup.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ingest_batching(
        self, mock_config, sample_document_metadata
    ):
        """Test that large documents are batched."""
        pipeline = IngestionPipeline(mock_config)
        pipeline.batch_size = 2
        
        # Create 5 chunks (will need 3 batches: 2, 2, 1)
        chunks = [
            {
                'text': f'Chunk {i}',
                'section_path': [],
                'position_in_doc': i,
                'token_count': 5,
                'overlap_start': 0,
                'overlap_end': 0,
                'metadata': {}
            }
            for i in range(5)
        ]
        
        # Mock components
        mock_docstore = AsyncMock()
        mock_encoder = AsyncMock()
        mock_vectordb = AsyncMock()
        
        mock_docstore.add_document.return_value = 'doc-uuid'
        mock_docstore.add_chunks.side_effect = [
            ['c1', 'c2'],
            ['c3', 'c4'],
            ['c5']
        ]
        mock_encoder.embed.side_effect = [
            np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]], dtype=np.float32),
            np.array([[0.7, 0.8, 0.9], [0.1, 0.1, 0.1]], dtype=np.float32),
            np.array([[0.2, 0.2, 0.2]], dtype=np.float32)
        ]
        
        pipeline.docstore = mock_docstore
        pipeline.encoder = mock_encoder
        pipeline.vectordb = mock_vectordb
        
        result = await pipeline.ingest_document(sample_document_metadata, chunks)
        
        # Verify batching
        assert mock_docstore.add_chunks.call_count == 3
        assert mock_encoder.embed.call_count == 3
        assert mock_vectordb.upsert.call_count == 3
        assert result.chunks_processed == 5
        assert result.vectors_stored == 5
    
    @pytest.mark.asyncio
    async def test_ingest_multiple_documents(
        self, mock_config, sample_document_metadata, sample_chunks
    ):
        """Test ingesting multiple documents."""
        pipeline = IngestionPipeline(mock_config)
        
        # Mock components
        mock_docstore = AsyncMock()
        mock_encoder = AsyncMock()
        mock_vectordb = AsyncMock()
        
        mock_docstore.add_document.return_value = 'doc-uuid'
        mock_docstore.add_chunks.return_value = ['chunk-1', 'chunk-2']
        mock_encoder.embed.return_value = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]], dtype=np.float32)
        
        pipeline.docstore = mock_docstore
        pipeline.encoder = mock_encoder
        pipeline.vectordb = mock_vectordb
        
        documents = [
            (sample_document_metadata, sample_chunks),
            (sample_document_metadata, sample_chunks)
        ]
        
        result = await pipeline.ingest_documents(documents)
        
        assert result.documents_processed == 2
        assert result.chunks_processed == 4
        assert result.vectors_stored == 4
    
    @pytest.mark.asyncio
    async def test_ingest_error_handling(
        self, mock_config, sample_document_metadata, sample_chunks
    ):
        """Test error handling during ingestion."""
        pipeline = IngestionPipeline(mock_config)
        
        # Mock docstore to fail
        mock_docstore = AsyncMock()
        mock_docstore.add_document.side_effect = DocStoreError("Database error")
        
        pipeline.docstore = mock_docstore
        pipeline.encoder = AsyncMock()
        pipeline.vectordb = AsyncMock()
        
        result = await pipeline.ingest_document(sample_document_metadata, sample_chunks)
        
        assert result.documents_processed == 0
        assert len(result.errors) > 0


class TestIngestionPipelineHealthCheck:
    """Test health check functionality."""
    
    @pytest.mark.asyncio
    async def test_health_check_all_healthy(self, mock_config):
        """Test health check when all components are healthy."""
        pipeline = IngestionPipeline(mock_config)
        
        mock_docstore = AsyncMock()
        mock_encoder = AsyncMock()
        mock_vectordb = AsyncMock()
        
        mock_docstore.health_check.return_value = True
        mock_encoder.health_check.return_value = True
        mock_vectordb.health_check.return_value = True
        
        pipeline.docstore = mock_docstore
        pipeline.encoder = mock_encoder
        pipeline.vectordb = mock_vectordb
        
        result = await pipeline.health_check()
        
        assert result == {
            'docstore': True,
            'encoder': True,
            'vectordb': True
        }
    
    @pytest.mark.asyncio
    async def test_health_check_auto_setup(self, mock_config):
        """Test that health check calls setup if needed."""
        pipeline = IngestionPipeline(mock_config)
        
        with patch.object(pipeline, 'setup', new_callable=AsyncMock) as mock_setup:
            async def setup_side_effect():
                pipeline.docstore = AsyncMock()
                pipeline.encoder = AsyncMock()
                pipeline.vectordb = AsyncMock()
                pipeline.docstore.health_check.return_value = True
                pipeline.encoder.health_check.return_value = True
                pipeline.vectordb.health_check.return_value = True
            
            mock_setup.side_effect = setup_side_effect
            
            await pipeline.health_check()
            
            mock_setup.assert_called_once()


class TestIngestionPipelineCleanup:
    """Test cleanup functionality."""
    
    @pytest.mark.asyncio
    async def test_close(self, mock_config):
        """Test close method."""
        pipeline = IngestionPipeline(mock_config)
        
        mock_docstore = AsyncMock()
        mock_encoder = AsyncMock()
        mock_vectordb = AsyncMock()
        
        pipeline.docstore = mock_docstore
        pipeline.encoder = mock_encoder
        pipeline.vectordb = mock_vectordb
        
        await pipeline.close()
        
        mock_docstore.close.assert_called_once()
        mock_encoder.close.assert_called_once()
        mock_vectordb.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_context_manager(self, mock_config):
        """Test using pipeline as context manager."""
        pipeline = IngestionPipeline(mock_config)
        
        with patch.object(pipeline, 'setup', new_callable=AsyncMock) as mock_setup, \
             patch.object(pipeline, 'close', new_callable=AsyncMock) as mock_close:
            
            async with pipeline as p:
                assert p is pipeline
            
            mock_setup.assert_called_once()
            mock_close.assert_called_once()


# Test Retrieval Pipeline

class TestRetrievalPipelineInit:
    """Test RetrievalPipeline initialization."""
    
    def test_init_from_config(self, mock_config):
        """Test initialization from configuration."""
        pipeline = RetrievalPipeline(mock_config)
        
        assert pipeline.config == mock_config
        assert pipeline.encoder is None
        assert pipeline.vectordb is None
        assert pipeline.decoder is None
    
    def test_factory_function(self):
        """Test factory function."""
        with patch('src.embedding.pipeline.load_config') as mock_load:
            mock_load.return_value = MagicMock()
            
            pipeline = create_retrieval_pipeline(Path("config/embedding.toml"))
            
            assert isinstance(pipeline, RetrievalPipeline)
            mock_load.assert_called_once()


class TestRetrievalPipelineSetup:
    """Test RetrievalPipeline setup."""
    
    @pytest.mark.asyncio
    async def test_setup_components(self, mock_config):
        """Test component setup."""
        pipeline = RetrievalPipeline(mock_config)
        
        with patch('src.embedding.pipeline.ONNXBGEEncoder') as mock_encoder_class, \
             patch('src.embedding.pipeline.ChromaVectorDB') as mock_vectordb_class, \
             patch('src.embedding.pipeline.PostgresDecoder') as mock_decoder_class:
            
            # Create mock instances
            mock_encoder = AsyncMock()
            mock_vectordb = AsyncMock()
            mock_decoder = AsyncMock()
            
            mock_encoder_class.return_value = mock_encoder
            mock_vectordb_class.return_value = mock_vectordb
            mock_decoder_class.return_value = mock_decoder
            
            await pipeline.setup()
            
            # Verify components initialized
            assert pipeline.encoder == mock_encoder
            assert pipeline.vectordb == mock_vectordb
            assert pipeline.decoder == mock_decoder
            
            # Verify setup methods called
            mock_encoder.load_model.assert_called_once()
            mock_vectordb.setup.assert_called_once()
            mock_decoder.connect.assert_called_once()


class TestRetrievalPipelineRetrieve:
    """Test retrieval functionality."""
    
    @pytest.mark.asyncio
    async def test_retrieve_success(
        self, mock_config, sample_embeddings, sample_chunk_content
    ):
        """Test successful retrieval."""
        pipeline = RetrievalPipeline(mock_config)
        
        # Mock components
        mock_encoder = AsyncMock()
        mock_vectordb = AsyncMock()
        mock_decoder = AsyncMock()
        
        mock_encoder.embed.return_value = sample_embeddings[:1]  # Query embedding
        mock_vectordb.query.return_value = [
            QueryResult(chunk_id='chunk-1', score=0.95, metadata={}),
            QueryResult(chunk_id='chunk-2', score=0.85, metadata={})
        ]
        mock_decoder.lookup.return_value = sample_chunk_content
        
        pipeline.encoder = mock_encoder
        pipeline.vectordb = mock_vectordb
        pipeline.decoder = mock_decoder
        
        result = await pipeline.retrieve("test query", top_k=2)
        
        assert len(result.chunks) == 2
        assert len(result.scores) == 2
        assert result.scores[0] == 0.95
        assert result.scores[1] == 0.85
        assert result.query_time_ms > 0
        
        # Verify components called
        mock_encoder.embed.assert_called_once_with(["test query"])
        mock_vectordb.query.assert_called_once()
        mock_decoder.lookup.assert_called_once_with(['chunk-1', 'chunk-2'])
    
    @pytest.mark.asyncio
    async def test_retrieve_with_filter(self, mock_config, sample_embeddings):
        """Test retrieval with metadata filter."""
        pipeline = RetrievalPipeline(mock_config)
        
        mock_encoder = AsyncMock()
        mock_vectordb = AsyncMock()
        mock_decoder = AsyncMock()
        
        mock_encoder.embed.return_value = sample_embeddings[:1]
        mock_vectordb.query.return_value = []
        mock_decoder.lookup.return_value = []
        
        pipeline.encoder = mock_encoder
        pipeline.vectordb = mock_vectordb
        pipeline.decoder = mock_decoder
        
        filter_dict = {'doc_id': 'doc-1'}
        await pipeline.retrieve("test query", top_k=5, filter_dict=filter_dict)
        
        call_args = mock_vectordb.query.call_args[1]
        assert call_args['filter_dict'] == filter_dict
    
    @pytest.mark.asyncio
    async def test_retrieve_filters_none_results(
        self, mock_config, sample_embeddings
    ):
        """Test that None results are filtered out."""
        pipeline = RetrievalPipeline(mock_config)
        
        mock_encoder = AsyncMock()
        mock_vectordb = AsyncMock()
        mock_decoder = AsyncMock()
        
        mock_encoder.embed.return_value = sample_embeddings[:1]
        mock_vectordb.query.return_value = [
            QueryResult(chunk_id='chunk-1', score=0.95, metadata={}),
            QueryResult(chunk_id='chunk-missing', score=0.85, metadata={}),
            QueryResult(chunk_id='chunk-2', score=0.75, metadata={})
        ]
        # Middle result is None (missing chunk)
        mock_decoder.lookup.return_value = [
            ChunkContent(
                chunk_id='chunk-1', text='text1', document_id='doc-1',
                source_type='arxiv', section_path=[], position_in_doc=0,
                token_count=5, overlap_start=0, overlap_end=0,
                source_url='', created_at='', additional_metadata={}
            ),
            None,  # Missing chunk
            ChunkContent(
                chunk_id='chunk-2', text='text2', document_id='doc-1',
                source_type='arxiv', section_path=[], position_in_doc=1,
                token_count=5, overlap_start=0, overlap_end=0,
                source_url='', created_at='', additional_metadata={}
            )
        ]
        
        pipeline.encoder = mock_encoder
        pipeline.vectordb = mock_vectordb
        pipeline.decoder = mock_decoder
        
        result = await pipeline.retrieve("test query", top_k=3)
        
        # Should only return valid chunks
        assert len(result.chunks) == 2
        assert len(result.scores) == 2
        assert result.chunks[0].chunk_id == 'chunk-1'
        assert result.chunks[1].chunk_id == 'chunk-2'
    
    @pytest.mark.asyncio
    async def test_retrieve_auto_setup(self, mock_config):
        """Test that retrieve calls setup if not initialized."""
        pipeline = RetrievalPipeline(mock_config)
        
        with patch.object(pipeline, 'setup', new_callable=AsyncMock) as mock_setup:
            async def setup_side_effect():
                pipeline.encoder = AsyncMock()
                pipeline.vectordb = AsyncMock()
                pipeline.decoder = AsyncMock()
                pipeline.encoder.embed.return_value = np.array([[0.1, 0.2, 0.3]], dtype=np.float32)
                pipeline.vectordb.query.return_value = []
                pipeline.decoder.lookup.return_value = []
            
            mock_setup.side_effect = setup_side_effect
            
            await pipeline.retrieve("test query")
            
            mock_setup.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_retrieve_error_handling(self, mock_config):
        """Test error handling during retrieval."""
        pipeline = RetrievalPipeline(mock_config)
        
        mock_encoder = AsyncMock()
        mock_encoder.embed.side_effect = EncoderError("Encoding failed")
        
        pipeline.encoder = mock_encoder
        pipeline.vectordb = AsyncMock()
        pipeline.decoder = AsyncMock()
        
        result = await pipeline.retrieve("test query")
        
        # Should return empty result on error
        assert len(result.chunks) == 0
        assert len(result.scores) == 0
        assert result.query_time_ms >= 0
    
    @pytest.mark.asyncio
    async def test_retrieve_by_document(self, mock_config, sample_chunk_content):
        """Test retrieving chunks by document ID."""
        pipeline = RetrievalPipeline(mock_config)
        
        mock_decoder = AsyncMock()
        mock_decoder.get_document_chunks.return_value = sample_chunk_content
        
        pipeline.decoder = mock_decoder
        pipeline.encoder = AsyncMock()
        pipeline.vectordb = AsyncMock()
        
        result = await pipeline.retrieve_by_document("doc-1", limit=10)
        
        assert result == sample_chunk_content
        mock_decoder.get_document_chunks.assert_called_once_with("doc-1", 10)


class TestRetrievalPipelineHealthCheck:
    """Test health check functionality."""
    
    @pytest.mark.asyncio
    async def test_health_check_all_healthy(self, mock_config):
        """Test health check when all components are healthy."""
        pipeline = RetrievalPipeline(mock_config)
        
        mock_encoder = AsyncMock()
        mock_vectordb = AsyncMock()
        mock_decoder = AsyncMock()
        
        mock_encoder.health_check.return_value = True
        mock_vectordb.health_check.return_value = True
        mock_decoder.health_check.return_value = True
        
        pipeline.encoder = mock_encoder
        pipeline.vectordb = mock_vectordb
        pipeline.decoder = mock_decoder
        
        result = await pipeline.health_check()
        
        assert result == {
            'encoder': True,
            'vectordb': True,
            'decoder': True
        }


class TestRetrievalPipelineCleanup:
    """Test cleanup functionality."""
    
    @pytest.mark.asyncio
    async def test_close(self, mock_config):
        """Test close method."""
        pipeline = RetrievalPipeline(mock_config)
        
        mock_encoder = AsyncMock()
        mock_vectordb = AsyncMock()
        mock_decoder = AsyncMock()
        
        pipeline.encoder = mock_encoder
        pipeline.vectordb = mock_vectordb
        pipeline.decoder = mock_decoder
        
        await pipeline.close()
        
        mock_encoder.close.assert_called_once()
        mock_vectordb.close.assert_called_once()
        mock_decoder.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_context_manager(self, mock_config):
        """Test using pipeline as context manager."""
        pipeline = RetrievalPipeline(mock_config)
        
        with patch.object(pipeline, 'setup', new_callable=AsyncMock) as mock_setup, \
             patch.object(pipeline, 'close', new_callable=AsyncMock) as mock_close:
            
            async with pipeline as p:
                assert p is pipeline
            
            mock_setup.assert_called_once()
            mock_close.assert_called_once()

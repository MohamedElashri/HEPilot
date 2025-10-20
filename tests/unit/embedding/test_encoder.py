"""Unit tests for ONNX BGE Encoder."""

import pytest
import numpy as np
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from src.embedding.adapters.onnx_bge_encoder import ONNXBGEEncoder
from src.embedding.exceptions import EncoderError


@pytest.fixture
def encoder():
    """Create an Encoder instance."""
    return ONNXBGEEncoder(
        model_name="BAAI/bge-small-en-v1.5",  # Use small model for tests
        device="cpu",
        batch_size=32,
        normalize=True,
        cache_dir=Path(".cache/test_models")
    )


class TestEncoderInit:
    """Test initialization and configuration."""
    
    def test_init_defaults(self):
        """Test encoder initialization with defaults."""
        encoder = ONNXBGEEncoder()
        assert encoder.model_name == "BAAI/bge-base-en-v1.5"
        assert encoder.device == "cpu"
        assert encoder.batch_size == 32
        assert encoder.normalize is True
        assert encoder._model is None
    
    def test_init_custom(self):
        """Test encoder initialization with custom values."""
        encoder = ONNXBGEEncoder(
            model_name="custom/model",
            device="cuda",
            batch_size=16,
            normalize=False,
            cache_dir=Path("/custom/cache")
        )
        assert encoder.model_name == "custom/model"
        assert encoder.device == "cuda"
        assert encoder.batch_size == 16
        assert encoder.normalize is False
        assert encoder.cache_dir == Path("/custom/cache")


class TestModelLoading:
    """Test model loading operations."""
    
    @pytest.mark.asyncio
    async def test_load_model_success(self, encoder):
        """Test successful model loading."""
        # Mock SentenceTransformer
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.max_seq_length = 512
        mock_model.eval.return_value = None
        
        with patch('src.embedding.adapters.onnx_bge_encoder.SentenceTransformer', return_value=mock_model):
            await encoder.load_model()
            
            assert encoder._model is not None
            assert encoder._dimension == 384
            assert encoder._max_tokens == 512
    
    @pytest.mark.asyncio
    async def test_load_model_already_loaded(self, encoder):
        """Test loading when model is already loaded."""
        # Set up mock model
        mock_model = MagicMock()
        encoder._model = mock_model
        encoder._dimension = 384
        encoder._max_tokens = 512
        
        # Call load_model again
        await encoder.load_model()
        
        # Should not reload
        assert encoder._model == mock_model
    
    @pytest.mark.asyncio
    async def test_load_model_failure(self, encoder):
        """Test model loading failure."""
        with patch('src.embedding.adapters.onnx_bge_encoder.SentenceTransformer', side_effect=Exception("Download failed")):
            with pytest.raises(EncoderError, match="Failed to load model"):
                await encoder.load_model()


class TestEmbedding:
    """Test embedding operations."""
    
    @pytest.mark.asyncio
    async def test_embed_single_text(self, encoder):
        """Test embedding a single text."""
        # Mock model
        mock_model = MagicMock()
        mock_embeddings = np.array([[0.1, 0.2, 0.3]], dtype=np.float32)
        mock_model.encode.return_value = mock_embeddings
        
        encoder._model = mock_model
        encoder._dimension = 3
        encoder._max_tokens = 512
        
        result = await encoder.embed(["test text"])
        
        assert result.shape == (1, 3)
        assert result.dtype == np.float32
        np.testing.assert_array_equal(result, mock_embeddings)
    
    @pytest.mark.asyncio
    async def test_embed_multiple_texts(self, encoder):
        """Test embedding multiple texts."""
        # Mock model
        mock_model = MagicMock()
        mock_embeddings = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9]
        ], dtype=np.float32)
        mock_model.encode.return_value = mock_embeddings
        
        encoder._model = mock_model
        encoder._dimension = 3
        encoder._max_tokens = 512
        
        result = await encoder.embed(["text 1", "text 2", "text 3"])
        
        assert result.shape == (3, 3)
        assert result.dtype == np.float32
        np.testing.assert_array_equal(result, mock_embeddings)
    
    @pytest.mark.asyncio
    async def test_embed_empty_list(self, encoder):
        """Test embedding empty list."""
        encoder._dimension = 384
        
        result = await encoder.embed([])
        
        assert result.shape == (0, 384)
        assert result.dtype == np.float32
    
    @pytest.mark.asyncio
    async def test_embed_loads_model_if_needed(self, encoder):
        """Test that embed loads model if not loaded."""
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.max_seq_length = 512
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]], dtype=np.float32)
        mock_model.eval.return_value = None
        
        with patch('src.embedding.adapters.onnx_bge_encoder.SentenceTransformer', return_value=mock_model):
            result = await encoder.embed(["test"])
            
            assert encoder._model is not None
            assert result.shape == (1, 3)
    
    @pytest.mark.asyncio
    async def test_embed_dtype_conversion(self, encoder):
        """Test that embeddings are converted to float32."""
        # Mock model returning float64
        mock_model = MagicMock()
        mock_embeddings = np.array([[0.1, 0.2, 0.3]], dtype=np.float64)
        mock_model.encode.return_value = mock_embeddings
        
        encoder._model = mock_model
        encoder._dimension = 3
        encoder._max_tokens = 512
        
        result = await encoder.embed(["test"])
        
        assert result.dtype == np.float32
    
    @pytest.mark.asyncio
    async def test_embed_with_batch_size(self, encoder):
        """Test embedding respects batch_size."""
        mock_model = MagicMock()
        mock_embeddings = np.array([[0.1, 0.2, 0.3]], dtype=np.float32)
        mock_model.encode.return_value = mock_embeddings
        
        encoder._model = mock_model
        encoder._dimension = 3
        encoder._max_tokens = 512
        encoder.batch_size = 16
        
        await encoder.embed(["test"])
        
        # Verify batch_size was passed to encode
        call_kwargs = mock_model.encode.call_args[1]
        assert call_kwargs['batch_size'] == 16
    
    @pytest.mark.asyncio
    async def test_embed_with_normalization(self, encoder):
        """Test embedding respects normalize setting."""
        mock_model = MagicMock()
        mock_embeddings = np.array([[0.1, 0.2, 0.3]], dtype=np.float32)
        mock_model.encode.return_value = mock_embeddings
        
        encoder._model = mock_model
        encoder._dimension = 3
        encoder._max_tokens = 512
        encoder.normalize = True
        
        await encoder.embed(["test"])
        
        # Verify normalize_embeddings was passed
        call_kwargs = mock_model.encode.call_args[1]
        assert call_kwargs['normalize_embeddings'] is True
    
    @pytest.mark.asyncio
    async def test_embed_error_handling(self, encoder):
        """Test error handling during embedding."""
        mock_model = MagicMock()
        mock_model.encode.side_effect = Exception("Encoding failed")
        
        encoder._model = mock_model
        encoder._dimension = 3
        encoder._max_tokens = 512
        
        with pytest.raises(EncoderError, match="Failed to encode texts"):
            await encoder.embed(["test"])


class TestProperties:
    """Test property accessors."""
    
    def test_dimension_before_load(self, encoder):
        """Test dimension property before model load."""
        with pytest.raises(EncoderError, match="Model not loaded"):
            _ = encoder.dimension
    
    def test_dimension_after_load(self, encoder):
        """Test dimension property after model load."""
        encoder._dimension = 384
        assert encoder.dimension == 384
    
    def test_max_tokens_before_load(self, encoder):
        """Test max_tokens property before model load."""
        with pytest.raises(EncoderError, match="Model not loaded"):
            _ = encoder.max_tokens
    
    def test_max_tokens_after_load(self, encoder):
        """Test max_tokens property after model load."""
        encoder._max_tokens = 512
        assert encoder.max_tokens == 512


class TestHealthCheck:
    """Test health check functionality."""
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, encoder):
        """Test health check when encoder is healthy."""
        # Mock model
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.max_seq_length = 512
        
        # Create normalized vector
        normalized_vector = np.array([[0.57735027, 0.57735027, 0.57735027]], dtype=np.float32)
        mock_model.encode.return_value = normalized_vector
        mock_model.eval.return_value = None
        
        with patch('src.embedding.adapters.onnx_bge_encoder.SentenceTransformer', return_value=mock_model):
            encoder._dimension = 3
            encoder._max_tokens = 512
            encoder._model = mock_model
            
            result = await encoder.health_check()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_loads_model(self, encoder):
        """Test health check loads model if needed."""
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 3  # Match dimension
        mock_model.max_seq_length = 512
        normalized_vector = np.array([[0.57735027, 0.57735027, 0.57735027]], dtype=np.float32)
        mock_model.encode.return_value = normalized_vector
        mock_model.eval.return_value = None
        
        with patch('src.embedding.adapters.onnx_bge_encoder.SentenceTransformer', return_value=mock_model):
            result = await encoder.health_check()
            
            assert result is True
            assert encoder._model is not None
    
    @pytest.mark.asyncio
    async def test_health_check_wrong_shape(self, encoder):
        """Test health check fails with wrong shape."""
        mock_model = MagicMock()
        # Wrong shape
        mock_embeddings = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
        mock_model.encode.return_value = mock_embeddings
        
        encoder._model = mock_model
        encoder._dimension = 3
        encoder._max_tokens = 512
        
        result = await encoder.health_check()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_health_check_not_normalized(self, encoder):
        """Test health check fails if not normalized when should be."""
        mock_model = MagicMock()
        # Not normalized vector
        mock_embeddings = np.array([[1.0, 2.0, 3.0]], dtype=np.float32)
        mock_model.encode.return_value = mock_embeddings
        
        encoder._model = mock_model
        encoder._dimension = 3
        encoder._max_tokens = 512
        encoder.normalize = True
        
        result = await encoder.health_check()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_health_check_exception(self, encoder):
        """Test health check returns False on exception."""
        mock_model = MagicMock()
        mock_model.encode.side_effect = Exception("Health check failed")
        
        encoder._model = mock_model
        encoder._dimension = 3
        encoder._max_tokens = 512
        
        result = await encoder.health_check()
        
        assert result is False


class TestCleanup:
    """Test cleanup operations."""
    
    @pytest.mark.asyncio
    async def test_close_cpu(self, encoder):
        """Test closing encoder on CPU."""
        mock_model = MagicMock()
        encoder._model = mock_model
        encoder.device = "cpu"
        
        await encoder.close()
        
        # Close should complete without calling to() for CPU
        # (to() is only called for CUDA)
    
    @pytest.mark.asyncio
    async def test_close_cuda(self, encoder):
        """Test closing encoder on CUDA."""
        mock_model = MagicMock()
        encoder._model = mock_model
        encoder.device = "cuda"
        
        with patch('torch.cuda.is_available', return_value=True):
            with patch('torch.cuda.empty_cache') as mock_empty_cache:
                await encoder.close()
                
                # Should move to CPU and clear cache
                mock_model.to.assert_called_with("cpu")
                mock_empty_cache.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_no_model(self, encoder):
        """Test closing when no model loaded."""
        await encoder.close()  # Should not raise


class TestContextManager:
    """Test async context manager support."""
    
    @pytest.mark.asyncio
    async def test_context_manager(self, encoder):
        """Test using encoder as async context manager."""
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.max_seq_length = 512
        mock_model.eval.return_value = None
        mock_model.to.return_value = mock_model
        
        encoder.device = "cuda"  # Set to CUDA so to() gets called
        
        with patch('src.embedding.adapters.onnx_bge_encoder.SentenceTransformer', return_value=mock_model):
            with patch('torch.cuda.is_available', return_value=True):
                with patch('torch.cuda.empty_cache') as mock_empty_cache:
                    async with encoder as enc:
                        assert enc._model is not None
                        assert enc is encoder
                    
                    # Should be closed after exit with CUDA cleanup
                    mock_model.to.assert_called_with("cpu")
                    mock_empty_cache.assert_called_once()

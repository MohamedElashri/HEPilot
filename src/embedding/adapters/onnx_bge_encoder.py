"""ONNX-based BGE text encoder for embedding layer."""

import asyncio
from typing import List, Optional
from pathlib import Path
import numpy as np
from numpy.typing import NDArray

from sentence_transformers import SentenceTransformer
import torch

from src.embedding.exceptions import EncoderError


class ONNXBGEEncoder:
    """Text-to-vector encoder using BGE models via sentence-transformers.
    
    This encoder uses the sentence-transformers library which handles:
    - Model downloading and caching
    - Tokenization with proper handling of context length
    - Batch processing with automatic padding
    - Vector normalization
    - CPU/CUDA device management
    
    The encoder is configured to work with BGE (BAAI General Embedding) models
    but can work with any sentence-transformers compatible model.
    """
    
    def __init__(
        self,
        model_name: str = "BAAI/bge-base-en-v1.5",
        device: str = "cpu",
        batch_size: int = 32,
        normalize: bool = True,
        cache_dir: Optional[Path] = None
    ):
        """Initialize encoder.
        
        Args:
            model_name: HuggingFace model identifier (e.g., "BAAI/bge-base-en-v1.5")
            device: Device to run on ("cpu" or "cuda")
            batch_size: Batch size for encoding
            normalize: Whether to L2-normalize embeddings (recommended for BGE)
            cache_dir: Directory to cache models (default: ~/.cache/torch/sentence_transformers)
        """
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size
        self.normalize = normalize
        self.cache_dir = cache_dir
        self._model: Optional[SentenceTransformer] = None
        self._dimension: Optional[int] = None
        self._max_tokens: Optional[int] = None
    
    async def load_model(self):
        """Load the sentence-transformers model.
        
        This downloads the model if not cached and initializes it.
        Runs in executor to avoid blocking the event loop.
        
        Raises:
            EncoderError: If model loading fails
        """
        if self._model is not None:
            # Already loaded
            return
        
        try:
            # Run model loading in executor (blocking operation)
            loop = asyncio.get_event_loop()
            self._model = await loop.run_in_executor(
                None,
                self._load_model_sync
            )
            
            # Get model properties
            self._dimension = self._model.get_sentence_embedding_dimension()
            
            # Get max sequence length from tokenizer
            # sentence-transformers models have max_seq_length attribute
            if hasattr(self._model, 'max_seq_length'):
                self._max_tokens = self._model.max_seq_length
            else:
                # Fallback to tokenizer's model_max_length
                self._max_tokens = self._model.tokenizer.model_max_length
            
        except Exception as e:
            raise EncoderError(f"Failed to load model '{self.model_name}': {e}")
    
    def _load_model_sync(self) -> SentenceTransformer:
        """Synchronous model loading helper.
        
        Returns:
            Loaded SentenceTransformer model
        """
        # Prepare cache_dir parameter
        cache_dir_str = str(self.cache_dir) if self.cache_dir else None
        
        # Load model
        model = SentenceTransformer(
            self.model_name,
            device=self.device,
            cache_folder=cache_dir_str
        )
        
        # Set to evaluation mode
        model.eval()
        
        return model
    
    async def embed(self, texts: List[str]) -> NDArray[np.float32]:
        """Encode text strings to vectors.
        
        Handles:
        - Automatic batching for large inputs
        - Tokenization with truncation for long texts
        - Padding for variable-length texts
        - L2 normalization (if configured)
        - Device placement (CPU/CUDA)
        
        Args:
            texts: List of text strings to encode
            
        Returns:
            2D numpy array of shape (len(texts), embedding_dim)
            All vectors are L2-normalized if normalize=True
            
        Raises:
            EncoderError: If encoding fails
        """
        if not texts:
            return np.array([], dtype=np.float32).reshape(0, self.dimension)
        
        # Ensure model is loaded
        if self._model is None:
            await self.load_model()
        
        try:
            # Run encoding in executor (blocking operation)
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                self._encode_sync,
                texts
            )
            
            return embeddings
            
        except Exception as e:
            raise EncoderError(f"Failed to encode texts: {e}")
    
    def _encode_sync(self, texts: List[str]) -> NDArray[np.float32]:
        """Synchronous encoding helper.
        
        Args:
            texts: List of text strings
            
        Returns:
            2D numpy array of embeddings
        """
        # sentence-transformers handles:
        # - Tokenization with truncation
        # - Batching
        # - Padding
        # - Device placement
        # - Normalization (if normalize_embeddings=True)
        embeddings = self._model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=self.normalize,
            show_progress_bar=False,  # Disable for production
            convert_to_numpy=True,
            device=self.device
        )
        
        # Ensure float32 dtype
        if embeddings.dtype != np.float32:
            embeddings = embeddings.astype(np.float32)
        
        return embeddings
    
    @property
    def dimension(self) -> int:
        """Vector dimensionality.
        
        Returns:
            Embedding dimension (e.g., 384 for bge-base, 768 for bge-large)
            
        Raises:
            EncoderError: If model not loaded yet
        """
        if self._dimension is None:
            raise EncoderError("Model not loaded. Call load_model() first.")
        return self._dimension
    
    @property
    def max_tokens(self) -> int:
        """Maximum token length supported by the model.
        
        Texts longer than this will be truncated during encoding.
        
        Returns:
            Maximum sequence length (typically 512 for BGE models)
            
        Raises:
            EncoderError: If model not loaded yet
        """
        if self._max_tokens is None:
            raise EncoderError("Model not loaded. Call load_model() first.")
        return self._max_tokens
    
    async def health_check(self) -> bool:
        """Verify encoder is operational.
        
        Tests that:
        - Model is loaded
        - Can encode a simple test string
        - Returns expected embedding shape
        
        Returns:
            True if operational, False otherwise
        """
        try:
            # Ensure model is loaded
            if self._model is None:
                await self.load_model()
            
            # Test encoding a simple string
            test_text = "This is a test."
            embeddings = await self.embed([test_text])
            
            # Verify shape
            if embeddings.shape != (1, self.dimension):
                return False
            
            # Verify normalized (if configured)
            if self.normalize:
                norm = np.linalg.norm(embeddings[0])
                if not np.isclose(norm, 1.0, atol=1e-5):
                    return False
            
            return True
            
        except Exception:
            return False
    
    async def close(self):
        """Clean up resources.
        
        Moves model to CPU and clears CUDA cache if using GPU.
        """
        if self._model is not None:
            # Run cleanup in executor (blocking operation)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._close_sync)
    
    def _close_sync(self):
        """Synchronous cleanup helper."""
        # Move to CPU to free GPU memory
        if self.device == "cuda":
            self._model = self._model.to("cpu")
            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.load_model()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

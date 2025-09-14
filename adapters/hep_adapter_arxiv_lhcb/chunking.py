#!/usr/bin/env python3
"""
Chunking Module for HEPilot ArXiv Adapter
Handles segmenting documents into LLM-sized chunks with semantic boundaries and overlap.
"""

import logging
import re
import uuid
from typing import Dict, Any, Iterator, List
from pathlib import Path

from sentence_transformers import SentenceTransformer

from models import Chunk
from progress_tracker import ProgressTracker


class ChunkingEngine:
    """Chunking engine for segmenting documents into LLM-sized pieces."""
    
    def __init__(self, config: Dict[str, Any], output_dir: Path = None):
        """Initialize the chunking engine.
        
        Args:
            config: Adapter configuration dictionary
            output_dir: Output directory path for progress tracking (optional)
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.tokenizer = SentenceTransformer(self.config["x_extension"]["tokenizer_model"]).tokenizer
        self.progress_tracker = ProgressTracker(output_dir) if output_dir else None
    
    def chunk_document(self, document_id: str, content: str) -> Iterator[Chunk]:
        """Chunk document content into LLM-sized pieces.
        
        Args:
            document_id: UUID of the document
            content: Full document content as markdown
            
        Yields:
            Chunk objects with overlapping content
        """
        # Simple sentence-based chunking with overlap
        sentences = self._split_sentences(content)
        
        chunk_index = 0
        total_tokens = self._count_tokens_safely(content)
        total_chunks = self._estimate_chunk_count(total_tokens)
        
        current_chunk = []
        current_tokens = 0
        
        for i, sentence in enumerate(sentences):
            sentence_tokens = self._count_sentence_tokens_safely(sentence)
            
            # Check if adding this sentence exceeds chunk size
            if current_tokens + sentence_tokens > self.config["processing_config"]["chunk_size"] and current_chunk:
                # Create chunk
                chunk_content = ' '.join(current_chunk)
                chunk = self._create_chunk(
                    document_id, chunk_index, total_chunks, chunk_content, current_tokens
                )
                yield chunk
                
                # Handle overlap
                overlap_size = int(self.config["processing_config"]["chunk_size"] * 
                                 self.config["processing_config"]["chunk_overlap"])
                
                # Keep some sentences for overlap
                overlap_sentences = self._get_overlap_sentences(current_chunk, overlap_size)
                current_chunk = overlap_sentences
                current_tokens = sum(self._count_sentence_tokens_safely(s) for s in current_chunk)
                
                chunk_index += 1
            
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
        
        # Create final chunk if there's remaining content
        if current_chunk:
            chunk_content = ' '.join(current_chunk)
            chunk = self._create_chunk(
                document_id, chunk_index, total_chunks, chunk_content, current_tokens
            )
            yield chunk
    
    def _split_sentences(self, content: str) -> List[str]:
        """Split content into sentences while preserving structure.
        
        Args:
            content: Document content
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting - can be enhanced with more sophisticated NLP
        sentences = re.split(r'(?<=[.!?])\s+', content)
        return [s.strip() for s in sentences if s.strip()]
    
    def _estimate_chunk_count(self, total_tokens: int) -> int:
        """Estimate the total number of chunks needed.
        
        Args:
            total_tokens: Total token count in the document
            
        Returns:
            Estimated number of chunks
        """
        chunk_size = self.config["processing_config"]["chunk_size"]
        overlap = self.config["processing_config"]["chunk_overlap"]
        effective_chunk_size = chunk_size * (1 - overlap)
        return max(1, int(total_tokens / effective_chunk_size))
    
    def _create_chunk(self, document_id: str, chunk_index: int, total_chunks: int, 
                     content: str, token_count: int) -> Chunk:
        """Create a Chunk object with metadata.
        
        Args:
            document_id: Document UUID
            chunk_index: Index of this chunk
            total_chunks: Total estimated chunks
            content: Chunk content
            token_count: Number of tokens in chunk
            
        Returns:
            Chunk object with complete metadata
        """
        chunk_id = str(uuid.uuid4())
        
        # Analyze content features
        content_features = self._analyze_content(content)
        
        # Determine chunk type based on content
        chunk_type = self._determine_chunk_type(content_features)
        
        return Chunk(
            chunk_id=chunk_id,
            document_id=document_id,
            chunk_index=chunk_index,
            total_chunks=total_chunks,
            content=content,
            token_count=token_count,
            chunk_type=chunk_type,
            section_path=self._extract_section_path(content),
            has_overlap_previous=chunk_index > 0,
            has_overlap_next=chunk_index < total_chunks - 1,
            content_features=content_features
        )
    
    def _get_overlap_sentences(self, sentences: List[str], overlap_tokens: int) -> List[str]:
        """Get sentences for overlap with the next chunk.
        
        Args:
            sentences: Current chunk sentences
            overlap_tokens: Target number of overlap tokens
            
        Returns:
            List of sentences to include in overlap
        """
        overlap_sentences = []
        current_tokens = 0
        
        # Start from the end and work backwards
        for sentence in reversed(sentences):
            sentence_tokens = self._count_sentence_tokens_safely(sentence)
            if current_tokens + sentence_tokens <= overlap_tokens:
                overlap_sentences.insert(0, sentence)
                current_tokens += sentence_tokens
            else:
                break
        
        return overlap_sentences
    
    def _analyze_content(self, content: str) -> Dict[str, int]:
        """Analyze content to count different features.
        
        Args:
            content: Chunk content
            
        Returns:
            Dictionary with feature counts
        """
        return {
            "heading_count": len(re.findall(r'^#+\s', content, re.MULTILINE)),
            "list_count": len(re.findall(r'^[-*+]\s', content, re.MULTILINE)),
            "table_count": len(re.findall(r'\|.*\|', content)),
            "equation_count": len(re.findall(r'\$.*?\$', content, re.DOTALL))
        }
    
    def _determine_chunk_type(self, features: Dict[str, int]) -> str:
        """Determine chunk type based on content features.
        
        Args:
            features: Content feature counts
            
        Returns:
            Chunk type string
        """
        if features["table_count"] > 0 and features["equation_count"] > 0:
            return "mixed"
        elif features["table_count"] > 0:
            return "table"
        elif features["equation_count"] > 0:
            return "equation"
        else:
            return "text"
    
    def _extract_section_path(self, content: str) -> List[str]:
        """Extract section hierarchy from content.
        
        Args:
            content: Chunk content
            
        Returns:
            List representing section path
        """
        # Extract the first heading found in the chunk
        headings = re.findall(r'^(#+)\s+(.+)$', content, re.MULTILINE)
        if headings:
            level, title = headings[0]
            return [title.strip()]
        return []
    
    def _count_tokens_safely(self, content: str) -> int:
        """Safely count tokens by processing content in smaller batches to avoid memory issues.
        
        Args:
            content: Document content to count tokens for
            
        Returns:
            Total token count
        """
        # Split content into manageable chunks for token counting
        max_chars_per_batch = 10000  # Process ~10KB at a time
        total_tokens = 0
        
        # Process content in batches to avoid hitting token limits
        for i in range(0, len(content), max_chars_per_batch):
            batch = content[i:i + max_chars_per_batch]
            try:
                batch_tokens = len(self.tokenizer.encode(batch, add_special_tokens=False))
                total_tokens += batch_tokens
            except Exception as e:
                self.logger.warning(f"Token counting failed for batch {i//max_chars_per_batch}, using character estimation: {e}")
                # Fallback to character-based estimation (rough approximation: 4 chars per token)
                total_tokens += len(batch) // 4
        
        self.logger.debug(f"Document token count: {total_tokens}")
        return total_tokens
    
    def _count_sentence_tokens_safely(self, sentence: str) -> int:
        """Safely count tokens for a single sentence with fallback for very long sentences.
        
        Args:
            sentence: Single sentence to count tokens for
            
        Returns:
            Token count for the sentence
        """
        try:
            # If sentence is extremely long, use character estimation instead
            if len(sentence) > 20000:  # ~20KB sentence, likely corrupted or concatenated
                self.logger.warning(f"Very long sentence detected ({len(sentence)} chars), using character estimation")
                return len(sentence) // 4  # Rough approximation
            
            return len(self.tokenizer.encode(sentence, add_special_tokens=False))
        except Exception as e:
            self.logger.warning(f"Token counting failed for sentence, using character estimation: {e}")
            # Fallback to character-based estimation
            return len(sentence) // 4

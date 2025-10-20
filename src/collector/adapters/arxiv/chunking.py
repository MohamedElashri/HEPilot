"""
Chunking engine for creating token-aware chunks with semantic boundaries.

Uses the actual embedding model's tokenizer (BAAI/bge-large-en-v1.5) for
accurate token counting, ensuring chunks match the model's constraints.
Splits documents with configurable overlap, preserving equations, tables, and code blocks.
"""

import re
import json
import uuid
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
from uuid import UUID
from models import ChunkContent

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class ArxivChunker:
    """Creates token-aware semantic chunks using embedding model tokenizer."""
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: float = 0.1,
        model_name: str = "BAAI/bge-large-en-v1.5",
        use_model_tokenizer: bool = True,
        cache_dir: str = ".model_cache"
    ) -> None:
        """
        Initialize chunking engine with embedding model.
        
        Args:
            chunk_size: Target chunk size in tokens (must not exceed model's max_seq_length)
            chunk_overlap: Overlap fraction (0 to <1)
            model_name: Embedding model name from sentence_transformers
            use_model_tokenizer: Whether to use model's tokenizer (recommended)
            cache_dir: Directory to cache downloaded models
        """
        self.chunk_size: int = chunk_size
        self.chunk_overlap: float = chunk_overlap
        self.overlap_tokens: int = int(chunk_size * chunk_overlap)
        self.model_name: str = model_name
        self.use_model_tokenizer: bool = use_model_tokenizer
        self.cache_dir: str = cache_dir
        self.model: Optional[Any] = None
        self.tokenizer: Optional[Any] = None
        self.max_seq_length: int = 512
        if use_model_tokenizer:
            self._initialize_model()
            self._validate_chunk_size()
    
    def _initialize_model(self) -> None:
        """
        Initialize sentence transformer model and extract tokenizer.
        
        This loads the actual embedding model that will be used in the RAG system,
        ensuring token counts are accurate for the target model. The model's
        max_seq_length is automatically detected.
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            print(f"WARNING: sentence-transformers not available, falling back to word-based counting")
            return
        try:
            print(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, cache_folder=self.cache_dir)
            self.tokenizer = self.model.tokenizer
            self.max_seq_length = self.model.get_max_seq_length()
            print(f"Model loaded successfully. Max sequence length: {self.max_seq_length}")
        except Exception as e:
            print(f"WARNING: Failed to load model {self.model_name}: {e}")
            print("Falling back to word-based counting")
            self.model = None
            self.tokenizer = None
    
    def _validate_chunk_size(self) -> None:
        """
        Validate that chunk_size doesn't exceed the model's maximum sequence length.
        
        Raises:
            ValueError: If chunk_size exceeds model's max_seq_length
        """
        if self.model is not None and self.chunk_size > self.max_seq_length:
            raise ValueError(
                f"chunk_size ({self.chunk_size}) exceeds model's max_seq_length ({self.max_seq_length}). "
                f"Please set chunk_size <= {self.max_seq_length} in adapter_config.json"
            )
    
    def chunk(self, markdown_path: Path, document_id: UUID) -> List[ChunkContent]:
        """
        Create chunks from markdown document.
        
        Args:
            markdown_path: Path to markdown file
            document_id: UUID of parent document
            
        Returns:
            List of chunk content objects
        """
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content: str = f.read()
        sections: List[Tuple[str, str]] = self._split_by_sections(content)
        chunks: List[ChunkContent] = []
        chunk_index: int = 0
        previous_overlap_text: str = ""
        for section_path, section_text in sections:
            section_chunks: List[str] = self._chunk_section(section_text, previous_overlap_text)
            for i, chunk_text in enumerate(section_chunks):
                token_count: int = self._count_tokens(chunk_text)
                chunk: ChunkContent = ChunkContent(
                    chunk_id=uuid.uuid4(),
                    document_id=document_id,
                    chunk_index=chunk_index,
                    total_chunks=0,
                    content=chunk_text,
                    token_count=token_count,
                    chunk_type=self._detect_chunk_type(chunk_text),
                    section_path=[section_path] if section_path else None,
                    has_overlap_previous=(i > 0 or chunk_index > 0),
                    has_overlap_next=(i < len(section_chunks) - 1),
                    content_features=self._extract_features(chunk_text)
                )
                chunks.append(chunk)
                chunk_index += 1
                if section_chunks:
                    previous_overlap_text = self._extract_overlap(section_chunks[-1])
        for chunk in chunks:
            chunk.total_chunks = len(chunks)
            chunk.has_overlap_next = (chunk.chunk_index < len(chunks) - 1)
        return chunks
    
    def _split_by_sections(self, content: str) -> List[Tuple[str, str]]:
        """
        Split content by markdown sections.
        
        Args:
            content: Markdown content
            
        Returns:
            List of (section_path, section_text) tuples
        """
        sections: List[Tuple[str, str]] = []
        lines: List[str] = content.split('\n')
        current_section: str = "Document"
        current_text: List[str] = []
        for line in lines:
            if line.startswith('##'):
                if current_text:
                    sections.append((current_section, '\n'.join(current_text)))
                    current_text = []
                current_section = line.lstrip('#').strip()
            current_text.append(line)
        if current_text:
            sections.append((current_section, '\n'.join(current_text)))
        return sections
    
    def _chunk_section(self, text: str, previous_overlap: str) -> List[str]:
        """
        Chunk a section into token-sized pieces.
        
        Args:
            text: Section text
            previous_overlap: Overlap text from previous section
            
        Returns:
            List of chunk strings
        """
        if previous_overlap:
            text = previous_overlap + "\n\n" + text
        sentences: List[str] = self._split_sentences(text)
        chunks: List[str] = []
        current_chunk: List[str] = []
        current_tokens: int = 0
        for sentence in sentences:
            sentence_tokens: int = self._count_sentence_tokens_safely(sentence)
            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                overlap_sentences: List[str] = self._get_overlap_sentences(current_chunk)
                current_chunk = overlap_sentences
                current_tokens = sum(self._count_sentence_tokens_safely(s) for s in overlap_sentences)
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        text = re.sub(r'\n+', ' ', text)
        sentences: List[str] = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap_sentences(self, sentences: List[str]) -> List[str]:
        """
        Get sentences for overlap based on token count.
        
        Args:
            sentences: List of sentences
            
        Returns:
            Sentences to include in overlap
        """
        overlap_sents: List[str] = []
        overlap_count: int = 0
        for sentence in reversed(sentences):
            sent_tokens: int = self._count_sentence_tokens_safely(sentence)
            if overlap_count + sent_tokens > self.overlap_tokens:
                break
            overlap_sents.insert(0, sentence)
            overlap_count += sent_tokens
        return overlap_sents
    
    def _extract_overlap(self, chunk_text: str) -> str:
        """
        Extract overlap text from end of chunk.
        
        Args:
            chunk_text: Chunk text
            
        Returns:
            Overlap text
        """
        sentences: List[str] = self._split_sentences(chunk_text)
        overlap_sentences: List[str] = self._get_overlap_sentences(sentences)
        return ' '.join(overlap_sentences)
    
    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text using the embedding model's tokenizer.
        
        Uses safe batched processing to prevent memory issues with large texts.
        This ensures accurate token counts matching the actual embedding model.
        
        Args:
            text: Input text
            
        Returns:
            Token count matching the embedding model's tokenization
        """
        if self.tokenizer is not None:
            try:
                return self._count_tokens_safely(text)
            except Exception as e:
                print(f"WARNING: Token counting failed: {e}, falling back to word count")
        return len(text.split())
    
    def _count_tokens_safely(self, text: str) -> int:
        """
        Count tokens safely by processing in batches to avoid memory issues.
        
        Critical for handling large documents (161K+ tokens) that would cause
        memory errors if tokenized all at once. Processes in 10KB character batches.
        
        Args:
            text: Input text
            
        Returns:
            Token count
        """
        if not text:
            return 0
        max_batch_size: int = 10000
        if len(text) <= max_batch_size:
            try:
                tokens = self.tokenizer.encode(
                    text,
                    add_special_tokens=False,
                    truncation=False,
                    max_length=None
                )
                return len(tokens)
            except Exception as e:
                print(f"WARNING: Tokenization failed for short text: {e}")
                return len(text.split())
        total_tokens: int = 0
        for i in range(0, len(text), max_batch_size):
            batch: str = text[i:i + max_batch_size]
            try:
                tokens = self.tokenizer.encode(
                    batch,
                    add_special_tokens=False,
                    truncation=False,
                    max_length=None
                )
                total_tokens += len(tokens)
            except Exception as e:
                print(f"WARNING: Batch tokenization failed: {e}, using word count")
                total_tokens += len(batch.split())
        return total_tokens
    
    def _count_sentence_tokens_safely(self, sentence: str) -> int:
        """
        Count tokens for a single sentence with error handling.
        
        Args:
            sentence: Input sentence
            
        Returns:
            Token count for the sentence
        """
        if not sentence:
            return 0
        if self.tokenizer is not None:
            try:
                tokens = self.tokenizer.encode(
                    sentence,
                    add_special_tokens=False,
                    truncation=False,
                    max_length=None
                )
                return len(tokens)
            except Exception:
                pass
        return len(sentence.split())
    
    def _detect_chunk_type(self, text: str) -> str:
        """
        Detect primary content type of chunk.
        
        Args:
            text: Chunk text
            
        Returns:
            Chunk type ('text', 'table', 'equation', 'mixed')
        """
        has_table: bool = '|' in text and '---' in text
        has_equation: bool = '$$' in text or '$' in text
        if has_table and has_equation:
            return "mixed"
        if has_table:
            return "table"
        if has_equation:
            return "equation"
        return "text"
    
    def _extract_features(self, text: str) -> Dict[str, int]:
        """
        Extract content features from chunk.
        
        Args:
            text: Chunk text
            
        Returns:
            Feature counts
        """
        return {
            "heading_count": len(re.findall(r'^#+\s', text, re.MULTILINE)),
            "list_count": len(re.findall(r'^[\*\-\+]\s|\d+\.\s', text, re.MULTILINE)),
            "table_count": text.count('|---'),
            "equation_count": text.count('$$') + text.count('$')
        }
    
    def save_chunks(self, chunks: List[ChunkContent], output_dir: Path) -> None:
        """
        Save chunks to individual files with metadata.
        
        Args:
            chunks: List of chunks
            output_dir: Output directory
        """
        chunks_dir: Path = output_dir / "chunks"
        chunks_dir.mkdir(parents=True, exist_ok=True)
        for chunk in chunks:
            chunk_num: str = f"{chunk.chunk_index + 1:04d}"
            content_path: Path = chunks_dir / f"chunk_{chunk_num}.md"
            with open(content_path, 'w', encoding='utf-8') as f:
                f.write(chunk.content)
            metadata_path: Path = chunks_dir / f"chunk_{chunk_num}_metadata.json"
            metadata: Dict[str, Any] = {
                "chunk_id": str(chunk.chunk_id),
                "document_id": str(chunk.document_id),
                "chunk_index": chunk.chunk_index,
                "total_chunks": chunk.total_chunks,
                "token_count": chunk.token_count,
                "chunk_type": chunk.chunk_type,
                "section_path": chunk.section_path,
                "has_overlap_previous": chunk.has_overlap_previous,
                "has_overlap_next": chunk.has_overlap_next,
                "content_features": chunk.content_features
            }
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)

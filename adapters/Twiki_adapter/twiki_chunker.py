"""
TWiki Chunking Engine for HEPilot

Splits TWiki Markdown documents into token-aware chunks with semantic boundaries
(sections → paragraphs → sentences). Uses the embedding model tokenizer
(BAAI/bge-large-en-v1.5) for accurate token counts.

Outputs:
  - chunk_output.json  → aggregate chunk list (for embeddings)
  - chunk_XXXX_metadata.json  → per-chunk metadata (for QA & diagnostics)
  - chunk_XXXX.md  → raw chunk content

Schema compliance:
  - chunk_output.schema.json
  - chunk_metadata.schema.json
"""

import re
import json
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
from uuid import UUID
from datetime import datetime, timezone

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class ChunkContent:
    # Lightweight container for chunk data 
    def __init__(self,
                 chunk_id: UUID,
                 document_id: UUID,
                 chunk_index: int,
                 total_chunks: int,
                 content: str,
                 token_count: int,
                 chunk_type: str,
                 section_path: Optional[List[str]] = None,
                 has_overlap_previous: bool = False,
                 has_overlap_next: bool = False,
                 content_features: Optional[Dict[str, int]] = None):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.chunk_index = chunk_index
        self.total_chunks = total_chunks
        self.content = content
        self.token_count = token_count
        self.chunk_type = chunk_type
        self.section_path = section_path or []
        self.has_overlap_previous = has_overlap_previous
        self.has_overlap_next = has_overlap_next
        self.content_features = content_features or {}


class TWikiChunker:
    # Token-aware chunker for TWiki Markdown documents

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: float = 0.1,
        model_name: str = "BAAI/bge-large-en-v1.5",
        use_model_tokenizer: bool = True,
        cache_dir: str = ".model_cache",
        verbose: bool = True
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.overlap_tokens = int(chunk_size * chunk_overlap)
        self.model_name = model_name
        self.use_model_tokenizer = use_model_tokenizer
        self.cache_dir = cache_dir
        self.verbose = verbose

        self.model = None
        self.tokenizer = None
        self.max_seq_length = 512

        if use_model_tokenizer:
            self._initialize_model()
            self._validate_chunk_size()

    def _initialize_model(self) -> None:
        # Load embedding model tokenizer
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            print("[WARNING] sentence-transformers not installed; falling back to word counting.")
            return
        try:
            if self.verbose:
                print(f"Loading tokenizer from {self.model_name}...")
            self.model = SentenceTransformer(self.model_name, cache_folder=self.cache_dir)
            self.tokenizer = self.model.tokenizer
            self.max_seq_length = self.model.get_max_seq_length()
            if self.verbose:
                print(f"Tokenizer loaded. Max length = {self.max_seq_length}")
        except Exception as e:
            print(f"[ERROR] Could not load tokenizer: {e}")
            self.model = None
            self.tokenizer = None

    def _validate_chunk_size(self) -> None:
        # Ensure chunk_size is less than model max sequence length
        if self.model and self.chunk_size > self.max_seq_length: # type: ignore
            raise ValueError(
                f"chunk_size ({self.chunk_size}) exceeds max_seq_length ({self.max_seq_length})"
            )

    def _count_tokens(self, text: str) -> int:
        # Count tokens using model tokenizer, fallback to word count
        if self.tokenizer:
            try:
                tokens = self.tokenizer.encode(text, add_special_tokens=False)
                return len(tokens)
            except Exception:
                pass
        if not self.tokenizer and self.verbose:
            print("[INFO] Using word-based token approximation.")
        return len(text.split())

    def _split_sentences(self, text: str) -> List[str]:
        # Split text into sentences using punctuation boundaries
        text = re.sub(r'\n+', ' ', text)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _detect_chunk_type(self, text: str) -> str:
        # Detect content type: text, table, equation, mixed.
        has_table = bool(re.search(r'^\|.*\|', text, flags=re.MULTILINE))
        has_equation = "$" in text or "$$" in text
        if has_table and has_equation:
            return "mixed"
        if has_table:
            return "table"
        if has_equation:
            return "equation"
        return "text"

    def _extract_features(self, text: str) -> Dict[str, int]:
        # Extract content structure features
        return {
            "heading_count": len(re.findall(r'^#+\s', text, re.MULTILINE)),
            "list_count": len(re.findall(r'^[\*\-\+]\s|\d+\.\s', text, re.MULTILINE)),
            "table_count": len(re.findall(r'^\|.*\|', text, re.MULTILINE)),
            "equation_count": text.count("$$") + text.count("$")
        }

    def _get_overlap_sentences(self, sentences: List[str]) -> List[str]:
        # Return sentences to overlap based on token limit
        overlap = []
        overlap_count = 0
        for sentence in reversed(sentences):
            tcount = self._count_tokens(sentence)
            if overlap_count + tcount > self.overlap_tokens:
                break
            overlap.insert(0, sentence)
            overlap_count += tcount
        return overlap

    def chunk_document(self, markdown_path: Path, document_id: UUID) -> List[ChunkContent]:
        """
        Chunk a Markdown document into token-aware pieces.
        """
        with open(markdown_path, "r", encoding="utf-8") as f:
            content = f.read()

        sentences = self._split_sentences(content)
        chunks: List[ChunkContent] = []
        current_chunk: List[str] = []
        current_tokens = 0
        chunk_index = 0

        for sentence in sentences:
            tcount = self._count_tokens(sentence)
            if current_tokens + tcount > self.chunk_size and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunk = self._make_chunk(chunk_text, document_id, chunk_index, False)
                chunks.append(chunk)
                chunk_index += 1
                overlap_sents = self._get_overlap_sentences(current_chunk)
                current_chunk = overlap_sents + [sentence]
                current_tokens = sum(self._count_tokens(s) for s in overlap_sents) + tcount
            else:
                current_chunk.append(sentence)
                current_tokens += tcount

        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk = self._make_chunk(chunk_text, document_id, chunk_index, True)
            chunks.append(chunk)

        total = len(chunks)
        for c in chunks:
            c.total_chunks = total
            c.has_overlap_next = (c.chunk_index < total - 1)

        if self.verbose:
            print(f"[INFO] Generated {len(chunks)} chunks from {markdown_path.name}")
        return chunks

    def _make_chunk(self, text: str, document_id: UUID, index: int, is_last: bool) -> ChunkContent:
        # Build ChunkContent object.
        token_count = self._count_tokens(text)
        return ChunkContent(
            chunk_id=uuid.uuid4(),
            document_id=document_id,
            chunk_index=index,
            total_chunks=0,
            content=text,
            token_count=token_count,
            chunk_type=self._detect_chunk_type(text),
            section_path=self._extract_section_path(text),
            has_overlap_previous=index > 0,
            content_features=self._extract_features(text)
        )

    def _extract_section_path(self, text: str) -> List[str]:
        """Extract Markdown headers as section hierarchy."""
        headers = re.findall(r"^(#+)\s*(.+)", text, flags=re.MULTILINE)
        return [h[1].strip() for h in headers[:3]]

    def save_chunks(self, chunks: List[ChunkContent], output_dir: Path) -> None:
        """
        Save chunks, metadata, and aggregate output.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        chunks_dir = output_dir / "chunks"
        chunks_dir.mkdir(exist_ok=True)

        chunk_entries = []
        for chunk in chunks:
            num = f"{chunk.chunk_index:04d}"
            content_path = chunks_dir / f"chunk_{num}.md"
            with open(content_path, "w", encoding="utf-8") as f:
                f.write(chunk.content)

            # chunk metadata file
            metadata = self._make_metadata_dict(chunk)
            meta_path = chunks_dir / f"chunk_{num}_metadata.json"
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

            # add to chunk_output
            chunk_entries.append(self._make_output_dict(chunk))

        # write chunk_output.json
        output_path = chunks_dir / "chunk_output.json"
        output_data = {
            "document_id": str(chunks[0].document_id),
            "total_chunks": len(chunks),
            "processing_timestamp": datetime.now(timezone.utc).isoformat(),
            "chunks": chunk_entries
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        if self.verbose:
            print(f"[INFO] Saved chunk_output.json with {len(chunks)} entries at {output_path}")

  

    def _make_metadata_dict(self, chunk: ChunkContent) -> Dict[str, Any]:
        #Generate schema-compliant chunk metadata dict
        return {
            "chunk_id": str(chunk.chunk_id),
            "document_id": str(chunk.document_id),
            "chunk_index": chunk.chunk_index,
            "total_chunks": chunk.total_chunks,
            "section_hierarchy": chunk.section_path,
            "token_count": chunk.token_count,
            "character_count": len(chunk.content),
            "chunk_type": chunk.chunk_type,
            "contains_equations": "$" in chunk.content or "$$" in chunk.content,
            "contains_tables": bool(re.search(r'^\|.*\|', chunk.content, flags=re.MULTILINE)),
            "overlap_info": {
                "has_previous_overlap": chunk.has_overlap_previous,
                "has_next_overlap": chunk.has_overlap_next,
                "overlap_token_count": int(self.chunk_size * self.chunk_overlap)
            }
        }

    def _make_output_dict(self, chunk: ChunkContent) -> Dict[str, Any]:
        #Generate schema-compliant chunk_output entry
        return {
            "chunk_id": str(chunk.chunk_id),
            "document_id": str(chunk.document_id),
            "chunk_index": chunk.chunk_index,
            "total_chunks": chunk.total_chunks,
            "content": chunk.content,
            "token_count": chunk.token_count,
            "chunk_type": chunk.chunk_type,
            "section_hierarchy": chunk.section_path,
            "has_overlap_previous": chunk.has_overlap_previous,
            "has_overlap_next": chunk.has_overlap_next,
            "content_features": chunk.content_features
        }

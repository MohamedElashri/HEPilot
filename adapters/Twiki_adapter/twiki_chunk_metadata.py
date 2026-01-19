import json
import re
import uuid 
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer


class TwikiChunker:
    # Chunking engine for Twiki Markdown documents. 

    def __init__(self,
                chunk_size: int = 512,
                chunk_overlap: float = 0.1,
                model_name: str = "BAAI/bge-large-en-v1.5",
                cache_dir: str = ".model_cache",
                verbose: bool = False):

        """
        Initialize chunker

        Args: 
            chunks_size: Target chunk size in tokens
            chunk_overlap: Fractional overlap between consecutive chunks
            verbose: Enable verbose logging
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.verbose = verbose
        self.model_name = model_name
        self.cache_dir = cache_dir

        try:
            if self.verbose:
                print(f"[INFO] Loading tokenizer from {model_name}")
            self.model = SentenceTransformer(model_name, cache_folder=cache_dir)
            self.tokenizer = self.model.tokenizer
            self.max_seq_length = self.model.get_max_seq_length()
            if self.verbose:
                print("[WARNING] Tokenizer not found; fallback to character counts only.")
        except Exception as e:
            print(f"[ERROR] Could not load tokenizer: {e}")
            self.model = None
            self.tokenizer = None
            self.max_seq_length = chunk_size

    def _count_tokens(self, text: str) -> int:
        # Return token count using SentenceTransformers tokenizer.

        if self.tokenizer:
            try:
                tokens = self.tokenizer.encode(text, add_special_tokens=False)
                return len(tokens)
            except Exception:
                pass
        return len(text.split())

    def _extract_section_heirarchy(self, text: str) -> List[str]:
        # Extract Markdown headers as section hierarchy.
        headers = re.findall(r"^(#+)\s*(.+)", text, flags=re.MULTILINE) 
        return [h[1].strip() for h in headers[:3]] # 3 levels deep

    def _contains_equations(self, text: str) -> bool:
        # Detect inline or block Latex Math.
        return bool(re.search(r"(\$[^$]+\$|\$\$[^$]+\$\$)", text))

    def _contains_tables(self, text: str) -> bool:
           # Detect Markdown tables (| col | col |).
        return bool(re.search(r"^\|.*\|", text, flags=re.MULTILINE))
    
    def chunk_document(self, document_id: str, markdown_path: Path, output_dir: Path) -> List[Dict[str, Any]]:
        """
        Split Markdown document into chunks and generate metadata. 

        Args:
            document_id: UUID of parent document.
            markdown_path: Path to source Markdown file.
            output_dir: Directory to store chunk metadata and content.

        Returns:
            List of metadata dictionaries for all chunks.
        
        """

        with open(markdown_path, "r", encoding="utf-8") as f:
            full_text = f.read()
        
        # splitting texts into paragraphs
        paragraphs = re.split(r"\n\s*\n", full_text.strip())
        tokens_per_para = [self._count_tokens(p) for p in paragraphs]

        # chunk assembly
        chunks = []
        current_chunk, current_tokens = [], 0
        for para, tcount in zip(paragraphs, tokens_per_para):
            if current_tokens + tcount > self.chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                # Start overlap
                overlap_tokens = int(self.chunk_size * self.chunk_overlap)
                overlap_text = current_chunk[-1] if overlap_tokens > 0 else ""
                current_chunk = [overlap_text, para] if overlap_text else [para]
                current_tokens = tcount + self._count_tokens(overlap_text)
            else:
                current_chunk.append(para)
                current_tokens += tcount

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        total_chunks = len(chunks)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate metadata for each chunk
        metadata_list = []
        for idx, chunk_text in enumerate(chunks):
            chunk_id = str(uuid.uuid4())
            token_count = self._count_tokens(chunk_text)
            char_count = len(chunk_text)
            chunk_type = "text"
            contains_eq = self._contains_equations(chunk_text)
            contains_tbl = self._contains_tables(chunk_text)
            if contains_eq and contains_tbl:
                chunk_type = "mixed"
            elif contains_eq:
                chunk_type = "equation"
            elif contains_tbl:
                chunk_type = "table"

            overlap_info = {
                "has_previous_overlap": idx > 0,
                "has_next_overlap": idx < total_chunks - 1,
                "overlap_token_count": int(self.chunk_size * self.chunk_overlap)
            }

            metadata = {
                "chunk_id": chunk_id,
                "document_id": document_id,
                "chunk_index": idx,
                "total_chunks": total_chunks,
                "section_hierarchy": self._extract_section_heirarchy(chunk_text),
                "token_count": token_count,
                "character_count": char_count,
                "chunk_type": chunk_type,
                "contains_equations": contains_eq,
                "contains_tables": contains_tbl,
                "overlap_info": overlap_info
            }

            metadata_list.append(metadata)

            # Optionally save chunk text
            ext = markdown_path.suffix or ".md"
            chunk_file = output_dir / f"chunk_{idx:04d}{ext}"
            meta_file = output_dir / f"chunk_{idx:04d}_metadata.json"

            with open(chunk_file, "w", encoding="utf-8") as cf:
                cf.write(chunk_text)
            with open(meta_file, "w", encoding="utf-8") as mf:
                json.dump(metadata,  mf, indent=2)
                
            if self.verbose:
                print(f"[INFO] Created chunk {idx+1}/{total_chunks}: {chunk_file.name}")

        return metadata_list
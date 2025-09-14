#!/usr/bin/env python3
"""
Progress Tracker Module for HEPilot ArXiv Adapter
Tracks download and processing status for each paper to avoid redundant work.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, Set
from dataclasses import dataclass, asdict


@dataclass
class PaperProgress:
    """Progress information for a single paper."""
    arxiv_id: str
    document_id: str
    discovered_timestamp: str
    download_status: str = "pending"  # pending, completed, failed
    download_timestamp: Optional[str] = None
    download_path: Optional[str] = None
    processing_status: str = "pending"  # pending, completed, failed
    processing_timestamp: Optional[str] = None
    chunk_count: int = 0
    last_updated: Optional[str] = None
    retry_count: int = 0
    error_message: Optional[str] = None


class ProgressTracker:
    """Manages progress tracking for paper download and processing."""
    
    def __init__(self, output_dir: Path):
        """Initialize the progress tracker.
        
        Args:
            output_dir: Output directory path where progress file will be stored
        """
        self.output_dir = output_dir
        self.progress_file = output_dir / "progress.json"
        self.logger = logging.getLogger(__name__)
        self._progress_data: Dict[str, PaperProgress] = {}
        self._load_progress()
    
    def _load_progress(self) -> None:
        """Load progress data from file."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert dictionaries back to PaperProgress objects
                for doc_id, progress_dict in data.items():
                    self._progress_data[doc_id] = PaperProgress(**progress_dict)
                
                self.logger.info(f"Loaded progress for {len(self._progress_data)} papers")
            except (json.JSONDecodeError, TypeError, KeyError) as e:
                self.logger.warning(f"Could not load progress file: {e}. Starting with empty progress.")
                self._progress_data = {}
        else:
            self.logger.info("No existing progress file found. Starting with empty progress.")
            self._progress_data = {}
    
    def _save_progress(self) -> None:
        """Save progress data to file."""
        try:
            # Ensure output directory exists
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Convert PaperProgress objects to dictionaries
            data = {doc_id: asdict(progress) for doc_id, progress in self._progress_data.items()}
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            self.logger.error(f"Failed to save progress: {e}")
    
    def register_discovered_papers(self, discovered_docs: list) -> None:
        """Register discovered papers in the progress tracker.
        
        Args:
            discovered_docs: List of discovered document dictionaries
        """
        current_time = datetime.now(timezone.utc).isoformat()
        new_papers = 0
        
        for doc_dict in discovered_docs:
            doc_id = doc_dict["document_id"]
            arxiv_id = doc_dict.get("arxiv_id", doc_id)
            
            if doc_id not in self._progress_data:
                self._progress_data[doc_id] = PaperProgress(
                    arxiv_id=arxiv_id,
                    document_id=doc_id,
                    discovered_timestamp=current_time,
                    last_updated=current_time
                )
                new_papers += 1
        
        if new_papers > 0:
            self.logger.info(f"Registered {new_papers} new papers for tracking")
            self._save_progress()
    
    def get_papers_needing_download(self, discovered_docs: list) -> list:
        """Get papers that need to be downloaded.
        
        Args:
            discovered_docs: List of all discovered document dictionaries
            
        Returns:
            List of document dictionaries that need downloading
        """
        papers_to_download = []
        
        for doc_dict in discovered_docs:
            doc_id = doc_dict["document_id"]
            progress = self._progress_data.get(doc_id)
            
            if not progress or progress.download_status != "completed":
                # Check if file exists on disk as additional validation
                if progress and progress.download_path:
                    file_path = Path(progress.download_path)
                    if file_path.exists() and file_path.stat().st_size > 1024:
                        # File exists and is reasonable size, mark as completed
                        self.mark_download_completed(doc_id, str(file_path))
                        continue
                
                papers_to_download.append(doc_dict)
        
        self.logger.info(f"Found {len(papers_to_download)} papers needing download out of {len(discovered_docs)} total")
        return papers_to_download
    
    def get_papers_needing_processing(self, acquired_docs: list) -> list:
        """Get papers that need to be processed.
        
        Args:
            acquired_docs: List of acquired document dictionaries
            
        Returns:
            List of document dictionaries that need processing
        """
        papers_to_process = []
        
        for doc_dict in acquired_docs:
            doc_id = doc_dict["document_id"]
            progress = self._progress_data.get(doc_id)
            
            if not progress or progress.processing_status != "completed":
                papers_to_process.append(doc_dict)
        
        self.logger.info(f"Found {len(papers_to_process)} papers needing processing out of {len(acquired_docs)} total")
        return papers_to_process
    
    def mark_download_completed(self, document_id: str, local_path: str) -> None:
        """Mark a paper's download as completed.
        
        Args:
            document_id: Document ID
            local_path: Path to downloaded file
        """
        current_time = datetime.now(timezone.utc).isoformat()
        
        if document_id in self._progress_data:
            progress = self._progress_data[document_id]
            progress.download_status = "completed"
            progress.download_timestamp = current_time
            progress.download_path = local_path
            progress.last_updated = current_time
            progress.error_message = None
        else:
            self.logger.warning(f"Marking download completed for untracked paper: {document_id}")
        
        self._save_progress()
    
    def mark_download_failed(self, document_id: str, error_message: str) -> None:
        """Mark a paper's download as failed.
        
        Args:
            document_id: Document ID
            error_message: Error description
        """
        current_time = datetime.now(timezone.utc).isoformat()
        
        if document_id in self._progress_data:
            progress = self._progress_data[document_id]
            progress.download_status = "failed"
            progress.last_updated = current_time
            progress.retry_count += 1
            progress.error_message = error_message
        
        self._save_progress()
    
    def mark_processing_completed(self, document_id: str, chunk_count: int) -> None:
        """Mark a paper's processing as completed.
        
        Args:
            document_id: Document ID
            chunk_count: Number of chunks created
        """
        current_time = datetime.now(timezone.utc).isoformat()
        
        if document_id in self._progress_data:
            progress = self._progress_data[document_id]
            progress.processing_status = "completed"
            progress.processing_timestamp = current_time
            progress.chunk_count = chunk_count
            progress.last_updated = current_time
            progress.error_message = None
        else:
            self.logger.warning(f"Marking processing completed for untracked paper: {document_id}")
        
        self._save_progress()
    
    def mark_processing_failed(self, document_id: str, error_message: str) -> None:
        """Mark a paper's processing as failed.
        
        Args:
            document_id: Document ID
            error_message: Error description
        """
        current_time = datetime.now(timezone.utc).isoformat()
        
        if document_id in self._progress_data:
            progress = self._progress_data[document_id]
            progress.processing_status = "failed"
            progress.last_updated = current_time
            progress.retry_count += 1
            progress.error_message = error_message
        
        self._save_progress()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of current progress.
        
        Returns:
            Dictionary with progress statistics
        """
        total_papers = len(self._progress_data)
        
        download_completed = sum(1 for p in self._progress_data.values() if p.download_status == "completed")
        download_failed = sum(1 for p in self._progress_data.values() if p.download_status == "failed")
        download_pending = total_papers - download_completed - download_failed
        
        processing_completed = sum(1 for p in self._progress_data.values() if p.processing_status == "completed")
        processing_failed = sum(1 for p in self._progress_data.values() if p.processing_status == "failed")
        processing_pending = total_papers - processing_completed - processing_failed
        
        total_chunks = sum(p.chunk_count for p in self._progress_data.values())
        
        return {
            "total_papers": total_papers,
            "download": {
                "completed": download_completed,
                "failed": download_failed,
                "pending": download_pending
            },
            "processing": {
                "completed": processing_completed,
                "failed": processing_failed,
                "pending": processing_pending
            },
            "total_chunks_created": total_chunks,
            "fully_completed": sum(1 for p in self._progress_data.values() 
                                 if p.download_status == "completed" and p.processing_status == "completed")
        }
    
    def get_failed_papers(self) -> Dict[str, list]:
        """Get papers that failed download or processing.
        
        Returns:
            Dictionary with failed download and processing paper lists
        """
        download_failed = [p for p in self._progress_data.values() if p.download_status == "failed"]
        processing_failed = [p for p in self._progress_data.values() if p.processing_status == "failed"]
        
        return {
            "download_failed": [{"document_id": p.document_id, "arxiv_id": p.arxiv_id, "error": p.error_message} for p in download_failed],
            "processing_failed": [{"document_id": p.document_id, "arxiv_id": p.arxiv_id, "error": p.error_message} for p in processing_failed]
        }
    
    def reset_failed_papers(self) -> None:
        """Reset failed papers to pending status for retry."""
        reset_count = 0
        current_time = datetime.now(timezone.utc).isoformat()
        
        for progress in self._progress_data.values():
            if progress.download_status == "failed":
                progress.download_status = "pending"
                progress.last_updated = current_time
                progress.error_message = None
                reset_count += 1
            
            if progress.processing_status == "failed":
                progress.processing_status = "pending"
                progress.last_updated = current_time
                progress.error_message = None
                reset_count += 1
        
        if reset_count > 0:
            self.logger.info(f"Reset {reset_count} failed papers to pending status")
            self._save_progress()

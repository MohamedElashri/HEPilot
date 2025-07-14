"""
State management for the HEPilot arXiv adapter.

This module provides a simple state manager that uses a JSON file to track the
processing state of each document. This helps to avoid reprocessing documents
and allows the adapter to resume from a previous run.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class StateManager:
    """
    Manages the processing state of documents in a JSON file.
    """
    def __init__(self, state_file: Path):
        """
        Initialize the state manager.

        Args:
            state_file: The path to the JSON file for storing state.
        """
        self.state_file = state_file
        self.state: Dict[str, Any] = {}
        self._load_state()

    def _load_state(self):
        """
        Load the state from the JSON file.
        """
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                logger.warning(f"Could not load state file {self.state_file}: {e}")
                self.state = {}
        else:
            self.state = {}

    def _save_state(self):
        """
        Save the current state to the JSON file.
        """
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2)
        except IOError as e:
            logger.error(f"Could not write to state file {self.state_file}: {e}")

    def get_document_metadata(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get all metadata for a document.

        Args:
            document_id: The ID of the document.

        Returns:
            A dictionary of metadata, or None if not found.
        """
        return self.state.get(document_id)

    def set_document_state(self, document_id: str, state: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Set the processing state of a document.

        Args:
            document_id: The ID of the document.
            state: The new processing state.
            metadata: Additional metadata to store with the state.
        """
        if document_id not in self.state:
            self.state[document_id] = {}
        
        self.state[document_id]["status"] = state
        if metadata:
            self.state[document_id].update(metadata)
        
        self._save_state()

    def is_processed(self, document_id: str, file_hash: Optional[str] = None) -> bool:
        """
        Check if a document has been successfully processed and has not changed.

        Args:
            document_id: The ID of the document.
            file_hash: The current hash of the document file.

        Returns:
            True if the document has been processed and the hash matches, False otherwise.
        """
        doc_state = self.get_document_metadata(document_id)
        if not doc_state or doc_state.get("status") != "processed":
            return False
        
        # If a file hash is provided, check if it matches the stored hash
        if file_hash and doc_state.get("file_hash_sha256") != file_hash:
            logger.info(f"Hash mismatch for {document_id}. Reprocessing required.")
            return False
            
        return True

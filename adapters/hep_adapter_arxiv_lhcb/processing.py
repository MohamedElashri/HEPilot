#!/usr/bin/env python3
"""
Processing Module for HEPilot ArXiv Adapter
Handles PDF to Markdown conversion using docling with equation and table preservation.
"""

import logging
import re
import time
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, List, Optional

from docling.document_converter import DocumentConverter

from models import AcquiredDocument

try:
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
    DOCLING_ADVANCED_IMPORTS = True
except ImportError:
    # Fallback for different docling versions
    DOCLING_ADVANCED_IMPORTS = False


class DocumentProcessor:
    """Processing pipeline using docling for PDF conversion."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the document processor.
        
        Args:
            config: Adapter configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configure docling converter with correct API
        try:
            # Try the simpler configuration first
            self.converter = DocumentConverter()
        except Exception as e:
            self.logger.warning(f"Failed to create DocumentConverter with default options: {e}")
            # Fallback to basic configuration
            self.converter = DocumentConverter()
    
    def process_document(self, acquired_doc: AcquiredDocument) -> Tuple[str, Dict[str, Any]]:
        """Process a document using docling.
        
        Args:
            acquired_doc: AcquiredDocument object with file path and metadata
            
        Returns:
            Tuple of (markdown_content, processing_metadata)
        """
        start_time = time.time()
        warnings = []
        
        try:
            # Convert document using docling
            self.logger.info(f"Converting document with docling: {acquired_doc.local_path}")
            result = self.converter.convert(acquired_doc.local_path)
            
            # Extract markdown content - handle different API versions
            try:
                if hasattr(result.document, 'export_to_markdown'):
                    markdown_content = result.document.export_to_markdown()
                elif hasattr(result, 'document') and hasattr(result.document, 'markdown'):
                    markdown_content = result.document.markdown
                elif hasattr(result, 'markdown'):
                    markdown_content = result.markdown
                else:
                    # Fallback - try to extract text content
                    markdown_content = str(result.document) if hasattr(result, 'document') else str(result)
                    warnings.append("Used fallback method for markdown extraction")
            except Exception as e:
                self.logger.warning(f"Markdown extraction failed, using fallback: {e}")
                markdown_content = f"# Document Content\n\nFailed to extract content from {acquired_doc.local_path}"
                warnings.append(f"Markdown extraction failed: {e}")
            
            # Post-process markdown
            if self.config.get("processing_config", {}).get("preserve_equations"):
                markdown_content = self._preserve_equations(markdown_content)

            if self.config.get("x_extension", {}).get("preserve_inline_equations"):
                markdown_content = self._preserve_inline_equations(markdown_content)
            
            if self.config.get("processing_config", {}).get("preserve_tables"):
                markdown_content = self._enhance_tables(markdown_content)
            
            # Extract references if available
            references = self._extract_references(result)
            if references:
                markdown_content += "\n\n<!--references-->\n"
            
            processing_duration = time.time() - start_time
            
            processing_metadata = {
                "processor_used": "docling",
                "processing_timestamp": datetime.now(timezone.utc).isoformat(),
                "processing_duration": processing_duration,
                "conversion_warnings": warnings
            }
            
            return markdown_content, processing_metadata
            
        except Exception as e:
            self.logger.error(f"Processing failed for {acquired_doc.document_id}: {e}")
            # Create fallback content
            fallback_content = f"# Processing Failed\n\nFailed to process document {acquired_doc.document_id}\nError: {str(e)}"
            processing_metadata = {
                "processor_used": "docling",
                "processing_timestamp": datetime.now(timezone.utc).isoformat(),
                "processing_duration": time.time() - start_time,
                "conversion_warnings": [f"Processing failed: {str(e)}"]
            }
            return fallback_content, processing_metadata
    
    def _preserve_equations(self, content: str) -> str:
        """Wraps block equations in markdown code blocks.
        
        Args:
            content: Markdown content to process
            
        Returns:
            Content with preserved equations
        """
        # Process block equations $$...$$
        content = re.sub(r'(\$\$.*?\$\$)', r'\n```\n\1\n```\n', content, flags=re.DOTALL)
        # Process block equations \[...\]
        content = re.sub(r'(\\[.*?\\])', r'\n```\n\1\n```\n', content, flags=re.DOTALL)
        return content

    def _preserve_inline_equations(self, content: str) -> str:
        """Wraps inline equations in markdown backticks.
        
        Args:
            content: Markdown content to process
            
        Returns:
            Content with preserved inline equations
        """
        # Process inline equations that are not block equations
        return re.sub(r'(?<!\$)\$([^\$]+?)\$(?!\$)', r'`$\1$`', content)

    def _enhance_tables(self, content: str) -> str:
        """Enhance table formatting in markdown.
        
        Args:
            content: Markdown content to process
            
        Returns:
            Content with enhanced table formatting
        """
        # Basic table enhancement - can be extended
        return content
    
    def _extract_references(self, result) -> Optional[List[Dict[str, Any]]]:
        """Extract and format references from the docling result.
        
        Args:
            result: Docling conversion result
            
        Returns:
            List of reference dictionaries or None if no references found
        """
        if not hasattr(result, 'document') or not hasattr(result.document, 'references'):
            return None

        extracted_references = []
        # Assuming result.document.references is a list of reference objects
        for i, ref_obj in enumerate(result.document.references):
            # This is a speculative implementation based on a potential docling output.
            # We assume the reference object can be converted to a string.
            ref_text = str(ref_obj)
            
            extracted_references.append({
                "id": f"ref_{i+1}",
                "text": ref_text
            })

        return extracted_references

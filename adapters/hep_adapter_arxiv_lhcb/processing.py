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
    from docling.datamodel.settings import settings
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
        
        # Configure docling converter with optimized settings
        self.converter = self._create_optimized_converter()
    
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
            
            # Apply content filtering (exclude authors and acknowledgments by default)
            exclude_authors = self.config.get("x_extension", {}).get("exclude_authors", True)
            exclude_acknowledgments = self.config.get("x_extension", {}).get("exclude_acknowledgments", True)
            
            if exclude_authors or exclude_acknowledgments:
                markdown_content = self._filter_unwanted_sections(markdown_content)
                if exclude_authors:
                    markdown_content = self._remove_author_metadata_blocks(markdown_content)
                    warnings.append("Filtered out author sections and metadata")
                if exclude_acknowledgments:
                    warnings.append("Filtered out acknowledgment sections")
            
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
    
    def _create_optimized_converter(self) -> DocumentConverter:
        """Create an optimized docling converter with content filtering.
        
        Returns:
            Configured DocumentConverter instance
        """
        try:
            if DOCLING_ADVANCED_IMPORTS:
                # Configure pipeline options for content filtering
                pipeline_options = PdfPipelineOptions()
                
                # Configure to exclude unwanted sections
                pipeline_options.do_ocr = False  # Disable OCR for faster processing
                pipeline_options.images_scale = 1.0  # Keep original image scale
                
                converter = DocumentConverter(
                    format_options={
                        InputFormat.PDF: pipeline_options
                    }
                )
                
                self.logger.info("Created optimized docling converter with advanced options")
                return converter
            else:
                # Fallback for basic docling versions
                converter = DocumentConverter()
                self.logger.info("Created basic docling converter (advanced options not available)")
                return converter
                
        except Exception as e:
            self.logger.warning(f"Failed to create optimized converter: {e}")
            # Final fallback
            return DocumentConverter()
    
    def _filter_unwanted_sections(self, content: str) -> str:
        """Filter out unwanted sections from processed content.
        
        Args:
            content: Markdown content to filter
            
        Returns:
            Filtered content with unwanted sections removed
        """
        lines = content.split('\n')
        filtered_lines = []
        skip_section = False
        section_patterns = [
            # Author section patterns
            r'^#+ authors?\s*$',
            r'^#+ author information\s*$',
            r'^#+ correspondence\s*$',
            r'^#+ affiliations?\s*$',
            # Acknowledgment section patterns
            r'^#+ acknowledgments?\s*$',
            r'^#+ acknowledgements?\s*$',
            r'^#+ thanks?\s*$',
            r'^#+ funding\s*$',
            r'^#+ conflicts? of interest\s*$',
            r'^#+ data availability\s*$',
        ]
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if this line starts an unwanted section
            section_start = False
            for pattern in section_patterns:
                if re.match(pattern, line_lower, re.IGNORECASE):
                    skip_section = True
                    section_start = True
                    self.logger.debug(f"Filtering out section: {line.strip()}")
                    break
            
            # Check if we're starting a new section (end of unwanted section)
            if skip_section and not section_start and line.strip().startswith('#'):
                # Check if this is a section we want to keep
                keep_section = True
                for pattern in section_patterns:
                    if re.match(pattern, line_lower, re.IGNORECASE):
                        keep_section = False
                        break
                
                if keep_section:
                    skip_section = False
                    filtered_lines.append(line)
            elif not skip_section:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _remove_author_metadata_blocks(self, content: str) -> str:
        """Remove author metadata blocks from content.
        
        Args:
            content: Markdown content to process
            
        Returns:
            Content with author metadata blocks removed
        """
        # Remove author email patterns
        content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', content)
        
        # Remove ORCID patterns
        content = re.sub(r'ORCID:?\s*\d{4}-\d{4}-\d{4}-\d{4}', '', content)
        
        # Remove affiliation markers like [1], [2], etc.
        content = re.sub(r'\[[0-9]+\]', '', content)
        
        # Remove common affiliation indicators
        content = re.sub(r'\b(Department of|Institute of|University of|College of)\b.*?\n', '', content, flags=re.MULTILINE)
        
        return content

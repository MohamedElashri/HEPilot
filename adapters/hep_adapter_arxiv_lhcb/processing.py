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

from docling.document_converter import DocumentConverter, PdfFormatOption

from models import AcquiredDocument

try:
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.datamodel.base_models import InputFormat
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
            
            # Apply content filtering (exclude authors, acknowledgments, and references by default)
            exclude_authors = self.config.get("x_extension", {}).get("exclude_authors", True)
            exclude_acknowledgments = self.config.get("x_extension", {}).get("exclude_acknowledgments", True)
            exclude_references = self.config.get("x_extension", {}).get("exclude_references", True)
            
            if exclude_authors or exclude_acknowledgments or exclude_references:
                markdown_content = self._filter_unwanted_sections(markdown_content, exclude_references)
                if exclude_authors:
                    markdown_content = self._remove_author_metadata_blocks(markdown_content)
                    warnings.append("Filtered out author sections and metadata")
                if exclude_acknowledgments:
                    warnings.append("Filtered out acknowledgment sections")
                if exclude_references:
                    warnings.append("Filtered out reference sections")
            
            # Post-process markdown
            if self.config.get("processing_config", {}).get("preserve_equations"):
                markdown_content = self._preserve_equations(markdown_content)

            if self.config.get("x_extension", {}).get("preserve_inline_equations"):
                markdown_content = self._preserve_inline_equations(markdown_content)
            
            if self.config.get("processing_config", {}).get("preserve_tables"):
                markdown_content = self._enhance_tables(markdown_content)
            
            # Extract references if available and not excluded
            references = None
            if not exclude_references:
                references = self._extract_references(result)
                if references:
                    markdown_content += "\n\n<!--references-->\n"
                    for ref in references:
                        markdown_content += f"\n{ref['text']}\n"
            
            # Extract enriched formula data if available
            enriched_formulas = self._extract_enriched_formulas(result)
            if enriched_formulas:
                processing_metadata["enriched_formulas_count"] = len(enriched_formulas)
                processing_metadata["enriched_formulas"] = enriched_formulas[:10]  # Store first 10 for metadata
                self.logger.info(f"Extracted {len(enriched_formulas)} enriched formulas")
            
            processing_duration = time.time() - start_time
            
            processing_metadata = {
                "processor_used": "docling",
                "processing_timestamp": datetime.now(timezone.utc).isoformat(),
                "processing_duration": processing_duration,
                "conversion_warnings": warnings,
                "formula_enrichment_enabled": self.config.get("processing_config", {}).get("enable_formula_enrichment", False)
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
        """Comprehensively preserves LaTeX mathematical environments and equations.
        
        Args:
            content: Markdown content to process
            
        Returns:
            Content with enhanced equation preservation
        """
        # Define comprehensive LaTeX math environments
        math_environments = [
            r'equation\*?', r'align\*?', r'gather\*?', r'multline\*?', 
            r'split', r'alignat\*?', r'flalign\*?', r'eqnarray\*?',
            r'array', r'matrix', r'pmatrix', r'bmatrix', r'vmatrix', r'Vmatrix'
        ]
        
        # Process LaTeX math environments
        for env in math_environments:
            pattern = rf'(\\begin\{{{env}\}}.*?\\end\{{{env}\}})'
            content = re.sub(pattern, r'\n```latex\n\1\n```\n', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Process block equations $$...$$
        content = re.sub(r'(\$\$(?:(?!\$\$).)*\$\$)', r'\n```latex\n\1\n```\n', content, flags=re.DOTALL)
        
        # Process block equations \[...\]
        content = re.sub(r'(\\\[(?:(?!\\\]).)*\\\])', r'\n```latex\n\1\n```\n', content, flags=re.DOTALL)
        
        # Process numbered equations with labels
        content = re.sub(r'(\\begin\{equation\}.*?\\label\{[^}]+\}.*?\\end\{equation\})', 
                        r'\n```latex\n\1\n```\n', content, flags=re.DOTALL | re.IGNORECASE)
        
        return content

    def _preserve_inline_equations(self, content: str) -> str:
        """Comprehensively preserves inline mathematical expressions and LaTeX commands.
        
        Args:
            content: Markdown content to process
            
        Returns:
            Content with enhanced inline equation preservation
        """
        # Process inline equations that are not block equations
        content = re.sub(r'(?<!\$)\$([^\$\n]+?)\$(?!\$)', r'`$\1$`', content)
        
        # Process inline LaTeX \(...\)
        content = re.sub(r'\\\(([^)]+?)\\\)', r'`$\1$`', content)
        
        # Preserve common LaTeX mathematical commands and symbols
        latex_commands = [
            r'\\alpha', r'\\beta', r'\\gamma', r'\\delta', r'\\epsilon', r'\\zeta',
            r'\\eta', r'\\theta', r'\\iota', r'\\kappa', r'\\lambda', r'\\mu',
            r'\\nu', r'\\xi', r'\\pi', r'\\rho', r'\\sigma', r'\\tau',
            r'\\upsilon', r'\\phi', r'\\chi', r'\\psi', r'\\omega',
            r'\\Gamma', r'\\Delta', r'\\Theta', r'\\Lambda', r'\\Xi', r'\\Pi',
            r'\\Sigma', r'\\Upsilon', r'\\Phi', r'\\Chi', r'\\Psi', r'\\Omega',
            r'\\infty', r'\\partial', r'\\nabla', r'\\sum', r'\\prod', r'\\int',
            r'\\sqrt', r'\\frac', r'\\cdot', r'\\times', r'\\div', r'\\pm', r'\\mp',
            r'\\leq', r'\\geq', r'\\neq', r'\\approx', r'\\equiv', r'\\propto',
            r'\\in', r'\\notin', r'\\subset', r'\\supset', r'\\subseteq', r'\\supseteq',
            r'\\cup', r'\\cap', r'\\emptyset', r'\\forall', r'\\exists'
        ]
        
        # Preserve LaTeX commands when they appear inline
        for cmd in latex_commands:
            content = re.sub(f'({cmd})', r'`\1`', content)
        
        # Preserve LaTeX formatting commands
        formatting_commands = [r'\\textbf', r'\\textit', r'\\mathbf', r'\\mathit', r'\\mathrm']
        for cmd in formatting_commands:
            content = re.sub(f'({cmd}\{{[^}}]+\}})', r'`\1`', content)
        
        return content

    def _enhance_tables(self, content: str) -> str:
        """Enhance table formatting with special handling for mathematical content.
        
        Args:
            content: Markdown content to process
            
        Returns:
            Content with enhanced table formatting
        """
        # Preserve LaTeX table environments
        table_environments = [r'tabular', r'array', r'matrix', r'pmatrix', r'bmatrix']
        
        for env in table_environments:
            pattern = rf'(\\begin\{{{env}\}}.*?\\end\{{{env}\}})'
            content = re.sub(pattern, r'\n```latex\n\1\n```\n', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Enhanced markdown table formatting
        lines = content.split('\n')
        in_table = False
        enhanced_lines = []
        
        for line in lines:
            # Detect markdown table lines
            if '|' in line and line.count('|') >= 2:
                if not in_table:
                    # Start of table - add spacing
                    enhanced_lines.append('')
                    in_table = True
                
                # Clean up table cell content
                cells = line.split('|')
                cleaned_cells = []
                for cell in cells:
                    cell = cell.strip()
                    # Preserve mathematical expressions in table cells
                    if '$' in cell or '\\' in cell:
                        cell = self._preserve_table_math(cell)
                    cleaned_cells.append(cell)
                
                enhanced_lines.append('|'.join(cleaned_cells))
            else:
                if in_table:
                    # End of table - add spacing
                    enhanced_lines.append('')
                    in_table = False
                enhanced_lines.append(line)
        
        return '\n'.join(enhanced_lines)
    
    def _preserve_table_math(self, cell_content: str) -> str:
        """Preserve mathematical expressions within table cells.
        
        Args:
            cell_content: Content of a table cell
            
        Returns:
            Cell content with preserved mathematical expressions
        """
        # Preserve inline math in table cells
        cell_content = re.sub(r'(?<!\$)\$([^\$\n]+?)\$(?!\$)', r'`$\1$`', cell_content)
        
        # Preserve LaTeX commands in table cells
        cell_content = re.sub(r'(\\[a-zA-Z]+(?:\{[^}]*\})*)', r'`\1`', cell_content)
        
        return cell_content
    
    def _extract_enriched_formulas(self, result) -> List[Dict[str, Any]]:
        """Extract enriched formula data from docling result.
        
        Args:
            result: Docling conversion result with potential formula enrichment
            
        Returns:
            List of enriched formula dictionaries
        """
        enriched_formulas = []
        
        try:
            if hasattr(result, 'document') and hasattr(result.document, 'texts'):
                # Iterate through document text items to find formulas
                for item in result.document.texts:
                    if hasattr(item, 'label') and item.label == 'FORMULA':
                        formula_data = {
                            "text": str(item.text) if hasattr(item, 'text') else "",
                            "label": item.label
                        }
                        
                        # Extract LaTeX representation if available from enrichment
                        if hasattr(item, 'latex') and item.latex:
                            formula_data["latex"] = item.latex
                        elif hasattr(item, 'enrichment') and item.enrichment:
                            if hasattr(item.enrichment, 'latex'):
                                formula_data["latex"] = item.enrichment.latex
                            elif hasattr(item.enrichment, 'formula'):
                                formula_data["latex"] = item.enrichment.formula
                        
                        # Extract bounding box if available
                        if hasattr(item, 'prov') and item.prov:
                            for prov in item.prov:
                                if hasattr(prov, 'bbox'):
                                    formula_data["bbox"] = {
                                        "l": prov.bbox.l,
                                        "t": prov.bbox.t, 
                                        "r": prov.bbox.r,
                                        "b": prov.bbox.b
                                    }
                                    break
                        
                        enriched_formulas.append(formula_data)
                        
        except Exception as e:
            self.logger.warning(f"Failed to extract enriched formulas: {e}")
        
        return enriched_formulas
    
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
        """Create an optimized docling converter with formula enrichment.
        
        Returns:
            Configured DocumentConverter instance
        """
        try:
            if DOCLING_ADVANCED_IMPORTS:
                # Configure pipeline options for enhanced LaTeX processing
                pipeline_options = PdfPipelineOptions()
                
                # Enhanced configuration for mathematical content
                pipeline_options.do_ocr = False  # Disable OCR for faster processing
                pipeline_options.images_scale = 1.0  # Keep original image scale
                pipeline_options.generate_page_images = False  # Skip page images for performance
                pipeline_options.generate_picture_images = True  # Keep mathematical figures
                
                # Enable docling enrichment features
                enable_formula_enrichment = self.config.get("processing_config", {}).get("enable_formula_enrichment", True)
                if enable_formula_enrichment:
                    pipeline_options.do_formula_enrichment = True
                    self.logger.info("Enabling formula understanding enrichment - CodeFormula model will be downloaded if needed")
                
                # Use correct API - PdfFormatOption wrapper
                pdf_format_option = PdfFormatOption(pipeline_options=pipeline_options)
                
                converter = DocumentConverter(
                    format_options={
                        InputFormat.PDF: pdf_format_option
                    }
                )
                
                self.logger.info("Created optimized docling converter with formula enrichment enabled")
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
    
    def _filter_unwanted_sections(self, content: str, exclude_references: bool = True) -> str:
        """Filter out unwanted sections from processed content.
        
        Args:
            content: Markdown content to filter
            exclude_references: Whether to exclude reference sections
            
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
            r'^#+ lhcb collaboration\s*$',
            # Acknowledgment section patterns
            r'^#+ acknowledgments?\s*$',
            r'^#+ acknowledgements?\s*$',
            r'^#+ thanks?\s*$',
            r'^#+ funding\s*$',
            r'^#+ conflicts? of interest\s*$',
            r'^#+ data availability\s*$',
        ]
        
        # Add reference section patterns if excluding references
        if exclude_references:
            reference_patterns = [
                r'^#+ references?\s*$',
                r'^#+ bibliography\s*$',
                r'^#+ citations?\s*$',
                r'^#+ works? cited\s*$',
                r'^#+ literature cited\s*$',
            ]
            section_patterns.extend(reference_patterns)
        
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

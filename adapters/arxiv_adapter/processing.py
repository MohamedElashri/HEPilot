"""
Processing module for converting PDF to CommonMark markdown using docling.

Uses docling's ML models for advanced PDF processing including LaTeX formula
extraction, table handling, and section detection with comprehensive content filtering.
"""

import re
import json
import signal
import logging
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime, timezone
from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from models import AcquiredDocument, ProcessingMetadata


class TimeoutException(Exception):
    """Exception raised when processing times out."""
    pass


class ArxivProcessor:
    """Processes PDF documents to markdown format using docling."""
    
    def __init__(
        self,
        preserve_tables: bool = True,
        preserve_equations: bool = True,
        enrich_formulas: bool = True,
        table_mode: str = "fast",
        exclude_references: bool = True,
        exclude_acknowledgments: bool = True,
        exclude_author_lists: bool = True,
        processing_timeout: int = 600
    ) -> None:
        """
        Initialize processing module with docling.
        
        Args:
            preserve_tables: Whether to preserve tables in markdown
            preserve_equations: Whether to preserve LaTeX equations
            enrich_formulas: Whether to enrich formulas with LaTeX extraction
            table_mode: Table processing mode ('fast' or 'accurate')
            exclude_references: Whether to exclude references section
            exclude_acknowledgments: Whether to exclude acknowledgments
            exclude_author_lists: Whether to exclude author lists
            processing_timeout: Maximum seconds to process a single PDF (0 = no timeout)
        """
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.preserve_tables: bool = preserve_tables
        self.preserve_equations: bool = preserve_equations
        self.enrich_formulas: bool = enrich_formulas
        self.table_mode: str = table_mode.lower()
        self.exclude_references: bool = exclude_references
        self.exclude_acknowledgments: bool = exclude_acknowledgments
        self.exclude_author_lists: bool = exclude_author_lists
        self.processing_timeout: int = processing_timeout
        self.converter: DocumentConverter = self._initialize_converter()
    
    def _initialize_converter(self) -> DocumentConverter:
        """
        Initialize docling converter with optimized settings.
        
        Returns:
            Configured DocumentConverter instance
        """
        pipeline_options: PdfPipelineOptions = PdfPipelineOptions()
        pipeline_options.do_table_structure = self.preserve_tables
        if self.table_mode == "accurate":
            pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
            self.logger.info("Using ACCURATE table processing mode (slower but more precise)")
        else:
            pipeline_options.table_structure_options.mode = TableFormerMode.FAST
            self.logger.info("Using FAST table processing mode (faster but less precise)")
        pipeline_options.do_formula_enrichment = self.enrich_formulas
        pipeline_options.do_ocr = False
        pipeline_options.generate_page_images = False
        pipeline_options.generate_picture_images = False
        converter: DocumentConverter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options
                )
            }
        )
        return converter
    
    def _timeout_handler(self, signum: int, frame: Any) -> None:
        """Signal handler for processing timeout."""
        raise TimeoutException("PDF processing exceeded timeout limit")
    
    def process(self, acquired: AcquiredDocument, output_dir: Path) -> Tuple[Path, ProcessingMetadata]:
        """
        Process single document to markdown using docling.
        
        Args:
            acquired: Acquired document information
            output_dir: Directory for output files
            
        Returns:
            Tuple of (markdown_path, processing_metadata)
        """
        start_time: datetime = datetime.now(timezone.utc)
        warnings: List[str] = []
        old_handler = None
        try:
            pdf_path: Path = Path(acquired.local_path)
            self.logger.info(f"Starting PDF conversion for {pdf_path.name}")
            if self.processing_timeout > 0:
                old_handler = signal.signal(signal.SIGALRM, self._timeout_handler)
                signal.alarm(self.processing_timeout)
                self.logger.info(f"Set processing timeout to {self.processing_timeout} seconds")
            self.logger.info("Running docling converter (this may take several minutes for complex PDFs)...")
            result = self.converter.convert(str(pdf_path))
            if self.processing_timeout > 0:
                signal.alarm(0)
            self.logger.info("Docling conversion completed, exporting to markdown...")
            markdown: str = result.document.export_to_markdown()
            self.logger.info("Markdown export completed")
            markdown = self._filter_content(markdown, warnings)
            if self.preserve_equations:
                markdown = self._enhance_equations(markdown)
            markdown = self._clean_markdown(markdown)
            doc_dir: Path = output_dir / f"arxiv_{acquired.document_id}"
            doc_dir.mkdir(parents=True, exist_ok=True)
            md_path: Path = doc_dir / "full_document.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            duration: float = (datetime.now(timezone.utc) - start_time).total_seconds()
            metadata: ProcessingMetadata = ProcessingMetadata(
                processor_used="docling/1.0.0",
                processing_timestamp=start_time,
                processing_duration=duration,
                conversion_warnings=warnings
            )
            return md_path, metadata
        except TimeoutException as e:
            if self.processing_timeout > 0 and old_handler:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
            duration: float = (datetime.now(timezone.utc) - start_time).total_seconds()
            error_msg: str = f"Processing timeout after {duration:.1f}s (limit: {self.processing_timeout}s)"
            self.logger.error(error_msg)
            warnings.append(error_msg)
            metadata: ProcessingMetadata = ProcessingMetadata(
                processor_used="docling/1.0.0",
                processing_timestamp=start_time,
                processing_duration=duration,
                conversion_warnings=warnings
            )
            return Path(""), metadata
        except Exception as e:
            if self.processing_timeout > 0 and old_handler:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
            duration: float = (datetime.now(timezone.utc) - start_time).total_seconds()
            error_msg: str = f"Processing failed: {str(e)}"
            self.logger.error(error_msg)
            warnings.append(error_msg)
            metadata: ProcessingMetadata = ProcessingMetadata(
                processor_used="docling/1.0.0",
                processing_timestamp=start_time,
                processing_duration=duration,
                conversion_warnings=warnings
            )
            return Path(""), metadata
    
    def _filter_content(self, markdown: str, warnings: List[str]) -> str:
        """
        Filter unwanted sections from markdown content.
        
        Args:
            markdown: Input markdown text
            warnings: List to append warnings to
            
        Returns:
            Filtered markdown text
        """
        lines: List[str] = markdown.split('\n')
        filtered_lines: List[str] = []
        skip_until_next_section: bool = False
        in_excluded_section: bool = False
        for line in lines:
            stripped: str = line.strip()
            if line.startswith('#'):
                skip_until_next_section = False
                in_excluded_section = False
                lower_line: str = stripped.lower()
                if self.exclude_references and self._is_references_section(lower_line):
                    skip_until_next_section = True
                    in_excluded_section = True
                    warnings.append(f"Excluded references section: {stripped}")
                    continue
                if self.exclude_acknowledgments and self._is_acknowledgments_section(lower_line):
                    skip_until_next_section = True
                    in_excluded_section = True
                    warnings.append(f"Excluded acknowledgments section: {stripped}")
                    continue
                if self.exclude_author_lists and self._is_author_list_section(lower_line):
                    skip_until_next_section = True
                    in_excluded_section = True
                    warnings.append(f"Excluded author list section: {stripped}")
                    continue
            if skip_until_next_section and not line.startswith('#'):
                continue
            if not in_excluded_section:
                filtered_lines.append(line)
        return '\n'.join(filtered_lines)
    
    def _is_references_section(self, line: str) -> bool:
        """Check if line is a references section heading."""
        patterns: List[str] = [
            r'^#+ references\s*$',
            r'^#+ bibliography\s*$',
            r'^#+ citations\s*$',
            r'^#+ works cited\s*$',
            r'^#+ literature cited\s*$'
        ]
        return any(re.match(pattern, line) for pattern in patterns)
    
    def _is_acknowledgments_section(self, line: str) -> bool:
        """Check if line is an acknowledgments section heading."""
        patterns: List[str] = [
            r'^#+ acknowledgments?\s*$',
            r'^#+ acknowledgements?\s*$'
        ]
        return any(re.match(pattern, line) for pattern in patterns)
    
    def _is_author_list_section(self, line: str) -> bool:
        """Check if line is an author list or collaboration section heading."""
        patterns: List[str] = [
            r'^#+ authors?\s*$',
            r'^#+ lhcb collaboration\s*$',
            r'^#+ atlas collaboration\s*$',
            r'^#+ cms collaboration\s*$',
            r'^#+ alice collaboration\s*$',
            r'^#+ collaboration\s*$'
        ]
        return any(re.match(pattern, line) for pattern in patterns)
    
    def _enhance_equations(self, markdown: str) -> str:
        """
        Enhance LaTeX equation formatting with comprehensive math environment support.
        
        Args:
            markdown: Input markdown text
            
        Returns:
            Markdown with enhanced equations
        """
        math_envs: List[str] = [
            'equation', 'equation\\*',
            'align', 'align\\*',
            'gather', 'gather\\*',
            'multline', 'multline\\*',
            'split',
            'eqnarray', 'eqnarray\\*',
            'matrix', 'pmatrix', 'bmatrix', 'vmatrix', 'Vmatrix'
        ]
        for env in math_envs:
            env_clean: str = env.replace('\\', '')
            pattern: str = rf'\\begin\{{{env}\}}(.*?)\\end\{{{env}\}}'
            markdown = re.sub(pattern, r'$$\1$$', markdown, flags=re.DOTALL)
        markdown = re.sub(r'(?<!\$)\$(?!\$)([^\$]+?)\$(?!\$)', r'$\1$', markdown)
        markdown = re.sub(r'\$\$\s*\$\$', '', markdown)
        return markdown
    
    def _clean_markdown(self, markdown: str) -> str:
        """
        Clean markdown while preserving mathematical content and structure.
        
        Args:
            markdown: Input markdown text
            
        Returns:
            Cleaned markdown text
        """
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        lines: List[str] = markdown.split('\n')
        cleaned_lines: List[str] = []
        for line in lines:
            if line.strip():
                cleaned_lines.append(line.rstrip())
            elif cleaned_lines and cleaned_lines[-1] != '':
                cleaned_lines.append('')
        return '\n'.join(cleaned_lines)
    
    def save_processing_metadata(self, metadata: ProcessingMetadata, output_path: Path) -> None:
        """
        Save processing metadata to JSON file.
        
        Args:
            metadata: Processing metadata
            output_path: Path to output JSON file
        """
        data: Dict[str, Any] = {
            "processor_used": metadata.processor_used,
            "processing_timestamp": metadata.processing_timestamp.isoformat(),
            "processing_duration": metadata.processing_duration,
            "conversion_warnings": metadata.conversion_warnings
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

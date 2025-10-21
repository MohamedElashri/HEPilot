"""
Processing module for converting PDF to CommonMark markdown using docling.

Uses docling's ML models for advanced PDF processing including LaTeX formula
extraction, table handling, and section detection with comprehensive content filtering.
"""

import re
import json
import signal
import logging
import threading
import time
import os
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
        processing_timeout: int = 100
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
            processing_timeout: Maximum seconds to process a single PDF per attempt (0 = no timeout)
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
        # Converters are initialized on-demand for each processing strategy
        self.converter: Optional[DocumentConverter] = None
    
    def _initialize_converter(
        self, 
        enable_tables: bool = True, 
        enable_formulas: bool = True
    ) -> DocumentConverter:
        """
        Initialize docling converter with specified settings.
        
        Args:
            enable_tables: Whether to enable table structure detection
            enable_formulas: Whether to enable formula enrichment
        
        Returns:
            Configured DocumentConverter instance
        """
        pipeline_options: PdfPipelineOptions = PdfPipelineOptions()
        pipeline_options.do_table_structure = enable_tables and self.preserve_tables
        
        if enable_tables and self.preserve_tables:
            if self.table_mode == "accurate":
                pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
                self.logger.info("Using ACCURATE table processing mode (slower but more precise)")
            else:
                pipeline_options.table_structure_options.mode = TableFormerMode.FAST
                self.logger.info("Using FAST table processing mode (faster but less precise)")
        
        pipeline_options.do_formula_enrichment = enable_formulas and self.enrich_formulas
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
    
    def _progress_monitor(self, pdf_name: str, start_time: float, stop_event: threading.Event) -> None:
        """
        Monitor and log progress during conversion.
        
        Args:
            pdf_name: Name of the PDF being processed
            start_time: Start time of processing
            stop_event: Event to signal monitoring should stop
        """
        interval: int = 30
        while not stop_event.wait(interval):
            elapsed: float = time.time() - start_time
            self.logger.info(f"Still processing {pdf_name}... ({elapsed:.0f}s elapsed)")
    
    def _attempt_conversion(
        self,
        pdf_path: Path,
        enable_tables: bool,
        enable_formulas: bool,
        attempt_name: str
    ) -> Optional[str]:
        """
        Attempt PDF conversion with specified settings.
        
        Args:
            pdf_path: Path to PDF file
            enable_tables: Whether to enable table processing
            enable_formulas: Whether to enable formula enrichment
            attempt_name: Name of this attempt for logging
            
        Returns:
            Markdown string if successful, None if timeout/error
        """
        old_handler = None
        stop_event: threading.Event = threading.Event()
        monitor_thread: Optional[threading.Thread] = None
        
        try:
            self.logger.info(f"{attempt_name}: tables={enable_tables}, formulas={enable_formulas}")
            
            # Initialize converter with specific settings
            converter = self._initialize_converter(enable_tables, enable_formulas)
            
            if self.processing_timeout > 0:
                old_handler = signal.signal(signal.SIGALRM, self._timeout_handler)
                signal.alarm(self.processing_timeout)
                self.logger.info(f"Set timeout to {self.processing_timeout} seconds for this attempt")
            
            monitor_thread = threading.Thread(
                target=self._progress_monitor,
                args=(pdf_path.name, time.time(), stop_event),
                daemon=True
            )
            monitor_thread.start()
            
            result = converter.convert(str(pdf_path))
            
            stop_event.set()
            if monitor_thread:
                monitor_thread.join(timeout=1)
            
            if self.processing_timeout > 0:
                signal.alarm(0)
            
            self.logger.info(f"{attempt_name} succeeded, exporting to markdown...")
            markdown: str = result.document.export_to_markdown()
            return markdown
            
        except TimeoutException:
            stop_event.set()
            if monitor_thread:
                monitor_thread.join(timeout=1)
            if self.processing_timeout > 0 and old_handler:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
            self.logger.warning(f"{attempt_name} timed out after {self.processing_timeout}s")
            return None
            
        except Exception as e:
            stop_event.set()
            if monitor_thread:
                monitor_thread.join(timeout=1)
            if self.processing_timeout > 0 and old_handler:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
            self.logger.warning(f"{attempt_name} failed: {str(e)}")
            return None
    
    def process(self, acquired: AcquiredDocument, output_dir: Path) -> Tuple[Path, ProcessingMetadata]:
        """
        Process single document to markdown using docling with progressive degradation.
        
        Attempts processing in multiple stages:
        1. Full processing (tables + formulas)
        2. No tables, keep formulas
        3. No tables, no formulas
        4. Basic text extraction only
        
        Args:
            acquired: Acquired document information
            output_dir: Directory for output files
            
        Returns:
            Tuple of (markdown_path, processing_metadata)
        """
        start_time: datetime = datetime.now(timezone.utc)
        warnings: List[str] = []
        markdown: Optional[str] = None
        processor_mode: str = "unknown"
        
        try:
            pdf_path: Path = Path(acquired.local_path)
            pdf_size_mb: float = os.path.getsize(pdf_path) / (1024 * 1024)
            self.logger.info(f"Starting PDF conversion for {pdf_path.name} ({pdf_size_mb:.1f} MB)")
            
            if pdf_size_mb > 10:
                self.logger.warning(f"Large PDF detected ({pdf_size_mb:.1f} MB) - will use progressive degradation if needed")
            
            # Progressive degradation strategy
            strategies = [
                ("Attempt 1 (Full processing)", True, True, "full"),
                ("Attempt 2 (No tables)", False, True, "no_tables"),
                ("Attempt 3 (No tables, no formulas)", False, False, "basic"),
            ]
            
            for attempt_name, enable_tables, enable_formulas, mode in strategies:
                markdown = self._attempt_conversion(pdf_path, enable_tables, enable_formulas, attempt_name)
                
                if markdown is not None:
                    processor_mode = mode
                    if mode != "full":
                        warning_msg = f"Used degraded processing mode: {mode}"
                        self.logger.warning(warning_msg)
                        warnings.append(warning_msg)
                    break
            
            if markdown is None:
                error_msg = "All processing attempts failed or timed out"
                self.logger.error(error_msg)
                warnings.append(error_msg)
                duration: float = (datetime.now(timezone.utc) - start_time).total_seconds()
                metadata: ProcessingMetadata = ProcessingMetadata(
                    processor_used=f"docling/1.0.0 (failed)",
                    processing_timestamp=start_time,
                    processing_duration=duration,
                    conversion_warnings=warnings
                )
                return Path(""), metadata
            
            # Post-process markdown
            self.logger.info("Processing markdown content...")
            markdown = self._filter_content(markdown, warnings)
            
            if self.preserve_equations and processor_mode in ["full", "no_tables"]:
                markdown = self._enhance_equations(markdown)
            
            markdown = self._clean_markdown(markdown)
            
            # Save to file
            doc_dir: Path = output_dir / f"arxiv_{acquired.document_id}"
            doc_dir.mkdir(parents=True, exist_ok=True)
            md_path: Path = doc_dir / "full_document.md"
            
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            duration: float = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.logger.info(f"Processing completed in {duration:.1f}s using mode: {processor_mode}")
            
            metadata: ProcessingMetadata = ProcessingMetadata(
                processor_used=f"docling/1.0.0 (mode: {processor_mode})",
                processing_timestamp=start_time,
                processing_duration=duration,
                conversion_warnings=warnings
            )
            return md_path, metadata
            
        except Exception as e:
            duration: float = (datetime.now(timezone.utc) - start_time).total_seconds()
            error_msg: str = f"Fatal processing error: {str(e)}"
            self.logger.error(error_msg)
            warnings.append(error_msg)
            metadata: ProcessingMetadata = ProcessingMetadata(
                processor_used="docling/1.0.0 (fatal_error)",
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

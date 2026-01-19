"""
Processing module for converting ArXiv HTML to Markdown.

Uses BeautifulSoup for DOM manipulation and cleaning, and markdownify
for converting the cleaned HTML to Markdown format.
"""

import logging
import json
import re
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag
from markdownify import markdownify as md
from models import AcquiredDocument, ProcessingMetadata


class ArxivHtmlProcessor:
    """Processes HTML documents to markdown format."""

    def __init__(
        self,
        preserve_equations: bool = True,
        exclude_references: bool = True,
        exclude_acknowledgments: bool = True,
        exclude_author_lists: bool = True,
        processing_timeout: int = 60,
    ) -> None:
        """
        Initialize processing module.

        Args:
            preserve_equations: Whether to preserve math equations (if possible)
            exclude_references: Whether to exclude references section
            exclude_acknowledgments: Whether to exclude acknowledgments
            exclude_author_lists: Whether to exclude author lists
            processing_timeout: Maximum seconds to process a single file
        """
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.preserve_equations: bool = preserve_equations
        self.exclude_references: bool = exclude_references
        self.exclude_acknowledgments: bool = exclude_acknowledgments
        self.exclude_author_lists: bool = exclude_author_lists
        self.processing_timeout: int = processing_timeout

    def process(
        self, acquired: AcquiredDocument, output_dir: Path
    ) -> Tuple[Path, ProcessingMetadata]:
        """
        Process single HTML document to markdown.

        Args:
            acquired: Acquired document information
            output_dir: Directory for output files

        Returns:
            Tuple of (markdown_path, processing_metadata)
        """
        start_time: datetime = datetime.now(timezone.utc)
        warnings: List[str] = []

        try:
            html_path: Path = Path(acquired.local_path)
            if not html_path.exists():
                raise FileNotFoundError(f"HTML file not found: {html_path}")

            self.logger.info(f"Starting HTML conversion for {html_path.name}")

            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Parse HTML
            soup = BeautifulSoup(html_content, "html.parser")

            # --- Cleaning & Pre-processing ---

            # --- Cleaning & Pre-processing ---

            # Remove ArXiv header/footer and navigation
            for class_name in [
                "ltx_page_header",
                "ltx_page_footer",
                "ltx_navbar",
                "ar5iv-footer",
                "extra-services",
            ]:
                for tag in soup.find_all(class_=class_name):
                    tag.decompose()

            # Handle References/Bibliography
            if self.exclude_references:
                for tag in soup.find_all(class_="ltx_bibliography"):
                    tag.decompose()
                for tag in soup.find_all(id="bib"):
                    tag.decompose()

            # Handle Authors
            if self.exclude_author_lists:
                for tag in soup.find_all(class_="ltx_authors"):
                    tag.decompose()

            # Handle Acknowledgments
            if self.exclude_acknowledgments:
                for tag in soup.find_all(class_="ltx_acknowledgments"):
                    tag.decompose()
                for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
                    if h.get_text().lower().strip() in [
                        "acknowledgments",
                        "acknowledgements",
                    ]:
                        parent = h.find_parent(class_="ltx_section")
                        if parent:
                            parent.decompose()

            # --- Link Handling ---
            # Rewrite absolute ArXiv HTML URLs to internal fragments
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "arxiv.org/html/" in href and "#" in href:
                    # safely assume if it has a fragment, strict to fragment for cleaner markdown
                    fragment = href.split("#")[-1]
                    if fragment:
                        a["href"] = f"#{fragment}"

            # --- Math & Table Handling ---
            math_replacements = {}
            math_counter = 0

            # 1. SPECIAL CASE: Equation Tables (ltx_equationgroup etc.)
            # ArXiv sometimes puts equations in tables. We convert these to block math.
            if self.preserve_equations:
                for table in soup.find_all(
                    "table",
                    class_=re.compile(r"ltx_equationgroup|ltx_eqn_align|ltx_eqn_table"),
                ):
                    text = table.get_text(" ", strip=True)
                    if text:
                        placeholder = f"MATHPLACEHOLDER{math_counter}"
                        math_counter += 1
                        math_replacements[placeholder] = f"\n$${text}$$\n"
                        table.replace_with(NavigableString(placeholder))

            # 2. General Tables Cleaning
            # Use custom serialization for tables to improve quality vs markdownify
            for table in soup.find_all("table"):
                table_md = self._serialize_table(table)
                if table_md:
                    # Replace table with placeholder
                    placeholder = f"TABLEPLACEHOLDER{math_counter}"
                    math_counter += 1
                    math_replacements[placeholder] = f"\n\n{table_md}\n\n"
                    table.replace_with(NavigableString(placeholder))
                else:
                    table.decompose()

            # 3. Standard MathML conversion
            if self.preserve_equations:
                for math_tag in soup.find_all("math"):
                    latex = None

                    # Try annotation
                    annotation = math_tag.find(
                        "annotation", attrs={"encoding": "application/x-tex"}
                    )
                    if annotation:
                        latex = annotation.get_text().strip()

                    # Try alt-text
                    if not latex and math_tag.get("alttext"):
                        latex = math_tag.get("alttext").strip()

                    # Fallback
                    if not latex:
                        latex = math_tag.get_text(" ", strip=True)

                    if latex:
                        # Clean up LaTeX source (borrowed from arxiv2md)
                        latex = re.sub(r"(?<!\\)%", "", latex)  # Remove comments
                        latex = re.sub(
                            r"\\([_^])", r"\1", latex
                        )  # Unescape underscores/carets
                        latex = re.sub(r"\\(?=[\[\]])", "", latex)  # Unescape brackets

                        is_block = math_tag.get("display") == "block"

                        placeholder = f"MATHPLACEHOLDER{math_counter}"
                        math_counter += 1

                        if is_block:
                            math_replacements[placeholder] = f"\n$${latex}$$\n"
                        else:
                            math_replacements[placeholder] = f"${latex}$"

                        math_tag.replace_with(NavigableString(placeholder))

            # Convert to Markdown
            markdown = md(str(soup), heading_style="atx")

            # Restore Math & Tables
            # Sort by length descending to prevent substring collisions (e.g. replacing placeholder1 inside placeholder11)
            sorted_placeholders = sorted(
                math_replacements.keys(), key=len, reverse=True
            )
            for placeholder in sorted_placeholders:
                markdown = markdown.replace(placeholder, math_replacements[placeholder])

            # Post-processing clean up
            markdown = self._clean_markdown(markdown)

            doc_dir: Path = output_dir / f"arxiv_{acquired.document_id}"
            doc_dir.mkdir(parents=True, exist_ok=True)
            md_path: Path = doc_dir / "full_document.md"

            with open(md_path, "w", encoding="utf-8") as f:
                f.write(markdown)

            duration: float = (datetime.now(timezone.utc) - start_time).total_seconds()

            return md_path, ProcessingMetadata(
                processor_used="html-adapter/1.0",
                processing_timestamp=start_time,
                processing_duration=duration,
                conversion_warnings=warnings,
            )

        except Exception as e:
            duration: float = (datetime.now(timezone.utc) - start_time).total_seconds()
            error_msg: str = f"HTML processing failed: {str(e)}"
            self.logger.error(error_msg)
            warnings.append(error_msg)

            return Path(""), ProcessingMetadata(
                processor_used="html-adapter/1.0",
                processing_timestamp=start_time,
                processing_duration=duration,
                conversion_warnings=warnings,
            )

    def _serialize_table(self, table: Tag) -> str:
        """
        Custom table serializer that handles colspan/rowspan by building a 2D grid.
        Produces a standard Markdown table.
        """
        # 1. Parse into a grid
        grid = {}  # (row, col) -> text
        rows = table.find_all("tr")
        if not rows:
            return ""

        max_row = len(rows)
        max_col = 0

        # Track occupied cells for rowspans: (row, col) -> bool
        occupied = set()

        for r, row in enumerate(rows):
            cells = row.find_all(["th", "td"], recursive=False)
            current_col = 0

            for cell in cells:
                # Skip occupied cells (from previous rowspans)
                while (r, current_col) in occupied:
                    current_col += 1

                # Clean text
                cell_text = self._clean_text(cell.get_text(" ", strip=True))
                cell_text = cell_text.replace("\n", "<br>").replace("|", "\\|")

                # Get span attributes
                try:
                    colspan = int(cell.get("colspan", 1))
                except (ValueError, TypeError):
                    colspan = 1

                try:
                    rowspan = int(cell.get("rowspan", 1))
                except (ValueError, TypeError):
                    rowspan = 1

                # Fill grid
                for i in range(rowspan):
                    for j in range(colspan):
                        if i == 0 and j == 0:
                            grid[(r + i, current_col + j)] = cell_text
                        else:
                            # For Markdown, we usually just leave spanned cells empty
                            # or repeat the value. Repeating is safer for alignment.
                            # But standard markdown text tables don't support merge.
                            # Leaving empty is standard convention.
                            grid[(r + i, current_col + j)] = ""

                        occupied.add((r + i, current_col + j))

                current_col += colspan
                max_col = max(max_col, current_col)

        if max_col == 0:
            return ""

        # 2. Build Markdown lines
        lines = []

        # Header (Row 0)
        header_cells = [grid.get((0, c), "") for c in range(max_col)]
        lines.append("| " + " | ".join(header_cells) + " |")

        # Separator
        lines.append("| " + " | ".join("---" for _ in header_cells) + " |")

        # Body (Row 1+)
        for r in range(1, max_row):
            row_cells = [grid.get((r, c), "") for c in range(max_col)]
            lines.append("| " + " | ".join(row_cells) + " |")

        return "\n".join(lines)

    def _clean_text(self, text: str) -> str:
        """normalize whitespace"""
        return re.sub(r"\s+", " ", text).strip()

    def _clean_markdown(self, markdown: str) -> str:
        """
        Clean markdown output.
        """
        # Remove excessive newlines
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)

        lines = markdown.split("\n")
        cleaned_lines = []
        for line in lines:
            if line.strip():
                cleaned_lines.append(line.rstrip())
            elif cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")

        return "\n".join(cleaned_lines)

    def save_processing_metadata(
        self, metadata: ProcessingMetadata, output_path: Path
    ) -> None:
        """Save processing metadata to JSON file."""
        data: Dict[str, Any] = {
            "processor_used": metadata.processor_used,
            "processing_timestamp": metadata.processing_timestamp.isoformat(),
            "processing_duration": metadata.processing_duration,
            "conversion_warnings": metadata.conversion_warnings,
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

"""
Utility functions for the ArXiv adapter.

Provides colored output, validation helpers, and common utilities.
"""

from typing import Optional
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""
    
    RESET: str = '\033[0m'
    BOLD: str = '\033[1m'
    DIM: str = '\033[2m'
    
    # Foreground colors
    BLACK: str = '\033[30m'
    RED: str = '\033[31m'
    GREEN: str = '\033[32m'
    YELLOW: str = '\033[33m'
    BLUE: str = '\033[34m'
    MAGENTA: str = '\033[35m'
    CYAN: str = '\033[36m'
    WHITE: str = '\033[37m'
    
    # Bright foreground colors
    BRIGHT_BLACK: str = '\033[90m'
    BRIGHT_RED: str = '\033[91m'
    BRIGHT_GREEN: str = '\033[92m'
    BRIGHT_YELLOW: str = '\033[93m'
    BRIGHT_BLUE: str = '\033[94m'
    BRIGHT_MAGENTA: str = '\033[95m'
    BRIGHT_CYAN: str = '\033[96m'
    BRIGHT_WHITE: str = '\033[97m'
    
    @staticmethod
    def disable() -> None:
        """Disable all colors (set to empty strings)."""
        for attr in dir(Colors):
            if not attr.startswith('_') and attr.isupper():
                setattr(Colors, attr, '')


def print_header(text: str) -> None:
    """
    Print a bold header with separator lines.
    
    Args:
        text: Header text
    """
    separator: str = "=" * 80
    print(f"\n{Colors.BOLD}{Colors.CYAN}{separator}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{separator}{Colors.RESET}\n")


def print_config(config: dict) -> None:
    """
    Print configuration in a colorful, organized format.
    
    Args:
        config: Configuration dictionary
    """
    print_header("ArXiv Adapter Configuration")
    
    for key, value in config.items():
        if isinstance(value, dict):
            print(f"{Colors.BOLD}{Colors.YELLOW}[{key}]{Colors.RESET}")
            for sub_key, sub_value in value.items():
                _print_config_item(sub_key, sub_value, indent=2)
        else:
            _print_config_item(key, value)
    
    print()


def _print_config_item(key: str, value: any, indent: int = 0) -> None:
    """
    Print a single configuration item with color coding.
    
    Args:
        key: Configuration key
        value: Configuration value
        indent: Indentation level
    """
    prefix: str = " " * indent
    key_colored: str = f"{Colors.BRIGHT_BLUE}{key}{Colors.RESET}"
    
    if isinstance(value, bool):
        value_str: str = f"{Colors.GREEN if value else Colors.RED}{value}{Colors.RESET}"
    elif isinstance(value, (int, float)):
        value_str: str = f"{Colors.CYAN}{value}{Colors.RESET}"
    elif value is None:
        value_str: str = f"{Colors.DIM}None{Colors.RESET}"
    else:
        value_str: str = f"{Colors.WHITE}{value}{Colors.RESET}"
    
    print(f"{prefix}{key_colored}: {value_str}")


def print_cache_summary(cached: int, to_download: int, to_retry: int) -> None:
    """
    Print cache summary with color coding.
    
    Args:
        cached: Number of fully cached papers
        to_download: Number of papers to download
        to_retry: Number of papers to retry processing
    """
    parts: list = []
    
    if cached > 0:
        parts.append(f"{Colors.GREEN}{cached} cached{Colors.RESET}")
    if to_download > 0:
        parts.append(f"{Colors.YELLOW}{to_download} to download{Colors.RESET}")
    if to_retry > 0:
        parts.append(f"{Colors.CYAN}{to_retry} to retry{Colors.RESET}")
    
    if parts:
        summary: str = ", ".join(parts)
        print(f"\n{Colors.BOLD}[CACHE]{Colors.RESET} {summary}\n")


def print_status(status: str, message: str) -> None:
    """
    Print a status message with color coding.
    
    Args:
        status: Status level (INFO, SUCCESS, WARNING, ERROR)
        message: Status message
    """
    status_colors: dict = {
        "INFO": Colors.BLUE,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED
    }
    
    color: str = status_colors.get(status.upper(), Colors.WHITE)
    print(f"{color}[{status}]{Colors.RESET} {message}")


def validate_pdf_exists(pdf_path: Path) -> bool:
    """
    Validate that a PDF file exists and has non-zero size.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        True if file exists and is valid
    """
    try:
        return pdf_path.exists() and pdf_path.stat().st_size > 0
    except Exception:
        return False


def get_pdf_path(output_dir: Path, document_id: str) -> Path:
    """
    Get the path to a PDF file.
    
    Args:
        output_dir: Output directory
        document_id: Document ID
        
    Returns:
        Path to PDF file
    """
    return output_dir / "downloads" / f"{document_id}.pdf"

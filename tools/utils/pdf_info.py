"""
PDF information utilities for reading metadata and page count.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Optional, Union


def get_pdf_page_count(pdf_path: Union[str, Path]) -> int:
    """
    Get the number of pages in a PDF file.
    
    Tries multiple methods in order:
    1. pdfinfo command (poppler-utils)
    2. PyPDF2 if available
    3. Regex search in binary content (fallback)
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        Number of pages
    
    Raises:
        FileNotFoundError: If PDF doesn't exist
        RuntimeError: If page count cannot be determined
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    # Method 1: pdfinfo command
    try:
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if line.startswith("Pages:"):
                    return int(line.split(":", 1)[1].strip())
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pass
    
    # Method 2: PyPDF2
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(str(pdf_path))
        return len(reader.pages)
    except ImportError:
        pass
    except Exception:
        pass
    
    # Method 3: Regex fallback (search for /Count in PDF)
    try:
        with open(pdf_path, "rb") as f:
            content = f.read(100000)  # Read first 100KB
            # Look for /Count N in PDF structure
            matches = re.findall(rb"/Count\s+(\d+)", content)
            if matches:
                # Usually the last match in the header is the correct one
                return int(matches[-1])
    except Exception:
        pass
    
    raise RuntimeError(f"Could not determine page count for: {pdf_path}")


def get_pdf_metadata(pdf_path: Union[str, Path]) -> dict:
    """
    Extract metadata from PDF file.
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        Dictionary of metadata fields
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    metadata = {
        "file_name": pdf_path.name,
        "file_size": os.path.getsize(pdf_path),
        "file_path": str(pdf_path),
    }
    
    # Try to get page count
    try:
        metadata["page_count"] = get_pdf_page_count(pdf_path)
    except Exception as e:
        metadata["page_count_error"] = str(e)
    
    # Try pdfinfo for more metadata
    try:
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().lower().replace(" ", "_")
                    value = value.strip()
                    if value and value != "none":
                        metadata[key] = value
    except Exception:
        pass
    
    # Try PyPDF2 for additional metadata
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(str(pdf_path))
        if reader.metadata:
            pdf_metadata = reader.metadata
            for key in ["/Title", "/Author", "/Subject", "/Creator", "/Producer"]:
                if key in pdf_metadata:
                    value = pdf_metadata[key]
                    if value:
                        metadata[key.lower().strip("/")] = str(value)
    except ImportError:
        pass
    except Exception:
        pass
    
    return metadata


def is_valid_pdf(pdf_path: Union[str, Path]) -> bool:
    """
    Check if file is a valid PDF.
    
    Args:
        pdf_path: Path to file
    
    Returns:
        True if valid PDF, False otherwise
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        return False
    
    # Check PDF magic number
    try:
        with open(pdf_path, "rb") as f:
            header = f.read(5)
            return header.startswith(b"%PDF-")
    except Exception:
        return False


def scan_pdf_directory(directory: Union[str, Path]) -> list[Path]:
    """
    Recursively scan directory for PDF files.
    
    Args:
        directory: Directory to scan
    
    Returns:
        List of PDF file paths
    """
    directory = Path(directory)
    
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    pdf_files = []
    for pdf_path in directory.rglob("*.pdf"):
        if is_valid_pdf(pdf_path):
            pdf_files.append(pdf_path)
    
    return sorted(pdf_files)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


if __name__ == "__main__":
    # Simple CLI for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_info.py <pdf_path> [--scan <directory>]")
        sys.exit(1)
    
    if sys.argv[1] == "--scan" and len(sys.argv) >= 3:
        directory = sys.argv[2]
        try:
            pdfs = scan_pdf_directory(directory)
            print(f"Found {len(pdfs)} PDF(s) in {directory}:")
            for pdf in pdfs:
                try:
                    pages = get_pdf_page_count(pdf)
                    size = format_file_size(os.path.getsize(pdf))
                    print(f"  - {pdf} ({pages} pages, {size})")
                except Exception as e:
                    print(f"  - {pdf} (error: {e})")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        pdf_path = sys.argv[1]
        try:
            metadata = get_pdf_metadata(pdf_path)
            print(f"PDF Info: {pdf_path}")
            for key, value in metadata.items():
                if key == "file_size":
                    value = format_file_size(value)
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

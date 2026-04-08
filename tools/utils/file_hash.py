"""
File hash utilities for PDF deduplication and identification.
"""

import hashlib
import os
from pathlib import Path
from typing import Union


def compute_file_hash(file_path: Union[str, Path], algorithm: str = "sha256") -> str:
    """
    Compute hash of a file.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm (sha256, md5, sha1)
    
    Returns:
        Hex digest of the file hash
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If algorithm is not supported
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if algorithm == "sha256":
        hasher = hashlib.sha256()
    elif algorithm == "md5":
        hasher = hashlib.md5()
    elif algorithm == "sha1":
        hasher = hashlib.sha1()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    # Read file in chunks to handle large files
    chunk_size = 8192
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    
    return hasher.hexdigest()


def compute_file_hash_with_prefix(file_path: Union[str, Path]) -> str:
    """
    Compute SHA256 hash with 'sha256:' prefix.
    
    Args:
        file_path: Path to the file
    
    Returns:
        Hash string with prefix (e.g., "sha256:abc123...")
    """
    return f"sha256:{compute_file_hash(file_path, 'sha256')}"


def generate_pdf_id(file_path: Union[str, Path]) -> str:
    """
    Generate a unique PDF ID from file hash (first 8 characters).
    
    Args:
        file_path: Path to the PDF file
    
    Returns:
        PDF ID in format "pdf_{hash_prefix}"
    """
    file_hash = compute_file_hash(file_path, "sha256")
    return f"pdf_{file_hash[:8]}"


def find_duplicates(pdf_paths: list[Union[str, Path]]) -> dict[str, list[Path]]:
    """
    Find duplicate PDFs based on file hash.
    
    Args:
        pdf_paths: List of PDF file paths
    
    Returns:
        Dictionary mapping hash to list of duplicate paths
    """
    hash_to_paths: dict[str, list[Path]] = {}
    
    for path in pdf_paths:
        path = Path(path)
        if not path.exists():
            continue
        
        file_hash = compute_file_hash(path)
        if file_hash not in hash_to_paths:
            hash_to_paths[file_hash] = []
        hash_to_paths[file_hash].append(path)
    
    # Filter to only duplicates (more than one file)
    return {h: paths for h, paths in hash_to_paths.items() if len(paths) > 1}


def verify_file_integrity(file_path: Union[str, Path], expected_hash: str) -> bool:
    """
    Verify file integrity by comparing hash.
    
    Args:
        file_path: Path to the file
        expected_hash: Expected hash value (with or without prefix)
    
    Returns:
        True if hash matches, False otherwise
    """
    # Remove prefix if present
    if ":" in expected_hash:
        expected_hash = expected_hash.split(":", 1)[1]
    
    actual_hash = compute_file_hash(file_path)
    return actual_hash.lower() == expected_hash.lower()


if __name__ == "__main__":
    # Simple CLI for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python file_hash.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    try:
        file_hash = compute_file_hash_with_prefix(pdf_path)
        pdf_id = generate_pdf_id(pdf_path)
        file_size = os.path.getsize(pdf_path)
        
        print(f"File: {pdf_path}")
        print(f"Size: {file_size} bytes")
        print(f"Hash: {file_hash}")
        print(f"PDF ID: {pdf_id}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

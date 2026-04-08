"""
PDF-Content Linker - Establish links between PDFs and extracted content.

Usage:
    python link_pdf_content.py --scan
    python link_pdf_content.py --link <pdf_id> <content_path>
    python link_pdf_content.py --auto-link
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from manifest_generator import load_manifest, save_manifest
from utils.file_hash import compute_file_hash, generate_pdf_id


# Default paths
CANG_ROOT = Path(__file__).parent.parent
MANIFEST_PATH = CANG_ROOT / "lineage" / "pdf_content_manifest.json"
EXTRACTED_ROOT = CANG_ROOT / "staging" / "pdf_extracted"


def scan_extracted_content() -> Dict[str, List[Path]]:
    """
    Scan for extracted content files.
    
    Returns:
        Dictionary mapping pdf_id to list of version files
    """
    content_files = {}
    
    if not EXTRACTED_ROOT.exists():
        return content_files
    
    for pdf_dir in EXTRACTED_ROOT.iterdir():
        if not pdf_dir.is_dir():
            continue
        
        pdf_id = pdf_dir.name
        version_files = []
        
        for file in pdf_dir.glob("v*_extracted.json"):
            version_files.append(file)
        
        if version_files:
            content_files[pdf_id] = sorted(version_files)
    
    return content_files


def link_content(
    pdf_id: str,
    content_path: Path,
    version: int,
    extractor_version: str = "1.0.0",
    status: str = "success"
) -> bool:
    """
    Link extracted content to a PDF.
    
    Args:
        pdf_id: PDF ID
        content_path: Path to content JSON
        version: Version number
        extractor_version: Extractor version used
        status: Extraction status
    
    Returns:
        True if successful
    """
    manifest = load_manifest()
    
    if pdf_id not in manifest["pdfs"]:
        print(f"PDF not in manifest: {pdf_id}")
        return False
    
    entry = manifest["pdfs"][pdf_id]
    
    # Ensure relative path
    try:
        relative_content_path = str(content_path.relative_to(CANG_ROOT))
    except ValueError:
        relative_content_path = str(content_path)
    
    # Create version entry
    version_entry = {
        "version": version,
        "extracted_at": entry.get("updated_at", ""),
        "extractor_version": extractor_version,
        "content_path": relative_content_path,
        "status": status
    }
    
    # Update versions list
    versions = entry.get("versions", [])
    
    # Remove existing entry for same version
    versions = [v for v in versions if v["version"] != version]
    versions.append(version_entry)
    
    # Keep only 3 most recent
    versions = sorted(versions, key=lambda x: x["version"])[-3:]
    
    entry["versions"] = versions
    entry["latest_version"] = version
    entry["latest_content_path"] = relative_content_path
    entry["status"] = "extracted" if status == "success" else "failed"
    
    save_manifest(manifest)
    print(f"Linked content to {pdf_id} (version {version})")
    return True


def auto_link() -> int:
    """
    Automatically link all found content files to PDFs.
    
    Returns:
        Number of successful links
    """
    manifest = load_manifest()
    content_files = scan_extracted_content()
    
    linked = 0
    
    for pdf_id, files in content_files.items():
        if pdf_id not in manifest["pdfs"]:
            print(f"Warning: Content found for unknown PDF: {pdf_id}")
            continue
        
        for file_path in files:
            # Extract version from filename (v{N}_extracted.json)
            match = re.match(r"v(\d+)_extracted\.json", file_path.name)
            if not match:
                continue
            
            version = int(match.group(1))
            
            # Check if already linked
            entry = manifest["pdfs"][pdf_id]
            existing = [v for v in entry.get("versions", []) if v["version"] == version]
            
            if existing:
                print(f"Already linked: {pdf_id} v{version}")
                continue
            
            # Try to read content to verify it's valid
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                
                # Determine status based on content
                status = "success" if content.get("title") else "failed"
                
                if link_content(pdf_id, file_path, version, status=status):
                    linked += 1
                    
            except json.JSONDecodeError:
                print(f"Invalid JSON: {file_path}")
                link_content(pdf_id, file_path, version, status="failed", 
                           error_message="Invalid JSON format")
            except Exception as e:
                print(f"Error linking {file_path}: {e}")
    
    return linked


def unlink_content(pdf_id: str, version: Optional[int] = None) -> bool:
    """
    Remove content link from a PDF.
    
    Args:
        pdf_id: PDF ID
        version: Specific version to unlink (None for all)
    
    Returns:
        True if successful
    """
    manifest = load_manifest()
    
    if pdf_id not in manifest["pdfs"]:
        print(f"PDF not found: {pdf_id}")
        return False
    
    entry = manifest["pdfs"][pdf_id]
    
    if version is None:
        # Remove all versions
        entry["versions"] = []
        entry["latest_version"] = 0
        entry["latest_content_path"] = None
        entry["status"] = "pending"
        print(f"Unlinked all versions from {pdf_id}")
    else:
        # Remove specific version
        versions = entry.get("versions", [])
        versions = [v for v in versions if v["version"] != version]
        entry["versions"] = versions
        
        # Update latest
        if versions:
            latest = max(versions, key=lambda x: x["version"])
            entry["latest_version"] = latest["version"]
            entry["latest_content_path"] = latest["content_path"]
        else:
            entry["latest_version"] = 0
            entry["latest_content_path"] = None
            entry["status"] = "pending"
        
        print(f"Unlinked version {version} from {pdf_id}")
    
    save_manifest(manifest)
    return True


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PDF-Content Linker"
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scan for extracted content files"
    )
    parser.add_argument(
        "--link",
        metavar=("PDF_ID", "CONTENT_PATH"),
        nargs=2,
        help="Link content to PDF"
    )
    parser.add_argument(
        "--auto-link",
        action="store_true",
        help="Automatically link all found content"
    )
    parser.add_argument(
        "--unlink",
        metavar="PDF_ID",
        help="Unlink content from PDF (use --version for specific version)"
    )
    parser.add_argument(
        "--version",
        type=int,
        help="Specific version number"
    )
    parser.add_argument(
        "--status",
        choices=["success", "failed"],
        default="success",
        help="Extraction status"
    )
    
    args = parser.parse_args()
    
    if args.scan:
        content_files = scan_extracted_content()
        print(f"Found extracted content for {len(content_files)} PDF(s):")
        for pdf_id, files in content_files.items():
            print(f"  {pdf_id}: {len(files)} version(s)")
            for f in files:
                print(f"    - {f.name}")
    
    elif args.link:
        pdf_id, content_path = args.link
        version = args.version or 1
        link_content(pdf_id, Path(content_path), version, status=args.status)
    
    elif args.auto_link:
        linked = auto_link()
        print(f"\nLinked {linked} content file(s)")
    
    elif args.unlink:
        unlink_content(args.unlink, args.version)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

"""
Manifest Generator - Create and manage PDF-content manifest.

Usage:
    python manifest_generator.py --init
    python manifest_generator.py --scan
    python manifest_generator.py --update <pdf_id>
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.file_hash import compute_file_hash, generate_pdf_id
from utils.pdf_info import get_pdf_page_count, scan_pdf_directory


# Default paths
CANG_ROOT = Path(__file__).parent.parent
PDF_ROOT = CANG_ROOT / "raw" / "pdf"
MANIFEST_PATH = CANG_ROOT / "lineage" / "pdf_content_manifest.json"
EXTRACTED_ROOT = CANG_ROOT / "staging" / "pdf_extracted"


def load_manifest() -> Dict:
    """Load existing manifest or create new one."""
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "version": "1.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "pdfs": {}
    }


def save_manifest(manifest: Dict) -> None:
    """Save manifest to file."""
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def get_disease_area_from_path(pdf_path: Path) -> Optional[str]:
    """Extract disease area from PDF path."""
    try:
        # Path structure: raw/pdf/{specialty}/{disease}/file.pdf
        parts = pdf_path.relative_to(PDF_ROOT).parts
        if len(parts) >= 2:
            return parts[1]  # disease area
    except ValueError:
        pass
    return None


def get_category_path_from_path(pdf_path: Path) -> Optional[str]:
    """Extract category path from PDF path."""
    try:
        parts = pdf_path.relative_to(PDF_ROOT).parts
        if len(parts) >= 2:
            specialty = parts[0]
            disease = parts[1]
            return f"文献库/{specialty}/{disease}"
    except ValueError:
        pass
    return None


def scan_and_update_manifest(
    manifest: Dict,
    dry_run: bool = False
) -> Dict:
    """
    Scan PDF directory and update manifest.
    
    Args:
        manifest: Current manifest
        dry_run: If True, don't save changes
    
    Returns:
        Updated manifest
    """
    if not PDF_ROOT.exists():
        print(f"Warning: PDF root not found: {PDF_ROOT}")
        return manifest
    
    # Scan for PDFs
    print(f"Scanning {PDF_ROOT}...")
    pdf_files = scan_pdf_directory(PDF_ROOT)
    print(f"Found {len(pdf_files)} PDF(s)")
    
    # Track changes
    added = 0
    updated = 0
    unchanged = 0
    
    for pdf_path in pdf_files:
        try:
            # Get PDF info
            file_hash = compute_file_hash(pdf_path)
            pdf_id = generate_pdf_id(pdf_path)
            relative_path = str(pdf_path.relative_to(CANG_ROOT))
            
            # Try to get page count
            try:
                total_pages = get_pdf_page_count(pdf_path)
            except Exception:
                total_pages = 0
            
            file_size = pdf_path.stat().st_size
            disease_area = get_disease_area_from_path(pdf_path)
            category_path = get_category_path_from_path(pdf_path)
            
            # Check if already in manifest
            if pdf_id in manifest["pdfs"]:
                existing = manifest["pdfs"][pdf_id]
                
                # Check if file changed
                if existing.get("file_hash") != file_hash:
                    print(f"  Updated: {pdf_path.name} (hash changed)")
                    existing["file_hash"] = file_hash
                    existing["file_size"] = file_size
                    existing["total_pages"] = total_pages
                    updated += 1
                else:
                    unchanged += 1
            else:
                # New entry
                print(f"  Added: {pdf_path.name}")
                manifest["pdfs"][pdf_id] = {
                    "relative_path": relative_path,
                    "file_hash": file_hash,
                    "file_size": file_size,
                    "total_pages": total_pages,
                    "status": "pending",
                    "disease_area": disease_area,
                    "category_path": category_path,
                    "versions": [],
                    "latest_version": 0,
                    "latest_content_path": None
                }
                added += 1
                
        except Exception as e:
            print(f"  Error processing {pdf_path}: {e}")
    
    # Update timestamp
    manifest["generated_at"] = datetime.utcnow().isoformat() + "Z"
    
    print(f"\nSummary:")
    print(f"  Added: {added}")
    print(f"  Updated: {updated}")
    print(f"  Unchanged: {unchanged}")
    print(f"  Total: {len(manifest['pdfs'])}")
    
    if not dry_run:
        save_manifest(manifest)
        print(f"\nManifest saved to: {MANIFEST_PATH}")
    else:
        print("\nDry run - changes not saved")
    
    return manifest


def initialize_manifest(force: bool = False) -> Dict:
    """
    Initialize manifest from scratch.
    
    Args:
        force: If True, overwrite existing manifest
    
    Returns:
        New manifest
    """
    if MANIFEST_PATH.exists() and not force:
        print(f"Manifest already exists at: {MANIFEST_PATH}")
        print("Use --force to overwrite")
        return load_manifest()
    
    print("Initializing new manifest...")
    manifest = {
        "version": "1.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "pdfs": {}
    }
    
    return scan_and_update_manifest(manifest)


def update_pdf_entry(pdf_id: str) -> bool:
    """
    Update a single PDF entry in manifest.
    
    Args:
        pdf_id: PDF ID to update
    
    Returns:
        True if updated, False otherwise
    """
    manifest = load_manifest()
    
    if pdf_id not in manifest["pdfs"]:
        print(f"PDF not found in manifest: {pdf_id}")
        return False
    
    entry = manifest["pdfs"][pdf_id]
    pdf_path = CANG_ROOT / entry["relative_path"]
    
    if not pdf_path.exists():
        print(f"PDF file not found: {pdf_path}")
        return False
    
    try:
        # Update file info
        entry["file_hash"] = compute_file_hash(pdf_path)
        entry["file_size"] = pdf_path.stat().st_size
        try:
            entry["total_pages"] = get_pdf_page_count(pdf_path)
        except Exception:
            pass
        
        save_manifest(manifest)
        print(f"Updated: {pdf_id}")
        return True
        
    except Exception as e:
        print(f"Error updating {pdf_id}: {e}")
        return False


def remove_missing_pdfs(dry_run: bool = False) -> int:
    """
    Remove entries for PDFs that no longer exist.
    
    Args:
        dry_run: If True, don't actually remove
    
    Returns:
        Number of entries removed
    """
    manifest = load_manifest()
    to_remove = []
    
    for pdf_id, entry in manifest["pdfs"].items():
        pdf_path = CANG_ROOT / entry["relative_path"]
        if not pdf_path.exists():
            to_remove.append(pdf_id)
    
    if not dry_run:
        for pdf_id in to_remove:
            del manifest["pdfs"][pdf_id]
        
        if to_remove:
            save_manifest(manifest)
    
    print(f"Removed {len(to_remove)} missing PDF(s)")
    return len(to_remove)


def get_stats() -> Dict:
    """Get manifest statistics."""
    manifest = load_manifest()
    
    total = len(manifest["pdfs"])
    by_status = {}
    by_disease = {}
    with_versions = 0
    
    for entry in manifest["pdfs"].values():
        status = entry.get("status", "unknown")
        by_status[status] = by_status.get(status, 0) + 1
        
        disease = entry.get("disease_area", "unknown")
        by_disease[disease] = by_disease.get(disease, 0) + 1
        
        if entry.get("versions"):
            with_versions += 1
    
    return {
        "total": total,
        "by_status": by_status,
        "by_disease_area": by_disease,
        "with_versions": with_versions,
        "without_versions": total - with_versions
    }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PDF Content Manifest Generator"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize manifest from scratch"
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scan for new PDFs and update manifest"
    )
    parser.add_argument(
        "--update",
        metavar="PDF_ID",
        help="Update specific PDF entry"
    )
    parser.add_argument(
        "--remove-missing",
        action="store_true",
        help="Remove entries for missing PDFs"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show manifest statistics"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite existing manifest"
    )
    
    args = parser.parse_args()
    
    if args.init:
        initialize_manifest(force=args.force)
    
    elif args.scan:
        manifest = load_manifest()
        scan_and_update_manifest(manifest, dry_run=args.dry_run)
    
    elif args.update:
        update_pdf_entry(args.update)
    
    elif args.remove_missing:
        remove_missing_pdfs(dry_run=args.dry_run)
    
    elif args.stats:
        stats = get_stats()
        print("Manifest Statistics:")
        print(f"  Total PDFs: {stats['total']}")
        print(f"  With versions: {stats['with_versions']}")
        print(f"  Without versions: {stats['without_versions']}")
        print("\nBy status:")
        for status, count in stats['by_status'].items():
            print(f"  {status}: {count}")
        print("\nBy disease area:")
        for disease, count in stats['by_disease_area'].items():
            print(f"  {disease}: {count}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

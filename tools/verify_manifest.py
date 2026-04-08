"""
Manifest Verification - Verify manifest integrity and consistency.

Usage:
    python verify_manifest.py
    python verify_manifest.py --fix
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from manifest_generator import load_manifest, save_manifest
from utils.file_hash import compute_file_hash, verify_file_integrity
from utils.pdf_info import is_valid_pdf


# Default paths
CANG_ROOT = Path(__file__).parent.parent
MANIFEST_PATH = CANG_ROOT / "lineage" / "pdf_content_manifest.json"


def verify_entry(pdf_id: str, entry: Dict) -> List[str]:
    """
    Verify a single manifest entry.
    
    Args:
        pdf_id: PDF ID
        entry: Manifest entry
    
    Returns:
        List of issues found
    """
    issues = []
    
    # Check required fields
    required_fields = ["relative_path", "file_hash", "file_size", "total_pages", "status"]
    for field in required_fields:
        if field not in entry:
            issues.append(f"Missing field: {field}")
    
    # Check PDF file exists
    pdf_path = CANG_ROOT / entry.get("relative_path", "")
    if not pdf_path.exists():
        issues.append(f"PDF file not found: {pdf_path}")
    else:
        # Verify hash
        try:
            stored_hash = entry.get("file_hash", "")
            if stored_hash and not verify_file_integrity(pdf_path, stored_hash):
                issues.append(f"Hash mismatch")
        except Exception as e:
            issues.append(f"Hash verification error: {e}")
        
        # Verify PDF validity
        if not is_valid_pdf(pdf_path):
            issues.append(f"Invalid PDF file")
    
    # Check versions
    versions = entry.get("versions", [])
    for version in versions:
        # Check version fields
        if "version" not in version:
            issues.append(f"Version entry missing version number")
            continue
        
        # Check content file exists (if successful)
        if version.get("status") == "success":
            content_path = CANG_ROOT / version.get("content_path", "")
            if not content_path.exists():
                issues.append(f"v{version['version']} content file not found: {content_path}")
            else:
                # Try to parse JSON
                try:
                    with open(content_path, "r", encoding="utf-8") as f:
                        json.load(f)
                except json.JSONDecodeError:
                    issues.append(f"v{version['version']} content file is invalid JSON")
        
        # Check failed versions have error message
        if version.get("status") == "failed" and not version.get("error_message"):
            issues.append(f"v{version['version']} failed but has no error message")
    
    # Check latest_version matches
    if versions:
        latest = max(v["version"] for v in versions)
        if entry.get("latest_version") != latest:
            issues.append(f"latest_version mismatch: {entry.get('latest_version')} != {latest}")
    
    return issues


def verify_manifest(fix: bool = False) -> Tuple[int, int, List[str]]:
    """
    Verify entire manifest.
    
    Args:
        fix: If True, attempt to fix issues
    
    Returns:
        Tuple of (verified_count, issue_count, fixed_issues)
    """
    manifest = load_manifest()
    
    verified = 0
    total_issues = 0
    fixed = []
    to_remove = []
    
    print(f"Verifying {len(manifest['pdfs'])} PDF entries...\n")
    
    for pdf_id, entry in manifest["pdfs"].items():
        issues = verify_entry(pdf_id, entry)
        
        if issues:
            print(f"✗ {pdf_id}:")
            for issue in issues:
                print(f"    - {issue}")
            total_issues += len(issues)
            
            # Check if PDF is missing and should be removed
            pdf_path = CANG_ROOT / entry.get("relative_path", "")
            if not pdf_path.exists() and fix:
                to_remove.append(pdf_id)
                fixed.append(f"Removed missing PDF: {pdf_id}")
                print(f"    [FIXED] Will remove from manifest")
        else:
            verified += 1
    
    # Apply fixes
    if fix and to_remove:
        for pdf_id in to_remove:
            del manifest["pdfs"][pdf_id]
        save_manifest(manifest)
        print(f"\nRemoved {len(to_remove)} missing PDF(s)")
    
    return verified, total_issues, fixed


def check_orphans() -> List[Path]:
    """
    Find extracted content without manifest entries.
    
    Returns:
        List of orphaned content paths
    """
    manifest = load_manifest()
    extracted_root = CANG_ROOT / "staging" / "pdf_extracted"
    
    orphans = []
    
    if not extracted_root.exists():
        return orphans
    
    for pdf_dir in extracted_root.iterdir():
        if not pdf_dir.is_dir():
            continue
        
        pdf_id = pdf_dir.name
        
        if pdf_id not in manifest["pdfs"]:
            orphans.append(pdf_dir)
    
    return orphans


def check_duplicates() -> Dict[str, List[str]]:
    """
    Check for duplicate entries (same hash, different IDs).
    
    Returns:
        Dictionary mapping hash to list of PDF IDs
    """
    manifest = load_manifest()
    
    hash_to_ids: Dict[str, List[str]] = {}
    
    for pdf_id, entry in manifest["pdfs"].items():
        file_hash = entry.get("file_hash", "")
        if file_hash:
            if file_hash not in hash_to_ids:
                hash_to_ids[file_hash] = []
            hash_to_ids[file_hash].append(pdf_id)
    
    # Filter to only duplicates
    return {h: ids for h, ids in hash_to_ids.items() if len(ids) > 1}


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Verify PDF Content Manifest"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to fix issues"
    )
    parser.add_argument(
        "--orphans",
        action="store_true",
        help="Check for orphaned content"
    )
    parser.add_argument(
        "--duplicates",
        action="store_true",
        help="Check for duplicate entries"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run all checks"
    )
    
    args = parser.parse_args()
    
    if args.full or (not args.orphans and not args.duplicates):
        verified, issues, fixed = verify_manifest(fix=args.fix)
        print(f"\nVerification complete:")
        print(f"  Verified: {verified}")
        print(f"  Issues: {issues}")
        if fixed:
            print(f"  Fixed: {len(fixed)}")
    
    if args.full or args.orphans:
        orphans = check_orphans()
        if orphans:
            print(f"\nFound {len(orphans)} orphaned content directory(ies):")
            for orphan in orphans:
                print(f"  - {orphan}")
        else:
            print("\nNo orphaned content found.")
    
    if args.full or args.duplicates:
        duplicates = check_duplicates()
        if duplicates:
            print(f"\nFound {len(duplicates)} duplicate hash(es):")
            for file_hash, pdf_ids in duplicates.items():
                print(f"  Hash: {file_hash[:16]}...")
                for pdf_id in pdf_ids:
                    print(f"    - {pdf_id}")
        else:
            print("\nNo duplicates found.")


if __name__ == "__main__":
    main()

"""
Version Manager - Manage extracted content versions.

Maintains up to 3 versions per PDF with automatic cleanup.
"""

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Default paths
CANG_ROOT = Path(__file__).parent.parent
MANIFEST_PATH = CANG_ROOT / "lineage" / "pdf_content_manifest.json"
EXTRACTED_ROOT = CANG_ROOT / "staging" / "pdf_extracted"

MAX_VERSIONS = 3


def load_manifest() -> Dict:
    """Load manifest from file."""
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "1.0", "generated_at": "", "pdfs": {}}


def save_manifest(manifest: Dict) -> None:
    """Save manifest to file."""
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def get_pdf_dir(pdf_id: str) -> Path:
    """Get directory for PDF extracted content."""
    return EXTRACTED_ROOT / pdf_id


def get_version_path(pdf_id: str, version: int) -> Path:
    """Get path to specific version file."""
    return get_pdf_dir(pdf_id) / f"v{version}_extracted.json"


def get_latest_link_path(pdf_id: str) -> Path:
    """Get path to latest symlink."""
    return get_pdf_dir(pdf_id) / "latest.json"


def read_version_content(pdf_id: str, version: int) -> Optional[Dict]:
    """Read content of a specific version."""
    path = get_version_path(pdf_id, version)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def add_version(
    pdf_id: str,
    content: Dict,
    extractor_version: str = "1.0.0",
    status: str = "success",
    error_message: Optional[str] = None
) -> int:
    """
    Add a new version for a PDF.
    
    Args:
        pdf_id: PDF ID
        content: Extracted content (or None if failed)
        extractor_version: Version of extractor used
        status: "success" or "failed"
        error_message: Error message if failed
    
    Returns:
        New version number
    """
    manifest = load_manifest()
    
    if pdf_id not in manifest["pdfs"]:
        raise ValueError(f"PDF not in manifest: {pdf_id}")
    
    entry = manifest["pdfs"][pdf_id]
    
    # Calculate new version number
    versions = entry.get("versions", [])
    new_version = max([v["version"] for v in versions] + [0]) + 1
    
    # Create directory
    pdf_dir = get_pdf_dir(pdf_id)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    
    # Save content file
    version_path = get_version_path(pdf_id, new_version)
    if content:
        with open(version_path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
    
    # Add version entry
    version_entry = {
        "version": new_version,
        "extracted_at": datetime.utcnow().isoformat() + "Z",
        "extractor_version": extractor_version,
        "content_path": str(version_path.relative_to(CANG_ROOT)),
        "status": status
    }
    if error_message:
        version_entry["error_message"] = error_message
    
    versions.append(version_entry)
    
    # Keep only MAX_VERSIONS most recent
    if len(versions) > MAX_VERSIONS:
        # Remove oldest version files
        removed = versions[:-MAX_VERSIONS]
        for v in removed:
            old_path = get_version_path(pdf_id, v["version"])
            if old_path.exists():
                old_path.unlink()
        # Keep only recent versions
        versions = versions[-MAX_VERSIONS:]
    
    # Update entry
    entry["versions"] = versions
    entry["latest_version"] = new_version
    entry["latest_content_path"] = str(version_path.relative_to(CANG_ROOT))
    entry["status"] = "extracted" if status == "success" else "failed"
    
    # Update symlink
    latest_link = get_latest_link_path(pdf_id)
    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()
    latest_link.symlink_to(version_path.name)
    
    save_manifest(manifest)
    
    return new_version


def rollback_version(pdf_id: str, target_version: int) -> bool:
    """
    Rollback to a specific version.
    
    Args:
        pdf_id: PDF ID
        target_version: Version to rollback to
    
    Returns:
        True if successful
    """
    manifest = load_manifest()
    
    if pdf_id not in manifest["pdfs"]:
        print(f"PDF not found: {pdf_id}")
        return False
    
    entry = manifest["pdfs"][pdf_id]
    versions = entry.get("versions", [])
    
    # Find target version
    target = None
    for v in versions:
        if v["version"] == target_version:
            target = v
            break
    
    if not target:
        print(f"Version {target_version} not found for {pdf_id}")
        return False
    
    if target["status"] != "success":
        print(f"Cannot rollback to failed version {target_version}")
        return False
    
    # Update symlink
    pdf_dir = get_pdf_dir(pdf_id)
    latest_link = pdf_dir / "latest.json"
    version_path = get_version_path(pdf_id, target_version)
    
    if not version_path.exists():
        print(f"Version file not found: {version_path}")
        return False
    
    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()
    latest_link.symlink_to(version_path.name)
    
    # Update manifest
    entry["latest_version"] = target_version
    entry["latest_content_path"] = str(version_path.relative_to(CANG_ROOT))
    
    save_manifest(manifest)
    
    print(f"Rolled back {pdf_id} to version {target_version}")
    return True


def list_versions(pdf_id: str) -> List[Dict]:
    """
    List all versions for a PDF.
    
    Args:
        pdf_id: PDF ID
    
    Returns:
        List of version entries
    """
    manifest = load_manifest()
    
    if pdf_id not in manifest["pdfs"]:
        return []
    
    return manifest["pdfs"][pdf_id].get("versions", [])


def get_latest_version(pdf_id: str) -> Optional[Dict]:
    """
    Get latest version info for a PDF.
    
    Args:
        pdf_id: PDF ID
    
    Returns:
        Latest version entry or None
    """
    manifest = load_manifest()
    
    if pdf_id not in manifest["pdfs"]:
        return None
    
    entry = manifest["pdfs"][pdf_id]
    latest_version = entry.get("latest_version", 0)
    
    for v in entry.get("versions", []):
        if v["version"] == latest_version:
            return v
    
    return None


def cleanup_versions(pdf_id: str, dry_run: bool = False) -> int:
    """
    Clean up old versions, keeping only MAX_VERSIONS.
    
    Args:
        pdf_id: PDF ID
        dry_run: If True, don't actually delete
    
    Returns:
        Number of versions removed
    """
    manifest = load_manifest()
    
    if pdf_id not in manifest["pdfs"]:
        return 0
    
    entry = manifest["pdfs"][pdf_id]
    versions = entry.get("versions", [])
    
    if len(versions) <= MAX_VERSIONS:
        return 0
    
    to_remove = versions[:-MAX_VERSIONS]
    
    if not dry_run:
        for v in to_remove:
            version_path = get_version_path(pdf_id, v["version"])
            if version_path.exists():
                version_path.unlink()
                print(f"Removed: {version_path}")
        
        entry["versions"] = versions[-MAX_VERSIONS:]
        save_manifest(manifest)
    else:
        for v in to_remove:
            print(f"Would remove: v{v['version']}")
    
    return len(to_remove)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PDF Content Version Manager"
    )
    parser.add_argument(
        "--list",
        metavar="PDF_ID",
        help="List versions for a PDF"
    )
    parser.add_argument(
        "--rollback",
        metavar="PDF_ID",
        help="Rollback to version (use with --version)"
    )
    parser.add_argument(
        "--version",
        type=int,
        help="Version number for rollback"
    )
    parser.add_argument(
        "--cleanup",
        metavar="PDF_ID",
        help="Clean up old versions for a PDF"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    
    if args.list:
        versions = list_versions(args.list)
        if not versions:
            print(f"No versions found for: {args.list}")
        else:
            print(f"Versions for {args.list}:")
            for v in versions:
                status = "✓" if v["status"] == "success" else "✗"
                print(f"  {status} v{v['version']}: {v['extracted_at'][:10]} ({v['status']})")
    
    elif args.rollback:
        if not args.version:
            print("Error: --version required for rollback")
            return
        rollback_version(args.rollback, args.version)
    
    elif args.cleanup:
        removed = cleanup_versions(args.cleanup, dry_run=args.dry_run)
        if args.dry_run:
            print(f"Would remove {removed} old version(s)")
        else:
            print(f"Removed {removed} old version(s)")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

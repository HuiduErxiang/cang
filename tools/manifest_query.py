"""
Manifest Query - Query PDF-content relationships.

Usage:
    python manifest_query.py --pdf <pdf_id>
    python manifest_query.py --path <relative_path>
    python manifest_query.py --status <status>
    python manifest_query.py --disease <disease_area>
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional

# Default paths
CANG_ROOT = Path(__file__).parent.parent
MANIFEST_PATH = CANG_ROOT / "lineage" / "pdf_content_manifest.json"


def load_manifest() -> Dict:
    """Load manifest from file."""
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "1.0", "generated_at": "", "pdfs": {}}


def get_by_pdf_id(pdf_id: str) -> Optional[Dict]:
    """Get entry by PDF ID."""
    manifest = load_manifest()
    return manifest["pdfs"].get(pdf_id)


def get_by_path(relative_path: str) -> Optional[Dict]:
    """Get entry by relative path."""
    manifest = load_manifest()
    
    for pdf_id, entry in manifest["pdfs"].items():
        if entry.get("relative_path") == relative_path:
            entry_copy = entry.copy()
            entry_copy["pdf_id"] = pdf_id
            return entry_copy
    
    return None


def get_by_hash(file_hash: str) -> Optional[Dict]:
    """Get entry by file hash."""
    manifest = load_manifest()
    
    for pdf_id, entry in manifest["pdfs"].items():
        if entry.get("file_hash") == file_hash:
            entry_copy = entry.copy()
            entry_copy["pdf_id"] = pdf_id
            return entry_copy
    
    return None


def get_by_status(status: str) -> List[Dict]:
    """Get all entries with given status."""
    manifest = load_manifest()
    results = []
    
    for pdf_id, entry in manifest["pdfs"].items():
        if entry.get("status") == status:
            entry_copy = entry.copy()
            entry_copy["pdf_id"] = pdf_id
            results.append(entry_copy)
    
    return results


def get_by_disease_area(disease_area: str) -> List[Dict]:
    """Get all entries for a disease area."""
    manifest = load_manifest()
    results = []
    
    for pdf_id, entry in manifest["pdfs"].items():
        if entry.get("disease_area") == disease_area:
            entry_copy = entry.copy()
            entry_copy["pdf_id"] = pdf_id
            results.append(entry_copy)
    
    return results


def get_content_path(pdf_id: str, version: Optional[int] = None) -> Optional[str]:
    """
    Get path to extracted content.
    
    Args:
        pdf_id: PDF ID
        version: Specific version (None for latest)
    
    Returns:
        Path to content file or None
    """
    entry = get_by_pdf_id(pdf_id)
    
    if not entry:
        return None
    
    if version is None:
        return entry.get("latest_content_path")
    
    for v in entry.get("versions", []):
        if v["version"] == version:
            return v["content_path"]
    
    return None


def find_by_keyword(keyword: str) -> List[Dict]:
    """
    Search entries by keyword in path or disease area.
    
    Args:
        keyword: Search keyword
    
    Returns:
        Matching entries
    """
    manifest = load_manifest()
    results = []
    keyword_lower = keyword.lower()
    
    for pdf_id, entry in manifest["pdfs"].items():
        match = False
        
        # Check path
        if keyword_lower in entry.get("relative_path", "").lower():
            match = True
        
        # Check disease area
        if keyword_lower in (entry.get("disease_area") or "").lower():
            match = True
        
        # Check category path
        if keyword_lower in (entry.get("category_path") or "").lower():
            match = True
        
        if match:
            entry_copy = entry.copy()
            entry_copy["pdf_id"] = pdf_id
            results.append(entry_copy)
    
    return results


def get_statistics() -> Dict:
    """Get manifest statistics."""
    manifest = load_manifest()
    
    total = len(manifest["pdfs"])
    
    by_status = {}
    by_disease = {}
    version_counts = []
    
    for entry in manifest["pdfs"].values():
        status = entry.get("status", "unknown")
        by_status[status] = by_status.get(status, 0) + 1
        
        disease = entry.get("disease_area") or "unknown"
        by_disease[disease] = by_disease.get(disease, 0) + 1
        
        versions = len(entry.get("versions", []))
        version_counts.append(versions)
    
    return {
        "total_pdfs": total,
        "by_status": by_status,
        "by_disease_area": by_disease,
        "with_versions": sum(1 for v in version_counts if v > 0),
        "without_versions": sum(1 for v in version_counts if v == 0),
        "total_versions": sum(version_counts)
    }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Query PDF Content Manifest"
    )
    parser.add_argument(
        "--pdf",
        metavar="PDF_ID",
        help="Query by PDF ID"
    )
    parser.add_argument(
        "--path",
        metavar="REL_PATH",
        help="Query by relative path"
    )
    parser.add_argument(
        "--hash",
        metavar="HASH",
        help="Query by file hash"
    )
    parser.add_argument(
        "--status",
        metavar="STATUS",
        choices=["pending", "extracting", "extracted", "failed"],
        help="Query by status"
    )
    parser.add_argument(
        "--disease",
        metavar="DISEASE",
        help="Query by disease area"
    )
    parser.add_argument(
        "--search",
        metavar="KEYWORD",
        help="Search by keyword"
    )
    parser.add_argument(
        "--content-path",
        metavar="PDF_ID",
        help="Get content path for PDF (use --version for specific version)"
    )
    parser.add_argument(
        "--version",
        type=int,
        help="Specific version number"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    result = None
    
    if args.pdf:
        result = get_by_pdf_id(args.pdf)
    
    elif args.path:
        result = get_by_path(args.path)
    
    elif args.hash:
        result = get_by_hash(args.hash)
    
    elif args.status:
        result = get_by_status(args.status)
    
    elif args.disease:
        result = get_by_disease_area(args.disease)
    
    elif args.search:
        result = find_by_keyword(args.search)
    
    elif args.content_path:
        result = get_content_path(args.content_path, args.version)
    
    elif args.stats:
        result = get_statistics()
    
    else:
        parser.print_help()
        return
    
    # Output result
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if isinstance(result, list):
            print(f"Found {len(result)} result(s):")
            for item in result:
                if isinstance(item, dict):
                    pdf_id = item.get("pdf_id", "unknown")
                    status = item.get("status", "unknown")
                    path = item.get("relative_path", "unknown")
                    versions = len(item.get("versions", []))
                    print(f"  [{status}] {pdf_id}: {path} ({versions} versions)")
                else:
                    print(f"  {item}")
        elif isinstance(result, dict):
            for key, value in result.items():
                if isinstance(value, dict):
                    print(f"{key}:")
                    for k, v in value.items():
                        print(f"  {k}: {v}")
                else:
                    print(f"{key}: {value}")
        else:
            print(result if result is not None else "Not found")


if __name__ == "__main__":
    main()

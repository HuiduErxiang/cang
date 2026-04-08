"""
PDF Scanner - Scan and catalog PDF files.

Usage:
    python pdf_scanner.py --list
    python pdf_scanner.py --duplicates
    python pdf_scanner.py --validate
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Add utils to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from utils.file_hash import compute_file_hash, find_duplicates, generate_pdf_id
from utils.pdf_info import get_pdf_page_count, get_pdf_metadata, scan_pdf_directory, format_file_size


# Default paths
CANG_ROOT = Path(__file__).parent.parent
PDF_ROOT = CANG_ROOT / "raw" / "pdf"


def scan_all_pdfs() -> List[Path]:
    """Scan for all PDFs in the raw/pdf directory."""
    if not PDF_ROOT.exists():
        print(f"Warning: PDF root not found: {PDF_ROOT}")
        return []
    
    return scan_pdf_directory(PDF_ROOT)


def list_pdfs() -> None:
    """List all PDFs with basic info."""
    pdfs = scan_all_pdfs()
    
    print(f"Found {len(pdfs)} PDF(s):\n")
    
    for pdf in pdfs:
        try:
            metadata = get_pdf_metadata(pdf)
            pages = metadata.get("page_count", "?")
            size = format_file_size(metadata.get("file_size", 0))
            print(f"  {pdf.relative_to(CANG_ROOT)}")
            print(f"    Pages: {pages}, Size: {size}")
        except Exception as e:
            print(f"  {pdf.relative_to(CANG_ROOT)}")
            print(f"    Error: {e}")


def find_duplicate_pdfs() -> Dict[str, List[Path]]:
    """Find duplicate PDFs by hash."""
    pdfs = scan_all_pdfs()
    print(f"Scanning {len(pdfs)} PDF(s) for duplicates...")
    
    return find_duplicates(pdfs)


def validate_pdfs() -> Tuple[int, int]:
    """
    Validate all PDFs.
    
    Returns:
        Tuple of (valid_count, invalid_count)
    """
    pdfs = scan_all_pdfs()
    
    valid = 0
    invalid = 0
    
    print(f"Validating {len(pdfs)} PDF(s):\n")
    
    for pdf in pdfs:
        try:
            # Try to get metadata (this validates the PDF)
            get_pdf_page_count(pdf)
            print(f"  ✓ {pdf.name}")
            valid += 1
        except Exception as e:
            print(f"  ✗ {pdf.name}: {e}")
            invalid += 1
    
    return valid, invalid


def get_directory_stats() -> Dict:
    """Get statistics about PDF directory."""
    pdfs = scan_all_pdfs()
    
    total_size = 0
    total_pages = 0
    by_specialty: Dict[str, int] = {}
    by_disease: Dict[str, int] = {}
    
    for pdf in pdfs:
        try:
            metadata = get_pdf_metadata(pdf)
            total_size += metadata.get("file_size", 0)
            total_pages += metadata.get("page_count", 0)
            
            # Parse path
            try:
                parts = pdf.relative_to(PDF_ROOT).parts
                if len(parts) >= 1:
                    specialty = parts[0]
                    by_specialty[specialty] = by_specialty.get(specialty, 0) + 1
                if len(parts) >= 2:
                    disease = parts[1]
                    by_disease[disease] = by_disease.get(disease, 0) + 1
            except ValueError:
                pass
                
        except Exception:
            pass
    
    return {
        "total_pdfs": len(pdfs),
        "total_size_bytes": total_size,
        "total_size_formatted": format_file_size(total_size),
        "total_pages": total_pages,
        "by_specialty": by_specialty,
        "by_disease": by_disease
    }


def export_catalog(output_file: str) -> None:
    """Export PDF catalog to JSON."""
    pdfs = scan_all_pdfs()
    catalog = []
    
    for pdf in pdfs:
        try:
            metadata = get_pdf_metadata(pdf)
            pdf_id = generate_pdf_id(pdf)
            
            entry = {
                "pdf_id": pdf_id,
                "relative_path": str(pdf.relative_to(CANG_ROOT)),
                "file_name": pdf.name,
                "file_hash": compute_file_hash(pdf),
                "file_size": metadata.get("file_size", 0),
                "page_count": metadata.get("page_count", 0),
            }
            
            # Parse path for categorization
            try:
                parts = pdf.relative_to(PDF_ROOT).parts
                if len(parts) >= 1:
                    entry["specialty"] = parts[0]
                if len(parts) >= 2:
                    entry["disease_area"] = parts[1]
            except ValueError:
                pass
            
            catalog.append(entry)
            
        except Exception as e:
            print(f"Error processing {pdf}: {e}")
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    print(f"Exported {len(catalog)} entries to: {output_path}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PDF Scanner and Catalog Tool"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all PDFs"
    )
    parser.add_argument(
        "--duplicates",
        action="store_true",
        help="Find duplicate PDFs"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate all PDFs"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics"
    )
    parser.add_argument(
        "--export",
        metavar="OUTPUT_FILE",
        help="Export catalog to JSON file"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output stats as JSON"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_pdfs()
    
    elif args.duplicates:
        duplicates = find_duplicate_pdfs()
        if duplicates:
            print(f"\nFound {len(duplicates)} duplicate group(s):")
            for file_hash, paths in duplicates.items():
                print(f"\n  Hash: {file_hash[:16]}...")
                for path in paths:
                    print(f"    - {path}")
        else:
            print("\nNo duplicates found.")
    
    elif args.validate:
        valid, invalid = validate_pdfs()
        print(f"\nSummary: {valid} valid, {invalid} invalid")
    
    elif args.stats:
        stats = get_directory_stats()
        
        if args.json:
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        else:
            print(f"PDF Directory Statistics:")
            print(f"  Total PDFs: {stats['total_pdfs']}")
            print(f"  Total Size: {stats['total_size_formatted']}")
            print(f"  Total Pages: {stats['total_pages']}")
            print(f"\nBy Specialty:")
            for specialty, count in sorted(stats['by_specialty'].items()):
                print(f"  {specialty}: {count}")
            print(f"\nBy Disease Area (top 10):")
            for disease, count in sorted(stats['by_disease'].items(), key=lambda x: -x[1])[:10]:
                print(f"  {disease}: {count}")
    
    elif args.export:
        export_catalog(args.export)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

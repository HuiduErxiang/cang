#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fulltext JSON Splitter
将 fulltext_*.json 拆分为独立文章文件并生成索引

Usage:
    python split_fulltext_json.py [--dry-run]
"""

import json
import os
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
import argparse


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(r"D:\汇度编辑部1")
SOURCE_BASE = BASE_DIR / "藏经阁待入库"
TARGET_BASE = BASE_DIR / "藏经阁" / "staging" / "editorial" / "source_articles"

# Corpus prefix mapping
CORPUS_CONFIG = {
    "dailaoban": {
        "source_file": SOURCE_BASE / "戴老板" / "source_json" / "fulltext_ftdlb.json",
        "target_dir": TARGET_BASE / "dailaoban" / "articles",
        "corpus_prefix": "DBA",
        "source_account": "饭统戴老板",
        "expected_count": 53,
    },
    "chengongzi_yjwyj": {
        "source_file": SOURCE_BASE / "辰公子" / "医界望远镜" / "source_json" / "fulltext_chengongzi_yjwyj.json",
        "target_dir": TARGET_BASE / "chengongzi" / "yjwyj" / "articles",
        "corpus_prefix": "CGZ-YJWYJ",
        "source_account": "医界望远镜",
        "expected_count": 64,
    },
    "chengongzi_ysd": {
        "source_file": SOURCE_BASE / "辰公子" / "药时代" / "source_json" / "fulltext_chengongzi_ysd.json",
        "target_dir": TARGET_BASE / "chengongzi" / "ysd" / "articles",
        "corpus_prefix": "CGZ-YSD",
        "source_account": "药时代",
        "expected_count": 104,
    },
    "kongzhike": {
        "source_file": SOURCE_BASE / "空之客" / "source_json" / "fulltext_kongzhike.json",
        "target_dir": TARGET_BASE / "kongzhike" / "articles",
        "corpus_prefix": "KZK",
        "source_account": "空之客",
        "expected_count": 50,
    },
}


# ============================================================
# Data Classes
# ============================================================

@dataclass
class ArticleMeta:
    """Article metadata for index.json"""
    article_id: str
    title: str
    publish_time: str
    url: str
    author_name: str
    source_account: str
    content_length: int
    status: str
    path: str


@dataclass
class Article:
    """Full article with provenance"""
    article_id: str
    title: str
    publish_time: str
    url: str
    author: str
    content: str
    content_length: int
    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExceptionRecord:
    """Record for skipped/problematic articles"""
    source_index: int
    title: Optional[str]
    reason: str
    original_data: Dict[str, Any]


@dataclass
class BatchResult:
    """Result of processing one corpus"""
    corpus_name: str
    expected: int
    written: int
    skipped: int
    index_count: int
    exceptions_count: int
    errors: List[str] = field(default_factory=list)


# ============================================================
# Utility Functions
# ============================================================

def sanitize_filename(text: str, max_length: int = 50) -> str:
    """
    Sanitize text for use in filename.
    Remove/replace unsafe characters, limit length.
    """
    if not text:
        return "untitled"
    
    # Remove or replace unsafe characters
    sanitized = re.sub(r'[<>:"/\\|?*\n\r\t]', '', text)
    sanitized = re.sub(r'\s+', '_', sanitized)
    sanitized = sanitized.strip('._')
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip('_')
    
    return sanitized or "untitled"


def parse_date(date_str: str) -> Tuple[str, str]:
    """
    Parse date string and return (YYYYMMDD, YYYY-MM-DD).
    Returns ("unknown", "unknown") if parsing fails.
    """
    if not date_str:
        return ("unknown", "unknown")
    
    # Try common formats
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y年%m月%d日",
        "%Y.%m.%d",
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return (dt.strftime("%Y%m%d"), dt.strftime("%Y-%m-%d"))
        except ValueError:
            continue
    
    # Try to extract YYYY-MM-DD pattern
    match = re.search(r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})', date_str)
    if match:
        y, m, d = match.groups()
        return (f"{y}{m.zfill(2)}{d.zfill(2)}", f"{y}-{m.zfill(2)}-{d.zfill(2)}")
    
    return ("unknown", date_str)


def generate_article_id(corpus_prefix: str, date_str: str, seq: int) -> str:
    """
    Generate article ID: {corpus_prefix}-{YYYYMMDD}-{seq4}
    """
    date_part, _ = parse_date(date_str)
    return f"{corpus_prefix}-{date_part}-{seq:04d}"


def generate_filename(article_id: str) -> str:
    """
    Generate filename: {article_id}.json
    """
    return f"{article_id}.json"


# ============================================================
# Processing Functions
# ============================================================

def load_source_json(file_path: Path) -> Tuple[List[Dict], Optional[str]]:
    """
    Load source JSON file.
    Returns (articles_list, error_message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            return (data, None)
        elif isinstance(data, dict) and 'articles' in data:
            return (data['articles'], None)
        else:
            return ([], f"Unexpected JSON structure in {file_path}")
    except json.JSONDecodeError as e:
        return ([], f"JSON parse error in {file_path}: {e}")
    except Exception as e:
        return ([], f"Error reading {file_path}: {e}")


def process_article(
    article_data: Dict,
    index: int,
    corpus_prefix: str,
    source_account: str,
    source_file_name: str,
    source_file_path: str,
) -> Tuple[Optional[Article], Optional[ExceptionRecord]]:
    """
    Process a single article.
    Returns (article, exception_record)
    """
    # Check required fields
    title = article_data.get('title', '').strip()
    content = article_data.get('content', '')
    
    if not title:
        return (None, ExceptionRecord(
            source_index=index,
            title=None,
            reason="Missing title",
            original_data=article_data
        ))
    
    if not content or not content.strip():
        return (None, ExceptionRecord(
            source_index=index,
            title=title,
            reason="Empty content",
            original_data=article_data
        ))
    
    # Extract fields
    date_str = article_data.get('date', '')
    url = article_data.get('url', '')
    author = article_data.get('author', '')
    content_len = article_data.get('content_len', len(content))
    
    # Generate IDs
    date_part, publish_time = parse_date(date_str)
    article_id = generate_article_id(corpus_prefix, date_str, index + 1)
    filename = generate_filename(article_id)
    
    # Build article
    article = Article(
        article_id=article_id,
        title=title,
        publish_time=publish_time,
        url=url,
        author=author,
        content=content,
        content_length=content_len,
        provenance={
            "source_file": source_file_name,
            "source_file_path": str(source_file_path),
            "source_index": index,
            "original_title": title,
            "original_url": url,
            "author_name": author,
            "source_account": source_account,
            "extracted_at": datetime.now().isoformat(),
        }
    )
    
    return (article, None)


def write_article(article: Article, target_dir: Path, dry_run: bool = False) -> bool:
    """
    Write article to JSON file.
    Returns success status.
    """
    filename = generate_filename(article.article_id)
    file_path = target_dir / filename
    
    if dry_run:
        return True
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(article), f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"  ERROR writing {filename}: {e}")
        return False


def write_index(
    articles_meta: List[ArticleMeta],
    target_dir: Path,
    source_file_name: str,
    corpus_prefix: str,
    dry_run: bool = False
) -> bool:
    """
    Write index.json file.
    """
    index_data = {
        "schema_version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "source_file": source_file_name,
        "corpus_prefix": corpus_prefix,
        "article_count": len(articles_meta),
        "articles": [asdict(a) for a in articles_meta]
    }
    
    index_path = target_dir / "index.json"
    
    if dry_run:
        print(f"  [DRY-RUN] Would write index.json with {len(articles_meta)} articles")
        return True
    
    try:
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"  ERROR writing index.json: {e}")
        return False


def write_exceptions(
    exceptions: List[ExceptionRecord],
    target_dir: Path,
    dry_run: bool = False
) -> bool:
    """
    Write exceptions.json file.
    """
    if not exceptions:
        return True
    
    exceptions_data = {
        "generated_at": datetime.now().isoformat(),
        "exception_count": len(exceptions),
        "exceptions": [asdict(e) for e in exceptions]
    }
    
    exceptions_path = target_dir / "exceptions.json"
    
    if dry_run:
        print(f"  [DRY-RUN] Would write exceptions.json with {len(exceptions)} records")
        return True
    
    try:
        with open(exceptions_path, 'w', encoding='utf-8') as f:
            json.dump(exceptions_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"  ERROR writing exceptions.json: {e}")
        return False


# ============================================================
# Batch Processing
# ============================================================

def process_corpus(
    corpus_name: str,
    config: Dict,
    dry_run: bool = False
) -> BatchResult:
    """
    Process one corpus (one source file).
    """
    source_file: Path = config['source_file']
    target_dir: Path = config['target_dir']
    corpus_prefix: str = config['corpus_prefix']
    source_account: str = config['source_account']
    expected_count: int = config['expected_count']
    
    print(f"\n{'='*60}")
    print(f"Processing: {corpus_name}")
    print(f"  Source: {source_file}")
    print(f"  Target: {target_dir}")
    print(f"  Expected: {expected_count} articles")
    print(f"{'='*60}")
    
    result = BatchResult(
        corpus_name=corpus_name,
        expected=expected_count,
        written=0,
        skipped=0,
        index_count=0,
        exceptions_count=0,
        errors=[]
    )
    
    # Check source file exists
    if not source_file.exists():
        result.errors.append(f"Source file not found: {source_file}")
        print(f"  ERROR: Source file not found")
        return result
    
    # Create target directory
    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"  Created directory: {target_dir}")
    else:
        print(f"  [DRY-RUN] Would create: {target_dir}")
    
    # Load source JSON
    articles_data, error = load_source_json(source_file)
    if error:
        result.errors.append(error)
        print(f"  ERROR: {error}")
        return result
    
    print(f"  Loaded {len(articles_data)} articles from source")
    
    # Process each article
    articles_meta: List[ArticleMeta] = []
    exceptions: List[ExceptionRecord] = []
    
    for idx, article_data in enumerate(articles_data):
        article, exception = process_article(
            article_data=article_data,
            index=idx,
            corpus_prefix=corpus_prefix,
            source_account=source_account,
            source_file_name=source_file.name,
            source_file_path=str(source_file),
        )
        
        if exception:
            exceptions.append(exception)
            result.skipped += 1
            continue
        
        if article:
            # Write article file
            success = write_article(article, target_dir, dry_run)
            if success:
                result.written += 1
                
                # Add to index
                articles_meta.append(ArticleMeta(
                    article_id=article.article_id,
                    title=article.title,
                    publish_time=article.publish_time,
                    url=article.url,
                    author_name=article.author,
                    source_account=source_account,
                    content_length=article.content_length,
                    status="active",
                    path=generate_filename(article.article_id)
                ))
            else:
                result.skipped += 1
                result.errors.append(f"Failed to write article {idx}")
    
    # Write index.json
    if articles_meta:
        write_index(articles_meta, target_dir, source_file.name, corpus_prefix, dry_run)
        result.index_count = len(articles_meta)
    
    # Write exceptions.json
    if exceptions:
        write_exceptions(exceptions, target_dir, dry_run)
        result.exceptions_count = len(exceptions)
    
    return result


def verify_results(results: List[BatchResult]) -> Dict[str, Any]:
    """
    Verify all results and generate summary.
    """
    total_expected = sum(r.expected for r in results)
    total_written = sum(r.written for r in results)
    total_skipped = sum(r.skipped for r in results)
    total_index = sum(r.index_count for r in results)
    total_exceptions = sum(r.exceptions_count for r in results)
    
    all_errors = []
    for r in results:
        all_errors.extend(r.errors)
    
    # Check consistency
    consistency_ok = (total_written == total_index)
    
    return {
        "total_expected": total_expected,
        "total_written": total_written,
        "total_skipped": total_skipped,
        "total_index": total_index,
        "total_exceptions": total_exceptions,
        "consistency_check": "PASS" if consistency_ok else "FAIL",
        "errors": all_errors,
    }


def print_summary(results: List[BatchResult], summary: Dict):
    """
    Print execution summary.
    """
    print("\n" + "="*60)
    print("EXECUTION SUMMARY")
    print("="*60)
    
    for r in results:
        status = "[OK]" if r.written == r.expected else "[WARN]"
        print(f"\n{status} {r.corpus_name}")
        print(f"    Expected: {r.expected}")
        print(f"    Written:  {r.written}")
        print(f"    Skipped:  {r.skipped}")
        print(f"    Index:    {r.index_count}")
        print(f"    Exceptions: {r.exceptions_count}")
        if r.errors:
            for e in r.errors:
                print(f"    ERROR: {e}")
    
    print("\n" + "-"*60)
    print("TOTALS")
    print("-"*60)
    print(f"  Expected:   {summary['total_expected']}")
    print(f"  Written:    {summary['total_written']}")
    print(f"  Skipped:    {summary['total_skipped']}")
    print(f"  Index:      {summary['total_index']}")
    print(f"  Exceptions: {summary['total_exceptions']}")
    print(f"  Consistency: {summary['consistency_check']}")
    
    if summary['errors']:
        print(f"\n  ERRORS ({len(summary['errors'])}):")
        for e in summary['errors']:
            print(f"    - {e}")
    
    print("="*60)


# ============================================================
# Main
# ============================================================

def main(dry_run: bool = False):
    """
    Main entry point.
    """
    print("="*60)
    print("Fulltext JSON Splitter")
    print("="*60)
    print(f"Mode: {'DRY-RUN' if dry_run else 'EXECUTE'}")
    print(f"Time: {datetime.now().isoformat()}")
    
    results: List[BatchResult] = []
    
    # Process each corpus
    for corpus_name, config in CORPUS_CONFIG.items():
        result = process_corpus(corpus_name, config, dry_run)
        results.append(result)
    
    # Verify and summarize
    summary = verify_results(results)
    print_summary(results, summary)
    
    # Return exit code
    if summary['consistency_check'] == 'FAIL' or summary['errors']:
        return 1
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split fulltext JSON files into individual articles")
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing files')
    args = parser.parse_args()
    
    exit_code = main(dry_run=args.dry_run)
    exit(exit_code)
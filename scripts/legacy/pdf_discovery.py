#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Discovery and Metadata Extraction Script
藏经阁 PDF 处理链 - ST-2 阶段产物

功能：
1. 批量发现指定目录下的所有 PDF 文件
2. 提取元数据：文件名、路径、size、mtime
3. 记录处理状态和错误归因
4. 输出 JSON 格式结果

Usage:
    python pdf_discovery.py --root <root_dir> [--output <output_dir>]
"""

import os
import sys
import json
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class ProcessStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PDFMetadata:
    """PDF 文件元数据结构"""

    filename: str
    filepath: str
    size_bytes: int
    size_human: str
    mtime: str
    mtime_iso: str
    extension: str
    status: str
    error: Optional[str] = None
    checksum_md5: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class DiscoveryResult:
    """发现结果汇总"""

    root_dir: str
    scan_time: str
    total_files: int
    success_count: int
    failed_count: int
    skipped_count: int
    files: List[Dict]
    errors: List[Dict]


def human_readable_size(size_bytes: int) -> str:
    """将字节数转换为人类可读格式"""
    size = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"


def calculate_md5(filepath: str, chunk_size: int = 8192) -> Optional[str]:
    """计算文件的 MD5 校验和"""
    md5_hash = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    except Exception:
        return None


def extract_metadata(
    filepath: Path, calculate_hash: bool = False
) -> Tuple[Optional[PDFMetadata], Optional[str]]:
    """
    提取单个 PDF 文件的元数据

    Args:
        filepath: PDF 文件路径
        calculate_hash: 是否计算 MD5 校验和

    Returns:
        (PDFMetadata | None, error_message | None)
    """
    try:
        stat = filepath.stat()

        # 验证文件是否可读
        if not os.access(filepath, os.R_OK):
            return None, f"文件不可读: {filepath}"

        # 验证是否为有效 PDF（检查文件头）
        with open(filepath, "rb") as f:
            header = f.read(5)
            if header != b"%PDF-":
                return None, f"无效 PDF 文件头: {filepath}"

        mtime_ts = stat.st_mtime
        mtime_dt = datetime.fromtimestamp(mtime_ts)

        metadata = PDFMetadata(
            filename=filepath.name,
            filepath=str(filepath),
            size_bytes=stat.st_size,
            size_human=human_readable_size(stat.st_size),
            mtime=str(mtime_ts),
            mtime_iso=mtime_dt.isoformat(),
            extension=filepath.suffix.lower(),
            status=ProcessStatus.SUCCESS.value,
            checksum_md5=calculate_md5(str(filepath)) if calculate_hash else None,
        )

        return metadata, None

    except PermissionError as e:
        return None, f"权限错误: {e}"
    except FileNotFoundError as e:
        return None, f"文件不存在: {e}"
    except Exception as e:
        return None, f"未知错误: {type(e).__name__}: {e}"


def discover_pdfs(
    root_dir: str,
    output_dir: Optional[str] = None,
    calculate_hash: bool = False,
    max_files: Optional[int] = None,
) -> DiscoveryResult:
    """
    扫描目录下的所有 PDF 文件并提取元数据

    Args:
        root_dir: 扫描根目录
        output_dir: 输出目录（默认为 root_dir）
        calculate_hash: 是否计算 MD5 校验和
        max_files: 最大处理文件数（用于测试）

    Returns:
        DiscoveryResult 对象
    """
    root_path = Path(root_dir)

    if not root_path.exists():
        raise ValueError(f"根目录不存在: {root_dir}")

    if output_dir is None:
        output_dir = str(root_path / "pdf_metadata")

    scan_time = datetime.now().isoformat()

    # 发现所有 PDF 文件
    pdf_files = list(root_path.rglob("*.pdf"))

    if max_files:
        pdf_files = pdf_files[:max_files]

    results = []
    errors = []
    success_count = 0
    failed_count = 0
    skipped_count = 0

    for pdf_path in pdf_files:
        metadata, error = extract_metadata(pdf_path, calculate_hash)

        if error:
            failed_count += 1
            error_record = {
                "filepath": str(pdf_path),
                "filename": pdf_path.name,
                "error": error,
                "timestamp": datetime.now().isoformat(),
            }
            errors.append(error_record)

            # 也记录到结果中
            results.append(
                {
                    "filename": pdf_path.name,
                    "filepath": str(pdf_path),
                    "status": ProcessStatus.FAILED.value,
                    "error": error,
                }
            )
        else:
            success_count += 1
            if metadata is not None:
                results.append(metadata.to_dict())

    return DiscoveryResult(
        root_dir=str(root_path.absolute()),
        scan_time=scan_time,
        total_files=len(pdf_files),
        success_count=success_count,
        failed_count=failed_count,
        skipped_count=skipped_count,
        files=results,
        errors=errors,
    )


def save_results(result: DiscoveryResult, output_dir: str) -> Dict[str, str]:
    """
    保存结果到文件

    Returns:
        生成的文件路径字典
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 保存完整元数据 JSON
    metadata_file = output_path / f"pdf_metadata_{timestamp}.json"
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(asdict(result), f, ensure_ascii=False, indent=2)

    # 保存错误日志
    error_log_file = output_path / f"pdf_errors_{timestamp}.json"
    with open(error_log_file, "w", encoding="utf-8") as f:
        json.dump(result.errors, f, ensure_ascii=False, indent=2)

    # 保存摘要
    summary_file = output_path / f"pdf_summary_{timestamp}.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(f"PDF Discovery Summary\n")
        f.write(f"{'=' * 50}\n")
        f.write(f"Scan Time: {result.scan_time}\n")
        f.write(f"Root Directory: {result.root_dir}\n")
        f.write(f"Total Files: {result.total_files}\n")
        f.write(f"Success: {result.success_count}\n")
        f.write(f"Failed: {result.failed_count}\n")
        f.write(f"Skipped: {result.skipped_count}\n")
        f.write(f"\nOutput Files:\n")
        f.write(f"  Metadata: {metadata_file}\n")
        f.write(f"  Error Log: {error_log_file}\n")

    return {
        "metadata": str(metadata_file),
        "error_log": str(error_log_file),
        "summary": str(summary_file),
    }


def main():
    parser = argparse.ArgumentParser(
        description="PDF Discovery and Metadata Extraction"
    )
    parser.add_argument(
        "--root", "-r", required=True, help="Root directory to scan for PDFs"
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output directory for results (default: <root>/pdf_metadata)",
    )
    parser.add_argument(
        "--hash", action="store_true", help="Calculate MD5 hash for each file (slower)"
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=None,
        help="Maximum number of files to process (for testing)",
    )

    args = parser.parse_args()

    print(f"开始扫描 PDF 文件...")
    print(f"根目录: {args.root}")

    result = discover_pdfs(
        root_dir=args.root,
        output_dir=args.output,
        calculate_hash=args.hash,
        max_files=args.max_files,
    )

    print(f"\n扫描完成:")
    print(f"  总文件数: {result.total_files}")
    print(f"  成功: {result.success_count}")
    print(f"  失败: {result.failed_count}")

    # 保存结果
    output_dir = args.output or str(Path(args.root) / "pdf_metadata")
    files = save_results(result, output_dir)

    print(f"\n结果已保存:")
    print(f"  元数据: {files['metadata']}")
    print(f"  错误日志: {files['error_log']}")
    print(f"  摘要: {files['summary']}")

    return 0 if result.failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

"""
藏经阁 → 侠客岛 知识发布导出器

将 staging 中的证据和知识资产导出到消费者发布目录。
路径: staging → exporters/xiakedao → publish/current/consumers/xiakedao

用法:
    python -m exporters.xiakedao.exporter
    或在藏经阁目录下: python exporters/xiakedao/exporter.py
"""
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


def get_zangjinge_root() -> Path:
    """推断藏经阁根目录"""
    # 当前文件位于 exporters/xiakedao/exporter.py
    return Path(__file__).resolve().parent.parent.parent


def export_evidence(zangjinge_root: Path, dry_run: bool = False) -> dict:
    """
    将 staging/evidence/rebuilt/*.json 导出到 consumer 目录

    Returns:
        导出报告
    """
    staging_dir = zangjinge_root / "staging" / "evidence" / "rebuilt"
    consumer_dir = zangjinge_root / "publish" / "current" / "consumers" / "xiakedao" / "staging" / "evidence" / "rebuilt"

    report = {
        "exported": [],
        "skipped": [],
        "errors": [],
        "timestamp": datetime.now().isoformat(),
    }

    if not staging_dir.exists():
        report["errors"].append(f"staging 源目录不存在: {staging_dir}")
        return report

    consumer_dir.mkdir(parents=True, exist_ok=True)

    for src_file in sorted(staging_dir.glob("*.json")):
        dst_file = consumer_dir / src_file.name
        try:
            # 验证 JSON 格式
            with open(src_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 检查是否需要更新
            if dst_file.exists():
                with open(dst_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                if data == existing:
                    report["skipped"].append(src_file.name)
                    continue

            if not dry_run:
                shutil.copy2(src_file, dst_file)
            report["exported"].append(src_file.name)
        except json.JSONDecodeError as e:
            report["errors"].append(f"{src_file.name}: JSON 格式错误 - {e}")
        except Exception as e:
            report["errors"].append(f"{src_file.name}: {e}")

    return report


def export_l4_knowledge(zangjinge_root: Path, dry_run: bool = False) -> dict:
    """
    同步 L4 产品知识到 consumer 目录
    """
    source_l4 = zangjinge_root / "l4"
    consumer_l4 = zangjinge_root / "publish" / "current" / "consumers" / "xiakedao" / "l4"

    report = {
        "synced": [],
        "skipped": [],
        "errors": [],
    }

    if not source_l4.exists():
        report["errors"].append(f"L4 源目录不存在: {source_l4}")
        return report

    for product_dir in sorted(source_l4.iterdir()):
        if not product_dir.is_dir():
            continue
        consumer_product = consumer_l4 / product_dir.name
        consumer_product.mkdir(parents=True, exist_ok=True)

        for src_file in sorted(product_dir.rglob("*.json")):
            rel = src_file.relative_to(product_dir)
            dst_file = consumer_product / rel
            try:
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                if dst_file.exists() and src_file.stat().st_mtime <= dst_file.stat().st_mtime:
                    report["skipped"].append(f"{product_dir.name}/{rel}")
                    continue
                if not dry_run:
                    shutil.copy2(src_file, dst_file)
                report["synced"].append(f"{product_dir.name}/{rel}")
            except Exception as e:
                report["errors"].append(f"{product_dir.name}/{rel}: {e}")

    return report


def run_export(dry_run: bool = False) -> dict:
    """执行完整导出"""
    root = get_zangjinge_root()
    print(f"藏经阁根目录: {root}")
    print(f"模式: {'dry-run' if dry_run else '实际执行'}")
    print()

    evidence_report = export_evidence(root, dry_run)
    print(f"[Evidence] 导出: {len(evidence_report['exported'])}, "
          f"跳过: {len(evidence_report['skipped'])}, "
          f"错误: {len(evidence_report['errors'])}")
    for f in evidence_report["exported"]:
        print(f"  + {f}")
    for e in evidence_report["errors"]:
        print(f"  ! {e}")

    l4_report = export_l4_knowledge(root, dry_run)
    print(f"[L4] 同步: {len(l4_report['synced'])}, "
          f"跳过: {len(l4_report['skipped'])}, "
          f"错误: {len(l4_report['errors'])}")
    for f in l4_report["synced"]:
        print(f"  + {f}")

    return {
        "evidence": evidence_report,
        "l4": l4_report,
        "dry_run": dry_run,
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    run_export(dry_run=dry)

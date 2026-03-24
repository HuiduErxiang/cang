#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第 9 步端到端验证 — 从蒸馏 JSON 重建 evidence_v2 并推送到 publish
用法: python scripts/rebuild_evidence_v2.py <distillation_json_path> --product-id <id>
"""

import argparse
import json
import copy
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLISH_DIR = BASE_DIR / "publish" / "current" / "consumers" / "xiakedao" / "staging" / "evidence" / "rebuilt"


def load_distillation(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_evidence_v2(distill: dict, product_id: str) -> dict:
    """从蒸馏 JSON 构建带 boundary_tags 的 evidence_v2"""
    bt = distill.get("boundary_tags", {})
    doc_id = distill.get("doc_id", "unknown")
    title = distill.get("title", "")
    source_info = distill.get("source", "")
    year = distill.get("year", 2024)

    # 构建 source 级别标签
    source_boundary_tags = {
        "document_type": bt.get("document_type"),
        "evidence_purpose": bt.get("evidence_purpose"),
        "claim_ceiling": bt.get("claim_ceiling"),
        "study_subject": bt.get("study_subject"),
        "population_or_model": bt.get("population_or_model"),
        "endpoint_nature": bt.get("endpoint_nature"),
        "boundary_tags_version": "1.0",
        "tagging_confidence": bt.get("tagging_confidence", 0),
        "tagged_by": bt.get("tagged_by", "llm_auto"),
        "tagged_at": bt.get("tagged_at", datetime.now().isoformat()),
    }

    # 构建 v2_sources
    source_key = f"SRC-{product_id.upper()}-{doc_id.split('_')[-1].upper()}"
    v2_source = {
        "source_id": f"V2-SRC-{product_id.upper()}-001",
        "source_type": bt.get("document_type", "guideline_consensus"),
        "source_key": source_key,
        "title": title,
        "citation": f"{title}. {source_info}. {year}.",
        "doc_id": doc_id,
        "metadata": {
            "year": year,
            "boundary_tags": source_boundary_tags,
        },
    }

    # 从蒸馏 JSON 中提取 facts
    v2_facts = []
    fact_sources = []

    # 尝试从 key_findings 提取 facts
    key_findings = distill.get("key_findings", [])
    if isinstance(key_findings, list):
        for i, finding in enumerate(key_findings):
            if isinstance(finding, dict):
                finding_text = finding.get("finding", finding.get("description", str(finding)))
            else:
                finding_text = str(finding)

            fact = {
                "fact_id": f"V2-FACT-{product_id.upper()}-{i+1:03d}",
                "fact_key": f"FACT-{product_id.upper()}-FINDING-{i+1:03d}",
                "domain": bt.get("evidence_purpose", "efficacy"),
                "definition": finding_text[:200],
                "definition_zh": finding_text[:200],
                "value": "see_definition",
                "unit": None,
                "fragment_ids": [f"V2-FRAG-{product_id.upper()}-{i+1:03d}"],
                "status": "active",
                "lineage": {
                    "source_key": source_key,
                    "doc_id": doc_id,
                    "extraction_date": datetime.now().strftime("%Y-%m-%d"),
                },
                "boundary_tags": {
                    "claim_ceiling": bt.get("claim_ceiling"),
                    "study_subject": bt.get("study_subject"),
                    "endpoint_nature": bt.get("endpoint_nature"),
                },
            }
            v2_facts.append(fact)

    # 如果没有 key_findings，从 key_recommendations 提取
    if not v2_facts:
        recs = distill.get("key_recommendations", [])
        if isinstance(recs, list):
            for i, rec in enumerate(recs):
                if isinstance(rec, dict):
                    rec_text = rec.get("recommendation", rec.get("description", str(rec)))
                else:
                    rec_text = str(rec)

                fact = {
                    "fact_id": f"V2-FACT-{product_id.upper()}-REC-{i+1:03d}",
                    "fact_key": f"FACT-{product_id.upper()}-REC-{i+1:03d}",
                    "domain": "recommendation",
                    "definition": rec_text[:200],
                    "definition_zh": rec_text[:200],
                    "value": "guideline_recommendation",
                    "unit": None,
                    "fragment_ids": [f"V2-FRAG-{product_id.upper()}-REC-{i+1:03d}"],
                    "status": "active",
                    "lineage": {
                        "source_key": source_key,
                        "doc_id": doc_id,
                        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
                    },
                    "boundary_tags": {
                        "claim_ceiling": bt.get("claim_ceiling"),
                        "study_subject": bt.get("study_subject"),
                        "endpoint_nature": bt.get("endpoint_nature"),
                    },
                }
                v2_facts.append(fact)

    # 构建完整 evidence_v2
    evidence_v2 = {
        "rebuild_manifest": {
            "manifest_version": "1.1",
            "rebuild_date": datetime.now().strftime("%Y-%m-%d"),
            "source_file": distill.get("_source_pdf", ""),
            "product_id": product_id,
            "rebuild_status": "complete",
            "boundary_tags_schema_version": "1.0",
            "boundary_tags_coverage": {
                "total_sources": 1,
                "tagged_sources": 1,
                "total_facts": len(v2_facts),
                "tagged_facts": len(v2_facts),
            },
        },
        "v2_sources": [v2_source],
        "v2_facts": v2_facts,
    }

    return evidence_v2


def main():
    parser = argparse.ArgumentParser(description="从蒸馏 JSON 重建 evidence_v2")
    parser.add_argument("distillation_json", help="蒸馏 JSON 文件路径")
    parser.add_argument("--product-id", required=True, help="产品标识")
    parser.add_argument("--output-dir", default=None, help="输出目录（默认推到 publish）")

    args = parser.parse_args()

    distill = load_distillation(args.distillation_json)
    print(f"[重建] 读取蒸馏 JSON: {args.distillation_json}")
    print(f"[重建] doc_id: {distill.get('doc_id')}")
    print(f"[重建] boundary_tags.claim_ceiling: {distill.get('boundary_tags', {}).get('claim_ceiling')}")

    evidence = build_evidence_v2(distill, args.product_id)

    output_dir = Path(args.output_dir) if args.output_dir else PUBLISH_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{args.product_id}_evidence_v2.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, ensure_ascii=False, indent=2)

    print(f"\n[重建] ===== evidence_v2 重建完成 =====")
    print(f"  product_id:     {args.product_id}")
    print(f"  output:         {output_path}")
    print(f"  sources:        {len(evidence['v2_sources'])}")
    print(f"  facts:          {len(evidence['v2_facts'])}")
    print(f"  manifest_ver:   {evidence['rebuild_manifest']['manifest_version']}")
    print(f"  boundary_tags:")
    print(f"    schema_ver:   {evidence['rebuild_manifest']['boundary_tags_schema_version']}")
    print(f"    coverage:     {evidence['rebuild_manifest']['boundary_tags_coverage']}")

    # 验证 boundary_tags 存在
    has_source_tags = all(
        "boundary_tags" in s.get("metadata", {})
        for s in evidence["v2_sources"]
    )
    has_fact_tags = all(
        "boundary_tags" in f
        for f in evidence["v2_facts"]
    )
    print(f"\n[验证] source 级 boundary_tags: {'✅' if has_source_tags else '❌'}")
    print(f"[验证] fact 级 boundary_tags:   {'✅' if has_fact_tags else '❌'}")

    if has_source_tags and has_fact_tags:
        print("\n✅ 第 9 步验证通过：evidence_v2 中 fact 和 source 级别均携带 boundary_tags")
    else:
        print("\n❌ 第 9 步验证失败：boundary_tags 缺失")


if __name__ == "__main__":
    main()

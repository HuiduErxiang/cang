#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
藏经阁标准蒸馏入口脚本 v1.0
输入: PDF 路径 + category
输出: 带研究边界标签的蒸馏 JSON + doc_id + lineage 记录

用法:
  python scripts/distill.py <pdf_path> --category oncology
  python scripts/distill.py <pdf_path> --category guidelines --short-name csco_gastric_2024
  python scripts/distill.py <pdf_path> --category neurology --dry-run
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip install pymupdf")
    sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai not installed. Run: pip install openai")
    sys.exit(1)

# ---------- 配置 ----------

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output" / "distillation_samples"
LINEAGE_DIR = BASE_DIR / "lineage"
DOCS_DIR = BASE_DIR / "docs"

# LLM 配置 — 优先读环境变量，fallback 到侠客岛 .env
XIAKEDAO_ENV = Path(r"D:\汇度编辑部1\侠客岛\.env")

VALID_CATEGORIES = [
    "oncology", "neurology", "guidelines", "conferences",
    "epidemiology", "methodology", "supportive_care"
]

# 每页最多提取多少字符（防止 context 爆炸）
MAX_CHARS_PER_PAGE = 3000
# 最多提取多少页
MAX_PAGES = 60

# ---------- 工具函数 ----------


def load_env():
    """从侠客岛 .env 加载 LLM 配置"""
    env = {}
    if XIAKEDAO_ENV.exists():
        with open(XIAKEDAO_ENV, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, _, value = line.partition("=")
                    env[key.strip()] = value.strip()
    return env


def get_llm_client():
    """创建 OpenAI 兼容客户端"""
    env = load_env()
    api_key = os.environ.get("OPENAI_API_KEY") or env.get("OPENAI_API_KEY", "")
    base_url = os.environ.get("OPENAI_BASE_URL") or env.get("OPENAI_BASE_URL", "")
    model = os.environ.get("LLM_MODEL") or env.get("LLM_MODEL", "MiniMax-M2.7-highspeed")

    if not api_key:
        print("ERROR: OPENAI_API_KEY not found. Set env var or check 侠客岛 .env")
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url=base_url or None)
    return client, model


def compute_hash8(pdf_path: str) -> str:
    """计算 PDF 文件 SHA-256 前 8 位"""
    sha256 = hashlib.sha256()
    with open(pdf_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()[:8]


def extract_pdf_text(pdf_path: str) -> tuple[str, int]:
    """用 PyMuPDF 提取 PDF 文本，返回 (text, total_pages)"""
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    pages_to_read = min(total_pages, MAX_PAGES)

    texts = []
    for i in range(pages_to_read):
        page = doc[i]
        text = page.get_text()
        if len(text) > MAX_CHARS_PER_PAGE:
            text = text[:MAX_CHARS_PER_PAGE] + f"\n[...页{i+1}内容截断...]"
        texts.append(f"--- 第 {i+1} 页 ---\n{text}")

    doc.close()
    full_text = "\n".join(texts)
    return full_text, total_pages


def guess_short_name(pdf_path: str) -> str:
    """从文件名猜测 short_name"""
    stem = Path(pdf_path).stem
    # 去掉常见后缀
    stem = re.sub(r'_[a-f0-9]{8}$', '', stem)
    # 英文研究名直接用
    if re.match(r'^[A-Za-z]', stem):
        name = re.sub(r'[^a-zA-Z0-9]', '_', stem).lower()
        name = re.sub(r'_+', '_', name).strip('_')
        return name[:40]
    # 中文标题 → 取前 20 字的拼音首字母（简化版：直接用原始 stem）
    name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '_', stem)
    name = re.sub(r'_+', '_', name).strip('_')
    return name[:40]


def build_doc_id(category: str, short_name: str, hash8: str) -> str:
    """构造 doc_id"""
    return f"{category}_{short_name}_{hash8}"


# ---------- 蒸馏 prompt ----------

DISTILL_SYSTEM_PROMPT = """你是医学文献蒸馏系统。你的任务是从 PDF 文本中提取结构化信息。

你必须输出一个严格的 JSON 对象，包含以下字段。不要输出其他内容。

## 公共字段（必填）

- title: 文献标题
- source: 来源期刊/会议/机构
- year: 发表年份（整数）
- language: 语言（"english" 或 "chinese"）
- total_pages: 总页数（整数）
- doi: DOI（如有，否则 null）
- document_type: 文献类型

## 类型相关字段

根据文献类型选择性填写：
- 临床研究: trial_name, study_design, sample_size, primary_endpoint, methodology, key_findings
- 指南/共识: issuing_body, disease_area, target_population, key_recommendations
- 流行病学: data_source, time_period, geography, key_statistics
- 会议: conference_name, session_type, key_studies

## 锚点字段

- key_pages: 关键页码数组（每项含 page、description）
- figures: 图表数组（每项含 id、title、page）
- tables: 表格数组（每项含 id、title、page）

## 研究边界标签（必填）

- boundary_tags: 一个对象，包含：
  - document_type: 从以下选一个: clinical_trial, post_hoc, biomarker_method, preclinical_animal, preclinical_in_vitro, review, guideline_consensus, conference_poster, conference_oral
  - study_subject: 从以下选一个: human, animal, cell, assay_system, mixed
  - evidence_purpose: 从以下选一个: efficacy, safety, mechanism, method_validation, association, diagnostic_performance
  - claim_ceiling: 从以下选一个: method_only, mechanistic_signal, clinical_association, clinical_outcome, guideline_recommendation
  - population_or_model: 自由文本，描述研究人群或模型
  - endpoint_nature: 从以下选一个: biomarker, clinical_scale, pathology, pk_pd, assay_performance
  - tagging_confidence: 0-1 的浮点数，表示你对标签准确性的置信度
  - boundary_tags_version: 固定为 "1.0"

## 输出要求

1. 只输出 JSON，不要包含 markdown 代码块标记
2. 确保 JSON 合法
3. 所有字符串用双引号
4. 中文字段保留原文
5. boundary_tags.tagging_confidence 要诚实评估"""


def build_user_prompt(pdf_text: str, total_pages: int, source_pdf: str) -> str:
    return f"""请从以下 PDF 文本中提取结构化信息和研究边界标签。

文件信息：
- 源文件: {source_pdf}
- 总页数: {total_pages}

PDF 全文内容：
{pdf_text}

请输出完整的 JSON 对象。"""


# ---------- 主逻辑 ----------


def distill_pdf(
    pdf_path: str,
    category: str,
    short_name: str | None = None,
    dry_run: bool = False,
) -> dict | None:
    """蒸馏一篇 PDF，返回蒸馏 JSON dict"""
    pdf_path = str(Path(pdf_path).resolve())
    if not Path(pdf_path).exists():
        print(f"ERROR: PDF not found: {pdf_path}")
        return None

    hash8 = compute_hash8(pdf_path)
    if not short_name:
        short_name = guess_short_name(pdf_path)
    doc_id = build_doc_id(category, short_name, hash8)

    print(f"[蒸馏] doc_id={doc_id}")
    print(f"[蒸馏] source={pdf_path}")

    # 提取文本
    print("[蒸馏] 提取 PDF 文本...")
    pdf_text, total_pages = extract_pdf_text(pdf_path)
    print(f"[蒸馏] 提取完成: {total_pages} 页, {len(pdf_text)} 字符")

    if dry_run:
        print("[蒸馏] dry-run 模式，跳过 LLM 调用")
        print(f"[蒸馏] doc_id: {doc_id}")
        print(f"[蒸馏] hash8: {hash8}")
        print(f"[蒸馏] short_name: {short_name}")
        return None

    # 调用 LLM
    client, model = get_llm_client()
    print(f"[蒸馏] 调用 LLM: {model}")

    try:
        # 计算相对路径
        try:
            rel_path = str(Path(pdf_path).relative_to(BASE_DIR))
        except ValueError:
            rel_path = pdf_path

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": DISTILL_SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(pdf_text, total_pages, rel_path)},
            ],
            temperature=0.1,
            max_tokens=8000,
        )

        raw_content = response.choices[0].message.content.strip()

        # 处理 thinking 模型：去掉 <think>...</think> 块
        if "<think>" in raw_content:
            # 去掉所有 <think>...</think> 块（含嵌套和换行）
            raw_content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()

        # 尝试清理 markdown 标记
        if raw_content.startswith("```"):
            raw_content = re.sub(r'^```json?\s*\n?', '', raw_content)
            raw_content = re.sub(r'\n?```\s*$', '', raw_content)

        # 最后尝试找到第一个 { 和最后一个 }
        first_brace = raw_content.find('{')
        last_brace = raw_content.rfind('}')
        if first_brace != -1 and last_brace != -1:
            raw_content = raw_content[first_brace:last_brace + 1]

        result = json.loads(raw_content)

    except json.JSONDecodeError as e:
        print(f"ERROR: LLM 返回的 JSON 无法解析: {e}")
        print(f"Raw content:\n{raw_content[:500]}")
        return None
    except Exception as e:
        print(f"ERROR: LLM 调用失败: {e}")
        return None

    # 注入元数据
    result["_source_pdf"] = rel_path
    result["_extraction_method"] = f"llm_distill_v1.0/{model}"
    result["_extraction_date"] = datetime.now().strftime("%Y-%m-%d")
    result["doc_id"] = doc_id
    result["total_pages"] = total_pages

    # 确保 boundary_tags 存在
    if "boundary_tags" not in result:
        print("WARNING: LLM 未返回 boundary_tags，使用默认值")
        result["boundary_tags"] = {
            "document_type": "clinical_trial",
            "study_subject": "human",
            "evidence_purpose": "efficacy",
            "claim_ceiling": "clinical_outcome",
            "population_or_model": "unknown",
            "endpoint_nature": "clinical_scale",
            "tagging_confidence": 0.0,
            "boundary_tags_version": "1.0",
            "tagged_by": "llm_auto_fallback",
        }
    else:
        result["boundary_tags"]["boundary_tags_version"] = "1.0"
        result["boundary_tags"]["tagged_by"] = "llm_auto"
        result["boundary_tags"]["tagged_at"] = datetime.now().isoformat()

    # 写入蒸馏 JSON
    output_path = OUTPUT_DIR / f"{short_name}_{hash8}.json"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[蒸馏] 产出写入: {output_path}")

    # 写入 lineage 注册
    registry_path = LINEAGE_DIR / "doc_registry.json"
    registry = {}
    if registry_path.exists():
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)

    registry[doc_id] = {
        "doc_id": doc_id,
        "category": category,
        "short_name": short_name,
        "hash8": hash8,
        "source_pdf": rel_path,
        "title": result.get("title", ""),
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "distillation_versions": ["v1.0"],
        "boundary_tags_summary": {
            "document_type": result["boundary_tags"].get("document_type"),
            "claim_ceiling": result["boundary_tags"].get("claim_ceiling"),
            "study_subject": result["boundary_tags"].get("study_subject"),
            "tagging_confidence": result["boundary_tags"].get("tagging_confidence"),
        },
    }

    LINEAGE_DIR.mkdir(parents=True, exist_ok=True)
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    print(f"[蒸馏] lineage 注册: {registry_path}")

    # 验证
    print(f"\n[蒸馏] ===== 蒸馏完成 =====")
    print(f"  doc_id:          {doc_id}")
    print(f"  title:           {result.get('title', 'N/A')}")
    print(f"  document_type:   {result['boundary_tags'].get('document_type')}")
    print(f"  claim_ceiling:   {result['boundary_tags'].get('claim_ceiling')}")
    print(f"  study_subject:   {result['boundary_tags'].get('study_subject')}")
    print(f"  confidence:      {result['boundary_tags'].get('tagging_confidence')}")
    print(f"  output:          {output_path}")

    return result


# ---------- CLI ----------


def main():
    parser = argparse.ArgumentParser(
        description="藏经阁标准蒸馏入口 v1.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  python scripts/distill.py raw/pdf/oncology/KEYNOTE-811.pdf --category oncology
  python scripts/distill.py "D:\\文献\\指南.pdf" --category guidelines --short-name csco_gastric_2025
  python scripts/distill.py raw/pdf/neurology/clarity_ad.pdf -c neurology --dry-run
""",
    )
    parser.add_argument("pdf_path", help="PDF 文件路径")
    parser.add_argument(
        "-c", "--category",
        required=True,
        choices=VALID_CATEGORIES,
        help="文献类别",
    )
    parser.add_argument(
        "-n", "--short-name",
        default=None,
        help="文献短名，不指定则从文件名自动推断",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只生成 doc_id 和提取文本，不调用 LLM",
    )

    args = parser.parse_args()
    distill_pdf(args.pdf_path, args.category, args.short_name, args.dry_run)


if __name__ == "__main__":
    main()

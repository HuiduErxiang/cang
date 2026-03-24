#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Distillation script for chengongzi/yjwyj articles
Processes 63 articles and generates distilled JSON files
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = BASE_DIR / "staging" / "editorial" / "source_articles" / "chengongzi" / "yjwyj" / "articles"
OUTPUT_DIR = BASE_DIR / "staging" / "editorial" / "distilled_articles" / "chengongzi" / "yjwyj"
INDEX_FILE = SOURCE_DIR / "index.json"

# Rhetoric device patterns for chengongzi style
RHETORIC_PATTERNS = {
    "contrast_juxtaposition": [
        r"然而[，,]?",
        r"但是[，,]?",
        r"与之形成鲜明对比",
        r"同源不同命",
    ],
    "rhetorical_question": [
        r"[？！]+$",
        r"为何.+[？?]",
        r"怎么.+[？?]",
        r"难道.+[？?]",
    ],
    "colloquial_emphasis": [
        r"真是[。，]",
        r"不得不说",
        r"不得不说",
        r"这下",
        r"可谓",
    ],
    "data_citation": [
        r"\d+\.?\d*%",
        r"mOS[^\d]*\d+",
        r"mPFS[^\d]*\d+",
        r"ORR[^\d]*\d+",
        r"HR[=＝][\d.]+",
    ],
    "analogy_metaphor": [
        r"好比",
        r"就像",
        r"如同",
        r"这就像",
        r"好比说",
    ],
    "concession_transition": [
        r"虽然.+但是",
        r"尽管.+还是",
        r"即便.+也",
    ],
}

# Topic classification keywords
TOPIC_KEYWORDS = {
    "肿瘤免疫": ["PD-1", "PD-L1", "免疫", "checkpoint", "免疫治疗", "IO"],
    "靶向治疗": ["TKI", "靶向", "EGFR", "ALK", "HER2", "突变", "抑制剂"],
    "ADC药物": ["ADC", "T-DXd", "DS-8201", "抗体偶联"],
    "阿尔茨海默": ["阿尔茨海默", "AD", "Aβ", "淀粉样", "仑卡奈", "Donanemab"],
    "胃癌": ["胃癌", "胃", "GC"],
    "肺癌": ["肺癌", "NSCLC", "SCLC", "肺"],
    "乳腺癌": ["乳腺癌", "BC", "TNBC"],
    "临床研究": ["临床", "试验", "研究", "ORR", "OS", "PFS", "HR"],
    "监管审批": ["FDA", "NMPA", "获批", "批准", "审批", "EMA"],
    "指南更新": ["指南", "CSCO", "NCCN", "推荐"],
}

def extract_topic(title: str, content: str) -> tuple:
    """Extract topic and subtopic from title and content"""
    text = (title + " " + content[:1000]).lower()
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text:
                # Determine subtopic
                if "获批" in text or "批准" in text or "FDA" in text:
                    return topic, "监管动态"
                elif "临床" in text or "试验" in text:
                    return topic, "临床研究"
                elif "指南" in text:
                    return topic, "指南解读"
                else:
                    return topic, "前沿进展"
    
    return "医药前沿", "行业动态"

def extract_rhetoric_devices(content: str) -> list:
    """Extract rhetoric devices from content"""
    devices = []
    
    for device_type, patterns in RHETORIC_PATTERNS.items():
        examples = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            if matches:
                examples.extend(matches[:2])
        
        if examples:
            devices.append({
                "device_type": device_type,
                "pattern": RHETORIC_PATTERNS[device_type][0],
                "count": len(examples),
                "examples": examples[:3]
            })
    
    return devices[:5]  # Top 5 devices

def extract_narrative_frame(content: str, title: str) -> dict:
    """Extract narrative frame from content"""
    frame_type = "analytical_commentary"
    key_elements = []
    
    # Detect frame type
    if "！" in title or "突发" in title or "重磅" in title:
        frame_type = "breaking_news_analysis"
        key_elements.append("新闻驱动")
    elif "？" in title or "为何" in title or "怎么" in title:
        frame_type = "question_driven_inquiry"
        key_elements.append("问题导向")
    elif "指南" in title or "CSCO" in title:
        frame_type = "guideline_interpretation"
        key_elements.append("指南解读")
    elif "获批" in title or "批准" in title:
        frame_type = "regulatory_analysis"
        key_elements.append("监管分析")
    
    # Add content-based elements
    if "对比" in content or "vs" in content.lower():
        key_elements.append("对比分析")
    if re.search(r"\d+\.?\d*%", content):
        key_elements.append("数据支撑")
    if "FDA" in content or "EMA" in content:
        key_elements.append("国际视角")
    
    return {
        "frame_type": frame_type,
        "key_elements": key_elements or ["专业分析"]
    }

def extract_argument_skeleton(content: str, title: str) -> dict:
    """Extract argument skeleton from content"""
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    
    # Main claim from title and first paragraph
    main_claim = title
    if paragraphs:
        first_para = paragraphs[0][:200]
        if first_para:
            main_claim = first_para
    
    # Supporting points
    supporting_points = []
    for p in paragraphs[1:4]:  # Next 3 paragraphs
        if len(p) > 50 and "来源" not in p:
            supporting_points.append(p[:100] + "..." if len(p) > 100 else p)
    
    # Conclusion hook - look for conclusion markers
    conclusion_hook = ""
    conclusion_markers = ["总之", "综上所述", "可以说", "不难看出", "可见"]
    for marker in conclusion_markers:
        if marker in content:
            idx = content.rfind(marker)
            conclusion_hook = content[idx:idx+100]
            break
    
    return {
        "main_claim": main_claim[:300] if len(main_claim) > 300 else main_claim,
        "supporting_points": supporting_points[:3],
        "conclusion_hook": conclusion_hook[:150] if conclusion_hook else ""
    }

def extract_reusable_fragments(content: str) -> list:
    """Extract reusable expression fragments"""
    fragments = []
    
    # Pattern 1: Colloquial openings
    colloquial_patterns = [
        r"(真是[^。！？]+[。！？])",
        r"(不得不说[^。！？]+[。！？])",
        r"(这下[^。！？]+[。！？])",
    ]
    
    for pattern in colloquial_patterns:
        matches = re.findall(pattern, content)
        for m in matches:
            if 10 < len(m) < 80:
                fragments.append({
                    "fragment": m,
                    "context": "口语化开头/过渡",
                    "reusability_score": 4
                })
    
    # Pattern 2: Data-driven statements
    data_patterns = [
        r"([^。！？]*\d+\.?\d*%[^。！？]*[。！？])",
        r"([^。！？]*mOS[^。！？]*[。！？])",
        r"([^。！？]*HR[=＝][\d.]+[^。！？]*[。！？])",
    ]
    
    for pattern in data_patterns:
        matches = re.findall(pattern, content)
        for m in matches:
            if 20 < len(m) < 100:
                fragments.append({
                    "fragment": m,
                    "context": "数据驱动陈述",
                    "reusability_score": 5
                })
    
    # Pattern 3: Contrast statements
    contrast_patterns = [
        r"(然而[^。！？]+[。！？])",
        r"(与之形成鲜明对比[^。！？]+[。！？])",
    ]
    
    for pattern in contrast_patterns:
        matches = re.findall(pattern, content)
        for m in matches:
            if 15 < len(m) < 100:
                fragments.append({
                    "fragment": m,
                    "context": "对比转折",
                    "reusability_score": 5
                })
    
    # Deduplicate and return top 5
    seen = set()
    unique_fragments = []
    for f in fragments:
        if f["fragment"] not in seen:
            seen.add(f["fragment"])
            unique_fragments.append(f)
    
    return unique_fragments[:5]

def extract_tone_signals(content: str) -> dict:
    """Extract tone and syntax signals"""
    tone_markers = []
    syntax_patterns = []
    
    # Tone markers
    if "！" in content:
        tone_markers.append("感叹语气")
    if "？" in content:
        tone_markers.append("疑问语气")
    if any(w in content for w in ["真是", "可谓", "这下"]):
        tone_markers.append("口语化表达")
    if any(w in content for w in ["FDA", "EMA", "CSCO"]):
        tone_markers.append("专业权威")
    if any(w in content for w in ["然而", "但是", "不过"]):
        tone_markers.append("批判性思考")
    
    # Syntax patterns
    if re.search(r"[，,][^，,。！？]*[，,]", content):
        syntax_patterns.append("插入语修饰")
    if re.search(r"[0-9]+[%％]", content):
        syntax_patterns.append("数据嵌入")
    if re.search(r"[（(][^）)]+[）)]", content):
        syntax_patterns.append("括号补充说明")
    if "——" in content:
        syntax_patterns.append("破折号强调")
    
    return {
        "tone_markers": tone_markers[:4] or ["专业客观"],
        "syntax_patterns": syntax_patterns[:4] or ["标准陈述"]
    }

def extract_evidence_pattern(content: str) -> dict:
    """Extract evidence usage pattern"""
    evidence_types = []
    
    if re.search(r"ORR|OS|PFS|HR", content):
        evidence_types.append("临床终点数据")
    if re.search(r"FDA|EMA|NMPA|获批|批准", content):
        evidence_types.append("监管决策")
    if re.search(r"指南|CSCO|NCCN|推荐", content):
        evidence_types.append("临床指南")
    if re.search(r"研究|试验|TRAILBLAZER|DESTINY|CLARITY", content):
        evidence_types.append("临床研究")
    if re.search(r"\d+年|\d+月|\d+日", content):
        evidence_types.append("时间线证据")
    
    # Integration style
    integration_style = "数据驱动分析"
    if "对比" in content:
        integration_style = "对比分析+数据支撑"
    if "指南" in content:
        integration_style = "指南解读+临床实践"
    
    return {
        "evidence_types": evidence_types[:4] or ["行业资讯"],
        "integration_style": integration_style
    }

def distill_article(article_data: dict) -> dict:
    """Distill a single article"""
    article_id = article_data.get("article_id", "")
    title = article_data.get("title", "")
    content = article_data.get("content", "")
    url = article_data.get("url", "")
    publish_time = article_data.get("publish_time", "")
    source_account = article_data.get("source_account", "医界望远镜")
    
    # Generate one paragraph essence (100-300 chars)
    essence = content[:300] if len(content) > 300 else content
    # Clean up
    essence = re.sub(r"\n+", " ", essence)
    essence = re.sub(r"\s+", " ", essence)
    if len(essence) > 300:
        essence = essence[:297] + "..."
    
    # Extract topic
    topic, subtopic = extract_topic(title, content)
    
    # Determine audience
    audience = "医药从业者、临床医生"
    if "科普" in title or "大众" in content:
        audience = "大众读者"
    elif "投资" in content:
        audience = "医药投资者、行业从业者"
    
    # Extract all components
    narrative_frame = extract_narrative_frame(content, title)
    argument_skeleton = extract_argument_skeleton(content, title)
    rhetoric_devices = extract_rhetoric_devices(content)
    evidence_pattern = extract_evidence_pattern(content)
    tone_signals = extract_tone_signals(content)
    reusable_fragments = extract_reusable_fragments(content)
    
    # Build distilled JSON
    distilled = {
        "article_id": article_id,
        "normalized_title": title,
        "one_paragraph_essence": essence,
        "category": source_account,
        "topic": topic,
        "subtopic": subtopic,
        "audience": audience,
        "narrative_frame": narrative_frame,
        "argument_skeleton": argument_skeleton,
        "rhetoric_devices": rhetoric_devices,
        "evidence_usage_pattern": evidence_pattern,
        "tone_and_syntax_signals": tone_signals,
        "reusable_expression_fragments": reusable_fragments,
        "provenance": {
            "source_author": "chengongzi",
            "sub_source": "yjwyj",
            "source_file": f"{article_id}.json",
            "original_url": article_data.get("provenance", {}).get("original_url", url),
            "publish_time": publish_time,
            "distilled_at": datetime.now().isoformat()
        }
    }
    
    return distilled

def main():
    print("=" * 60)
    print("辰公子/医界望远镜 文章蒸馏脚本")
    print("=" * 60)
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Read index
    print(f"\n读取索引文件: {INDEX_FILE}")
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        index_data = json.load(f)
    
    articles = index_data.get("articles", [])
    print(f"索引中文章数量: {len(articles)}")
    
    # Process each article
    success_count = 0
    failed_articles = []
    
    for i, article_meta in enumerate(articles, 1):
        article_id = article_meta.get("article_id", "")
        article_path = article_meta.get("path", "")
        
        if not article_id or not article_path:
            print(f"  [{i}] 跳过: 缺少article_id或path")
            continue
        
        source_file = SOURCE_DIR / article_path
        
        try:
            # Read source file
            with open(source_file, "r", encoding="utf-8") as f:
                article_data = json.load(f)
            
            # Check for empty content
            content = article_data.get("content", "")
            if not content or len(content) < 100:
                print(f"  [{i}] 跳过: {article_id} (内容为空或过短)")
                continue
            
            # Distill
            distilled = distill_article(article_data)
            
            # Write output
            output_file = OUTPUT_DIR / f"{article_id}_distilled.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(distilled, f, ensure_ascii=False, indent=2)
            
            success_count += 1
            print(f"  [{i}] OK {article_id}")
            
        except Exception as e:
            failed_articles.append((article_id, str(e)))
            print(f"  [{i}] FAIL {article_id}: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("蒸馏完成")
    print("=" * 60)
    print(f"成功: {success_count} 篇")
    print(f"失败: {len(failed_articles)} 篇")
    
    if failed_articles:
        print("\n失败文章:")
        for aid, err in failed_articles:
            print(f"  - {aid}: {err}")
    
    # Write summary
    summary = {
        "distilled_at": datetime.now().isoformat(),
        "source_author": "chengongzi",
        "sub_source": "yjwyj",
        "total_in_index": len(articles),
        "successfully_distilled": success_count,
        "failed": len(failed_articles),
        "failed_articles": [aid for aid, _ in failed_articles],
        "output_directory": str(OUTPUT_DIR)
    }
    
    summary_file = OUTPUT_DIR / "_distillation_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n摘要已写入: {summary_file}")
    
    return success_count

if __name__ == "__main__":
    main()
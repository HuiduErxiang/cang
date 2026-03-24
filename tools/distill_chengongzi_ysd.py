#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Distillation script for chengongzi/ysd articles (药时代)
Processes 103 articles and generates distilled JSON files
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = BASE_DIR / "staging" / "editorial" / "source_articles" / "chengongzi" / "ysd" / "articles"
OUTPUT_DIR = BASE_DIR / "staging" / "editorial" / "distilled_articles" / "chengongzi" / "ysd"
INDEX_FILE = SOURCE_DIR / "index.json"

# Rhetoric device patterns for chengongzi style (药时代风格)
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
        r"这是.+[？?]",
    ],
    "colloquial_emphasis": [
        r"真是[。，]",
        r"不得不说",
        r"这下",
        r"可谓",
        r"这下",
        r"这下可",
    ],
    "data_citation": [
        r"\d+\.?\d*%",
        r"mOS[^\d]*\d+",
        r"mPFS[^\d]*\d+",
        r"ORR[^\d]*\d+",
        r"HR[=＝][\d.]+",
        r"\d+亿美元",
        r"\d+亿美元",
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

# Topic classification keywords (药时代文章主题更广泛)
TOPIC_KEYWORDS = {
    "新药研发": ["新药", "研发", "药物发现", "管线", "Pipeline", "临床前"],
    "肿瘤免疫": ["PD-1", "PD-L1", "免疫", "checkpoint", "免疫治疗", "IO", "CAR-T"],
    "靶向治疗": ["TKI", "靶向", "EGFR", "ALK", "HER2", "突变", "抑制剂"],
    "ADC药物": ["ADC", "T-DXd", "DS-8201", "抗体偶联", "Enhertu"],
    "阿尔茨海默": ["阿尔茨海默", "AD", "Aβ", "淀粉样", "仑卡奈", "Donanemab", "Aducanumab"],
    "疫苗": ["疫苗", "mRNA", "新冠", "COVID", "接种"],
    "代谢疾病": ["糖尿病", "GLP-1", "司美格鲁肽", "减肥", "肥胖", "NASH"],
    "临床研究": ["临床", "试验", "研究", "ORR", "OS", "PFS", "HR", "三期", "二期"],
    "监管审批": ["FDA", "NMPA", "获批", "批准", "审批", "EMA", "ODAC"],
    "企业并购": ["并购", "收购", "BD", "交易", "License", "合作"],
    "企业动态": ["裁员", "融资", "IPO", "股价", "市值"],
    "专访": ["专访", "对话", "访谈"],
}

def extract_topic(title: str, content: str) -> tuple:
    """Extract topic and subtopic from title and content"""
    text = (title + " " + content[:1500]).lower()
    
    # Check for interview/special features first
    if "专访" in title or "对话" in title or "访谈" in title:
        return "人物专访", "行业领袖"
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text:
                # Determine subtopic based on content
                if "获批" in text or "批准" in text or "FDA" in text:
                    return topic, "监管动态"
                elif "临床" in text or "试验" in text:
                    return topic, "临床研究"
                elif "指南" in text:
                    return topic, "指南解读"
                elif "专访" in text or "对话" in text:
                    return topic, "人物专访"
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
    
    # Detect frame type from title
    if "！" in title or "突发" in title or "重磅" in title or "刚刚" in title:
        frame_type = "breaking_news_analysis"
        key_elements.append("新闻驱动")
    elif "？" in title or "为何" in title or "怎么" in title or "为什么" in title:
        frame_type = "question_driven_inquiry"
        key_elements.append("问题导向")
    elif "专访" in title or "对话" in title:
        frame_type = "interview_profile"
        key_elements.append("人物专访")
    elif "指南" in title or "CSCO" in title:
        frame_type = "guideline_interpretation"
        key_elements.append("指南解读")
    elif "获批" in title or "批准" in title:
        frame_type = "regulatory_analysis"
        key_elements.append("监管分析")
    elif "股价" in title or "市值" in title or "收购" in title:
        frame_type = "market_analysis"
        key_elements.append("市场分析")
    
    # Add content-based elements
    if "对比" in content or "vs" in content.lower():
        key_elements.append("对比分析")
    if re.search(r"\d+\.?\d*%", content):
        key_elements.append("数据支撑")
    if "FDA" in content or "EMA" in content:
        key_elements.append("国际视角")
    if "专访" in content or "对话" in content:
        key_elements.append("人物故事")
    
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
        if first_para and "来源" not in first_para[:50]:
            main_claim = first_para
    
    # Supporting points
    supporting_points = []
    for p in paragraphs[1:4]:  # Next 3 paragraphs
        if len(p) > 50 and "来源" not in p[:30]:
            supporting_points.append(p[:100] + "..." if len(p) > 100 else p)
    
    # Conclusion hook - look for conclusion markers
    conclusion_hook = ""
    conclusion_markers = ["总之", "综上所述", "可以说", "不难看出", "可见", "这意", "这意味着"]
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
        r"([^。！？]*\d+亿美元[^。！？]*[。！？])",
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
    if any(w in content for w in ["FDA", "EMA", "CSCO", "NMPA"]):
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
    if re.search(r"专访|对话|访谈", content):
        evidence_types.append("人物观点")
    
    # Integration style
    integration_style = "数据驱动分析"
    if "对比" in content:
        integration_style = "对比分析+数据支撑"
    if "专访" in content or "对话" in content:
        integration_style = "人物专访+行业洞察"
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
    source_account = article_data.get("source_account", "药时代")
    
    # Get provenance from source if available
    provenance_data = article_data.get("provenance", {})
    original_url = provenance_data.get("original_url", url)
    
    # Generate one paragraph essence (100-300 chars)
    # Skip common headers like "作者 | xxx 来源 | xxx"
    essence_text = content
    # Remove HTML entities
    essence_text = re.sub(r"&nbsp;", " ", essence_text)
    essence_text = re.sub(r"&[a-z]+;", "", essence_text)
    # Clean up
    essence_text = re.sub(r"\n+", " ", essence_text)
    essence_text = re.sub(r"\s+", " ", essence_text)
    
    # Try to get meaningful content
    if len(essence_text) > 300:
        essence = essence_text[:297] + "..."
    else:
        essence = essence_text
    
    # Extract topic
    topic, subtopic = extract_topic(title, content)
    
    # Determine audience
    audience = "医药从业者、临床医生"
    if "专访" in title or "对话" in title:
        audience = "医药从业者、投资者"
    elif "投资" in content or "股价" in content or "市值" in content:
        audience = "医药投资者、行业从业者"
    elif "科普" in title or "大众" in content:
        audience = "大众读者"
    
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
            "sub_source": "ysd",
            "source_file": f"{article_id}.json",
            "original_url": original_url,
            "publish_time": publish_time,
            "distilled_at": datetime.now().isoformat()
        }
    }
    
    return distilled

def main():
    print("=" * 60)
    print("辰公子/药时代 文章蒸馏脚本")
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
    skipped_articles = []
    
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
                skipped_articles.append(article_id)
                continue
            
            # Distill
            distilled = distill_article(article_data)
            
            # Write output
            output_file = OUTPUT_DIR / f"{article_id}_distilled.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(distilled, f, ensure_ascii=False, indent=2)
            
            success_count += 1
            print(f"  [{i}] OK {article_id}")
            
            # Progress checkpoint every 10 articles
            if success_count % 10 == 0:
                print(f"  --- 进度检查点: {success_count} 篇已完成 ---")
            
        except Exception as e:
            failed_articles.append((article_id, str(e)))
            print(f"  [{i}] FAIL {article_id}: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("蒸馏完成")
    print("=" * 60)
    print(f"成功: {success_count} 篇")
    print(f"跳过: {len(skipped_articles)} 篇")
    print(f"失败: {len(failed_articles)} 篇")
    
    if failed_articles:
        print("\n失败文章:")
        for aid, err in failed_articles:
            print(f"  - {aid}: {err}")
    
    if skipped_articles:
        print("\n跳过文章 (内容为空或过短):")
        for aid in skipped_articles:
            print(f"  - {aid}")
    
    # Write summary
    summary = {
        "distilled_at": datetime.now().isoformat(),
        "source_author": "chengongzi",
        "sub_source": "ysd",
        "source_account": "药时代",
        "total_in_index": len(articles),
        "successfully_distilled": success_count,
        "skipped": len(skipped_articles),
        "skipped_articles": skipped_articles,
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
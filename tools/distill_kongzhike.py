#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kongzhike Article Distillation Script
Distills 42 KZK articles to L1/L2 writing craft assets
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Paths
BASE_DIR = Path(r"D:\汇度编辑部1\藏经阁")
SOURCE_DIR = BASE_DIR / "staging" / "editorial" / "source_articles" / "kongzhike" / "articles"
OUTPUT_DIR = BASE_DIR / "staging" / "editorial" / "distilled_articles" / "kongzhike"
L1_DIR = BASE_DIR / "l1" / "writing_craft"
L2_DIR = BASE_DIR / "l2" / "medical_playbook"
CHECKPOINT_DIR = BASE_DIR / "docs" / "checkpoints"

# Kongzhike style patterns
KONGZHIKE_PATTERNS = {
    "title_prefixes": ["【药海听涛】", "【医苑观畴】", "【特刊】"],
    "signature_metaphors": [
        ("乔峰", "武侠隐喻 - 乔峰"), ("段誉", "武侠隐喻 - 段誉"), 
        ("太祖长拳", "武侠隐喻 - 太祖长拳"), ("六脉神剑", "武侠隐喻 - 六脉神剑"),
        ("降龙十八掌", "武侠隐喻 - 降龙十八掌"), ("打狗棒法", "武侠隐喻 - 打狗棒法"),
        ("聚贤庄", "武侠隐喻 - 聚贤庄"), ("BGM", "武侠隐喻 - BGM")
    ],
    "rhetoric_patterns": {
        "consensus_teardown": [
            r"似乎并没有太多人认真关心",
            r"本能地认为只是微不足道的扰动",
            r"这种思路的问题，是仅从逻辑而无需专业判断就可以发现的",
            r"然而\s*.*\s*，\s*就因为",
            r"乃至于经常能听到",
            r"怎么看也不如"
        ],
        "source_tracing": [
            r"https?://[^\s]+",
            r"据.*估计",
            r"电话会议中",
            r"管理层说道"
        ],
        "dimensional_reduction": [
            r"医药之所以是一个工业门类，就意味着",
            r"最终要创造价值依然需要",
            r"真正.*从来都是极高的壁垒",
            r"一个比较简单粗暴的比方是"
        ],
        "self_deprecation": [
            r"在下孤陋",
            r"年少轻狂",
            r"笔者.*门外汉",
            r"恕在下孤陋",
            r"半吊子"
        ]
    }
}

def extract_title_category(title):
    """Extract article category from title prefix"""
    for prefix in KONGZHIKE_PATTERNS["title_prefixes"]:
        if prefix in title:
            return prefix.replace("【", "").replace("】", "")
    return "未分类"

def extract_rhetoric_devices(content):
    """Extract rhetoric devices from content"""
    devices = []
    
    # Consensus teardown patterns
    for pattern in KONGZHIKE_PATTERNS["rhetoric_patterns"]["consensus_teardown"]:
        matches = re.findall(pattern, content)
        if matches:
            devices.append({
                "device_type": "consensus_teardown",
                "pattern": pattern,
                "count": len(matches),
                "examples": matches[:2] if len(matches) > 0 else []
            })
    
    # Dimensional reduction patterns
    for pattern in KONGZHIKE_PATTERNS["rhetoric_patterns"]["dimensional_reduction"]:
        matches = re.findall(pattern, content)
        if matches:
            devices.append({
                "device_type": "dimensional_reduction",
                "pattern": pattern,
                "count": len(matches),
                "examples": matches[:2] if len(matches) > 0 else []
            })
    
    # Source tracing (count URLs and citations)
    urls = re.findall(r"https?://[^\s\)]+", content)
    if urls:
        devices.append({
            "device_type": "source_tracing",
            "count": len(urls),
            "examples": urls[:3]
        })
    
    # Metaphors
    for keyword, label in KONGZHIKE_PATTERNS["signature_metaphors"]:
        if keyword in content:
            devices.append({
                "device_type": "metaphor",
                "label": label,
                "keyword": keyword
            })
    
    # Self-deprecation
    for pattern in KONGZHIKE_PATTERNS["rhetoric_patterns"]["self_deprecation"]:
        if re.search(pattern, content):
            devices.append({
                "device_type": "self_deprecation",
                "pattern": pattern
            })
            break
    
    return devices

def extract_argument_skeleton(content, title):
    """Extract main argument structure"""
    # Simple extraction based on paragraph structure
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip() and len(p.strip()) > 50]
    
    skeleton = {
        "main_claim": None,
        "supporting_points": [],
        "conclusion_hook": None
    }
    
    if len(paragraphs) >= 2:
        # First substantive paragraph often contains the main claim
        skeleton["main_claim"] = paragraphs[0][:200] + "..." if len(paragraphs[0]) > 200 else paragraphs[0]
    
    # Look for conclusion indicators
    conclusion_patterns = [
        r"至此唯有再次陈述",
        r"总之",
        r"更直观一点",
        r"有幸能围观",
        r"最后"
    ]
    
    for pattern in conclusion_patterns:
        match = re.search(pattern + r"[^。]*。", content)
        if match:
            skeleton["conclusion_hook"] = match.group(0)
            break
    
    return skeleton

def extract_topic_info(title, content):
    """Extract topic and subtopic"""
    topic = "医药投资"
    subtopic = "行业分析"
    
    if "【药海听涛】" in title:
        topic = "医药投资"
        subtopic = "药物临床与商业分析"
    elif "【医苑观畴】" in title:
        topic = "医药政策"
        subtopic = "行业政策与市场分析"
    elif "【特刊】" in title:
        topic = "宏观经济"
        subtopic = "政策解读"
    
    # Refine based on content keywords
    if "FDA" in content or "临床" in content:
        subtopic = "临床与监管分析"
    elif "医保" in content or "IRA" in content:
        subtopic = "医保支付政策"
    elif "BD" in content or "授权" in content or "license" in content.lower():
        subtopic = "BD交易分析"
    
    return topic, subtopic

def extract_reusable_fragments(content):
    """Extract reusable expression fragments"""
    fragments = []
    
    # Pattern 1: Simple analogy openings
    analogy_patterns = [
        (r"一个比较简单粗暴的比方是[:：]([^。]+)。", "简单粗暴比喻", 5),
        (r"在金庸世界中[^。]+。", "武侠世界比喻", 4),
        (r"犹如[^，。]+[,，]", "明喻句式", 3)
    ]
    
    for pattern, context, score in analogy_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            fragments.append({
                "fragment": match if isinstance(match, str) else match[0],
                "context": context,
                "reusability_score": score
            })
    
    # Pattern 2: Transition phrases
    transition_patterns = [
        (r"真心关注也好，吃瓜看戏也罢[,，]([^。]+)", "反问式过渡", 4),
        (r"然而\s*[^。]{0,20}[,，]\s*就因为[^。]+。", "转折归因句式", 5),
        (r"至此唯有再次陈述以下我多次表达过的浅见[:：]([^。]+)", "总结式观点重申", 4)
    ]
    
    for pattern, context, score in transition_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if len(match) > 10:
                fragments.append({
                    "fragment": match[:100] if len(match) > 100 else match,
                    "context": context,
                    "reusability_score": score
                })
    
    return fragments[:5]  # Limit to top 5

def distill_article(article_data):
    """Distill a single article to structured format"""
    article_id = article_data["article_id"]
    title = article_data["title"]
    content = article_data["content"]
    url = article_data.get("url", "")
    publish_time = article_data.get("publish_time", "")
    
    # Extract components
    category = extract_title_category(title)
    topic, subtopic = extract_topic_info(title, content)
    rhetoric_devices = extract_rhetoric_devices(content)
    argument_skeleton = extract_argument_skeleton(content, title)
    reusable_fragments = extract_reusable_fragments(content)
    
    # Generate one-paragraph essence (first ~300 chars of substantial content)
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip() and len(p.strip()) > 30]
    essence = paragraphs[0] if paragraphs else content[:300]
    if len(essence) > 400:
        essence = essence[:400] + "..."
    
    # Build narrative frame
    narrative_frame = {
        "frame_type": "analytical_commentary",
        "key_elements": []
    }
    
    if "共识拆解" in str(rhetoric_devices):
        narrative_frame["frame_type"] = "consensus_teardown"
        narrative_frame["key_elements"].append("共识拆解")
    
    if any(d.get("device_type") == "metaphor" for d in rhetoric_devices):
        narrative_frame["key_elements"].append("武侠隐喻")
    
    if any(d.get("device_type") == "source_tracing" for d in rhetoric_devices):
        narrative_frame["key_elements"].append("溯源求证")
    
    # Build distilled output
    distilled = {
        "article_id": article_id,
        "normalized_title": title.replace("【药海听涛】", "").replace("【医苑观畴】", "").replace("【特刊】", "").strip(),
        "one_paragraph_essence": essence,
        "category": category,
        "topic": topic,
        "subtopic": subtopic,
        "audience": "医药投资者、行业从业者",
        "narrative_frame": narrative_frame,
        "argument_skeleton": argument_skeleton,
        "rhetoric_devices": rhetoric_devices,
        "evidence_usage_pattern": {
            "evidence_types": ["clinical_data", "market_data", "policy_documents"],
            "integration_style": "数据驱动+逻辑推演+常识比喻"
        },
        "tone_and_syntax_signals": {
            "tone_markers": ["analytical", "skeptical", "wry"],
            "syntax_patterns": ["反问句式", "转折归因", "简单粗暴比喻"]
        },
        "reusable_expression_fragments": reusable_fragments,
        "provenance": {
            "source_author": "kongzhike",
            "source_file": f"{article_id}.json",
            "original_url": url,
            "publish_time": publish_time,
            "distilled_at": datetime.now().isoformat()
        }
    }
    
    return distilled

def aggregate_patterns(distilled_articles):
    """Aggregate patterns across all articles for L1/L2 updates"""
    patterns = {
        "rhetoric_frequency": defaultdict(int),
        "topic_distribution": defaultdict(int),
        "metaphor_usage": defaultdict(list),
        "signature_expressions": [],
        "cross_article_patterns": []
    }
    
    for article in distilled_articles:
        # Track rhetoric device frequency
        for device in article.get("rhetoric_devices", []):
            device_type = device.get("device_type", "unknown")
            patterns["rhetoric_frequency"][device_type] += 1
        
        # Track topics
        patterns["topic_distribution"][article.get("topic", "unknown")] += 1
        
        # Track metaphors with article references
        for device in article.get("rhetoric_devices", []):
            if device.get("device_type") == "metaphor":
                patterns["metaphor_usage"][device.get("label", "unknown")].append(article["article_id"])
        
        # Collect reusable fragments
        for fragment in article.get("reusable_expression_fragments", []):
            if fragment["reusability_score"] >= 4:
                patterns["signature_expressions"].append({
                    "fragment": fragment["fragment"],
                    "context": fragment["context"],
                    "source_article": article["article_id"]
                })
    
    return patterns

def main():
    print("=" * 60)
    print("Kongzhike Article Distillation")
    print("=" * 60)
    
    # Read index to get article list
    index_path = SOURCE_DIR / "index.json"
    with open(index_path, "r", encoding="utf-8") as f:
        index_data = json.load(f)
    
    articles = index_data.get("articles", [])
    print(f"Found {len(articles)} articles in index")
    
    # Distill each article
    distilled_articles = []
    for i, article_meta in enumerate(articles):
        article_id = article_meta["article_id"]
        article_path = SOURCE_DIR / article_meta["path"]
        
        try:
            with open(article_path, "r", encoding="utf-8") as f:
                article_data = json.load(f)
            
            distilled = distill_article(article_data)
            distilled_articles.append(distilled)
            
            # Write individual distilled file
            output_path = OUTPUT_DIR / f"{article_id}_distilled.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(distilled, f, ensure_ascii=False, indent=2)
            
            print(f"[{i+1}/{len(articles)}] Distilled: {article_id}")
            
        except Exception as e:
            print(f"[{i+1}/{len(articles)}] ERROR processing {article_id}: {e}")
    
    # Aggregate patterns
    print("\nAggregating patterns...")
    patterns = aggregate_patterns(distilled_articles)
    
    print(f"\nRhetoric frequency: {dict(patterns['rhetoric_frequency'])}")
    print(f"Topic distribution: {dict(patterns['topic_distribution'])}")
    
    # Write summary
    summary = {
        "distilled_at": datetime.now().isoformat(),
        "total_articles": len(distilled_articles),
        "rhetoric_frequency": dict(patterns["rhetoric_frequency"]),
        "topic_distribution": dict(patterns["topic_distribution"]),
        "metaphor_usage": {k: len(v) for k, v in patterns["metaphor_usage"].items()},
        "key_articles": [a["article_id"] for a in distilled_articles[:5]]
    }
    
    summary_path = OUTPUT_DIR / "_distillation_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\nSummary written to: {summary_path}")
    print(f"Total distilled articles: {len(distilled_articles)}")
    
    return distilled_articles, patterns

if __name__ == "__main__":
    distilled_articles, patterns = main()
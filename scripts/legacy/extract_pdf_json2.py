import fitz
import json
import re

pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2024 CSCO指南\2024CSCO胃癌诊疗指南(OCR).pdf'
doc = fitz.open(pdf_path)

# 提取关键页面内容
figures = []
tables = []
all_recommendations = []
rec_strength = []

# 扫描关键页面 - 指南的主要内容通常在中间部分
key_sections = [
    (20, 40),   # 诊断部分
    (40, 70),   # 外科治疗
    (70, 100),  # 药物治疗
    (100, 130), # 系统治疗
    (150, 170), # 随访
]

for start, end in key_sections:
    for page_num in range(start, min(end, len(doc))):
        page = doc[page_num]
        text = page.get_text()
        lines = text.split('\n')
        
        # 查找表格 - 更精确的匹配
        for line in lines:
            line = line.strip()
            # 匹配表编号
            match = re.match(r'(?:表|Table)\s*(\d+[\-\.]?\d*)[\.:\s]*(.+)', line, re.I)
            if match:
                tables.append({
                    "id": match.group(1),
                    "title": line,
                    "page": page_num + 1
                })
            
            # 匹配图编号
            fig_match = re.match(r'(?:图|Figure)\s*(\d+[\-\.]?\d*)[\.:\s]*(.+)', line, re.I)
            if fig_match:
                figures.append({
                    "id": fig_match.group(1),
                    "title": line,
                    "page": page_num + 1
                })
        
        # 查找推荐内容
        for line in lines:
            line = line.strip()
            if '推荐' in line and len(line) > 15 and len(line) < 300:
                # 过滤掉目录和页眉页脚
                if not line.startswith('2024') and 'CSCO' not in line and '胃癌' not in line[:10]:
                    all_recommendations.append({
                        "content": line,
                        "page": page_num + 1
                    })
        
        # 查找推荐等级
        for level in ['I级', 'II级', 'III级', '1级', '2级', '3级', 'I类', 'II类', 'III类']:
            if level in text:
                for line in lines:
                    if level in line and len(line) > 10 and len(line) < 300:
                        rec_strength.append({
                            "level": level,
                            "content": line.strip(),
                            "page": page_num + 1
                        })

# 去重函数
def deduplicate(items, key_len=50):
    seen = set()
    result = []
    for item in items:
        key = item["content"][:key_len] if "content" in item else str(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result

unique_recs = deduplicate(all_recommendations, 60)
unique_strength = deduplicate(rec_strength, 60)
unique_tables = deduplicate(tables, 30)
unique_figures = deduplicate(figures, 30)

# 构建最终结果
result = {
    "title": "2024 CSCO胃癌诊疗指南",
    "source": "CSCO (Chinese Society of Clinical Oncology)",
    "year": 2024,
    "language": "zh-CN",
    "total_pages": len(doc),
    "doi": None,
    "document_type": "guideline_consensus",
    "_source_pdf": "guidelines\\2024 CSCO指南\\2024CSCO胃癌诊疗指南(OCR).pdf",
    "issuing_body": "CSCO (中国临床肿瘤学会)",
    "disease_area": "胃癌 (Gastric Cancer)",
    "target_population": "胃癌患者",
    "key_recommendations": unique_recs[:50],
    "recommendation_strength": unique_strength[:30],
    "key_pages": {
        "cover": 1,
        "table_of_contents": [2, 3, 4],
        "diagnosis": list(range(20, 40)),
        "surgical_treatment": list(range(40, 70)),
        "systemic_therapy": list(range(70, 130)),
        "follow_up": list(range(150, min(170, len(doc)+1)))
    },
    "figures": unique_figures[:20],
    "tables": unique_tables[:30]
}

print(json.dumps(result, ensure_ascii=False, indent=2))
doc.close()

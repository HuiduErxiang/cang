import fitz
import json
import re

pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2024 CSCO指南\2024CSCO胃癌诊疗指南(OCR).pdf'
doc = fitz.open(pdf_path)

figures = []
tables = []
all_recommendations = []
rec_strength_list = []

# 扫描整个文档的关键部分
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or len(line) > 500:
            continue
            
        # 匹配表格 - 任何包含"表"的行
        if '表' in line and re.search(r'表\s*\d', line):
            tables.append({
                "id": re.search(r'表\s*\d[\d\-\.]*', line).group() if re.search(r'表\s*\d[\d\-\.]*', line) else None,
                "title": line[:200],
                "page": page_num + 1
            })
        
        # 匹配图 - 任何包含"图"的行
        if '图' in line and re.search(r'图\s*\d', line) and '胃癌' not in line[:5]:
            figures.append({
                "id": re.search(r'图\s*\d[\d\-\.]*', line).group() if re.search(r'图\s*\d[\d\-\.]*', line) else None,
                "title": line[:200],
                "page": page_num + 1
            })
        
        # 推荐内容 - 更精确的匹配
        if '推荐' in line and len(line) > 15 and len(line) < 350:
            # 过滤掉目录、页眉、页脚
            skip_keywords = ['2024', 'CSCO', '目录', '附录', '页', '====', '----']
            if not any(kw in line for kw in skip_keywords):
                all_recommendations.append({
                    "content": line,
                    "page": page_num + 1
                })
        
        # 推荐等级
        for level in ['I级', 'II级', 'III级', '1级', '2级', '3级']:
            if level in line and len(line) > 10 and len(line) < 350:
                rec_strength_list.append({
                    "level": level,
                    "content": line[:280],
                    "page": page_num + 1
                })

# 去重
def deduplicate(items, key_func):
    seen = set()
    result = []
    for item in items:
        key = key_func(item)
        if key not in seen and key:
            seen.add(key)
            result.append(item)
    return result

unique_recs = deduplicate(all_recommendations, lambda x: x["content"][:50])[:50]
unique_strength = deduplicate(rec_strength_list, lambda x: f"{x.get('level', '')}_{x['content'][:40]}")[:25]
unique_tables = deduplicate(tables, lambda x: f"{x.get('id', '')}_{x['page']}")[:30]
unique_figures = deduplicate(figures, lambda x: f"{x.get('id', '')}_{x['page']}")[:20]

# 确保所有必需的字段都存在
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
    "key_recommendations": unique_recs,
    "recommendation_strength": unique_strength,
    "key_pages": {
        "cover": 1,
        "table_of_contents": [2, 3, 4],
        "introduction": list(range(5, 20)),
        "diagnosis": list(range(20, 40)),
        "surgical_treatment": list(range(40, 70)),
        "systemic_therapy": list(range(70, 130)),
        "supportive_care": list(range(120, 150)),
        "follow_up": list(range(150, min(170, len(doc)+1))),
        "references": list(range(170, len(doc)+1))
    },
    "figures": unique_figures,
    "tables": unique_tables
}

print(json.dumps(result, ensure_ascii=False, indent=2))
doc.close()

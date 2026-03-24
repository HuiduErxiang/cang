import fitz
import json
import re

pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2024 CSCO指南\2024CSCO胃癌诊疗指南(OCR).pdf'
doc = fitz.open(pdf_path)

# 提取关键页面内容
figures = []
tables = []

# 扫描前30页和后30页以及中间的关键页面
scan_pages = list(range(0, min(30, len(doc)))) + list(range(max(0, len(doc)-30), len(doc))) + [40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]
scan_pages = sorted(set(scan_pages))

for page_num in scan_pages:
    if page_num >= len(doc):
        continue
    page = doc[page_num]
    text = page.get_text()
    
    # 查找表格
    if '表' in text or 'Table' in text:
        lines = text.split('\n')
        for i, line in enumerate(lines):
            match = re.search(r'表\s*\d+[\.\s]*(.+)', line)
            if match:
                tables.append({
                    "id": re.search(r'表\s*\d+', line).group(),
                    "title": line.strip(),
                    "page": page_num + 1
                })
    
    # 查找图片/图
    if '图' in text:
        lines = text.split('\n')
        for i, line in enumerate(lines):
            match = re.search(r'图\s*\d+[\.\s]*(.+)', line)
            if match:
                figures.append({
                    "id": re.search(r'图\s*\d+', line).group(),
                    "title": line.strip(),
                    "page": page_num + 1
                })

# 尝试提取更多关键推荐
recommendations = []
rec_strength = []

for page_num in range(30, min(160, len(doc))):
    page = doc[page_num]
    text = page.get_text()
    
    # 查找包含"推荐"的行
    if '推荐' in text:
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if '推荐' in line and len(line) > 15 and len(line) < 250:
                recommendations.append({
                    "content": line,
                    "page": page_num + 1
                })
    
    # 查找推荐等级
    for level in ['I级推荐', 'II级推荐', 'III级推荐', '1级推荐', '2级推荐', '3级推荐']:
        if level in text:
            lines = text.split('\n')
            for line in lines:
                if level in line and len(line) > 10:
                    rec_strength.append({
                        "level": level,
                        "content": line.strip(),
                        "page": page_num + 1
                    })

# 去重
unique_recs = []
seen = set()
for rec in recommendations:
    key = rec["content"][:50]
    if key not in seen:
        seen.add(key)
        unique_recs.append(rec)

unique_strength = []
seen = set()
for s in rec_strength:
    key = s["content"][:50]
    if key not in seen:
        seen.add(key)
        unique_strength.append(s)

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
    "key_recommendations": unique_recs[:30],
    "recommendation_strength": unique_strength[:20],
    "key_pages": {
        "cover": 1,
        "table_of_contents": [2, 3, 4],
        "diagnosis": [5, 6, 7, 8, 9, 10],
        "treatment": list(range(11, 80)),
        "systemic_therapy": list(range(50, 120)),
        "follow_up": list(range(170, min(180, len(doc)+1)))
    },
    "figures": figures[:20],
    "tables": tables[:30]
}

print(json.dumps(result, ensure_ascii=False, indent=2))
doc.close()

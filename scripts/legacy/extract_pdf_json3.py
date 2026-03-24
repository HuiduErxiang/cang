import fitz
import json
import re

pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2024 CSCO指南\2024CSCO胃癌诊疗指南(OCR).pdf'
doc = fitz.open(pdf_path)

figures = []
tables = []
all_recommendations = []
rec_strength_list = []

# 扫描更多页面，包括中间的系统治疗部分
scan_ranges = [
    (0, 30),      # 前言和目录
    (50, 80),     # 系统治疗 - 一线治疗
    (80, 110),    # 二线/三线治疗
    (110, 140),   # 特殊人群
    (140, 170),   # 支持治疗
]

for start, end in scan_ranges:
    for page_num in range(start, min(end, len(doc))):
        page = doc[page_num]
        text = page.get_text()
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 匹配表格 - 多种格式
            # 表1, 表2, 表3-1, 表4.1 等
            table_patterns = [
                r'表\s*(\d+[\-\.]?\d*)[\.:\s]+(.{5,100})',
                r'Table\s*(\d+[\-\.]?\d*)[\.:\s]+(.{5,100})',
            ]
            for pattern in table_patterns:
                match = re.search(pattern, line, re.I)
                if match and len(line) < 200:
                    tables.append({
                        "id": f"表{match.group(1)}",
                        "title": line[:150],
                        "page": page_num + 1
                    })
                    break
            
            # 匹配图
            fig_patterns = [
                r'图\s*(\d+[\-\.]?\d*)[\.:\s]+(.{5,100})',
                r'Figure\s*(\d+[\-\.]?\d*)[\.:\s]+(.{5,100})',
            ]
            for pattern in fig_patterns:
                match = re.search(pattern, line, re.I)
                if match and len(line) < 200:
                    figures.append({
                        "id": f"图{match.group(1)}",
                        "title": line[:150],
                        "page": page_num + 1
                    })
                    break
            
            # 推荐内容
            if '推荐' in line and len(line) > 20 and len(line) < 300:
                # 过滤掉不相关的内容
                if not any(x in line for x in ['2024 CSCO', '页码', '目录', '指南', '===']):
                    all_recommendations.append({
                        "content": line,
                        "page": page_num + 1
                    })
            
            # 推荐等级
            strength_patterns = ['I级推荐', 'II级推荐', 'III级推荐', '1级推荐', '2级推荐', '3级推荐']
            for pattern in strength_patterns:
                if pattern in line and len(line) > 15 and len(line) < 300:
                    rec_strength_list.append({
                        "level": pattern,
                        "content": line[:250],
                        "page": page_num + 1
                    })

# 去重
def deduplicate(items, key_func):
    seen = set()
    result = []
    for item in items:
        key = key_func(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result

unique_recs = deduplicate(all_recommendations, lambda x: x["content"][:60])
unique_strength = deduplicate(rec_strength_list, lambda x: x["content"][:60])
unique_tables = deduplicate(tables, lambda x: f"{x['id']}_{x['page']}")
unique_figures = deduplicate(figures, lambda x: f"{x['id']}_{x['page']}")

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
    "key_recommendations": unique_recs[:40],
    "recommendation_strength": unique_strength[:20],
    "key_pages": {
        "cover": 1,
        "table_of_contents": [2, 3, 4],
        "diagnosis": list(range(20, 40)),
        "surgical_treatment": list(range(40, 70)),
        "systemic_therapy": list(range(70, 130)),
        "supportive_care": list(range(120, 150)),
        "follow_up": list(range(150, min(170, len(doc)+1)))
    },
    "figures": unique_figures[:15],
    "tables": unique_tables[:25]
}

print(json.dumps(result, ensure_ascii=False, indent=2))
doc.close()

import fitz
import json
import re

pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2024 CSCO指南\2024CSCO胃癌诊疗指南(OCR).pdf'
doc = fitz.open(pdf_path)

# 存储提取的内容
all_recommendations = []
rec_strength_list = []
treatment_regimens = []
special_notes = []

# 扫描关键页面
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 10 or len(line) > 400:
            continue
        
        # 跳过页眉页脚
        if any(kw in line for kw in ['2024 CSCO', '胃癌诊疗指南', '===', '---']):
            continue
        
        # 推荐内容
        if '推荐' in line:
            all_recommendations.append({
                "content": line,
                "page": page_num + 1
            })
        
        # 推荐等级
        for level in ['I级推荐', 'II级推荐', 'III级推荐', '1级推荐', '2级推荐', '3级推荐', '1类', '2A类', '2B类', '3类']:
            if level in line:
                rec_strength_list.append({
                    "level": level,
                    "content": line[:300],
                    "page": page_num + 1
                })
        
        # 治疗方案/药物方案
        regimen_patterns = ['SOX', 'XELOX', 'FOLFOX', 'FLOT', 'DOS', 'FP', 'SP', 'DCF', 'ECF', 'HER2', 'PD-1', 'PD-L1']
        if any(p in line for p in regimen_patterns) and len(line) > 20:
            treatment_regimens.append({
                "regimen": line[:250],
                "page": page_num + 1
            })

# 去重函数
def dedup(items, key_len=60):
    seen = set()
    result = []
    for item in items:
        key = item.get("content", item.get("regimen", str(item)))[:key_len]
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result

unique_recs = dedup(all_recommendations, 50)[:40]
unique_strength = dedup(rec_strength_list, 60)[:30]
unique_regimens = dedup(treatment_regimens, 80)[:25]

# 构建最终的JSON结果
result = {
    "title": "2024 CSCO胃癌诊疗指南",
    "source": "CSCO (Chinese Society of Clinical Oncology)",
    "year": 2024,
    "language": "zh-CN",
    "total_pages": 193,
    "doi": None,
    "document_type": "guideline_consensus",
    "_source_pdf": "guidelines\\2024 CSCO指南\\2024CSCO胃癌诊疗指南(OCR).pdf",
    "issuing_body": "CSCO (中国临床肿瘤学会)",
    "disease_area": "胃癌 (Gastric Cancer)",
    "target_population": "胃癌患者",
    "key_recommendations": unique_recs,
    "recommendation_strength": unique_strength,
    "treatment_regimens": unique_regimens,
    "key_pages": {
        "cover": 1,
        "table_of_contents": [2, 3, 4],
        "introduction": list(range(5, 20)),
        "diagnosis": list(range(20, 40)),
        "surgical_treatment": list(range(40, 70)),
        "systemic_therapy": list(range(70, 130)),
        "supportive_care": list(range(120, 150)),
        "follow_up": list(range(150, 170)),
        "references": list(range(170, 194))
    },
    "figures": [],
    "tables": []
}

print(json.dumps(result, ensure_ascii=False, indent=2))
doc.close()

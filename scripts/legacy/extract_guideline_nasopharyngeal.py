import fitz
import json
import re

pdf_path = r"D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2023 CSCO指南\2023CSCO鼻咽癌诊疗指南.pdf"

doc = fitz.open(pdf_path)
total_pages = len(doc)

print(f"PDF页数: {total_pages}")
print(f"PDF元数据: {doc.metadata}")

# 提取所有页面内容
all_pages = []
for i in range(total_pages):
    page = doc[i]
    text = page.get_text()
    all_pages.append({"page": i+1, "text": text})

# 查找表格和图
tables = []
figures = []

for i in range(total_pages):
    page = doc[i]
    text = page.get_text()
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        # 匹配表/Table
        if re.match(r'^(表|Table)\s*\d+', line):
            if len(line) < 300:
                tables.append({"page": i+1, "description": line})
        # 匹配图/Figure
        elif re.match(r'^(图|Figure)\s*\d+', line):
            if len(line) < 300:
                figures.append({"page": i+1, "description": line})

# 查找关键推荐内容
key_recommendations = []
key_pages = []

# 搜索关键词
keywords = ["推荐", "建议", "一线治疗", "放疗", "化疗", "分期", "诊断", "随访"]

for i, p in enumerate(all_pages):
    text = p['text']
    # 查找包含关键推荐的内容
    if '推荐' in text or '建议' in text:
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 500:
                if line.startswith('推荐') or line.startswith('1') or line.startswith('2') or line.startswith('3'):
                    if any(kw in line for kw in keywords):
                        key_recommendations.append({"content": line, "page": i+1})
    
    # 查找关键页面
    if any(kw in text for kw in ["摘要", "诊断", "分期", "治疗", "随访", "推荐意见"]):
        key_pages.append(i+1)

# 去重并限制数量
key_recommendations = key_recommendations[:50]
key_pages = sorted(list(set(key_pages)))

# 提取标题
first_page_text = all_pages[0]['text']
title_match = re.search(r'鼻咽癌.*?指南', first_page_text)
title = title_match.group(0) if title_match else "2023 CSCO鼻咽癌诊疗指南"

# 提取年份
year_match = re.search(r'2023', title)
year = 2023 if year_match else None

# 输出生成JSON结构
guideline_data = {
    "title": title,
    "source": "CSCO (Chinese Society of Clinical Oncology)",
    "year": 2023,
    "language": "zh-CN",
    "total_pages": total_pages,
    "doi": None,
    "document_type": "guideline_consensus",
    "_source_pdf": "guidelines\\2023 CSCO指南\\2023CSCO鼻咽癌诊疗指南.pdf",
    "issuing_body": "中国临床肿瘤学会 (CSCO)",
    "disease_area": "鼻咽癌 (Nasopharyngeal Carcinoma)",
    "target_population": "中国鼻咽癌患者",
    "key_recommendations": key_recommendations[:30],
    "recommendation_strength": None,
    "key_pages": key_pages[:20],
    "figures": figures[:20],
    "tables": tables[:20]
}

# 保存JSON
output_path = r"D:\汇度编辑部1\藏经阁\guideline_nasopharyngeal_output.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(guideline_data, f, ensure_ascii=False, indent=2)

print(f"\n输出已保存到: {output_path}")
print(f"\n找到的表格数: {len(tables)}")
print(f"找到的图数: {len(figures)}")
print(f"关键推荐数: {len(key_recommendations)}")
print(f"关键页数: {len(key_pages)}")

# 打印前10页内容摘要
print("\n=== 前10页内容摘要 ===")
for i in range(min(10, total_pages)):
    text = all_pages[i]['text'][:500].replace('\n', ' ')
    print(f"\n第{i+1}页: {text}...")

doc.close()

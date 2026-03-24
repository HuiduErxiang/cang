import fitz
import json
import re

pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2026\中国抗癌协会乳腺癌诊治指南与规范（2026年版）.pdf'
doc = fitz.open(pdf_path)

total_pages = len(doc)

# 提取关键推荐意见
key_recommendations = []
figures = []
tables = []

# 扫描所有页面提取信息
for page_idx in range(total_pages):
    page = doc[page_idx]
    text = page.get_text()
    page_num = page_idx + 1
    
    # 查找推荐（带编号的段落）
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if len(line) > 15:
            # 匹配中文编号格式
            if re.match(r'^[⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽①②③④⑤⑥⑦⑧⑨⑽]', line):
                key_recommendations.append({
                    'content': line[:300],
                    'page': page_num
                })
    
    # 更宽泛的表格和图搜索
    # 查找表格
    table_patterns = [
        r'附录[IVX\d]+',  # 附录
        r'表\s*\d+[\-\.]?\d*',  # 表1, 表2-1等
        r'Table\s*\d+',  # Table 1
    ]
    for pattern in table_patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            if not any(t['id'] == m for t in tables):
                tables.append({
                    'id': m,
                    'description': f'{m} (具体内容见原文)',
                    'page': page_num
                })
    
    # 查找图
    fig_patterns = [
        r'图\s*\d+[\-\.]?\d*',  # 图1, 图2-1等
        r'Figure\s*\d+',  # Figure 1
    ]
    for pattern in fig_patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            if not any(f['id'] == m for f in figures):
                figures.append({
                    'id': m,
                    'description': f'{m} (具体内容见原文)',
                    'page': page_num
                })

doc.close()

# 去重
tables = list({t['id']: t for t in tables}.values())
figures = list({f['id']: f for f in figures}.values())

print(f"Total pages: {total_pages}")
print(f"Recommendations found: {len(key_recommendations)}")
print(f"Tables found: {len(tables)}")
print(f"Figures found: {len(figures)}")

print("\n=== Tables ===")
for t in tables[:20]:
    print(f"Page {t['page']}: {t['id']}")

print("\n=== Figures ===")
for f in figures[:20]:
    print(f"Page {f['page']}: {f['id']}")

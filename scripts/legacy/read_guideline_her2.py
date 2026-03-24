import fitz
import json

pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\胃癌抗HER2治疗中国专家共识(2024年版).pdf'
doc = fitz.open(pdf_path)

# 获取所有页面内容
all_text = ''
pages_content = []
for i in range(len(doc)):
    page = doc[i]
    text = page.get_text()
    pages_content.append({
        'page_num': i + 1,
        'text': text
    })
    all_text += text

total_pages = len(doc)

# 输出所有页面内容
for p in pages_content:
    print(f'=== Page {p["page_num"]} ===')
    print(p['text'][:4000])
    print()

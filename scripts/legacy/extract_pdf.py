import fitz
import json

pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\oncology\lung_cancer\NSCLC\KRAS\CodeBreaK 200研究.pdf'
doc = fitz.open(pdf_path)

# 读取所有页面内容
pages_content = []
for i in range(len(doc)):
    page = doc[i]
    pages_content.append(page.get_text())

# 搜索Figure和Table
figures_info = []
tables_info = []

for i, text in enumerate(pages_content):
    lines = text.split('\n')
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith('Figure '):
            figures_info.append({'page': i+1, 'info': line_stripped[:200]})
        if line_stripped.startswith('Table '):
            tables_info.append({'page': i+1, 'info': line_stripped[:200]})

print('=== Figures found ===')
for f in figures_info:
    print(f)

print('\n=== Tables found ===')
for t in tables_info:
    print(t)

# 查找关键结果页码
print('\n=== Searching for key findings ===')
key_phrases = ['progression-free survival', 'overall survival', 'hazard ratio', 'median', 'p=0.0017', 'objective response']
for i, text in enumerate(pages_content):
    for phrase in key_phrases:
        if phrase.lower() in text.lower():
            print(f'Page {i+1}: contains "{phrase}"')
            break

# 打印第7页内容（可能有结果）
print('\n=== Page 7 content (partial) ===')
print(pages_content[6][:3000])

print('\n=== Page 8 content (partial) ===')
print(pages_content[7][:3000])

doc.close()

import fitz
import re
pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\oncology\gastric_cancer\免疫一线\COMPASSION-03补充资料.pdf'
doc = fitz.open(pdf_path)
page2_text = doc[1].get_text()

# 更简单的方法 - 按行查找表格引用
lines = page2_text.split('\n')
current_table = None
current_title = None
tables = []

for line in lines:
    match = re.match(r'Table (S\d+)\.\s*(.+)', line)
    if match:
        if current_table and current_title:
            # 查找当前表格的页码
            page_match = re.search(r'\.{3,}\s*(\d+)', line)
            if page_match:
                tables.append({
                    'id': current_table,
                    'title': current_title.strip(),
                    'page': int(page_match.group(1))
                })
        current_table = match.group(1)
        current_title = match.group(2)
    elif current_table and current_title:
        # 检查是否是页码行
        page_match = re.search(r'\.{3,}\s*(\d+)\s*$', line)
        if page_match:
            tables.append({
                'id': current_table,
                'title': current_title.strip(),
                'page': int(page_match.group(1))
            })
            current_table = None
            current_title = None
        else:
            current_title += ' ' + line.strip()

for t in tables[:15]:
    print(f"{t['id']}: {t['title'][:70]}... (Page {t['page']})")

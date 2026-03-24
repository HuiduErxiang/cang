import fitz

pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2025 CSCO指南\2025 CSCO胃癌指南.pdf'
doc = fitz.open(pdf_path)

# 检查前30页
for page_num in range(30):
    page = doc[page_num]
    text = page.get_text()
    print(f"\n=== Page {page_num + 1} ===")
    print(text[:1500])
    print("...")

doc.close()

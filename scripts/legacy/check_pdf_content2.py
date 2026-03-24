import fitz

pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2025 CSCO指南\2025 CSCO胃癌指南.pdf'
doc = fitz.open(pdf_path)

with open('pdf_check_output.txt', 'w', encoding='utf-8') as f:
    # 检查前30页
    for page_num in range(30):
        page = doc[page_num]
        text = page.get_text()
        f.write(f"\n=== Page {page_num + 1} ===\n")
        f.write(text[:2000])
        f.write("\n...\n")

print("Output saved to pdf_check_output.txt")
doc.close()

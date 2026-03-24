import fitz  # PyMuPDF
import sys
import json

pdf_path = r"D:\汇度编辑部1\藏经阁\raw\pdf\cardiology\anticoagulation\ROCKET-AF补充附录.pdf"

doc = fitz.open(pdf_path)

total_pages = doc.page_count
print(f"Total pages: {total_pages}")

# 提取所有页面的文本内容
full_text = ""
for page_num in range(total_pages):
    page = doc.load_page(page_num)
    text = page.get_text()
    full_text += f"\n--- Page {page_num + 1} ---\n{text}"

print(full_text[:30000])  # 先打印前30000字符

# 如果有更多内容，继续打印
if len(full_text) > 30000:
    print("\n...[内容继续]...\n")
    print(full_text[30000:])

doc.close()

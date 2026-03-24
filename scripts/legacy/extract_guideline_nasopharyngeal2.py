import fitz
import json
import re

pdf_path = r"D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2023 CSCO指南\2023CSCO鼻咽癌诊疗指南.pdf"

doc = fitz.open(pdf_path)
total_pages = len(doc)

print(f"PDF页数: {total_pages}")

# 保存完整内容到文件用于检查
with open("temp_nasopharyngeal_full.txt", "w", encoding="utf-8") as f:
    for i in range(min(50, total_pages)):
        page = doc[i]
        text = page.get_text()
        f.write(f"\n{'='*50}\n第{i+1}页\n{'='*50}\n")
        f.write(text)
        f.write("\n")

# 打印前几页详细内容
print("\n=== 详细内容检查 ===")
for i in range(min(5, total_pages)):
    page = doc[i]
    text = page.get_text()
    print(f"\n--- 第{i+1}页 (长度: {len(text)}) ---")
    print(repr(text[:2000]))

doc.close()

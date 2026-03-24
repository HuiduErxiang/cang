import fitz  # PyMuPDF
import os

pdf_path = r"D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2025 CSCO指南\2025 CSCO胃癌指南.pdf"
doc = fitz.open(pdf_path)

# Extract key pages with recommendation tables
key_pages = [1, 13, 14, 21, 22, 23, 24, 25, 26, 75, 76, 77, 78]

for page_num in key_pages:
    if page_num <= len(doc):
        page = doc[page_num - 1]
        pix = page.get_pixmap(dpi=150)
        output_path = f"temp_gastric_page_{page_num}.png"
        pix.save(output_path)
        print(f"Saved page {page_num} to: {output_path}")

doc.close()
print("\nDone!")

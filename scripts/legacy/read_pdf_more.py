import fitz  # PyMuPDF
import os

pdf_path = r"D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2025 CSCO指南\2025 CSCO胃癌指南.pdf"
doc = fitz.open(pdf_path)

# Extract key pages for analysis
# Pages 4-10: likely table of contents and introduction
# Pages with recommendations will be scattered

key_pages = [4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]

for page_num in key_pages:
    if page_num <= len(doc):
        page = doc[page_num - 1]
        pix = page.get_pixmap(dpi=150)
        output_path = f"temp_gastric_page_{page_num}.png"
        pix.save(output_path)
        print(f"Saved page {page_num} to: {output_path}")

doc.close()
print("\nDone!")

import fitz  # PyMuPDF
import os

pdf_path = r"D:\汇度编辑部1\藏经阁\raw\pdf\conferences\2025_asco_gi\2025 ASCO GI 会议幻灯集锦（中文版）-恒瑞医学\2025 ASCO GI 肝癌领域研究进展-恒瑞医学.pdf"
output_dir = r"D:\汇度编辑部1\藏经阁\temp_hcc_asco_images"

os.makedirs(output_dir, exist_ok=True)

doc = fitz.open(pdf_path)

print(f"Converting {len(doc)} pages to images...")

# Convert first few pages and some key pages
pages_to_convert = list(range(1, min(11, len(doc)+1)))  # First 10 pages

for page_num in pages_to_convert:
    page = doc[page_num - 1]
    # Render at 2x zoom for better readability
    mat = fitz.Matrix(2, 2)
    pix = page.get_pixmap(matrix=mat)
    output_path = os.path.join(output_dir, f"page_{page_num}.png")
    pix.save(output_path)
    print(f"Saved page {page_num}")

# Also convert some middle pages for more content
for page_num in [20, 30, 40, 50, 60, 70, 80, 89]:
    if page_num <= len(doc) and page_num not in pages_to_convert:
        page = doc[page_num - 1]
        mat = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat)
        output_path = os.path.join(output_dir, f"page_{page_num}.png")
        pix.save(output_path)
        print(f"Saved page {page_num}")

doc.close()
print("Conversion complete!")
